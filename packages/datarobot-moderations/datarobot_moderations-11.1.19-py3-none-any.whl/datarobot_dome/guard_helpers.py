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
import logging
import os

import pandas as pd
import requests
import tiktoken
from deepeval.metrics import TaskCompletionMetric
from deepeval.models import DeepEvalBaseLLM
from deepeval.test_case import LLMTestCase
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_nvidia_ai_endpoints import Model
from langchain_nvidia_ai_endpoints import register_model
from langchain_nvidia_ai_endpoints._statics import determine_model
from langchain_openai import AzureChatOpenAI
from langchain_openai import ChatOpenAI
from llama_index.core.evaluation import FaithfulnessEvaluator
from ragas import MultiTurnSample
from ragas.messages import AIMessage
from ragas.messages import HumanMessage
from ragas.messages import ToolMessage
from ragas.metrics import AgentGoalAccuracyWithoutReference
from rouge_score import rouge_scorer

from datarobot_dome.constants import AWS_MODEL_TO_AWS_MODEL_VERSION_MAP
from datarobot_dome.constants import ENABLE_LLM_GATEWAY_INFERENCE_RUNTIME_PARAM_NAME
from datarobot_dome.constants import GOOGLE_MODEL_TO_GOOGLE_MODEL_VERSION_MAP
from datarobot_dome.constants import LOGGER_NAME_PREFIX
from datarobot_dome.constants import PROMPT_TOKEN_COUNT_COLUMN_NAME_FROM_USAGE
from datarobot_dome.constants import RESPONSE_TOKEN_COUNT_COLUMN_NAME_FROM_USAGE
from datarobot_dome.constants import AwsModel
from datarobot_dome.constants import GoogleModel
from datarobot_dome.constants import GuardLLMType
from datarobot_dome.llm import DataRobotLLM
from datarobot_dome.runtime import get_runtime_parameter_value_bool

# Ideally, we want to return confidence score between 0.0 and 100.0,
# but for ROUGE-1 guard, UI allows the user to configure value between
# 0 and 1, so making scaling factor 1.
SCALING_FACTOR = 1
DEFAULT_OPEN_AI_API_VERSION = "2024-10-21"

_logger = logging.getLogger(LOGGER_NAME_PREFIX + ".guard_helpers")


def get_token_count(input: str, encoding: str = "cl100k_base") -> int:
    """Get the token count for the input."""
    if input is None:
        return 0
    encoding = tiktoken.get_encoding(encoding)
    return len(encoding.encode(str(input), disallowed_special=()))


def calculate_token_counts_for_cost_calculations(prompt_column_name, response_column_name, df):
    # For either interface, prompt is part of the predictions_df, so prompt_column_name
    # should be present in the df
    df[PROMPT_TOKEN_COUNT_COLUMN_NAME_FROM_USAGE] = df[prompt_column_name].apply(
        lambda x: get_token_count(x)
    )
    df[RESPONSE_TOKEN_COUNT_COLUMN_NAME_FROM_USAGE] = df[response_column_name].apply(
        lambda x: get_token_count(x)
    )
    return df


def get_citation_columns(columns: pd.Index) -> list:
    """
    Ensure that citation columns are returned in the order 0, 1, 2, etc
    Order matters
    """
    index = 0
    citation_columns = []
    while True:
        column_name = f"CITATION_CONTENT_{index}"
        if column_name in columns:
            citation_columns.append(column_name)
            index += 1
        else:
            break
    return citation_columns


def nemo_response_stage_input_formatter(bot_message: str) -> list:
    """
    Format the input message for the Nemo guard during response guard stage.
    only applicable to bot generated messages.
    this format is only suitable for openai-based nemo guardrails.
    """
    messages = [
        {"role": "context", "content": {"llm_output": bot_message}},
        {"role": "user", "content": "just some place holder message"},
    ]

    return messages


