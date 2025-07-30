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
import json
import os

import datarobot as dr
import trafaret as t

from datarobot_dome.constants import AWS_ACCOUNT_SECRET_DEFINITION_SUFFIX
from datarobot_dome.constants import GOOGLE_SERVICE_ACCOUNT_SECRET_DEFINITION_SUFFIX
from datarobot_dome.constants import OPENAI_SECRET_DEFINITION_SUFFIX
from datarobot_dome.constants import SECRET_DEFINITION_PREFIX
from datarobot_dome.constants import GuardLLMType
from datarobot_dome.constants import GuardType
from datarobot_dome.constants import OOTBType
from datarobot_dome.guard_helpers import DEFAULT_OPEN_AI_API_VERSION
from datarobot_dome.guard_helpers import get_azure_openai_client
from datarobot_dome.guard_helpers import get_bedrock_client
from datarobot_dome.guard_helpers import get_datarobot_llm
from datarobot_dome.guard_helpers import get_llm_gateway_client
from datarobot_dome.guard_helpers import get_vertex_client
from datarobot_dome.guard_helpers import use_llm_gateway_inference

basic_credential_trafaret = t.Dict(
    {
        t.Key("credentialType", to_name="credential_type", optional=False): t.Enum("basic"),
        t.Key("password", to_name="password", optional=False): t.String,
    },
    allow_extra=["*"],
)

api_token_credential_trafaret = t.Dict(
    {
        t.Key("credentialType", to_name="credential_type", optional=False): t.Enum("api_token"),
        t.Key("apiToken", to_name="api_token", optional=False): t.String,
    },
    allow_extra=["*"],
)

google_service_account_trafaret = t.Dict(
    {
        t.Key("credentialType", to_name="credential_type", optional=False): t.Enum("gcp"),
        t.Key("gcpKey", to_name="gcp_key", optional=False): t.Dict(allow_extra=["*"]),
    },
    allow_extra=["*"],
)

aws_account_trafaret = t.Dict(
    {
        t.Key("credentialType", to_name="credential_type", optional=False): t.Enum("s3"),
        t.Key("awsAccessKeyId", to_name="aws_access_key_id", optional=False): t.String,
        t.Key("awsSecretAccessKey", to_name="aws_secret_access_key", optional=False): t.String,
        t.Key("awsSessionToken", to_name="aws_session_token", optional=True, default=None): t.String
        | t.Null,
    },
    allow_extra=["*"],
)


credential_trafaret = t.Dict(
    {
        t.Key("type", optional=False): t.Enum("credential"),
        t.Key("payload", optional=False): t.Or(
            basic_credential_trafaret,
            api_token_credential_trafaret,
            google_service_account_trafaret,
            aws_account_trafaret,
        ),
    }
)


