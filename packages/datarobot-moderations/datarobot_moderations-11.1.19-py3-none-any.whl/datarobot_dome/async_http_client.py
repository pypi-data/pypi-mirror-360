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
import atexit
import datetime
import logging
import os
import traceback
from http import HTTPStatus
from io import StringIO

import aiohttp
import backoff
import nest_asyncio
import pandas as pd

from datarobot_dome.constants import DATAROBOT_ACTUAL_ON_PREM_ST_SAAS_URL
from datarobot_dome.constants import DATAROBOT_CONFIGURED_ON_PREM_ST_SAAS_URL
from datarobot_dome.constants import DATAROBOT_SERVERLESS_PLATFORM
from datarobot_dome.constants import DEFAULT_GUARD_PREDICTION_TIMEOUT_IN_SEC
from datarobot_dome.constants import LOGGER_NAME_PREFIX
from datarobot_dome.constants import RETRY_COUNT
from datarobot_dome.constants import ModerationEventTypes

RETRY_STATUS_CODES = [
    HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
    HTTPStatus.BAD_GATEWAY,
    HTTPStatus.GATEWAY_TIMEOUT,
]
RETRY_AFTER_STATUS_CODES = [HTTPStatus.TOO_MANY_REQUESTS, HTTPStatus.SERVICE_UNAVAILABLE]


# We want this logger to be available for backoff too, hence defining outside the class
logger = logging.getLogger(LOGGER_NAME_PREFIX + ".AsyncHTTPClient")


# Event handlers for backoff
def _timeout_backoff_handler(details):
    logger.warning(
        f"HTTP Timeout: Backing off {details['wait']} seconds after {details['tries']} tries"
    )


def _timeout_giveup_handler(details):
    url = details["args"][1]
    logger.error(f"Giving up predicting on {url}, Retried {details['tries']} after HTTP Timeout")


def _retry_backoff_handler(details):
    status_code = details["value"].status
    message = details["value"].reason
    retry_after_value = details["value"].headers.get("Retry-After")
    logger.warning(
        f"Received status code {status_code}, message {message},"
        f" Retry-After val: {retry_after_value} "
        f"Backing off {details['wait']} seconds after {details['tries']} tries"
    )


def _retry_giveup_handler(details):
    message = (
        f"Giving up predicting on {details['args'][1]}, Retried {details['tries']} retries, "
        f"elapsed time {details['elapsed']} sec, but couldn't get predictions"
    )
    raise Exception(message)