def nemo_response_stage_output_formatter(guard_message: dict) -> str:
    """
    Format the output message for the Nemo guard during response guard stage.
    applicable to nemo guard generated messages.
    this format is only suitable for openai-based nemo guardrails.
    """
    return guard_message["content"]


def get_rouge_1_scorer():
    return rouge_scorer.RougeScorer(["rouge1"], use_stemmer=True)


def get_rouge_1_score(
    scorer: rouge_scorer.RougeScorer,
    llm_context: list[str],
    llm_response: list[str],
) -> float:
    """Compute rouge score between list of context sent to LLM and its response.

    Calculate ROUGE score between provided LLM context and LLM's response.
    ROUGE is case insensitive, meaning that upper case letters are treated in same way as lower
    case letters. ROUGE uses a random resampling algorithm which is non-deterministic, so we need
    to fix seed.

    Parameters
    ----------
    llm_context
        context sent from vector database to Open-Source LLM
    llm_response
        confidence score from the Open-Source LLM

    Returns
    -------
        Rouge score between context and the answer
    """
    if (
        llm_response is None
        or len(llm_response) == 0
        or llm_context is None
        or len(llm_context) == 0
    ):
        return 0.0

    valid_llm_responses = list(filter(None, llm_response))
    if len(valid_llm_responses) == 0:
        return 0.0

    # Get only non None contexts for calculation
    valid_llm_contexts = list(filter(None, llm_context))
    if len(valid_llm_contexts) == 0:
        return 0.0

    response_to_score = " ".join([str(response) for response in valid_llm_responses])

    # Adapt Greedy Strategy for Maximizing Rouge Score
    # For each sentence keep max between sentence rouge1 precision and sentence rouge1 recall
    # for given llm response. At the end calculate and rouge1 precision and rouge1 recall
    # for the entire block.
    # rouge 1 precision = count of matching n-grams / count of context n-grams
    # rouge 1 recall = count of matching n-grams / count of llm response n-grams
    # According to detailed analysis of ROUGE: https://aclanthology.org/E17-2007.pdf
    # High ROUGE score is hard to achieve, but greedy approacha achieves acceptable results.
    # TODO: https://github.com/Tiiiger/bert_score/ use bert_score instead.
    # Rouge is broken because doesnt' care about semantic only compare token to token
    # We need to capture semantic and this will significantly boost results, because
    # in order to get high rouge, LLM response needs to do "parroting", just mimicking the
    # context as much as possible. Simple GPT paraphrasing with correct answer can break Rouge.

    best_rouge_score = 0.0
    # Greedy Strategy, pick best rouge score between each context sentence and llm response
    for context_sentence in valid_llm_contexts:
        sentence_score = scorer.score(str(context_sentence), response_to_score)
        best_rouge_score = max(
            best_rouge_score,
            sentence_score["rouge1"].precision,
            sentence_score["rouge1"].recall,
        )

    context_to_score = " ".join([str(context) for context in valid_llm_contexts])
    # Compute Rouge between whole context ( concatenated sentences ) and llm response
    block_score = scorer.score(context_to_score, response_to_score)
    best_rouge_score = max(
        best_rouge_score, block_score["rouge1"].precision, block_score["rouge1"].recall
    )
    return best_rouge_score * SCALING_FACTOR


def get_llm_gateway_client(
    model: str | None = None,
    llm_id: str | None = None,
    openai_deployment_id: str | None = None,
    credentials: dict | None = None,
) -> ChatOpenAI:
    """The LLM gateway client enables chat completions with DR provided credentials and metering.
    User provided credentials are optional and passed to the completion request as json string.

    Providing model is always required due to openai's chat api.
    llm_id and deployment_id override model if provided.
    The hierarchy is: model < llm_id < deployment_id
    """
    datarobot_endpoint, datarobot_api_token = get_datarobot_endpoint_and_token()
    client = ChatOpenAI(
        # default model is required by ChatOpenAI
        model=model or "azure/gpt-4o-2024-11-20",
        api_key=datarobot_api_token,
        base_url=f"{datarobot_endpoint}/genai/llmgw",
        # retries are handled by the LLM Gateway
        max_retries=0,
        default_headers={
            # used for metering
            "Client-Id": "moderations",
        },
        extra_body={
            # optional model overrides
            "deployment_id": openai_deployment_id,
            "llm_id": llm_id,
            # optional user provided credentials
            "credential_json": json.dumps(credentials) if credentials else None,
        },
    )
    return client


