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
import os
from abc import ABC

import datarobot as dr
import trafaret as t
from datarobot.enums import CustomMetricAggregationType
from datarobot.enums import CustomMetricDirectionality
from deepeval.metrics import TaskCompletionMetric
from llama_index.core import Settings
from llama_index.core.evaluation import FaithfulnessEvaluator
from nemoguardrails import LLMRails
from nemoguardrails import RailsConfig
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import AgentGoalAccuracyWithoutReference

from datarobot_dome.constants import AGENT_GOAL_ACCURACY_COLUMN_NAME
from datarobot_dome.constants import COST_COLUMN_NAME
from datarobot_dome.constants import CUSTOM_METRIC_DESCRIPTION_SUFFIX
from datarobot_dome.constants import DEFAULT_GUARD_PREDICTION_TIMEOUT_IN_SEC
from datarobot_dome.constants import DEFAULT_PROMPT_COLUMN_NAME
from datarobot_dome.constants import DEFAULT_RESPONSE_COLUMN_NAME
from datarobot_dome.constants import FAITHFULLNESS_COLUMN_NAME
from datarobot_dome.constants import NEMO_GUARD_COLUMN_NAME
from datarobot_dome.constants import NEMO_GUARDRAILS_DIR
from datarobot_dome.constants import ROUGE_1_COLUMN_NAME
from datarobot_dome.constants import SPAN_PREFIX
from datarobot_dome.constants import TASK_ADHERENCE_SCORE_COLUMN_NAME
from datarobot_dome.constants import TOKEN_COUNT_COLUMN_NAME
from datarobot_dome.constants import AwsModel
from datarobot_dome.constants import CostCurrency
from datarobot_dome.constants import GoogleModel
from datarobot_dome.constants import GuardAction
from datarobot_dome.constants import GuardLLMType
from datarobot_dome.constants import GuardModelTargetType
from datarobot_dome.constants import GuardOperatorType
from datarobot_dome.constants import GuardStage
from datarobot_dome.constants import GuardTimeoutAction
from datarobot_dome.constants import GuardType
from datarobot_dome.constants import OOTBType
from datarobot_dome.guard_helpers import DEFAULT_OPEN_AI_API_VERSION
from datarobot_dome.guard_helpers import ModerationDeepEvalLLM
from datarobot_dome.guard_helpers import get_azure_openai_client
from datarobot_dome.guard_helpers import get_chat_nvidia_llm
from datarobot_dome.guard_helpers import get_datarobot_endpoint_and_token
from datarobot_dome.guard_helpers import get_llm_gateway_client
from datarobot_dome.guard_helpers import use_llm_gateway_inference
from datarobot_dome.guards.guard_llm_mixin import GuardLLMMixin

MAX_GUARD_NAME_LENGTH = 255
MAX_COLUMN_NAME_LENGTH = 255
MAX_GUARD_COLUMN_NAME_LENGTH = 255
MAX_GUARD_MESSAGE_LENGTH = 4096
MAX_GUARD_DESCRIPTION_LENGTH = 4096
OBJECT_ID_LENGTH = 24
MAX_REGEX_LENGTH = 255
MAX_URL_LENGTH = 255
MAX_TOKEN_LENGTH = 255
NEMO_THRESHOLD = "TRUE"
MAX_GUARD_CUSTOM_METRIC_BASELINE_VALUE_LIST_LENGTH = 5


cost_metric_trafaret = t.Dict(
    {
        t.Key("currency", to_name="currency", optional=True, default=CostCurrency.USD): t.Enum(
            *CostCurrency.ALL
        ),
        t.Key("input_price", to_name="input_price", optional=False): t.Float(),
        t.Key("input_unit", to_name="input_unit", optional=False): t.Int(),
        t.Key("output_price", to_name="output_price", optional=False): t.Float(),
        t.Key("output_unit", to_name="output_unit", optional=False): t.Int(),
    }
)


