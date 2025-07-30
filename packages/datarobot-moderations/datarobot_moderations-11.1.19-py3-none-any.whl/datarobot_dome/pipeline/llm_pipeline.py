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
import logging
import math
import os
from datetime import datetime
from datetime import timezone

import numpy as np
import yaml
from datarobot.enums import CustomMetricAggregationType
from datarobot.enums import CustomMetricDirectionality

from datarobot_dome.async_http_client import AsyncHTTPClient
from datarobot_dome.constants import CUSTOM_METRIC_DESCRIPTION_SUFFIX
from datarobot_dome.constants import DEFAULT_PROMPT_COLUMN_NAME
from datarobot_dome.constants import LOGGER_NAME_PREFIX
from datarobot_dome.constants import GuardAction
from datarobot_dome.constants import GuardOperatorType
from datarobot_dome.constants import GuardStage
from datarobot_dome.guard import GuardFactory
from datarobot_dome.guard import moderation_config_trafaret
from datarobot_dome.guard_helpers import get_rouge_1_scorer
from datarobot_dome.pipeline.pipeline import Pipeline

CUSTOM_METRICS_BULK_UPLOAD_API_PREFIX = "deployments"
CUSTOM_METRICS_BULK_UPLOAD_API_SUFFIX = "customMetrics/bulkUpload/"


def get_stage_str(stage):
    return "Prompts" if stage == GuardStage.PROMPT else "Responses"


def get_blocked_custom_metric(stage):
    return {
        "name": f"Blocked {get_stage_str(stage)}",
        "directionality": CustomMetricDirectionality.LOWER_IS_BETTER,
        "units": "count",
        "type": CustomMetricAggregationType.SUM,
        "baselineValue": 0,
        "isModelSpecific": True,
        "timeStep": "hour",
        "description": (
            f"Number of blocked {get_stage_str(stage)}.  {CUSTOM_METRIC_DESCRIPTION_SUFFIX}"
        ),
    }


def get_total_custom_metric(stage):
    return {
        "name": f"Total {get_stage_str(stage)}",
        "directionality": CustomMetricDirectionality.HIGHER_IS_BETTER,
        "units": "count",
        "type": CustomMetricAggregationType.SUM,
        "baselineValue": 0,
        "isModelSpecific": True,
        "timeStep": "hour",
        "description": (
            f"Total Number of {get_stage_str(stage)}.  {CUSTOM_METRIC_DESCRIPTION_SUFFIX}"
        ),
    }


prescore_guard_latency_custom_metric = {
    "name": "Prescore Guard Latency",
    "directionality": CustomMetricDirectionality.LOWER_IS_BETTER,
    "units": "seconds",
    "type": CustomMetricAggregationType.AVERAGE,
    "baselineValue": 0,
    "isModelSpecific": True,
    "timeStep": "hour",
    "description": f"Latency to execute prescore guards.  {CUSTOM_METRIC_DESCRIPTION_SUFFIX}",
}

postscore_guard_latency_custom_metric = {
    "name": "Postscore Guard Latency",
    "directionality": CustomMetricDirectionality.LOWER_IS_BETTER,
    "units": "seconds",
    "type": CustomMetricAggregationType.AVERAGE,
    "baselineValue": 0,
    "isModelSpecific": True,
    "timeStep": "hour",
    "description": f"Latency to execute postscore guards.  {CUSTOM_METRIC_DESCRIPTION_SUFFIX}",
}

score_latency = {
    "name": "LLM Score Latency",
    "directionality": CustomMetricDirectionality.LOWER_IS_BETTER,
    "units": "seconds",
    "type": CustomMetricAggregationType.AVERAGE,
    "baselineValue": 0,
    "isModelSpecific": True,
    "timeStep": "hour",
    "description": f"Latency of actual LLM Score.  {CUSTOM_METRIC_DESCRIPTION_SUFFIX}",
}


