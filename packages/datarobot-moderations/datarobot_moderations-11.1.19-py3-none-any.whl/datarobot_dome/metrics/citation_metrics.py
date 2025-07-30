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
import pandas as pd
from datarobot.enums import CustomMetricAggregationType
from datarobot.enums import CustomMetricDirectionality

from datarobot_dome.constants import CUSTOM_METRIC_DESCRIPTION_SUFFIX
from datarobot_dome.guard_helpers import get_token_count
from datarobot_dome.metrics.metric_scorer import MetricScorer

CITATION_COLUMN = "response.citations"


class CitationTokenCountScorer(MetricScorer):
    NAME = "Total Citation Tokens"
    DESCRIPTION = f"Total number of citation tokens. {CUSTOM_METRIC_DESCRIPTION_SUFFIX}"
    DIRECTIONALITY = CustomMetricDirectionality.LOWER_IS_BETTER
    UNITS = "count"
    AGGREGATION_TYPE = CustomMetricAggregationType.SUM
    BASELINE_VALUE = 0
    INPUT_COLUMN = CITATION_COLUMN

    def score(self, df: pd.DataFrame) -> float:
        column = self.input_column
        if column not in df.columns:
            return 0.0

        return sum(
            sum(get_token_count(v, self.encoding) for v in cell) for cell in df[column].values
        )


class CitationTokenAverageScorer(MetricScorer):
    NAME = "Average Citation Tokens"
    DESCRIPTION = f"Average number of citation tokens. {CUSTOM_METRIC_DESCRIPTION_SUFFIX}"
    DIRECTIONALITY = CustomMetricDirectionality.LOWER_IS_BETTER
    UNITS = "count"
    AGGREGATION_TYPE = CustomMetricAggregationType.AVERAGE
    BASELINE_VALUE = 0
    INPUT_COLUMN = CITATION_COLUMN

    def score(self, df: pd.DataFrame) -> float:
        average = 0.0
        total = 0
        count = 0
        column = self.input_column
        if column not in df.columns:
            return 0.0

        for cell in df[column].values:
            total += sum(get_token_count(v, self.encoding) for v in cell)
            count += sum(v != "" for v in cell)
            average = total / count

        return average


class DocumentCountScorer(MetricScorer):
    NAME = "Total Documents"
    DESCRIPTION = f"Total number of documents. {CUSTOM_METRIC_DESCRIPTION_SUFFIX}"
    DIRECTIONALITY = CustomMetricDirectionality.LOWER_IS_BETTER
    UNITS = "count"
    AGGREGATION_TYPE = CustomMetricAggregationType.SUM
    BASELINE_VALUE = 0
    INPUT_COLUMN = CITATION_COLUMN

    def score(self, df: pd.DataFrame) -> float:
        column = self.input_column
        if column not in df.columns:
            return 0.0

        return sum(sum(bool(v) for v in cell) for cell in df[column].values)


class DocumentAverageScorer(MetricScorer):
    NAME = "Average Documents"
    DESCRIPTION = f"Average number of documents. {CUSTOM_METRIC_DESCRIPTION_SUFFIX}"
    DIRECTIONALITY = CustomMetricDirectionality.LOWER_IS_BETTER
    UNITS = "count"
    AGGREGATION_TYPE = CustomMetricAggregationType.AVERAGE
    BASELINE_VALUE = 0
    INPUT_COLUMN = CITATION_COLUMN

    def score(self, df: pd.DataFrame) -> float:
        column = self.input_column
        if column not in df.columns:
            return 0.0

        return sum(sum(bool(v) for v in cell) for cell in df[column].values)