def use_llm_gateway_inference(llm_type: str):
    """
    Determine whether the given LLM should use the LLM Gateway for inference.

    `DATAROBOT` and `NIM LLM` types are not supported by the gateway.

    Parameters
    ----------
    llm_type
        The type of the LLM used in the guard.

    Returns
    -------
    True if LLM Gateway should be used, False otherwise.
    """
    is_enabled_by_runtime_parameter = get_runtime_parameter_value_bool(
        param_name=ENABLE_LLM_GATEWAY_INFERENCE_RUNTIME_PARAM_NAME,
        default_value=False,
    )
    is_compatible_llm = llm_type not in [GuardLLMType.DATAROBOT, GuardLLMType.NIM]
    return is_enabled_by_runtime_parameter and is_compatible_llm


def get_azure_openai_client(
    openai_api_key: str,
    openai_api_base: str,
    openai_deployment_id: str,
) -> AzureChatOpenAI:
    azure_openai_client = AzureChatOpenAI(
        model=openai_deployment_id,
        azure_endpoint=openai_api_base,
        api_key=openai_api_key,
        deployment_name=openai_deployment_id,
        api_version=DEFAULT_OPEN_AI_API_VERSION,
    )
    return azure_openai_client


def get_vertex_client(
    google_model: GoogleModel,
    google_service_account: dict,
    google_region: str,
):
    from google.oauth2 import service_account
    from llama_index.llms.vertex import Vertex

    vertex_credentials = service_account.Credentials.from_service_account_info(
        google_service_account,
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )
    return Vertex(
        model=GOOGLE_MODEL_TO_GOOGLE_MODEL_VERSION_MAP[google_model],
        credentials=vertex_credentials,
        project=vertex_credentials.project_id,
        location=google_region,
    )


def get_bedrock_client(
    aws_model: AwsModel,
    aws_access_key_id: str,
    aws_secret_access_key: str,
    aws_region: str,
    aws_session_token: str | None,
):
    from llama_index.llms.bedrock_converse import BedrockConverse

    return BedrockConverse(
        model=AWS_MODEL_TO_AWS_MODEL_VERSION_MAP[aws_model],
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        aws_session_token=aws_session_token,
        region_name=aws_region,
    )


def get_datarobot_endpoint_and_token():
    datarobot_endpoint = os.environ.get("DATAROBOT_ENDPOINT", None)
    if datarobot_endpoint is None:
        raise ValueError(
            "Missing DataRobot endpoint 'DATAROBOT_ENDPOINT' in environment variable,"
            " can't create DataRobotLLM"
        )

    datarobot_api_token = os.environ.get("DATAROBOT_API_TOKEN", None)
    if datarobot_api_token is None:
        raise ValueError(
            "Missing DataRobot API Token 'DATAROBOT_API_TOKEN' in environment variable,"
            " can't create DataRobotLLM"
        )
    return datarobot_endpoint, datarobot_api_token


def get_datarobot_llm(deployment):
    datarobot_endpoint, datarobot_api_token = get_datarobot_endpoint_and_token()
    return DataRobotLLM(
        deployment,
        datarobot_endpoint=datarobot_endpoint,
        datarobot_api_token=datarobot_api_token,
    )


def get_nim_model_id_served_by_the_url(base_url: str, api_key: str):
    models_url = f"{base_url}/directAccess/nim/v1/models/"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
    }
    response = requests.get(models_url, headers=headers)
    response.raise_for_status()
    json_response = response.json()

    # We expect the API to adhere to OpenAI /v1/models spec, can't do
    # all checks
    for model in json_response["data"]:
        # Lets get the first model id of the list to query
        return model["id"]

    # No models? Raise
    raise Exception(f"The URL is not serving any models: {models_url}")