model_info_trafaret = t.Dict(
    {
        t.Key("class_names", to_name="class_names", optional=True): t.List(
            t.String(max_length=MAX_COLUMN_NAME_LENGTH)
        ),
        t.Key("model_id", to_name="model_id", optional=True): t.String(max_length=OBJECT_ID_LENGTH),
        t.Key("input_column_name", to_name="input_column_name", optional=False): t.String(
            max_length=MAX_COLUMN_NAME_LENGTH
        ),
        t.Key("target_name", to_name="target_name", optional=False): t.String(
            max_length=MAX_COLUMN_NAME_LENGTH
        ),
        t.Key(
            "replacement_text_column_name", to_name="replacement_text_column_name", optional=True
        ): t.Or(t.String(allow_blank=True, max_length=MAX_COLUMN_NAME_LENGTH), t.Null),
        t.Key("target_type", to_name="target_type", optional=False): t.Enum(
            *GuardModelTargetType.ALL
        ),
    },
    allow_extra=["*"],
)


model_guard_intervention_trafaret = t.Dict(
    {
        t.Key("comparand", to_name="comparand", optional=False): t.Or(
            t.String(max_length=MAX_GUARD_NAME_LENGTH),
            t.Float(),
            t.Bool(),
            t.List(t.String(max_length=MAX_GUARD_NAME_LENGTH)),
            t.List(t.Float()),
        ),
        t.Key("comparator", to_name="comparator", optional=False): t.Enum(*GuardOperatorType.ALL),
    },
    allow_extra=["*"],
)


guard_intervention_trafaret = t.Dict(
    {
        t.Key("action", to_name="action", optional=False): t.Enum(*GuardAction.ALL),
        t.Key("message", to_name="message", optional=True): t.String(
            max_length=MAX_GUARD_MESSAGE_LENGTH, allow_blank=True
        ),
        t.Key("conditions", to_name="conditions", optional=True): t.Or(
            t.List(
                model_guard_intervention_trafaret,
                max_length=1,
                min_length=0,
            ),
            t.Null,
        ),
        t.Key("send_notification", to_name="send_notification", optional=True): t.Bool(),
    },
    allow_extra=["*"],
)

additional_guard_config_trafaret = t.Dict(
    {
        t.Key("cost", to_name="cost", optional=True): t.Or(cost_metric_trafaret, t.Null),
        t.Key("tool_call", to_name="tool_call", optional=True): t.Or(t.Any(), t.Null),
    }
)


guard_trafaret = t.Dict(
    {
        t.Key("name", to_name="name", optional=False): t.String(max_length=MAX_GUARD_NAME_LENGTH),
        t.Key("description", to_name="description", optional=True): t.String(
            max_length=MAX_GUARD_DESCRIPTION_LENGTH
        ),
        t.Key("type", to_name="type", optional=False): t.Enum(*GuardType.ALL),
        t.Key("stage", to_name="stage", optional=False): t.Or(
            t.List(t.Enum(*GuardStage.ALL)), t.Enum(*GuardStage.ALL)
        ),
        t.Key("llm_type", to_name="llm_type", optional=True): t.Enum(*GuardLLMType.ALL),
        t.Key("ootb_type", to_name="ootb_type", optional=True): t.Enum(*OOTBType.ALL),
        t.Key("deployment_id", to_name="deployment_id", optional=True): t.Or(
            t.String(max_length=OBJECT_ID_LENGTH), t.Null
        ),
        t.Key("model_info", to_name="model_info", optional=True): model_info_trafaret,
        t.Key("intervention", to_name="intervention", optional=True): t.Or(
            guard_intervention_trafaret, t.Null
        ),
        t.Key("openai_api_key", to_name="openai_api_key", optional=True): t.Or(
            t.String(max_length=MAX_TOKEN_LENGTH), t.Null
        ),
        t.Key("openai_deployment_id", to_name="openai_deployment_id", optional=True): t.Or(
            t.String(max_length=OBJECT_ID_LENGTH), t.Null
        ),
        t.Key("openai_api_base", to_name="openai_api_base", optional=True): t.Or(
            t.String(max_length=MAX_URL_LENGTH), t.Null
        ),
        t.Key("google_region", to_name="google_region", optional=True): t.Or(t.String, t.Null),
        t.Key("google_model", to_name="google_model", optional=True): t.Or(
            t.Enum(*GoogleModel.ALL), t.Null
        ),
        t.Key("aws_region", to_name="aws_region", optional=True): t.Or(t.String, t.Null),
        t.Key("aws_model", to_name="aws_model", optional=True): t.Or(t.Enum(*AwsModel.ALL), t.Null),
        t.Key("faas_url", optional=True): t.Or(t.String(max_length=MAX_URL_LENGTH), t.Null),
        t.Key("copy_citations", optional=True, default=False): t.Bool(),
        t.Key("is_agentic", to_name="is_agentic", optional=True, default=False): t.Bool(),
        t.Key(
            "additional_guard_config",
            to_name="additional_guard_config",
            optional=True,
            default=None,
        ): t.Or(additional_guard_config_trafaret, t.Null),
    },
    allow_extra=["*"],
)