class AsyncHTTPClient:
    def __init__(self, timeout=DEFAULT_GUARD_PREDICTION_TIMEOUT_IN_SEC):
        self._logger = logging.getLogger(LOGGER_NAME_PREFIX + "." + self.__class__.__name__)
        self.csv_headers = {
            "Content-Type": "text/csv",
            "Accept": "text/csv",
            "Authorization": f"Bearer {os.environ['DATAROBOT_API_TOKEN']}",
        }
        self.json_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {os.environ['DATAROBOT_API_TOKEN']}",
        }
        self.session = None
        self.events_url = f"{os.environ['DATAROBOT_ENDPOINT']}/remoteEvents/"

        try:
            self.loop = asyncio.get_event_loop()
        except RuntimeError as e:
            if str(e).startswith("There is no current event loop in thread") or str(e).startswith(
                "Event loop is closed"
            ):
                self.loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self.loop)
            else:
                raise
        self.loop.run_until_complete(self.__create_client_session(timeout))
        self.loop.set_debug(True)
        nest_asyncio.apply(loop=self.loop)

        atexit.register(self.shutdown)

    async def __create_client_session(self, timeout):
        client_timeout = aiohttp.ClientTimeout(
            connect=timeout, sock_connect=timeout, sock_read=timeout
        )
        # Creation of client session needs to happen within in async function
        self.session = aiohttp.ClientSession(timeout=client_timeout)

    def shutdown(self):
        asyncio.run(self.session.close())

    @staticmethod
    def is_serverless_deployment(deployment):
        if not deployment.prediction_environment:
            return False

        if deployment.prediction_environment.get("platform") == DATAROBOT_SERVERLESS_PLATFORM:
            return True

        return False

    @staticmethod
    def is_on_prem_st_saas_endpoint():
        return os.environ.get("DATAROBOT_ENDPOINT").startswith(
            DATAROBOT_CONFIGURED_ON_PREM_ST_SAAS_URL
        )

    @backoff.on_predicate(
        backoff.runtime,
        predicate=lambda r: r.status in RETRY_AFTER_STATUS_CODES,
        value=lambda r: int(r.headers.get("Retry-After", DEFAULT_GUARD_PREDICTION_TIMEOUT_IN_SEC)),
        max_time=RETRY_COUNT * DEFAULT_GUARD_PREDICTION_TIMEOUT_IN_SEC,
        max_tries=RETRY_COUNT,
        jitter=None,
        logger=logger,
        on_backoff=_retry_backoff_handler,
        on_giveup=_retry_giveup_handler,
    )
    @backoff.on_predicate(
        backoff.fibo,
        predicate=lambda r: r.status in RETRY_STATUS_CODES,
        jitter=None,
        max_tries=RETRY_COUNT,
        max_time=RETRY_COUNT * DEFAULT_GUARD_PREDICTION_TIMEOUT_IN_SEC,
        logger=logger,
        on_backoff=_retry_backoff_handler,
        on_giveup=_retry_giveup_handler,
    )
    @backoff.on_exception(
        backoff.fibo,
        asyncio.TimeoutError,
        max_tries=RETRY_COUNT,
        max_time=RETRY_COUNT * DEFAULT_GUARD_PREDICTION_TIMEOUT_IN_SEC,
        logger=logger,
        on_backoff=_timeout_backoff_handler,
        on_giveup=_timeout_giveup_handler,
        raise_on_giveup=True,
    )
    async def post_predict_request(self, url_path, input_df):
        return await self.session.post(
            url_path, data=input_df.to_csv(index=False), headers=self.csv_headers
        )

    async def predict(self, deployment, input_df):
        deployment_id = str(deployment.id)
        if self.is_on_prem_st_saas_endpoint():
            url_path = DATAROBOT_ACTUAL_ON_PREM_ST_SAAS_URL
        elif self.is_serverless_deployment(deployment):
            url_path = f"{os.environ['DATAROBOT_ENDPOINT']}"
        else:
            prediction_server = deployment.default_prediction_server
            if not prediction_server:
                raise ValueError(
                    "Can't make prediction request because Deployment object doesn't contain "
                    "default prediction server"
                )
            datarobot_key = prediction_server.get("datarobot-key")
            if datarobot_key:
                self.csv_headers["datarobot-key"] = datarobot_key

            url_path = f"{prediction_server['url']}/predApi/v1.0"

        url_path += f"/deployments/{deployment_id}/predictions"
        response = await self.post_predict_request(url_path, input_df)
        if not response.ok:
            raise Exception(
                f"Failed to get guard predictions: {response.reason} Status: {response.status}"
            )
        csv_data = await response.text()
        return pd.read_csv(StringIO(csv_data))

    async def async_report_event(
        self, title, message, event_type, deployment_id, guard_name=None, metric_name=None
    ):
        payload = {
            "title": title,
            "message": message,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "deploymentId": str(deployment_id),
            "eventType": event_type,
            "moderationData": {"guardName": "", "metricName": ""},
        }
        error_text = ""
        if metric_name:
            payload["moderationData"]["metricName"] = metric_name
            error_text = f"for metric {metric_name}"
        if guard_name:
            payload["moderationData"]["guardName"] = guard_name
            error_text = f"for guard {guard_name}"

        response = await self.session.post(self.events_url, json=payload, headers=self.json_headers)
        if response.status != HTTPStatus.CREATED:
            # Lets not raise - we just failed to report an event, let the moderation
            # continue
            logger.error(
                f"Failed to post event {event_type} {error_text} "
                f" Status: {response.status} Message: {response.reason}"
            )

    async def bulk_upload_custom_metrics(self, url, payload, deployment_id):
        self._logger.debug("Uploading custom metrics")
        try:
            response = await self.session.post(url, json=payload, headers=self.json_headers)
            if response.status != HTTPStatus.ACCEPTED:
                raise Exception(
                    f"Error uploading custom metrics: Status Code: {response.status}"
                    f"Message: {response.text}"
                )
            self._logger.info("Successfully uploaded custom metrics")
        except Exception as e:
            title = "Failed to upload custom metrics"
            message = f"Exception: {e} Payload: {payload}"
            self._logger.error(title + " " + message)
            self._logger.error(traceback.format_exc())
            await self.async_report_event(
                title,
                message,
                ModerationEventTypes.MODERATION_METRIC_REPORTING_ERROR,
                deployment_id,
            )
            # Lets not raise the exception, just walk off