def get_chat_nvidia_llm(api_key: str, base_url: str) -> ChatNVIDIA:
    model_id = get_nim_model_id_served_by_the_url(base_url, api_key)
    _logger.info(f"Found model {model_id} being served at url: {base_url}")
    nim_model = determine_model(model_id)
    if nim_model is None:
        # Most likely a DataRobot NiM model, so first
        # register it and then use it
        chat_url = f"{base_url}/chat/completions"
        nim_model = Model(
            id=model_id,
            model_type="chat",
            client="ChatNVIDIA",
            endpoint=chat_url,
        )
        # This registration is for the sake of NeMo guardrails to find
        # the datarobot LLM
        register_model(nim_model)
    return ChatNVIDIA(model=nim_model.id, api_key=api_key)


def calculate_faithfulness(
    evaluator: FaithfulnessEvaluator,
    llm_query: str,
    llm_response: str,
    llm_context: list[str],
):
    """Compute faithfulness score between list of context and LL response for given metric.

    Parameters
    ----------
    llm_query
        query sent from vector database to Open-Source LLM
    llm_response
        response from the Open-Source LLM
    llm_context
        context sent from vector database to Open-Source LLM

    Returns
    -------
        Faithfulness score: 1.0 if the response is faithful to the query, 0.0 otherwise.
    """
    if llm_response is None or llm_query is None or llm_context is None or len(llm_context) == 0:
        return 0.0

    # Get only non None contexts for calculation
    valid_llm_contexts = list(filter(None, llm_context))
    if len(valid_llm_contexts) == 0:
        return 0.0

    llm_contexts = [str(context) for context in valid_llm_contexts]
    faithfulness_result = evaluator.evaluate(str(llm_query), str(llm_response), llm_contexts)
    return faithfulness_result.score


def calculate_agent_goal_accuracy(
    scorer: AgentGoalAccuracyWithoutReference,
    prompt: str,
    interactions: str,
    response: str,
):
    if interactions is None or interactions == "":
        # If interactions are missing - we use prompt and response to gauge the
        # goal accuracy
        sample = MultiTurnSample(
            user_input=[HumanMessage(content=prompt), AIMessage(content=response)]
        )
    else:
        samples_dict = json.loads(interactions)
        inputs = []
        for message in samples_dict["user_input"]:
            if message["type"] == "ai":
                inputs.append(
                    AIMessage(content=message["content"], tool_calls=message.get("tool_calls", []))
                )
            elif message["type"] == "human":
                inputs.append(HumanMessage(content=message["content"]))
            elif message["type"] == "tool":
                inputs.append(ToolMessage(content=message["content"]))
        sample = MultiTurnSample(user_input=inputs)
    return scorer.multi_turn_score(sample)


class ModerationDeepEvalLLM(DeepEvalBaseLLM):
    def __init__(self, llm, *args, **kwargs):
        self.llm = llm

    def load_model(self, *args, **kwargs):
        return self.llm

    def generate(self, prompt: str) -> str:
        return self.llm.invoke(prompt).content

    async def a_generate(self, prompt: str) -> str:
        res = await self.llm.ainvoke(prompt)
        return res.content

    def get_model_name(self):
        return "DeepEval LLM for Moderation"


def calculate_task_adherence(
    scorer: TaskCompletionMetric,
    prompt: str,
    interactions: str,
    response: str,
):
    # The library will calculate the task completion metric based on input and
    # output only and will not use tools information for now.
    #
    # But, we will keep `interactions` parameter (unused) so that it will be easier
    # to implement improvement whenever required.
    _ = interactions
    test_case = LLMTestCase(input=prompt, actual_output=response, tools_called=[])
    return scorer.measure(test_case)