moderation_config_trafaret = t.Dict(
    {
        t.Key(
            "timeout_sec",
            to_name="timeout_sec",
            optional=True,
            default=DEFAULT_GUARD_PREDICTION_TIMEOUT_IN_SEC,
        ): t.Int(gt=1),
        t.Key(
            "timeout_action",
            to_name="timeout_action",
            optional=True,
            default=GuardTimeoutAction.SCORE,
        ): t.Enum(*GuardTimeoutAction.ALL),
        # Why default is True?
        # We manually tested it and sending extra output with OpenAI completion object under
        # "datarobot_moderations" field seems to be working by default, "EVEN WITH" OpenAI client
        # It will always work with the API response (because it will simply be treated as extra data
        # in the json response).  So, most of the times it is going to work.  In future, if the
        # OpenAI client couldn't recognize extra data - we can simply disable this flag, so that
        # it won't break the client and user flow
        t.Key(
            "enable_extra_model_output_for_chat",
            to_name="enable_extra_model_output_for_chat",
            optional=True,
            default=True,
        ): t.Bool(),
        t.Key("guards", to_name="guards", optional=False): t.List(guard_trafaret),
    },
    allow_extra=["*"],
)


class Guard(ABC):
    def __init__(self, config: dict, stage=None):
        self._name = config["name"]
        self._description = config.get("description")
        self._type = config["type"]
        self._stage = stage if stage else config["stage"]
        self._pipeline = None
        self._model_info = None
        self.intervention = None
        self._deployment_id = config.get("deployment_id")
        self._dr_cm = None
        self._faas_url = config.get("faas_url")
        self._copy_citations = config["copy_citations"]
        self.is_agentic = config.get("is_agentic", False)

        if config.get("intervention"):
            self.intervention = GuardIntervention(config["intervention"])
        if config.get("model_info"):
            self._model_info = GuardModelInfo(config["model_info"])

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def type(self) -> GuardType:
        return self._type

    @property
    def stage(self) -> GuardStage:
        return self._stage

    @property
    def faas_url(self) -> str:
        return self._faas_url

    @property
    def copy_citations(self) -> str:
        return self._copy_citations

    def set_pipeline(self, pipeline):
        self._pipeline = pipeline

    @property
    def llm_type(self):
        return self._llm_type

    @staticmethod
    def get_stage_str(stage):
        return "Prompts" if stage == GuardStage.PROMPT else "Responses"

    def has_latency_custom_metric(self) -> bool:
        """Determines if latency metric is tracked for this guard type. Default is True."""
        return True

    def get_latency_custom_metric_name(self):
        return f"{self.name} Guard Latency"

    def get_latency_custom_metric(self):
        return {
            "name": self.get_latency_custom_metric_name(),
            "directionality": CustomMetricDirectionality.LOWER_IS_BETTER,
            "units": "seconds",
            "type": CustomMetricAggregationType.AVERAGE,
            "baselineValue": 0,
            "isModelSpecific": True,
            "timeStep": "hour",
            "description": (
                f"{self.get_latency_custom_metric_name()}.  {CUSTOM_METRIC_DESCRIPTION_SUFFIX}"
            ),
        }

    def has_average_score_custom_metric(self) -> bool:
        """Determines if an average score metric is tracked for this guard type. Default is True."""
        return True

    def get_average_score_custom_metric_name(self, stage):
        return f"{self.name} Guard Average Score for {self.get_stage_str(stage)}"

    def get_average_score_metric(self, stage):
        return {
            "name": self.get_average_score_custom_metric_name(stage),
            "directionality": CustomMetricDirectionality.LOWER_IS_BETTER,
            "units": "probability",
            "type": CustomMetricAggregationType.AVERAGE,
            "baselineValue": 0,
            "isModelSpecific": True,
            "timeStep": "hour",
            "description": (
                f"{self.get_average_score_custom_metric_name(stage)}. "
                f" {CUSTOM_METRIC_DESCRIPTION_SUFFIX}"
            ),
        }

    def get_guard_enforced_custom_metric_name(self, stage, moderation_method):
        if moderation_method == GuardAction.REPLACE:
            return f"{self.name} Guard replaced {self.get_stage_str(stage)}"
        return f"{self.name} Guard {moderation_method}ed {self.get_stage_str(stage)}"

    def get_enforced_custom_metric(self, stage, moderation_method):
        return {
            "name": self.get_guard_enforced_custom_metric_name(stage, moderation_method),
            "directionality": CustomMetricDirectionality.LOWER_IS_BETTER,
            "units": "count",
            "type": CustomMetricAggregationType.SUM,
            "baselineValue": 0,
            "isModelSpecific": True,
            "timeStep": "hour",
            "description": (
                f"Number of {self.get_stage_str(stage)} {moderation_method}ed by the "
                f"{self.name} guard.  {CUSTOM_METRIC_DESCRIPTION_SUFFIX}"
            ),
        }

    def get_input_column(self, stage):
        if stage == GuardStage.PROMPT:
            return (
                self._model_info.input_column_name
                if (self._model_info.input_column_name)
                else DEFAULT_PROMPT_COLUMN_NAME
            )
        else:
            return (
                self._model_info.input_column_name
                if (self._model_info and self._model_info.input_column_name)
                else DEFAULT_RESPONSE_COLUMN_NAME
            )

    def get_intervention_action(self):
        if not self.intervention:
            return GuardAction.NONE
        return self.intervention.action

    def get_comparand(self):
        return self.intervention.threshold

    def get_enforced_span_attribute_name(self, stage):
        intervention_action = self.get_intervention_action()
        if intervention_action in [GuardAction.BLOCK, GuardAction.REPORT]:
            return f"{SPAN_PREFIX}.{stage.lower()}.{intervention_action}ed"
        elif intervention_action == GuardAction.REPLACE:
            return f"{SPAN_PREFIX}.{stage.lower()}.replaced"
        else:
            raise NotImplementedError

    def get_span_column_name(self, _):
        raise NotImplementedError

    def get_span_attribute_name(self, _):
        raise NotImplementedError