class LLMPipeline(Pipeline):
    common_message = "Custom Metrics and deployment settings will not be available"

    def __init__(self, guards_config_filename):
        self._logger = logging.getLogger(LOGGER_NAME_PREFIX + "." + self.__class__.__name__)
        self._pre_score_guards = []
        self._post_score_guards = []
        self._prompt_column_name = None
        self._response_column_name = None
        self._custom_model_dir = os.path.dirname(guards_config_filename)

        self._modifier_guard_seen = {stage: None for stage in GuardStage.ALL}
        self.auto_generate_association_ids = False

        # Dictionary of async http clients per process - its important to maintain
        # this when moderation is running with CUSTOM_MODEL_WORKERS > 1
        self.async_http_clients = {}

        self.rouge_scorer = get_rouge_1_scorer()

        with open(guards_config_filename) as f:
            input_moderation_config = yaml.safe_load(f)

        moderation_config = moderation_config_trafaret.check(input_moderation_config)
        self.guard_timeout_sec = moderation_config["timeout_sec"]
        self.guard_timeout_action = moderation_config["timeout_action"]
        self.extra_model_output_for_chat_enabled = moderation_config.get(
            "extra_model_output_for_chat_enabled", True
        )
        super().__init__(async_http_timeout_sec=self.guard_timeout_sec)

        self._add_default_custom_metrics()
        for guard_config in moderation_config["guards"]:
            if isinstance(guard_config["stage"], list):
                for stage in guard_config["stage"]:
                    self._set_guard(guard_config, stage=stage)
            else:
                self._set_guard(guard_config)

        self.create_custom_metrics_if_any()
        if self._deployment:
            self._prompt_column_name = self._deployment.model.get("prompt")
            self._response_column_name = self._deployment.model["target_name"]
        self._run_llm_in_parallel_with_pre_score_guards = False

    def get_async_http_client(self):
        # For each process we create one Async HTTP Client and any requests to
        # that process will use that same client.
        pid = os.getpid()
        if pid not in self.async_http_clients:
            self.async_http_clients[pid] = AsyncHTTPClient(self.guard_timeout_sec)

        return self.async_http_clients[pid]

    def _get_average_score_metric_definition(self, guard):
        metric_definition = guard.get_average_score_metric(guard.stage)
        if not guard.intervention:
            return metric_definition

        if guard.intervention.comparator not in [
            GuardOperatorType.GREATER_THAN,
            GuardOperatorType.LESS_THAN,
        ]:
            # For all other guard types, its not possible to define baseline value
            return metric_definition

        metric_definition["baselineValue"] = guard.intervention.threshold
        if guard.intervention.comparator == GuardOperatorType.GREATER_THAN:
            # if threshold is "greater", lower is better and vice-a-versa
            metric_definition["directionality"] = CustomMetricDirectionality.LOWER_IS_BETTER
        else:
            metric_definition["directionality"] = CustomMetricDirectionality.HIGHER_IS_BETTER

        return metric_definition

    def _set_guard(self, guard_config, stage=None):
        guard = GuardFactory().create(guard_config, stage=stage, model_dir=self._custom_model_dir)

        guard_stage = stage if stage else guard.stage
        intervention_action = guard.get_intervention_action()

        if intervention_action == GuardAction.REPLACE:
            if self._modifier_guard_seen[guard_stage]:
                modifier_guard = self._modifier_guard_seen[guard_stage]
                raise ValueError(
                    "Cannot configure more than 1 modifier guards in the "
                    f"{guard_config['stage']} stage, "
                    f"guard {modifier_guard.name} already present"
                )
            else:
                self._modifier_guard_seen[guard_stage] = guard
        self._add_guard_to_pipeline(guard)
        guard.set_pipeline(self)

        if guard.has_average_score_custom_metric():
            self.custom_metric_map[guard.get_average_score_custom_metric_name(guard_stage)] = {
                "metric_definition": self._get_average_score_metric_definition(guard)
            }

        if guard.has_latency_custom_metric():
            self.custom_metric_map[guard.get_latency_custom_metric_name()] = {
                "metric_definition": guard.get_latency_custom_metric()
            }

        if intervention_action:
            # Enforced metric for all kinds of guards, as long as they have intervention
            # action defined - even for token count
            self.custom_metric_map[
                guard.get_guard_enforced_custom_metric_name(guard_stage, intervention_action)
            ] = {
                "metric_definition": guard.get_enforced_custom_metric(
                    guard_stage, intervention_action
                )
            }
        self.custom_metrics_no_association_ids.append(guard.get_latency_custom_metric_name())

    def _add_default_custom_metrics(self):
        """Default custom metrics"""
        metric_list = [
            get_total_custom_metric(GuardStage.PROMPT),
            get_total_custom_metric(GuardStage.RESPONSE),
            prescore_guard_latency_custom_metric,
            postscore_guard_latency_custom_metric,
            score_latency,
        ]
        # Metric list so far does not need association id for reporting
        for metric in metric_list:
            self.custom_metrics_no_association_ids.append(metric["name"])

        metric_list.append(get_blocked_custom_metric(GuardStage.PROMPT))
        metric_list.append(get_blocked_custom_metric(GuardStage.RESPONSE))
        for metric in metric_list:
            self.custom_metric_map[metric["name"]] = {"metric_definition": metric}

    def _add_guard_to_pipeline(self, guard):
        if guard.stage == GuardStage.PROMPT:
            self._pre_score_guards.append(guard)
        elif guard.stage == GuardStage.RESPONSE:
            self._post_score_guards.append(guard)
        else:
            print("Ignoring invalid guard stage", guard.stage)

    def report_stage_total_inputs(self, stage, num_rows):
        if self.aggregate_custom_metric is None:
            return

        entry = self.aggregate_custom_metric[f"Total {get_stage_str(stage)}"]
        self.set_custom_metrics_aggregate_entry(entry, num_rows)

    def get_prescore_guards(self):
        return self._pre_score_guards

    def get_postscore_guards(self):
        return self._post_score_guards

    def report_stage_latency(self, latency_in_sec, stage):
        if self.aggregate_custom_metric is None:
            return

        if stage == GuardStage.PROMPT:
            metric_name = prescore_guard_latency_custom_metric["name"]
        else:
            metric_name = postscore_guard_latency_custom_metric["name"]
        entry = self.aggregate_custom_metric[metric_name]
        self.set_custom_metrics_aggregate_entry(entry, latency_in_sec)

    def report_guard_latency(self, guard, latency_in_sec):
        if guard is None or self.aggregate_custom_metric is None:
            return

        guard_latency_name = guard.get_latency_custom_metric_name()
        entry = self.aggregate_custom_metric[guard_latency_name]
        self.set_custom_metrics_aggregate_entry(entry, latency_in_sec)

    def report_score_latency(self, latency_in_sec):
        if self.aggregate_custom_metric is None:
            return

        entry = self.aggregate_custom_metric[score_latency["name"]]
        self.set_custom_metrics_aggregate_entry(entry, latency_in_sec)

    def get_input_column(self, stage):
        if stage == GuardStage.PROMPT:
            return (
                self._prompt_column_name if self._prompt_column_name else DEFAULT_PROMPT_COLUMN_NAME
            )
        else:
            # DRUM ensures that TARGET_NAME is always set as environment variable, but
            # TARGET_NAME comes in double quotes, remove those
            return (
                self._response_column_name
                if self._response_column_name
                else (os.environ.get("TARGET_NAME").replace('"', ""))
            )

    def _set_custom_metrics_individual_entry(self, metric_id, value, association_id):
        if isinstance(value, bool):
            _value = 1.0 if value else 0.0
        elif isinstance(value, np.bool_):
            _value = 1.0 if value.item() else 0.0
        elif isinstance(value, np.generic):
            _value = value.item()
        else:
            _value = value
        return {
            "customMetricId": str(metric_id),
            "value": _value,
            "associationId": str(association_id),
            "sampleSize": 1,
            "timestamp": str(datetime.now(timezone.utc).isoformat()),
        }

    def get_enforced_column_name(self, guard, stage):
        input_column = self.get_input_column(stage)
        intervention_action = guard.get_intervention_action()
        if intervention_action == GuardAction.REPLACE:
            return f"{guard.name}_replaced_{input_column}"
        else:
            return f"{guard.name}_{intervention_action}ed_{input_column}"

    def get_guard_specific_custom_metric_names(self, guard):
        intervention_action = guard.get_intervention_action()
        metric_list = []
        if guard.has_average_score_custom_metric():
            metric_list = [
                (
                    guard.get_average_score_custom_metric_name(guard.stage),
                    guard.get_metric_column_name(guard.stage),
                )
            ]
        if intervention_action:
            metric_list.append(
                (
                    guard.get_guard_enforced_custom_metric_name(guard.stage, intervention_action),
                    self.get_enforced_column_name(guard, guard.stage),
                )
            )
        return metric_list

    def _add_guard_specific_custom_metrics(self, row, guards):
        if len(guards) == 0:
            return []

        association_id = row[self._association_id_column_name]

        buckets = []
        for guard in guards:
            for metric_name, column_name in self.get_guard_specific_custom_metric_names(guard):
                if column_name not in row:
                    # It is possible metric column is missing if there is exception
                    # executing the guard.  Just continue with rest
                    self._logger.warning(
                        f"Missing {column_name} in result for guard {guard.name} "
                        f"Not reporting the value with association id {association_id}"
                    )
                    continue
                if math.isnan(row[column_name]):
                    self._logger.warning(
                        f"{column_name} in result is NaN for guard {guard.name} "
                        f"Not reporting the value with association id {association_id}"
                    )
                    continue
                custom_metric_id = self.custom_metric_map[metric_name].get("id")
                if custom_metric_id is None:
                    self._logger.warning(f"No metric id for '{metric_name}', not reporting")
                    continue
                bucket = self._set_custom_metrics_individual_entry(
                    custom_metric_id, row[column_name], association_id
                )
                buckets.append(bucket)
        return buckets

    def _get_blocked_column_name_from_result_df(self, stage):
        input_column_name = self.get_input_column(stage)
        return f"blocked_{input_column_name}"

    def _set_individual_custom_metrics_entries(self, result_df, payload):
        for index, row in result_df.iterrows():
            association_id = row[self._association_id_column_name]
            for stage in GuardStage.ALL:
                blocked_metric_name = f"Blocked {get_stage_str(stage)}"
                blocked_column_name = self._get_blocked_column_name_from_result_df(stage)
                if blocked_metric_name not in self.custom_metric_map:
                    continue
                if blocked_column_name not in result_df.columns:
                    continue
                if math.isnan(row[blocked_column_name]):
                    # If prompt is blocked, response will be NaN, so don't report it
                    continue
                custom_metric_id = self.custom_metric_map[blocked_metric_name].get("id")
                if custom_metric_id is None:
                    self._logger.warning(f"No metric id for '{blocked_metric_name}', not reporting")
                    continue
                bucket = self._set_custom_metrics_individual_entry(
                    custom_metric_id, row[blocked_column_name], association_id
                )
                payload["buckets"].append(bucket)

            buckets = self._add_guard_specific_custom_metrics(row, self.get_prescore_guards())
            payload["buckets"].extend(buckets)
            buckets = self._add_guard_specific_custom_metrics(row, self.get_postscore_guards())
            payload["buckets"].extend(buckets)

    def report_custom_metrics(self, result_df):
        if self.delayed_custom_metric_creation:
            # Flag is not set yet, so no point reporting custom metrics
            return

        if self._association_id_column_name is None:
            return

        payload = {"buckets": []}

        if self._association_id_column_name in result_df.columns:
            # Custom metrics are reported only if the association id column
            # is defined and is "present" in result_df
            self._set_individual_custom_metrics_entries(result_df, payload)

        # Ensure that "Total Prompts" and "Total Responses" are set properly too.
        for stage in GuardStage.ALL:
            entry = self.aggregate_custom_metric[f"Total {get_stage_str(stage)}"]
            if "value" not in entry:
                if stage == GuardStage.PROMPT:
                    # If No prompt guards, then all entries are in Total Prompts
                    self.set_custom_metrics_aggregate_entry(entry, result_df.shape[0])
                    latency_entry = self.aggregate_custom_metric[
                        prescore_guard_latency_custom_metric["name"]
                    ]
                    self.set_custom_metrics_aggregate_entry(latency_entry, 0.0)
                else:
                    # Prompt guards might have blocked some, so remaining will be
                    # Total Responses
                    blocked_column_name = self._get_blocked_column_name_from_result_df(
                        GuardStage.PROMPT
                    )
                    value = result_df.shape[0] - ((result_df[blocked_column_name]).sum())
                    self.set_custom_metrics_aggregate_entry(entry, value)
                    latency_entry = self.aggregate_custom_metric[
                        postscore_guard_latency_custom_metric["name"]
                    ]
                    self.set_custom_metrics_aggregate_entry(latency_entry, 0.0)

        payload = self.add_aggregate_metrics_to_payload(payload)
        self.upload_custom_metrics(payload)

    async def send_event_async(self, title, message, event_type, guard_name=None, metric_name=None):
        if self._deployment_id is None or self.async_http_client is None:
            return

        await self.async_http_client.async_report_event(
            title,
            message,
            event_type,
            self._deployment_id,
            guard_name=guard_name,
            metric_name=metric_name,
        )

    def agentic_metrics_configured(self):
        if len(self.get_postscore_guards()) == 0:
            # All Agentic metrics at response stage only
            return False

        for guard in self.get_postscore_guards():
            if guard.is_agentic:
                return True

        return False
