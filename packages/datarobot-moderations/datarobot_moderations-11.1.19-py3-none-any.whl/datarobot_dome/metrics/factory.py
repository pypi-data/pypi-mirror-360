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
from typing import Any
from typing import ClassVar
from typing import Optional

from datarobot_dome.metrics.citation_metrics import CitationTokenAverageScorer
from datarobot_dome.metrics.citation_metrics import CitationTokenCountScorer
from datarobot_dome.metrics.citation_metrics import DocumentAverageScorer
from datarobot_dome.metrics.citation_metrics import DocumentCountScorer
from datarobot_dome.metrics.metric_scorer import MetricScorer
from datarobot_dome.metrics.metric_scorer import ScorerType

METRIC_SCORE_CLASS_MAP: dict[ScorerType, ClassVar] = {
    ScorerType.CITATION_TOKEN_AVERAGE: CitationTokenAverageScorer,
    ScorerType.CITATION_TOKEN_COUNT: CitationTokenCountScorer,
    ScorerType.DOCUMENT_AVERAGE: DocumentAverageScorer,
    ScorerType.DOCUMENT_COUNT: DocumentCountScorer,
}


class MetricScorerFactory:
    @staticmethod
    def get_class(metric_type: ScorerType) -> ClassVar:
        clazz = METRIC_SCORE_CLASS_MAP.get(metric_type)
        if clazz is None:
            raise ValueError(f"Unknown metric type: {metric_type}")

        return clazz

    @staticmethod
    def create(metric_type: ScorerType, config: Optional[dict[str, Any]] = None) -> MetricScorer:
        _config = config or {}
        clazz = MetricScorerFactory.get_class(metric_type)
        return clazz(_config)

    @staticmethod
    def custom_metric_config(
        metric_type: ScorerType, config: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        _config = config or {}
        clazz = MetricScorerFactory.get_class(metric_type)
        return clazz.custom_metric_definition(_config)