class GuardModelInfo:
    def __init__(self, model_config: dict):
        self._model_id = model_config.get("model_id")
        self._input_column_name = model_config["input_column_name"]
        self._target_name = model_config["target_name"]
        self._target_type = model_config["target_type"]
        self._class_names = model_config.get("class_names")
        self.replacement_text_column_name = model_config.get("replacement_text_column_name")

    @property
    def model_id(self) -> str:
        return self._model_id

    @property
    def input_column_name(self) -> str:
        return self._input_column_name

    @property
    def target_name(self) -> str:
        return self._target_name

    @property
    def target_type(self) -> str:
        return self._target_type

    @property
    def class_names(self):
        return self._class_names


class GuardIntervention:
    def __init__(self, intervention_config: dict) -> None:
        self.action = intervention_config["action"]
        self.message = intervention_config.get("message")
        self.threshold = None
        self.comparator = None
        if (
            "conditions" in intervention_config
            and intervention_config["conditions"] is not None
            and len(intervention_config["conditions"]) > 0
        ):
            self.threshold = intervention_config["conditions"][0].get("comparand")
            self.comparator = intervention_config["conditions"][0].get("comparator")


class ModelGuard(Guard):
    def __init__(self, config: dict, stage=None):
        super().__init__(config, stage)
        self._deployment_id = config["deployment_id"]
        self._model_info = GuardModelInfo(config["model_info"])
        # dr.Client is set in the Pipeline init, Lets query the deployment
        # to get the prediction server information
        self.deployment = dr.Deployment.get(self._deployment_id)

    @property
    def deployment_id(self) -> str:
        return self._deployment_id

    @property
    def model_info(self):
        return self._model_info

    def get_metric_column_name(self, stage):
        if self.model_info is None:
            raise NotImplementedError("Missing model_info for model guard")
        return self.get_stage_str(stage) + "_" + self._model_info.target_name

    def get_span_column_name(self, _):
        if self.model_info is None:
            raise NotImplementedError("Missing model_info for model guard")
        # Typically 0th index is the target name
        return self._model_info.target_name.split("_")[0]

    def get_span_attribute_name(self, stage):
        return f"{SPAN_PREFIX}.{stage.lower()}.{self.get_span_column_name(stage)}"

    def has_average_score_custom_metric(self) -> bool:
        """A couple ModelGuard types do not have an average score metric"""
        return self.model_info.target_type not in [
            "Multiclass",
            "TextGeneration",
        ]


