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

import datarobot as dr
import pandas as pd
from datarobot_predict.deployment import predict
from llama_index.core.base.llms.types import CompletionResponse
from llama_index.core.base.llms.types import LLMMetadata
from llama_index.core.bridge.pydantic import PrivateAttr
from llama_index.core.llms.callbacks import llm_chat_callback
from llama_index.core.llms.callbacks import llm_completion_callback
from llama_index.core.llms.llm import LLM

from datarobot_dome.async_http_client import AsyncHTTPClient

DEFAULT_TEMPERATURE = 1.0
MAX_TOKENS = 512
DEFAULT_TIMEOUT = 30
MAX_RETRIES = 5


class DataRobotLLM(LLM):
    # DataRobot deployment object.  Only one of `deployment` or `deployment_id` is required
    _deployment: dr.Deployment = PrivateAttr()
    # DataRobot endpoint URL, Only one of `dr_client` or the pair
    # (datarobot_endpoint, datarobot_api_token) is required
    _datarobot_endpoint: str = PrivateAttr()
    # DataRobot API Token to use, Only one of `dr_client` or the pair
    # (datarobot_endpoint, datarobot_api_token) is required
    _datarobot_api_token: str = PrivateAttr()
    # Async HTTP Client for all async prediction requests with DataRobot Deployment
    _async_http_client: Any = PrivateAttr()

    _prompt_column_name: str = PrivateAttr()
    _target_column_name: str = PrivateAttr()

    def __init__(
        self,
        deployment,
        datarobot_endpoint=None,
        datarobot_api_token=None,
        callback_manager=None,
    ):
        super().__init__(
            model="DataRobot LLM",
            temperature=DEFAULT_TEMPERATURE,
            max_tokens=MAX_TOKENS,
            timeout=DEFAULT_TIMEOUT,
            max_retries=MAX_RETRIES,
            callback_manager=callback_manager,
        )
        if deployment is None:
            raise ValueError("DataRobot deployment is required")

        if datarobot_api_token is None and datarobot_endpoint is None:
            raise ValueError(
                "Connection parameters 'datarobot_endpoint' and 'datarobot_api_token' "
                "needs to be provided"
            )
        self._deployment = deployment
        self._datarobot_endpoint = datarobot_endpoint
        self._datarobot_api_token = datarobot_api_token

        if self._deployment.model["target_type"] != "TextGeneration":
            raise ValueError(
                f"Invalid deployment '{self._deployment.label}' for LLM.  Expecting an LLM "
                f"deployment, but is a '{self._deployment.model['target_type']}' deployment"
            )

        self._prompt_column_name = self._deployment.model.get("prompt")
        if self._prompt_column_name is None:
            raise ValueError("Prompt column name 'prompt' is not set on the deployment / model")

        self._target_column_name = self._deployment.model["target_name"] + "_PREDICTION"
        self._async_http_client = AsyncHTTPClient(DEFAULT_TIMEOUT)

    @property
    def _llm_type(self) -> str:
        """Return type of llm."""
        return "datarobot-llm"

    @property
    def _identifying_params(self):
        """Get the identifying parameters."""
        _model_kwargs = self.model_kwargs or {}
        return {
            **{"endpoint_url": self._datarobot_endpoint, "deployment_id": str(self._deployment.id)},
            **{"model_kwargs": _model_kwargs},
        }

    def _call(self, prompt, stop=None, run_manager=None, **kwargs):
        df = pd.DataFrame({self._prompt_column_name: [prompt]})
        result_df, _ = predict(self._deployment, df)
        return result_df[self._target_column_name].iloc[0]

    @classmethod
    def class_name(cls) -> str:
        return "DataRobotLLM"

    @property
    def metadata(self):
        return LLMMetadata(is_chat_model=False)

    @llm_chat_callback()
    def chat(self, messages, **kwargs: Any):
        raise NotImplementedError

    @llm_completion_callback()
    def complete(self, prompt, formatted, **kwargs):
        df = pd.DataFrame({self._prompt_column_name: [prompt]})
        result_df, _ = predict(self._deployment, df)
        return CompletionResponse(text=result_df[self._target_column_name].iloc[0], raw={})

    @llm_chat_callback()
    def stream_chat(self, messages, **kwargs):
        raise NotImplementedError

    @llm_completion_callback()
    def stream_complete(self, prompt, formatted=False, **kwargs):
        raise NotImplementedError

    @llm_chat_callback()
    async def achat(self, messages, **kwargs):
        raise NotImplementedError

    @llm_completion_callback()
    async def acomplete(self, prompt, formatted=False, **kwargs):
        input_df_to_guard = pd.DataFrame({self._prompt_column_name: [prompt]})
        result_df = await self._async_http_client.predict(self._deployment, input_df_to_guard)
        return CompletionResponse(text=result_df[self._target_column_name].iloc[0], raw={})

    @llm_chat_callback()
    async def astream_chat(self, messages, **kwargs):
        raise NotImplementedError

    @llm_completion_callback()
    async def astream_complete(self, prompt, formatted=False, **kwargs):
        raise NotImplementedError
