#  ---------------------------------------------------------------------------------
#  Copyright (c) 2025 DataRobot, Inc. and its affiliates. All rights reserved.
#  Last updated 2025.
#
#  DataRobot, Inc. Confidential.
#  This is proprietary source code of DataRobot, Inc. and its affiliates.
#
#  This file and its contents are subject to DataRobot Tool and Utility Agreement.
#  For details, see
#  https://www.datarobot.com/wp-content/uploads/2021/07/DataRobot-Tool-and-Utility-Agreement.pdf.
#  ---------------------------------------------------------------------------------
import asyncio
import logging
import math
import os
import traceback
from datetime import datetime
from datetime import timezone

import datarobot as dr
import numpy as np
from datarobot.errors import ClientError
from datarobot.mlops.events import MLOpsEvent
from datarobot.models.deployment import CustomMetric

from datarobot_dome.async_http_client import AsyncHTTPClient
from datarobot_dome.constants import DEFAULT_GUARD_PREDICTION_TIMEOUT_IN_SEC
from datarobot_dome.constants import LOGGER_NAME_PREFIX
from datarobot_dome.constants import ModerationEventTypes

CUSTOM_METRICS_BULK_UPLOAD_API_PREFIX = "deployments"
CUSTOM_METRICS_BULK_UPLOAD_API_SUFFIX = "customMetrics/bulkUpload/"