class NeMoGuard(Guard, GuardLLMMixin):
    def __init__(self, config: dict, stage=None, model_dir: str = os.getcwd()):
        super().__init__(config, stage)
        # NeMo guard only takes a boolean as threshold and equal to as comparator.
        # Threshold bool == TRUE is defined in the colang file as the output of
        # `bot should intervene`
        if self.intervention:
            if not self.intervention.threshold:
                self.intervention.threshold = NEMO_THRESHOLD
            if not self.intervention.comparator:
                self.intervention.comparator = GuardOperatorType.EQUALS

        # Default LLM Type for NeMo is set to OpenAI
        self._llm_type = config.get("llm_type", GuardLLMType.OPENAI)
        self.openai_api_base = config.get("openai_api_base")
        self.openai_deployment_id = config.get("openai_deployment_id")
        llm_id = None
        credentials = None
        use_llm_gateway = use_llm_gateway_inference(self._llm_type)
        try:
            self.openai_api_key = self.get_openai_api_key(config, self._llm_type)
            if self._llm_type != GuardLLMType.NIM and self.openai_api_key is None:
                raise ValueError("OpenAI API key is required for NeMo Guardrails")

            if self.llm_type == GuardLLMType.OPENAI:
                credentials = {
                    "credential_type": "openai",
                    "api_key": self.openai_api_key,
                }
                os.environ["OPENAI_API_KEY"] = self.openai_api_key
                llm = None
            elif self.llm_type == GuardLLMType.AZURE_OPENAI:
                if self.openai_api_base is None:
                    raise ValueError("Azure OpenAI API base url is required for LLM Guard")
                if self.openai_deployment_id is None:
                    raise ValueError("Azure OpenAI deployment ID is required for LLM Guard")
                credentials = {
                    "credential_type": "azure_openai",
                    "api_base": self.openai_api_base,
                    "api_version": DEFAULT_OPEN_AI_API_VERSION,
                    "api_key": self.openai_api_key,
                }
                azure_openai_client = get_azure_openai_client(
                    openai_api_key=self.openai_api_key,
                    openai_api_base=self.openai_api_base,
                    openai_deployment_id=self.openai_deployment_id,
                )
                llm = azure_openai_client
            elif self.llm_type == GuardLLMType.GOOGLE:
                # llm_id = config["google_model"]
                raise NotImplementedError
            elif self.llm_type == GuardLLMType.AMAZON:
                # llm_id = config["aws_model"]
                raise NotImplementedError
            elif self.llm_type == GuardLLMType.DATAROBOT:
                raise NotImplementedError
            elif self.llm_type == GuardLLMType.NIM:
                if config.get("deployment_id") is None:
                    if self.openai_api_base is None:
                        raise ValueError("NIM DataRobot deployment id is required for NIM LLM Type")
                    else:
                        logging.warning(
                            "Using 'openai_api_base' is being deprecated and will be removed "
                            "in the next release.  Please configure NIM DataRobot deployment "
                            "using deployment_id"
                        )
                        if self.openai_api_key is None:
                            raise ValueError("OpenAI API key is required for NeMo Guardrails")
                else:
                    self.deployment = dr.Deployment.get(self._deployment_id)
                    datarobot_endpoint, self.openai_api_key = get_datarobot_endpoint_and_token()
                    self.openai_api_base = (
                        f"{datarobot_endpoint}/deployments/{str(self._deployment_id)}"
                    )
                llm = get_chat_nvidia_llm(
                    api_key=self.openai_api_key,
                    base_url=self.openai_api_base,
                )
            else:
                raise ValueError(f"Invalid LLMType: {self.llm_type}")

        except Exception as e:
            # no valid user credentials provided, raise if not using LLM Gateway
            credentials = None
            if not use_llm_gateway:
                raise e

        if use_llm_gateway:
            # Currently only OPENAI and AZURE_OPENAI are supported by NeMoGuard
            # For Bedrock and Vertex the model in the config is actually the LLM ID
            # For OpenAI we use the default model defined in get_llm_gateway_client
            # For Azure we use the deployment ID
            llm = get_llm_gateway_client(
                llm_id=llm_id,
                openai_deployment_id=self.openai_deployment_id,
                credentials=credentials,
            )

        # Use guard stage to determine whether to read from prompt/response subdirectory
        # for nemo configurations.  "nemo_guardrails" folder is at same level of custom.py
        # So, the config path becomes model_dir + "nemo_guardrails"
        nemo_config_path = os.path.join(model_dir, NEMO_GUARDRAILS_DIR)
        self.nemo_rails_config_path = os.path.join(nemo_config_path, self.stage)
        nemo_rails_config = RailsConfig.from_path(config_path=self.nemo_rails_config_path)
        self._nemo_llm_rails = LLMRails(nemo_rails_config, llm=llm)

    def has_average_score_custom_metric(self) -> bool:
        """No average score metrics for NemoGuard's"""
        return False

    def get_metric_column_name(self, stage):
        return self.get_stage_str(stage) + "_" + NEMO_GUARD_COLUMN_NAME

    @property
    def nemo_llm_rails(self):
        return self._nemo_llm_rails