class GuardLLMMixin:
    def get_secret_env_var_base(self, config, llm_type_str):
        guard_type = config["type"]
        guard_stage = config["stage"]
        secret_env_var_name_prefix = f"{SECRET_DEFINITION_PREFIX}_{guard_type}_{guard_stage}_"
        if guard_type == GuardType.NEMO_GUARDRAILS:
            return f"{secret_env_var_name_prefix}{llm_type_str}"
        elif guard_type == GuardType.OOTB:
            if config["ootb_type"] == OOTBType.FAITHFULNESS:
                return f"{secret_env_var_name_prefix}{OOTBType.FAITHFULNESS}_{llm_type_str}"
            elif config["ootb_type"] == OOTBType.AGENT_GOAL_ACCURACY:
                return f"{secret_env_var_name_prefix}{OOTBType.AGENT_GOAL_ACCURACY}_{llm_type_str}"
            elif config["ootb_type"] == OOTBType.TASK_ADHERENCE:
                return f"{secret_env_var_name_prefix}{OOTBType.TASK_ADHERENCE}_{llm_type_str}"
            else:
                raise Exception("Invalid guard config for building env var name")
        else:
            raise Exception("Invalid guard config for building env var name")

    def build_open_ai_api_key_env_var_name(self, config, llm_type):
        llm_type_str = ""
        if llm_type == GuardLLMType.AZURE_OPENAI:
            llm_type_str = "AZURE_"
        elif llm_type == GuardLLMType.NIM:
            llm_type_str = "NIM_"
        var_name = self.get_secret_env_var_base(config, llm_type_str)
        var_name += OPENAI_SECRET_DEFINITION_SUFFIX
        return var_name.upper()

    def get_openai_api_key(self, config, llm_type):
        api_key_env_var_name = self.build_open_ai_api_key_env_var_name(config, llm_type)
        if api_key_env_var_name not in os.environ:
            if llm_type == GuardLLMType.NIM:
                return None
            raise Exception(f"Expected environment variable '{api_key_env_var_name}' not found")

        env_var_value = json.loads(os.environ[api_key_env_var_name])
        credential_config = credential_trafaret.check(env_var_value)
        if credential_config["payload"]["credential_type"] == "basic":
            return credential_config["payload"]["password"]
        else:
            return credential_config["payload"]["api_token"]

    def get_google_service_account(self, config):
        service_account_env_var_name = self.get_secret_env_var_base(
            config, GOOGLE_SERVICE_ACCOUNT_SECRET_DEFINITION_SUFFIX
        ).upper()
        if service_account_env_var_name not in os.environ:
            raise Exception(
                f"Expected environment variable '{service_account_env_var_name}' not found"
            )

        env_var_value = json.loads(os.environ[service_account_env_var_name])
        credential_config = credential_trafaret.check(env_var_value)
        if credential_config["payload"]["credential_type"] == "gcp":
            return credential_config["payload"]["gcp_key"]
        else:
            raise Exception("Google model requires a credential of type 'gcp'")

    def get_aws_account(self, config):
        service_account_env_var_name = self.get_secret_env_var_base(
            config, AWS_ACCOUNT_SECRET_DEFINITION_SUFFIX
        ).upper()
        if service_account_env_var_name not in os.environ:
            raise Exception(
                f"Expected environment variable '{service_account_env_var_name}' not found"
            )

        env_var_value = json.loads(os.environ[service_account_env_var_name])
        credential_config = credential_trafaret.check(env_var_value)
        if credential_config["payload"]["credential_type"] == "s3":
            return credential_config["payload"]
        else:
            raise Exception("Amazon model requires a credential of type 's3'")

    def get_llm(self, config, llm_type):
        openai_api_base = config.get("openai_api_base")
        openai_deployment_id = config.get("openai_deployment_id")
        llm_id = None
        credentials = None
        use_llm_gateway = use_llm_gateway_inference(llm_type)
        try:
            if llm_type in [GuardLLMType.OPENAI, GuardLLMType.AZURE_OPENAI]:
                openai_api_key = self.get_openai_api_key(config, llm_type)
                if openai_api_key is None:
                    raise ValueError("OpenAI API key is required for Faithfulness guard")

                if llm_type == GuardLLMType.OPENAI:
                    credentials = {
                        "credential_type": "openai",
                        "api_key": openai_api_key,
                    }
                    os.environ["OPENAI_API_KEY"] = openai_api_key
                    llm = "default"
                elif llm_type == GuardLLMType.AZURE_OPENAI:
                    if openai_api_base is None:
                        raise ValueError("OpenAI API base url is required for LLM Guard")
                    if openai_deployment_id is None:
                        raise ValueError("OpenAI deployment ID is required for LLM Guard")
                    credentials = {
                        "credential_type": "azure_openai",
                        "api_key": openai_api_key,
                        "api_base": openai_api_base,
                        "api_version": DEFAULT_OPEN_AI_API_VERSION,
                    }
                    azure_openai_client = get_azure_openai_client(
                        openai_api_key=openai_api_key,
                        openai_api_base=openai_api_base,
                        openai_deployment_id=openai_deployment_id,
                    )
                    llm = azure_openai_client
            elif llm_type == GuardLLMType.GOOGLE:
                llm_id = config["google_model"]
                if llm_id is None:
                    raise ValueError("Google model is required for LLM Guard")
                if config.get("google_region") is None:
                    raise ValueError("Google region is required for LLM Guard")
                service_account_info = self.get_google_service_account(config)
                credentials = {
                    "credential_type": "google_vertex_ai",
                    "region": config["google_region"],
                    "service_account_info": service_account_info,
                }
                llm = get_vertex_client(
                    google_model=llm_id,
                    google_service_account=service_account_info,
                    google_region=config["google_region"],
                )
            elif llm_type == GuardLLMType.AMAZON:
                llm_id = config["aws_model"]
                if llm_id is None:
                    raise ValueError("AWS model is required for LLM Guard")
                if config.get("aws_region") is None:
                    raise ValueError("AWS region is required for LLM Guard")
                credential_config = self.get_aws_account(config)
                credentials = {
                    "credential_type": "amazon_bedrock",
                    "access_key_id": credential_config["aws_access_key_id"],
                    "secret_access_key": credential_config["aws_secret_access_key"],
                    "session_token": credential_config["aws_session_token"],
                    "region": config["aws_region"],
                }
                llm = get_bedrock_client(
                    aws_model=llm_id,
                    aws_access_key_id=credential_config["aws_access_key_id"],
                    aws_secret_access_key=credential_config["aws_secret_access_key"],
                    aws_session_token=credential_config["aws_session_token"],
                    aws_region=config["aws_region"],
                )
            elif llm_type == GuardLLMType.DATAROBOT:
                if config["type"] == GuardType.OOTB and config["ootb_type"] in [
                    OOTBType.AGENT_GOAL_ACCURACY,
                    OOTBType.TASK_ADHERENCE,
                ]:
                    # DataRobot LLM does not implement generate / agenerate yet
                    # so can't support it for Agent Goal Accuracy
                    raise NotImplementedError
                if config.get("deployment_id") is None:
                    raise ValueError("Deployment ID is required for LLM Guard")
                deployment = dr.Deployment.get(config["deployment_id"])
                llm = get_datarobot_llm(deployment)
            elif llm_type == GuardLLMType.NIM:
                raise NotImplementedError
            else:
                raise ValueError(f"Invalid LLMType: {llm_type}")

        except Exception as e:
            # no valid user credentials provided, raise if not using LLM Gateway
            credentials = None
            if not use_llm_gateway:
                raise e

        if use_llm_gateway:
            # For Bedrock and Vertex the model in the config is actually the LLM ID
            # For OpenAI we use the default model defined in get_llm_gateway_client
            # For Azure we use the deployment ID
            llm = get_llm_gateway_client(
                llm_id=llm_id,
                openai_deployment_id=openai_deployment_id,
                credentials=credentials,
            )

        return llm
