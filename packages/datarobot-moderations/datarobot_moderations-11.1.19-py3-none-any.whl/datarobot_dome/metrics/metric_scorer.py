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
from abc import ABC
from abc import abstractmethod
from enum import Enum
from typing import Any

import pandas as pd


class ScorerType(str, Enum):
    CITATION_TOKEN_AVERAGE = "CITATION_TOKEN_AVERAGE"
    CITATION_TOKEN_COUNT = "CITATION_TOKEN_COUNT"
    DOCUMENT_AVERAGE = "DOCUMENT_AVERAGE"
    DOCUMENT_COUNT = "DOCUMENT_COUNT"


class MetricScorer(ABC):
    IS_MODEL_SPECIFIC = True
    TIME_STEP = "hour"

    def __init__(
        self,
        config: dict[str, Any],
    ):
        self.config = config

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"

    @classmethod
    def custom_metric_definition(cls, config: dict[str, Any]) -> dict[str, Any]:
        """
        Generates a custom-metric configuration/definition that is used to create the
        custom-metric in the DR application.

        This is done as a class method because we create custom-metrics before creating
        the scorer.
        """
        return {
            "name": config.get("name", cls.NAME),
            "directionality": cls.DIRECTIONALITY,
            "units": cls.UNITS,
            "type": cls.AGGREGATION_TYPE,
            "baselineValue": config.get("baseline_value", cls.BASELINE_VALUE),
            "isModelSpecific": config.get("is_model_specific", cls.IS_MODEL_SPECIFIC),
            "timeStep": cls.TIME_STEP,
            "description": config.get("description", cls.DESCRIPTION),
        }

    @property
    def name(self) -> str:
        return self.config.get("name", self.NAME)

    @property
    def per_prediction(self) -> bool:
        return self.config.get("per_prediction", False)

    @property
    def input_column(self) -> str:
        return self.config.get("input_column", self.INPUT_COLUMN)

    @property
    def encoding(self) -> str:
        return self.config.get("encoding", "cl100k_base")

    @abstractmethod
    def score(self, df: pd.DataFrame) -> float:
        pass