class OOTBGuard(Guard):
    def __init__(self, config: dict, stage=None):
        super().__init__(config, stage)
        self._ootb_type = config["ootb_type"]

    @property
    def ootb_type(self):
        return self._ootb_type

    def has_latency_custom_metric(self):
        """Latency is not tracked for token counts guards"""
        return self._ootb_type != OOTBType.TOKEN_COUNT

    def get_metric_column_name(self, stage):
        if self._ootb_type == OOTBType.TOKEN_COUNT:
            return self.get_stage_str(stage) + "_" + TOKEN_COUNT_COLUMN_NAME
        elif self._ootb_type == OOTBType.ROUGE_1:
            return self.get_stage_str(stage) + "_" + ROUGE_1_COLUMN_NAME
        elif self._ootb_type == OOTBType.CUSTOM_METRIC:
            return self.get_stage_str(stage) + "_" + self.name
        else:
            raise NotImplementedError(f"No metric column name defined for {self._ootb_type} guard")

    def get_span_column_name(self, _):
        if self._ootb_type == OOTBType.TOKEN_COUNT:
            return TOKEN_COUNT_COLUMN_NAME
        elif self._ootb_type == OOTBType.ROUGE_1:
            return ROUGE_1_COLUMN_NAME
        elif self._ootb_type == OOTBType.CUSTOM_METRIC:
            return self.name
        else:
            raise NotImplementedError(f"No span attribute name defined for {self._ootb_type} guard")

    def get_span_attribute_name(self, stage):
        return f"{SPAN_PREFIX}.{stage.lower()}.{self.get_span_column_name(stage)}"