class Pipeline:
    common_message = "Custom Metrics and deployment settings will not be available"

    def __init__(self, async_http_timeout_sec=DEFAULT_GUARD_PREDICTION_TIMEOUT_IN_SEC):
        self._logger = logging.getLogger(LOGGER_NAME_PREFIX + "." + self.__class__.__name__)
        self.custom_metric = {}
        self._deployment = None
        self._association_id_column_name = None
        self._datarobot_url = None
        self._datarobot_api_token = None
        self.dr_client = None
        self._headers = None
        self._deployment_id = None
        self._model_id = None
        self.async_http_client = None
        self._custom_metrics_bulk_upload_url = None
        self._assoc_id_specific_custom_metric_ids = list()
        self.aggregate_custom_metric = None
        self.custom_metric_map = dict()
        # List of custom metrics names which do not need the association id while reporting
        self.custom_metrics_no_association_ids = list()
        self.delayed_custom_metric_creation = False
        self.upload_custom_metrics_tasks = set()

        self.create_dr_client()

        if self._datarobot_url and self._datarobot_api_token:
            self.async_http_client = AsyncHTTPClient(async_http_timeout_sec)

    def create_dr_client(self):
        if self.dr_client:
            return

        # This URL and Token is where the custom LLM model is running.
        self._datarobot_url = os.environ.get("DATAROBOT_ENDPOINT", None)
        if self._datarobot_url is None:
            self._logger.warning(f"Missing DataRobot endpoint, {self.common_message}")
            return

        self._datarobot_api_token = os.environ.get("DATAROBOT_API_TOKEN", None)
        if self._datarobot_api_token is None:
            self._logger.warning(f"Missing DataRobot API Token, {self.common_message}")
            return

        # This is regular / default DataRobot Client
        self.dr_client = dr.Client(endpoint=self._datarobot_url, token=self._datarobot_api_token)
        self._headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._datarobot_api_token}",
        }

    def _query_self_deployment(self):
        """
        Query the details of the deployment (LLM) that this pipeline is running
        moderations for
        :return:
        """
        self._deployment_id = os.environ.get("MLOPS_DEPLOYMENT_ID", None)
        if self._deployment_id is None:
            self._logger.warning(f'Custom Model workshop "test" mode?, {self.common_message}')
            return

        # Get the model id from environ variable, because moderation lib cannot
        # query deployment each time there is scoring data.
        self._model_id = os.environ.get("MLOPS_MODEL_ID", None)
        self._logger.info(f"Model ID from env variable {self._model_id}")

        try:
            self._deployment = dr.Deployment.get(deployment_id=self._deployment_id)
            self._logger.info(f"Model ID set on the deployment {self._deployment.model['id']}")
        except Exception as e:
            self._logger.warning(
                f"Couldn't query the deployment Exception: {e}, {self.common_message}"
            )

    def _query_association_id_column_name(self):
        self._logger.info(f"Deployment ID: {self._deployment_id}")
        if self._deployment is None:
            return

        self._logger.info(f"Check Association ID Column name: {self._association_id_column_name}")
        # Apparently, the pipeline.init() is called only once when deployment is created.
        # If the association id column name is not set (we cannot set it during creation
        # of the deployment), moderation library never gets it.  So, moderation library
        # is going to query it one time during prediction request
        if self._association_id_column_name:
            return

        try:
            association_id_settings = self._deployment.get_association_id_settings()
            self._logger.debug(f"Association id settings: {association_id_settings}")
            column_names = association_id_settings.get("column_names")
            if column_names and len(column_names) > 0:
                self._association_id_column_name = column_names[0]
                self.auto_generate_association_ids = association_id_settings.get(
                    "auto_generate_id", False
                )
        except Exception as e:
            self._logger.warning(
                f"Couldn't query the association id settings, "
                f"custom metrics will not be available {e}"
            )
            self._logger.error(traceback.format_exc())

        if self._association_id_column_name is None:
            self._logger.warning(
                "Association ID column is not set on the deployment, "
                "data quality analysis will not be available"
            )
        else:
            self._logger.info(f"Association ID column name: {self._association_id_column_name}")

    def create_custom_metrics_if_any(self):
        """
        Over-arching function to create the custom-metrics in the DR app for the deployment.
        Provides some protection for inactive deployments.
        """
        self._query_self_deployment()
        if self._deployment is None:
            return

        self._custom_metrics_bulk_upload_url = (
            CUSTOM_METRICS_BULK_UPLOAD_API_PREFIX
            + "/"
            + self._deployment_id
            + "/"
            + CUSTOM_METRICS_BULK_UPLOAD_API_SUFFIX
        )
        self._logger.info(f"URL: {self._custom_metrics_bulk_upload_url}")

        if self._deployment.status == "inactive":
            self.delayed_custom_metric_creation = True
            self._logger.warning("Deployment is not active, delaying custom metric creation")
        else:
            self._logger.info("Deployment is active, creating custom metrics")
            self.create_custom_metrics()
            self.delayed_custom_metric_creation = False

    def create_custom_metrics(self):
        """
        Creates all the custom-metrics in the DR app for an active deployment.

        The `custom_metric_map` and `_requires_association_id` attributes are consulted to
        insure the appropriate data is put in place for reporting.
        """
        cleanup_metrics_list = list()
        for index, (metric_name, custom_metric) in enumerate(self.custom_metric_map.items()):
            metric_definition = custom_metric["metric_definition"]
            try:
                # We create metrics one by one, instead of using a library call.  This gives
                # us control over which are duplicates, if max limit reached etc and we can
                # take appropriate actions accordingly.  Performance wise it is same, because
                # library also runs a loop to create custom metrics one by one
                _metric_obj = CustomMetric.create(
                    deployment_id=self._deployment_id,
                    name=metric_name,
                    directionality=metric_definition["directionality"],
                    aggregation_type=metric_definition["type"],
                    time_step=metric_definition["timeStep"],
                    units=metric_definition["units"],
                    baseline_value=metric_definition["baselineValue"],
                    is_model_specific=metric_definition["isModelSpecific"],
                )
                custom_metric["id"] = _metric_obj.id
                custom_metric["requires_association_id"] = self._requires_association_id(
                    metric_name
                )
            except ClientError as e:
                if e.status_code == 409:
                    if "not unique for deployment" in e.json["message"]:
                        # Duplicate entry nothing to worry - just continue
                        self._logger.error(f"Metric '{metric_name}' already exists, skipping")
                        continue
                    elif e.json["message"].startswith("Maximum number of custom metrics reached"):
                        # Reached the limit - we can't create more
                        cleanup_metrics_list = list(self.custom_metric_map.keys())[index:]
                        title = "Failed to create custom metric"
                        message = (
                            f"Metric Name '{metric_name}', "
                            "Maximum number of custom metrics reached, "
                            f"Cannot create rest of the metrics: {cleanup_metrics_list}"
                        )
                        self._logger.error(message)
                        self.send_event_sync(
                            title, message, ModerationEventTypes.MODERATION_METRIC_CREATION_ERROR
                        )
                        # Lets not raise the exception, for now - break the loop and
                        # consolidate valid custom metrics
                        break
                # Else raise it and catch in next block
                raise
            except Exception as e:
                title = "Failed to create custom metric"
                message = f"Exception: {e} Custom metric definition: {custom_metric}"
                self._logger.error(title + " " + message)
                self._logger.error(traceback.format_exc())
                cleanup_metrics_list.append(metric_name)
                self.send_event_sync(
                    title,
                    message,
                    ModerationEventTypes.MODERATION_METRIC_CREATION_ERROR,
                    metric_name=metric_name,
                )
                # Lets again not raise exception
                continue

        # Now query all the metrics and get their custom metric ids.  Specifically,
        # required in case a metric is duplicated, in which case, we don't have its
        # id in the loop above
        #
        # We have to go through pagination - dmm list_custom_metrics does not implement
        # pagination
        custom_metrics_list = []
        offset, limit = 0, 50
        while True:
            response_list = self.dr_client.get(
                f"deployments/{self._deployment_id}/customMetrics/?offset={offset}&limit={limit}"
            ).json()
            custom_metrics_list.extend(response_list["data"])
            offset += response_list["count"]
            if response_list["next"] is None:
                break

        for metric in custom_metrics_list:
            metric_name = metric["name"]
            if metric_name not in self.custom_metric_map:
                self._logger.error(f"Metric '{metric_name}' exists at DR but not in moderation")
                continue
            self.custom_metric_map[metric_name]["id"] = metric["id"]
            self.custom_metric_map[metric_name]["requires_association_id"] = (
                self._requires_association_id(metric_name)
            )

        # These are the metrics we couldn't create - so, don't track them
        for metric_name in cleanup_metrics_list:
            if not self.custom_metric_map[metric_name].get("id"):
                self._logger.error(f"Skipping metric creation: {metric_name}")
                del self.custom_metric_map[metric_name]

    def _requires_association_id(self, metric_name):
        return metric_name not in self.custom_metrics_no_association_ids

    @property
    def prediction_url(self):
        return self._datarobot_url

    @property
    def api_token(self):
        return self._datarobot_api_token

    def get_association_id_column_name(self):
        return self._association_id_column_name

    def get_new_metrics_payload(self):
        """
        Resets the data for aggregate metrics reporting based on the `custom_metric_map`.

        It will create the custom-metrics in DR app, if they have been delayed (e.g. originally
        inactive).
        """
        if self._deployment_id is None:
            return
        if self.delayed_custom_metric_creation:
            # Try creating custom metrics now if possible
            self.create_custom_metrics_if_any()
            if self.delayed_custom_metric_creation:
                return

        self._query_association_id_column_name()

        if self._deployment is None:
            return

        self.aggregate_custom_metric = dict()
        for metric_name, metric_info in self.custom_metric_map.items():
            if not metric_info["requires_association_id"]:
                self.aggregate_custom_metric[metric_name] = {
                    "customMetricId": str(metric_info["id"])
                }

    def set_custom_metrics_aggregate_entry(self, entry, value):
        if isinstance(value, np.generic):
            entry["value"] = value.item()
        else:
            entry["value"] = value
        entry["timestamp"] = str(datetime.now(timezone.utc).isoformat())
        entry["sampleSize"] = 1

    def upload_custom_metrics(self, payload):
        if len(payload["buckets"]) == 0:
            self._logger.warning("No custom metrics to report, empty payload")
            return
        url = self._datarobot_url + "/" + self._custom_metrics_bulk_upload_url
        asyncio.run(self.async_upload_custom_metrics(url, payload))

    async def async_upload_custom_metrics(self, url, payload):
        await self.async_http_client.bulk_upload_custom_metrics(url, payload, self._deployment_id)

    def add_aggregate_metrics_to_payload(self, payload):
        """
        Takes the provided payload and add aggregate metric values to it.
        Then, uploads the updated payload to the DR app using the bulk upload url.
        """
        if self._model_id:
            payload["modelId"] = self._model_id

        for metric_name, metric_value in self.aggregate_custom_metric.items():
            if "value" not in metric_value:
                # Different exception paths - especially with asyncio can
                # end up not adding values for some aggregated custom metrics
                # Capturing them for future fixes
                self._logger.warning(f"No value for custom metric {metric_name}")
                continue
            if not math.isnan(metric_value["value"]):
                payload["buckets"].append(metric_value)

        self._logger.debug(f"Payload: {payload}")
        return payload

    @property
    def custom_metrics(self):
        return {
            metric_name: metric_info for metric_name, metric_info in self.custom_metric_map.items()
        }

    def send_event_sync(self, title, message, event_type, guard_name=None, metric_name=None):
        if self._deployment_id is None:
            return

        MLOpsEvent.report_moderation_event(
            event_type=event_type,
            title=title,
            message=message,
            deployment_id=self._deployment_id,
            metric_name=metric_name,
            guard_name=guard_name,
        )
