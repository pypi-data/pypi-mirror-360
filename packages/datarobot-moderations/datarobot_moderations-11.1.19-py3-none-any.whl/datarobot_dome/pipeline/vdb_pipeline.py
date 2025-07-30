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
from typing import Any

from datarobot.enums import CustomMetricAggregationType
from datarobot.enums import CustomMetricDirectionality

from datarobot_dome.constants import CUSTOM_METRIC_DESCRIPTION_SUFFIX
from datarobot_dome.constants import LOGGER_NAME_PREFIX
from datarobot_dome.metrics.factory import MetricScorerFactory
from datarobot_dome.metrics.metric_scorer import MetricScorer
from datarobot_dome.metrics.metric_scorer import ScorerType
from datarobot_dome.pipeline.pipeline import Pipeline

LATENCY_NAME = "VDB Score Latency"

score_latency = {
    "name": LATENCY_NAME,
    "directionality": CustomMetricDirectionality.LOWER_IS_BETTER,
    "units": "seconds",
    "type": CustomMetricAggregationType.AVERAGE,
    "baselineValue": 0,
    "isModelSpecific": True,
    "timeStep": "hour",
    "description": f"Latency of actual VDB Score. {CUSTOM_METRIC_DESCRIPTION_SUFFIX}",
}


class VDBPipeline(Pipeline):
    def __init__(self):
        super().__init__()
        self._score_configs: dict[ScorerType, dict[str, Any]] = {
            ScorerType.CITATION_TOKEN_AVERAGE: {},
            ScorerType.CITATION_TOKEN_COUNT: {},
            ScorerType.DOCUMENT_AVERAGE: {},
            ScorerType.DOCUMENT_COUNT: {},
        }
        self._scorers: list[MetricScorer] = list()
        self._logger = logging.getLogger(LOGGER_NAME_PREFIX + "." + self.__class__.__name__)
        self._add_default_custom_metrics()
        self.create_custom_metrics_if_any()
        self.create_scorers()

    def _add_default_custom_metrics(self):
        """Adds the default custom metrics based on the `_score_configs` map."""
        # create a list of tuples, so we can track the scorer type
        metric_list = [(score_latency, None)]
        for score_type, score_config in self._score_configs.items():
            metric_config = MetricScorerFactory.custom_metric_config(score_type, score_config)
            metric_list.append((metric_config, score_type))

        # Metric list so far does not need association id for reporting
        for metric_config, score_type in metric_list:
            name = metric_config["name"]
            self.custom_metrics_no_association_ids.append(name)
            self.custom_metric_map[name] = {
                "metric_definition": metric_config,
                "scorer_type": score_type,
            }

    def create_scorers(self):
        """
        Creates a scorer for each metric in the custom_metric_map list.

        NOTE: all metrics that failed to be created in DR app have been removed
        """
        if not self._deployment:
            self._logger.debug("Skipping creation of scorers due to no deployment")
            return

        input_column = self._deployment.model["target_name"]
        for metric_name, metric_data in self.custom_metric_map.items():
            score_type = metric_data.get("scorer_type")
            if not score_type:
                continue

            score_config = self._score_configs.get(score_type)
            if score_config.get("input_column") is None:
                score_config["input_column"] = input_column
            scorer = MetricScorerFactory.create(score_type, score_config)
            self._scorers.append(scorer)

    def scorers(self) -> list[MetricScorer]:
        """Get all scorers for this pipeline."""
        return self._scorers

    def record_aggregate_value(self, metric_name: str, value: Any) -> None:
        """
        Locally records the metric_name/value in the pipeline's area for aggregate metrics where the
        bulk upload with pick it up.
        """
        if self.aggregate_custom_metric is None:
            return

        entry = self.aggregate_custom_metric[metric_name]
        self.set_custom_metrics_aggregate_entry(entry, value)

    def record_score_latency(self, latency_in_sec: float):
        """Records aggregate latency metric value locally"""
        self.record_aggregate_value(LATENCY_NAME, latency_in_sec)

    def report_custom_metrics(self):
        """
        Reports all the custom-metrics to DR app.

        The bulk upload includes grabbing all the aggregated metrics.
        """
        if self.delayed_custom_metric_creation:
            # Flag is not set yet, so no point reporting custom metrics
            return

        if not self._deployment:
            # in "test" mode, there is not a deployment and therefore no custom_metrics
            return

        payload = self.add_aggregate_metrics_to_payload({"buckets": []})
        self.upload_custom_metrics(payload)