class OOTBCostMetric(OOTBGuard):
    def __init__(self, config, stage):
        super().__init__(config, stage)
        # The cost is calculated based on the usage metrics returned by the
        # completion object, so it can be evaluated only at response stage
        self._stage = GuardStage.RESPONSE
        cost_config = config["additional_guard_config"]["cost"]
        self.currency = cost_config["currency"]
        self.input_price = cost_config["input_price"]
        self.input_unit = cost_config["input_unit"]
        self.input_multiplier = self.input_price / self.input_unit
        self.output_price = cost_config["output_price"]
        self.output_unit = cost_config["output_unit"]
        self.output_multiplier = self.output_price / self.output_unit

    def get_metric_column_name(self, _):
        return COST_COLUMN_NAME

    def get_average_score_custom_metric_name(self, _):
        return f"Total cost in {self.currency}"

    def get_average_score_metric(self, _):
        return {
            "name": self.get_average_score_custom_metric_name(_),
            "directionality": CustomMetricDirectionality.LOWER_IS_BETTER,
            "units": "value",
            "type": CustomMetricAggregationType.SUM,
            "baselineValue": 0,
            "isModelSpecific": True,
            "timeStep": "hour",
            "description": (
                f"{self.get_average_score_custom_metric_name(_)}. "
                f" {CUSTOM_METRIC_DESCRIPTION_SUFFIX}"
            ),
        }

    def get_span_column_name(self, _):
        return f"{COST_COLUMN_NAME}.{self.currency.lower()}"

    def get_span_attribute_name(self, _):
        return f"{SPAN_PREFIX}.{self._stage.lower()}.{self.get_span_column_name(_)}"


class FaithfulnessGuard(OOTBGuard, GuardLLMMixin):
    def __init__(self, config: dict, stage=None):
        super().__init__(config, stage)

        if self.stage == GuardStage.PROMPT:
            raise Exception("Faithfulness cannot be configured for the Prompt stage")

        # Default LLM Type for Faithfulness is set to Azure OpenAI
        self._llm_type = config.get("llm_type", GuardLLMType.AZURE_OPENAI)
        Settings.llm = self.get_llm(config, self._llm_type)
        Settings.embed_model = None
        self._evaluator = FaithfulnessEvaluator()

    def get_metric_column_name(self, stage):
        return self.get_stage_str(stage) + "_" + FAITHFULLNESS_COLUMN_NAME

    @property
    def faithfulness_evaluator(self):
        return self._evaluator

    def get_span_column_name(self, _):
        return FAITHFULLNESS_COLUMN_NAME

    def get_span_attribute_name(self, _):
        return f"{SPAN_PREFIX}.{self._stage.lower()}.{self.get_span_column_name(_)}"


class AgentGoalAccuracyGuard(OOTBGuard, GuardLLMMixin):
    def __init__(self, config: dict, stage=None):
        super().__init__(config, stage)

        if self.stage == GuardStage.PROMPT:
            raise Exception("Agent Goal Accuracy guard cannot be configured for the Prompt stage")

        # Default LLM Type for Agent Goal Accuracy is set to Azure OpenAI
        self._llm_type = config.get("llm_type", GuardLLMType.AZURE_OPENAI)
        llm = self.get_llm(config, self._llm_type)
        evaluator_llm = LangchainLLMWrapper(llm)
        self.scorer = AgentGoalAccuracyWithoutReference(llm=evaluator_llm)

    def get_metric_column_name(self, _):
        return AGENT_GOAL_ACCURACY_COLUMN_NAME

    @property
    def accuracy_scorer(self):
        return self.scorer

    def get_span_column_name(self, _):
        return AGENT_GOAL_ACCURACY_COLUMN_NAME

    def get_span_attribute_name(self, _):
        return f"{SPAN_PREFIX}.{self._stage.lower()}.{self.get_span_column_name(_)}"


class TaskAdherenceGuard(OOTBGuard, GuardLLMMixin):
    def __init__(self, config: dict, stage=None):
        super().__init__(config, stage)

        if self.stage == GuardStage.PROMPT:
            raise Exception("Agent Goal Accuracy guard cannot be configured for the Prompt stage")

        # Default LLM Type for Faithfulness is set to Azure OpenAI
        self._llm_type = config.get("llm_type", GuardLLMType.AZURE_OPENAI)
        llm = self.get_llm(config, self._llm_type)
        deepeval_llm = ModerationDeepEvalLLM(llm)
        self.scorer = TaskCompletionMetric(model=deepeval_llm, include_reason=True)

    def get_metric_column_name(self, _):
        return TASK_ADHERENCE_SCORE_COLUMN_NAME

    @property
    def task_adherence_scorer(self):
        return self.scorer

    def get_span_column_name(self, _):
        return TASK_ADHERENCE_SCORE_COLUMN_NAME

    def get_span_attribute_name(self, _):
        return f"{SPAN_PREFIX}.{self._stage.lower()}.{self.get_span_column_name(_)}"


class GuardFactory:
    @classmethod
    def _perform_post_validation_checks(cls, guard_config):
        if not guard_config.get("intervention"):
            return

        if guard_config["intervention"]["action"] == GuardAction.BLOCK and (
            guard_config["intervention"]["message"] is None
            or len(guard_config["intervention"]["message"]) == 0
        ):
            raise ValueError("Blocked action needs a blocking message")

        if guard_config["intervention"]["action"] == GuardAction.REPLACE:
            if "model_info" not in guard_config:
                raise ValueError("'Replace' action needs model_info section")
            if (
                "replacement_text_column_name" not in guard_config["model_info"]
                or guard_config["model_info"]["replacement_text_column_name"] is None
                or len(guard_config["model_info"]["replacement_text_column_name"]) == 0
            ):
                raise ValueError(
                    "'Replace' action needs valid 'replacement_text_column_name' "
                    "in 'model_info' section of the guard"
                )

        if not guard_config["intervention"].get("conditions"):
            return

        if len(guard_config["intervention"]["conditions"]) == 0:
            return

        condition = guard_config["intervention"]["conditions"][0]
        if condition["comparator"] in GuardOperatorType.REQUIRES_LIST_COMPARAND:
            if not isinstance(condition["comparand"], list):
                raise ValueError(
                    f"Comparand needs to be a list with {condition['comparator']} comparator"
                )
        elif isinstance(condition["comparand"], list):
            raise ValueError(
                f"Comparand needs to be a scalar with {condition['comparator']} comparator"
            )

    @staticmethod
    def create(input_config: dict, stage=None, model_dir: str = os.getcwd()) -> Guard:
        config = guard_trafaret.check(input_config)

        GuardFactory._perform_post_validation_checks(config)

        if config["type"] == GuardType.MODEL:
            guard = ModelGuard(config, stage)
        elif config["type"] == GuardType.OOTB:
            if config["ootb_type"] == OOTBType.FAITHFULNESS:
                guard = FaithfulnessGuard(config, stage)
            elif config["ootb_type"] == OOTBType.COST:
                guard = OOTBCostMetric(config, stage)
            elif config["ootb_type"] == OOTBType.AGENT_GOAL_ACCURACY:
                guard = AgentGoalAccuracyGuard(config, stage)
            elif config["ootb_type"] == OOTBType.TASK_ADHERENCE:
                guard = TaskAdherenceGuard(config, stage)
            else:
                guard = OOTBGuard(config, stage)
        elif config["type"] == GuardType.NEMO_GUARDRAILS:
            guard = NeMoGuard(config, stage, model_dir)
        else:
            raise ValueError(f"Invalid guard type: {config['type']}")

        return guard
