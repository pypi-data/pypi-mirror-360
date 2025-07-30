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
import copy
import itertools
import json
import logging
import os
import time
import traceback
import uuid
from collections.abc import Iterable
from typing import Optional

import numpy as np
import pandas as pd
from openai.types.chat import ChatCompletionChunk
from openai.types.chat.chat_completion import ChatCompletion
from openai.types.chat.chat_completion import Choice
from openai.types.chat.chat_completion_message import ChatCompletionMessage
from opentelemetry import trace

from datarobot_dome.chat_helper import add_citations_to_df
from datarobot_dome.chat_helper import add_token_count_columns_to_df
from datarobot_dome.chat_helper import build_moderations_attribute_for_completion
from datarobot_dome.chat_helper import calculate_token_counts_and_confidence_score
from datarobot_dome.chat_helper import get_all_citation_columns
from datarobot_dome.chat_helper import get_response_message_and_finish_reason
from datarobot_dome.chat_helper import remove_unnecessary_columns
from datarobot_dome.chat_helper import run_postscore_guards
from datarobot_dome.constants import AGENTIC_PIPELINE_INTERACTIONS_ATTR
from datarobot_dome.constants import CHAT_COMPLETION_OBJECT
from datarobot_dome.constants import CITATIONS_ATTR
from datarobot_dome.constants import DATAROBOT_MODERATIONS_ATTR
from datarobot_dome.constants import DISABLE_MODERATION_RUNTIME_PARAM_NAME
from datarobot_dome.constants import LLM_BLUEPRINT_ID_ATTR
from datarobot_dome.constants import LLM_CONTEXT_COLUMN_NAME
from datarobot_dome.constants import LLM_PROVIDER_GUARDS_ATTR
from datarobot_dome.constants import MODERATION_CONFIG_FILE_NAME
from datarobot_dome.constants import MODERATION_MODEL_NAME
from datarobot_dome.constants import NONE_CUSTOM_PY_RESPONSE
from datarobot_dome.constants import PROMPT_VECTOR_ATTR
from datarobot_dome.constants import USAGE_ATTR
from datarobot_dome.constants import GuardStage
from datarobot_dome.constants import ModerationEventTypes
from datarobot_dome.constants import TargetType
from datarobot_dome.guard_executor import AsyncGuardExecutor
from datarobot_dome.pipeline.llm_pipeline import LLMPipeline
from datarobot_dome.pipeline.vdb_pipeline import VDBPipeline
from datarobot_dome.runtime import get_runtime_parameter_value_bool
from datarobot_dome.streaming import ModerationIterator
from datarobot_dome.streaming import StreamingContextBuilder

tracer = trace.get_tracer(__name__)


_logger = logging.getLogger("drum_integration")


datarobot_metadata_columns = [
    "datarobot_token_count",
    "datarobot_latency",
    "datarobot_confidence_score",
]


def block_citations_if_prompt_blocked(pipeline, result_df):
    # Citations are already copied from postscore_df to result_df, we just
    # mask the blocked ones here.
    if LLM_CONTEXT_COLUMN_NAME not in result_df.columns:
        return

    prompt_column_name = pipeline.get_input_column(GuardStage.PROMPT)
    blocked_prompt_column_name = f"blocked_{prompt_column_name}"
    for index, row in result_df.iterrows():
        if row[blocked_prompt_column_name]:
            # If the row is blocked, set default value
            result_df.loc[index, LLM_CONTEXT_COLUMN_NAME] = ""


def _handle_result_df_error_cases(prompt_column_name, df, latency):
    replaced_message_prompt_column_name = f"replaced_message_{prompt_column_name}"
    moderated_prompt_column_name = f"moderated_{prompt_column_name}"
    replaced_prompt_column_name = f"replaced_{prompt_column_name}"
    for index, row in df.iterrows():
        if row.get(replaced_prompt_column_name):
            df.loc[index, moderated_prompt_column_name] = row[replaced_message_prompt_column_name]
        else:
            df.loc[index, moderated_prompt_column_name] = row[prompt_column_name]
    df["datarobot_latency"] = latency / df.shape[0]
    # No tokens, every prompt is blocked
    df["datarobot_token_count"] = 0
    df["datarobot_confidence_score"] = 0.0
    if prompt_column_name in df.columns:
        df.drop(prompt_column_name, axis=1, inplace=True)
    return df


def run_prescore_guards(pipeline, data):
    """
    Run prescore guards on the input data.

    Args:
        pipeline: Guard Pipeline
        data: Input dataframe sent for predictions by the user

    Returns:
        prescore_df: Dataframe with all moderations applied to the input.  It has
            all the moderation information into various columns and is required
            to build the final result dataframe (as `prescore_df` argument to
            the method `format_result_df`)
        filtered_df: Dataframe with blocked rows removed.  This is the dataframe
            to be used as input for the user's `score` method
        prescore_latency: Latency of executing prescore guards
    """
    prompt_column_name = pipeline.get_input_column(GuardStage.PROMPT)
    blocked_prompt_column_name = f"blocked_{prompt_column_name}"
    replaced_prompt_column_name = f"replaced_{prompt_column_name}"
    replaced_message_prompt_column_name = f"replaced_message_{prompt_column_name}"

    input_df = data.copy(deep=True)
    if len(pipeline.get_prescore_guards()) == 0:
        input_df[blocked_prompt_column_name] = False
        return input_df, input_df, 0

    start_time = time.time()

    try:
        prescore_df, prescore_latency = AsyncGuardExecutor(pipeline).run_guards(
            input_df, pipeline.get_prescore_guards(), GuardStage.PROMPT
        )
    except Exception as e:
        end_time = time.time()
        _logger.error(f"Failed to run prescore guards: {e}")
        _logger.error(traceback.format_exc())
        prescore_df = input_df
        prescore_df[blocked_prompt_column_name] = False
        prescore_latency = end_time - start_time

    _logger.debug(prescore_df)
    # Filter out the blocked prompts, we will not send those prompts
    # for LLM scoring
    if blocked_prompt_column_name in prescore_df.columns:
        filtered_df = prescore_df[~prescore_df[blocked_prompt_column_name]]
    else:
        filtered_df = prescore_df

    # Now we are done with pre-score stage, we have to change the prompts
    # as replaced by say PII kind of guards
    for index, row in filtered_df.iterrows():
        if row.get(replaced_prompt_column_name):
            filtered_df.loc[index, prompt_column_name] = row[replaced_message_prompt_column_name]

    # `filtered_df` is used to call the user's `score` method, so as
    # part of return value we only send the columns that were present in
    # the original input dataframe.  Moderation information should not be
    # in the filtered_df
    return prescore_df, filtered_df[data.columns], prescore_latency


def __add_citation_columns_to_predictions_df(predictions_df):
    if LLM_CONTEXT_COLUMN_NAME not in predictions_df.columns:
        return predictions_df

    # Remove existing citation columns - currently playground is sending CITATION_*
    # explicitly.  Lets remove those and generate our own
    citation_columns = get_all_citation_columns(predictions_df)
    if len(citation_columns) > 0:
        predictions_df = predictions_df.drop(columns=citation_columns, axis=1)
    citations_dataframe = pd.DataFrame()
    for row_index, llm_context in enumerate(predictions_df[LLM_CONTEXT_COLUMN_NAME].tolist()):
        docs = json.loads(llm_context)
        d = {}
        for index, doc in enumerate(docs):
            d[f"CITATION_CONTENT_{index}"] = [doc["content"]]
        df = pd.DataFrame.from_dict(d, orient="columns")
        df.index = [row_index]
        # Join it row wise first
        citations_dataframe = pd.concat([citations_dataframe, df], axis=0)

    # and then concat it to the original one
    return pd.concat([predictions_df, citations_dataframe], axis=1)


def run_user_score_function(filtered_df, model, pipeline, drum_score_fn, **kwargs):
    """
    A wrapper to execute user's `score` method.  Wrapper is useful to calculate the
    latency of the `score` method and handle any exceptional conditions

    Args:
        filtered_df: Input DataFrame to execute `score` on.  In the presence of
            prescore guards, it should be `filtered_df` returned by the method
            `run_prescore_guards`.  Otherwise, it is an input dataframe received
             from the user
        model: Model object as passed by DRUM
        pipeline: Guard Pipeline
        drum_score_fn: The `score` method to execute
        **kwargs:

    Returns:
        predictions_df: DataFrame obtained as a return value from user's `score`
            method
        score_latency: Latency to execute user's `score` method
    """
    response_column_name = pipeline.get_input_column(GuardStage.RESPONSE)
    start_time = time.time()

    try:
        predictions_df = drum_score_fn(filtered_df, model, **kwargs)
    except Exception as e:
        title = "Failed to execute user score function"
        message = f"Exception: {e}"
        _logger.error(title + " " + message)
        pd.set_option("display.max_columns", None)
        _logger.error(filtered_df)
        pipeline.send_event_sync(
            title, message, ModerationEventTypes.MODERATION_MODEL_SCORING_ERROR
        )
        raise

    if response_column_name not in predictions_df.columns:
        title = "Cannot execute postscore guards"
        message = (
            "Missing response column in predictions df, can't run postscore guards - "
            f"Columns received: {predictions_df.columns}, "
            f"Response column expected: {response_column_name}"
        )
        _logger.error(message)
        pipeline.send_event_sync(
            title, message, ModerationEventTypes.MODERATION_MODEL_SCORING_ERROR
        )
        pd.set_option("display.max_columns", None)
        _logger.error(predictions_df)
        raise Exception(
            f"Response column name {response_column_name} is missing in "
            "the predictions df returned by custom.py"
        )

    # Temporarily add citation columns to predictions_df
    predictions_df = __add_citation_columns_to_predictions_df(predictions_df)
    # Because 'score' function index is not same as filtered data index
    # we need to match the indexes first
    predictions_df.index = filtered_df.index
    none_predictions_df = predictions_df[predictions_df[response_column_name].isnull()]
    valid_predictions_df = predictions_df[predictions_df[response_column_name].notnull()]
    end_time = time.time()
    score_latency = end_time - start_time
    pipeline.report_score_latency(score_latency)
    return valid_predictions_df, none_predictions_df, score_latency


def _auto_generate_association_ids(num_rows):
    _logger.info(f"Auto generating {num_rows} association ids")
    return [str(uuid.uuid4()) for _ in range(num_rows)]


def guard_score_wrapper(data, model, pipeline, drum_score_fn, **kwargs):
    """
    Score wrapper function provided by the moderation library.  DRUM will invoke this
    function with the user's score function.  The wrapper will execute following steps:

        1.  Run prescore guards
        2.  Execute user's `score` method
        3.  Run postscore guards
        4.  Assemble the result dataframe using output from steps 1 to 3
        5.  Perform additional metadata calculations (eg. token counts, confidence
            score etc)

    Args:
        data: Input dataframe sent for predictions by the user
        model: Model object as passed by DRUM
        pipeline: Guard Pipeline (initialized in the `init()` call
        drum_score_fn: User's `score` method
    :return:
    """
    _logger.debug(data)

    pipeline.get_new_metrics_payload()
    prompt_column_name = pipeline.get_input_column(GuardStage.PROMPT)
    association_id_column_name = pipeline.get_association_id_column_name()
    if (
        association_id_column_name
        and association_id_column_name not in data.columns
        and pipeline.auto_generate_association_ids
    ):
        data[association_id_column_name] = _auto_generate_association_ids(data.shape[0])

    # ==================================================================
    # Step 1: Prescore Guards processing
    #
    prescore_df, filtered_df, prescore_latency = run_prescore_guards(pipeline, data)

    _logger.debug("After passing input through pre score guards")
    _logger.debug(filtered_df)
    _logger.debug(f"Pre Score Guard Latency: {prescore_latency} sec")

    if filtered_df.empty:
        blocked_message_prompt_column_name = f"blocked_message_{prompt_column_name}"
        # If all prompts in the input are blocked, means no need to
        # run score function and postscore guards, just simply return
        # the prescore_df
        prescore_df.rename(
            columns={
                blocked_message_prompt_column_name: pipeline.get_input_column(GuardStage.RESPONSE)
            },
            inplace=True,
        )
        pipeline.report_custom_metrics(prescore_df)
        return _handle_result_df_error_cases(prompt_column_name, prescore_df, prescore_latency)
    # ==================================================================

    # ==================================================================
    # Step 2: custom.py `score` call
    #
    predictions_df, none_predictions_df, score_latency = run_user_score_function(
        filtered_df, model, pipeline, drum_score_fn, **kwargs
    )
    _logger.debug("After invoking user's score function")
    _logger.debug(predictions_df)

    # Don't lose the association ids if they exist:
    if (
        association_id_column_name
        and association_id_column_name not in predictions_df.columns
        and association_id_column_name in filtered_df.columns
    ):
        predictions_df[association_id_column_name] = filtered_df[association_id_column_name]
    # ==================================================================

    # ==================================================================
    # Step 3: Postscore Guards processing
    #
    prompt_column_name = pipeline.get_input_column(GuardStage.PROMPT)
    # Required for faithfulness calculation, we get prompt from the filtered_df
    # because it will use the replaced prompt if present.
    predictions_df[prompt_column_name] = filtered_df[prompt_column_name]

    postscore_df, postscore_latency = run_postscore_guards(pipeline, predictions_df)

    # ==================================================================
    # Step 4: Assemble the result - we need to merge prescore, postscore
    #         Dataframes.
    #
    result_df = format_result_df(pipeline, prescore_df, postscore_df, data, none_predictions_df)

    # ==================================================================
    # Step 5: Additional metadata calculations
    #
    result_df["datarobot_latency"] = (
        score_latency + prescore_latency + postscore_latency
    ) / result_df.shape[0]

    return result_df


def format_result_df(pipeline, prescore_df, postscore_df, data, none_predictions_df=None):
    """
    Build the final response dataframe to be returned as response using
    moderation information from prescore and postscore guards as well as
    input dataframe

    Args:
        pipeline: Guard Pipeline
        prescore_df: `prescore_df` obtained from `run_prescore_guards`
        postscore_df: `postscore_df` obtained from `run_postscore_guards`
        data: Input dataframe sent for predictions by the user

    Returns:
        result_df: Final dataframe with predictions and moderation information
            combined to be returned to the user

    """
    prompt_column_name = pipeline.get_input_column(GuardStage.PROMPT)
    blocked_prompt_column_name = f"blocked_{prompt_column_name}"
    blocked_message_prompt_column_name = f"blocked_message_{prompt_column_name}"
    response_column_name = pipeline.get_input_column(GuardStage.RESPONSE)
    blocked_completion_column_name = f"blocked_{response_column_name}"
    unmoderated_response_column_name = f"unmoderated_{response_column_name}"
    moderated_prompt_column_name = f"moderated_{prompt_column_name}"
    replaced_prompt_column_name = f"replaced_{prompt_column_name}"
    replaced_message_prompt_column_name = f"replaced_message_{prompt_column_name}"

    # This is the final result_df to be returned to the user
    result_columns = (
        set(postscore_df.columns)
        .union(set(prescore_df.columns))
        .union(set(datarobot_metadata_columns))
        .union({unmoderated_response_column_name, moderated_prompt_column_name})
    )
    result_df = pd.DataFrame(index=data.index, columns=list(result_columns))

    # for the blocked prompts, their completion is the blocked message
    # configured by the guard
    for index, row in prescore_df.iterrows():
        if row.get(blocked_prompt_column_name):
            result_df.loc[index, response_column_name] = row[blocked_message_prompt_column_name]
            result_df.loc[index, unmoderated_response_column_name] = np.nan
        elif row.get(replaced_prompt_column_name):
            result_df.loc[index, moderated_prompt_column_name] = row[
                replaced_message_prompt_column_name
            ]
        else:
            result_df.loc[index, moderated_prompt_column_name] = row[prompt_column_name]
        # Copy metric columns from prescore_df - it has prediction values from
        # the prescore guards, whether prescore guard blocked the text or not
        # what action prescore guard took on that prompt etc
        for column in prescore_df.columns:
            result_df.loc[index, column] = row[column]

    if none_predictions_df is not None and not none_predictions_df.empty:
        for index, row in none_predictions_df.iterrows():
            result_df.loc[index, response_column_name] = NONE_CUSTOM_PY_RESPONSE
            result_df.loc[index, unmoderated_response_column_name] = NONE_CUSTOM_PY_RESPONSE
            result_df.loc[index, blocked_completion_column_name] = False
            for column in none_predictions_df.columns:
                if column != response_column_name:
                    result_df.loc[index, column] = row[column]

    blocked_message_completion_column_name = f"blocked_message_{response_column_name}"
    replaced_response_column_name = f"replaced_{response_column_name}"
    replaced_message_response_column_name = f"replaced_message_{response_column_name}"
    # Now for the rest of the prompts, we did get completions.  If the completion
    # is blocked, use that message, else use the completion.  Note that, even if
    # PII Guard has replaced the completion, it will still be under row['completion']
    for index, row in postscore_df.iterrows():
        if row.get(blocked_completion_column_name):
            result_df.loc[index, response_column_name] = row[blocked_message_completion_column_name]
        elif row.get(replaced_response_column_name):
            result_df.loc[index, response_column_name] = row[replaced_message_response_column_name]
        else:
            result_df.loc[index, response_column_name] = row[response_column_name]
        result_df.loc[index, unmoderated_response_column_name] = row[response_column_name]
        # Similarly, copy metric columns from the postscore df - it has prediction
        # values from the postscore guards, whether postscore guard blocked the
        # completion or reported the completion, what action postscore guard took on
        # that completion, citations etc
        for column in postscore_df.columns:
            if column != response_column_name:
                result_df.loc[index, column] = row[column]

    block_citations_if_prompt_blocked(pipeline, result_df)
    calculate_token_counts_and_confidence_score(pipeline, result_df)

    result_df = remove_unnecessary_columns(pipeline, result_df)

    # Single call custom metric reporting
    pipeline.report_custom_metrics(result_df)

    # Also, ensure that result_df does not contain columns from the input df, creates problem
    # during the data export
    for column in data.columns:
        if column in result_df.columns:
            result_df.drop(column, axis=1, inplace=True)

    _logger.debug("Return df")
    _logger.debug(result_df)

    return result_df


def run_user_chat_function(completion_create_params, model, pipeline, drum_chat_fn, **kwargs):
    """
    A wrapper to execute user's `chat` method.  Wrapper is useful to calculate the
    latency of the `chat` method and handle any exceptional conditions

    Args:
        completion_create_params: Prompt with chat history
        model: Model object as passed by DRUM
        pipeline: Guard Pipeline
        drum_chat_fn: The `chat` method to execute

    Returns:
        chat_completion: ChatCompletion object as returned by the user's chat method
        score_latency: Latency to execute user's `chat` method
    """
    start_time = time.time()

    try:
        chat_completion = drum_chat_fn(completion_create_params, model, **kwargs)
    except Exception as e:
        _logger.error(f"Failed to execute user chat function: {e}")
        raise

    end_time = time.time()
    score_latency = end_time - start_time
    pipeline.report_score_latency(score_latency)

    return chat_completion, score_latency


def build_predictions_df_from_completion(data, pipeline, chat_completion):
    response_column_name = pipeline.get_input_column(GuardStage.RESPONSE)
    predictions_df = data.copy(deep=True)
    if isinstance(chat_completion, ChatCompletion):
        if len(chat_completion.choices) == 0:
            raise ValueError("Invalid response from custom.py, len(choices) = 0")
        predictions_df[response_column_name] = chat_completion.choices[0].message.content
        if getattr(chat_completion, CITATIONS_ATTR, None):
            predictions_df = add_citations_to_df(chat_completion.citations, predictions_df)
        if getattr(chat_completion, USAGE_ATTR, None):
            predictions_df = add_token_count_columns_to_df(
                pipeline, predictions_df, usage=chat_completion.usage
            )
        pipeline_interactions = getattr(chat_completion, AGENTIC_PIPELINE_INTERACTIONS_ATTR, None)
        if pipeline_interactions:
            predictions_df[AGENTIC_PIPELINE_INTERACTIONS_ATTR] = pipeline_interactions
        else:
            predictions_df[AGENTIC_PIPELINE_INTERACTIONS_ATTR] = [None] * len(predictions_df)

        source_object = chat_completion
    elif isinstance(chat_completion, Iterable):
        # Assemble the chunk in a single message
        messages = []
        last_chunk = None
        for index, chunk in enumerate(chat_completion):
            if not isinstance(chunk, ChatCompletionChunk):
                raise ValueError(
                    f"Chunk at index {index} is not of type 'ChatCompletionChunk',"
                    f" but is of type '{type(chunk)}'"
                )
            last_chunk = chunk
            if len(chunk.choices) == 0:
                _logger.warning(f"No chunk delta at index {index}, skipping it..")
                continue
            if chunk.choices[0].delta.content:
                # First chunk contents are '' and last chunk contents is None
                # Ignore those 2
                messages.append(chunk.choices[0].delta.content)
        predictions_df[response_column_name] = "".join(messages)
        if getattr(last_chunk, CITATIONS_ATTR, None):
            predictions_df = add_citations_to_df(last_chunk.citations, predictions_df)
        source_object = last_chunk
    else:
        raise ValueError(
            "Object returned by custom.py is not of type 'ChatCompletion' or an "
            f"'Iterable[ChatCompletionChunk], but is of type '{type(chat_completion)}'"
        )

    extra_attributes = {
        attr: getattr(source_object, attr, None)
        for attr in [
            LLM_BLUEPRINT_ID_ATTR,
            LLM_PROVIDER_GUARDS_ATTR,
            PROMPT_VECTOR_ATTR,
            CITATIONS_ATTR,
            USAGE_ATTR,
        ]
    }
    extra_attributes[AGENTIC_PIPELINE_INTERACTIONS_ATTR] = getattr(
        source_object, AGENTIC_PIPELINE_INTERACTIONS_ATTR, None
    )
    return predictions_df, extra_attributes


def build_non_streaming_chat_completion(message, reason, extra_attributes=None):
    message = ChatCompletionMessage(content=message, role="assistant")
    choice = Choice(finish_reason=reason, index=0, message=message)
    completion = ChatCompletion(
        id=str(uuid.uuid4()),
        choices=[choice],
        created=int(time.time()),
        model=MODERATION_MODEL_NAME,
        object=CHAT_COMPLETION_OBJECT,
    )
    if extra_attributes:
        for attr, attr_value in extra_attributes.items():
            setattr(completion, attr, attr_value)
    return completion


def _set_moderation_attribute_to_completion(pipeline, chat_completion, df, association_id=None):
    if not pipeline.extra_model_output_for_chat_enabled:
        return chat_completion

    moderations = build_moderations_attribute_for_completion(pipeline, df)

    if association_id:
        moderations["association_id"] = association_id
    if isinstance(chat_completion, ChatCompletion):
        setattr(chat_completion, DATAROBOT_MODERATIONS_ATTR, moderations)
    else:
        # Extra attribute to the last chunk of completion
        setattr(chat_completion[-1], DATAROBOT_MODERATIONS_ATTR, moderations)

    return chat_completion


def get_chat_prompt(completion_create_params):
    # Get the prompt with role = User
    last_user_message = None
    tool_calls = []
    for message in completion_create_params["messages"]:
        if message["role"] == "user":
            last_user_message = message
        if message["role"] == "tool":
            tool_calls.append(f"{message.get('name', '')}_{message['content']}")
    if last_user_message is None:
        raise Exception("No message with 'user' role found in input")

    prompt_content = last_user_message["content"]
    tool_names = []
    if "tools" in completion_create_params:
        for tool in completion_create_params["tools"]:
            if "function" in tool and "name" in tool["function"]:
                tool_names.append(tool["function"]["name"])
    if isinstance(prompt_content, str):
        chat_prompt = prompt_content
    elif isinstance(prompt_content, list):
        concatenated_prompt = []
        for content in prompt_content:
            if content["type"] == "text":
                message = content["text"]
            elif content["type"] == "image_url":
                message = f"Image URL: {content['image_url']['url']}"
            elif content["type"] == "input_audio":
                message = f"Audio Input, Format: {content['input_audio']['format']}"
            else:
                message = f"Unhandled content type: {content['type']}"
            concatenated_prompt.append(message)
        chat_prompt = "\n".join(concatenated_prompt)
    else:
        raise Exception(f"Unhandled prompt type: {type(prompt_content)}")

    if len(tool_calls) > 0:
        # Lets not add tool names if tool calls are present.  Tool calls are more
        # informative than names
        return "\n".join([chat_prompt, "Tool Calls:", "\n".join(tool_calls)])

    if len(tool_names) > 0:
        return "\n".join([chat_prompt, "Tool Names:", "\n".join(tool_names)])

    return chat_prompt


def _is_llm_requesting_user_tool_call(completion):
    if not completion:
        return False, completion

    if isinstance(completion, ChatCompletion):
        if not completion.choices or len(completion.choices) == 0:
            return False, completion
        if completion.choices[0].finish_reason == "tool_calls":
            return True, completion
    elif hasattr(completion, "__next__"):
        # 'Peek' into first chunk to see if it is a tool call
        chunk = next(completion)
        # either way, make sure the iterator is conserved
        completion = itertools.chain([chunk], completion)
        if (
            not isinstance(chunk, ChatCompletionChunk)
            or not chunk.choices
            or len(chunk.choices) == 0
            or not chunk.choices[0].delta
            or not chunk.choices[0].delta.tool_calls
        ):
            return False, completion
        return True, completion
    return False, completion


def __get_otel_values(guards_list, stage, result_df):
    guard_values = {}
    for guard in guards_list:
        if not guard.has_average_score_custom_metric():
            continue
        guard_metric_column_name = guard.get_metric_column_name(stage)
        if guard_metric_column_name not in result_df.columns:
            _logger.warning(f"Missing column: {guard_metric_column_name} in result_df")
            continue
        guard_values[guard.get_span_column_name(stage)] = result_df[
            guard_metric_column_name
        ].tolist()[0]
    return guard_values


def report_otel_evaluation_set_metric(pipeline, result_df):
    current_span = trace.get_current_span()
    if not current_span:
        _logger.warning("No currently active span found to report evaluation set metric")
        return

    prompt_values = __get_otel_values(pipeline.get_prescore_guards(), GuardStage.PROMPT, result_df)
    response_values = __get_otel_values(
        pipeline.get_postscore_guards(), GuardStage.RESPONSE, result_df
    )

    final_value = {"prompt_guards": prompt_values, "response_guards": response_values}

    current_span.set_attribute("datarobot.moderation.evaluation", json.dumps(final_value))


def guard_chat_wrapper(
    completion_create_params, model, pipeline, drum_chat_fn, association_id=None, **kwargs
):
    pipeline.get_new_metrics_payload()

    prompt_column_name = pipeline.get_input_column(GuardStage.PROMPT)
    if (
        "messages" not in completion_create_params
        or completion_create_params["messages"] is None
        or len(completion_create_params["messages"]) == 0
        or not isinstance(completion_create_params["messages"][-1], dict)
        or "content" not in completion_create_params["messages"][-1]
    ):
        raise ValueError(f"Invalid chat input for moderation: {completion_create_params}")

    prompt = get_chat_prompt(completion_create_params)
    streaming_response_requested = completion_create_params.get("stream", False)

    data = pd.DataFrame({prompt_column_name: [prompt]})
    association_id_column_name = pipeline.get_association_id_column_name()
    if association_id_column_name:
        if association_id:
            data[association_id_column_name] = [association_id]
        elif pipeline.auto_generate_association_ids:
            data[association_id_column_name] = _auto_generate_association_ids(1)
            association_id = data[association_id_column_name].tolist()[0]

    # ==================================================================
    # Step 1: Prescore Guards processing
    #
    prescore_df, filtered_df, prescore_latency = run_prescore_guards(pipeline, data)

    _logger.debug("After passing input through pre score guards")
    _logger.debug(filtered_df)
    _logger.debug(f"Pre Score Guard Latency: {prescore_latency} sec")

    blocked_prompt_column_name = f"blocked_{prompt_column_name}"
    if prescore_df.loc[0, blocked_prompt_column_name]:
        pipeline.report_custom_metrics(prescore_df)
        blocked_message_prompt_column_name = f"blocked_message_{prompt_column_name}"
        # If all prompts in the input are blocked, means history as well as the prompt
        # are not worthy to be sent to LLM
        chat_completion = build_non_streaming_chat_completion(
            prescore_df.loc[0, blocked_message_prompt_column_name],
            "content_filter",
        )
        result_df = _handle_result_df_error_cases(prompt_column_name, prescore_df, prescore_latency)
        if streaming_response_requested:
            streaming_context = (
                StreamingContextBuilder()
                .set_input_df(data)
                .set_prescore_df(result_df)
                .set_prescore_latency(prescore_latency)
                .set_pipeline(pipeline)
                .set_association_id(association_id)
                .build()
            )
            return ModerationIterator(streaming_context, chat_completion)
        else:
            completion = _set_moderation_attribute_to_completion(
                pipeline, chat_completion, result_df, association_id=association_id
            )
            report_otel_evaluation_set_metric(pipeline, result_df)
            return completion

    replaced_prompt_column_name = f"replaced_{prompt_column_name}"
    if (
        replaced_prompt_column_name in prescore_df.columns
        and prescore_df.loc[0, replaced_prompt_column_name]
    ):
        # PII kind of guard could have modified the prompt, so use that modified prompt
        # for the user chat function
        _modified_chat = copy.deepcopy(completion_create_params)
        _modified_chat["messages"][-1]["content"] = filtered_df.loc[0, prompt_column_name]
    else:
        # If no modification, use the original input
        _modified_chat = completion_create_params
    # ==================================================================

    # ==================================================================
    # Step 2: custom.py `chat` call
    #
    chat_completion, score_latency = run_user_chat_function(
        _modified_chat, model, pipeline, drum_chat_fn, **kwargs
    )
    _logger.debug("After invoking user's chat function")
    _logger.debug(chat_completion)

    # If Tool call, content = None and tools_calls is not empty
    tool_call_request_by_llm, chat_completion = _is_llm_requesting_user_tool_call(chat_completion)
    if tool_call_request_by_llm:
        # Note: There is an opportunity to apply guard here, is LLM
        # asking the user to invoke right call? But, probably future work
        return chat_completion

    if streaming_response_requested:
        streaming_context = (
            StreamingContextBuilder()
            .set_input_df(data)
            .set_prescore_df(prescore_df)
            .set_prescore_latency(prescore_latency)
            .set_pipeline(pipeline)
            .set_association_id(association_id)
            .build()
        )
        return ModerationIterator(streaming_context, chat_completion)

    # Rest of the code flow below is non-streaming completion requested
    # ==================================================================
    # Step 3: Postscore Guards processing
    #
    # Prompt column name is already part of data and gets included for
    # faithfulness calculation processing
    response_column_name = pipeline.get_input_column(GuardStage.RESPONSE)
    predictions_df, extra_attributes = build_predictions_df_from_completion(
        data, pipeline, chat_completion
    )
    response = predictions_df.loc[0, response_column_name]

    if response is not None:
        none_predictions_df = None
        postscore_df, postscore_latency = run_postscore_guards(pipeline, predictions_df)
    else:
        postscore_df, postscore_latency = pd.DataFrame(), 0
        none_predictions_df = predictions_df

    # ==================================================================
    # Step 4: Assemble the result - we need to merge prescore, postscore
    #         Dataframes.
    #
    result_df = format_result_df(
        pipeline, prescore_df, postscore_df, data, none_predictions_df=none_predictions_df
    )

    # ==================================================================
    # Step 5: Additional metadata calculations
    #
    result_df["datarobot_latency"] = (
        score_latency + prescore_latency + postscore_latency
    ) / result_df.shape[0]

    response_message, finish_reason = get_response_message_and_finish_reason(pipeline, postscore_df)
    report_otel_evaluation_set_metric(pipeline, result_df)

    final_completion = build_non_streaming_chat_completion(
        response_message, finish_reason, extra_attributes
    )
    return _set_moderation_attribute_to_completion(
        pipeline, final_completion, result_df, association_id=association_id
    )


def run_vdb_score_function(
    input_df: pd.DataFrame, model, pipeline, drum_score_fn, **kwargs
) -> pd.DataFrame:
    """
    A wrapper to execute vdb's `score` method.  Wrapper is useful to calculate the
    latency of the `score` method and handle any exceptional conditions
    Returns:
        predictions_df: DataFrame obtained as a return value from user's `score`
            method
    """
    start_time = time.time()

    try:
        predictions_df = drum_score_fn(input_df, model, **kwargs)
    except Exception as e:
        title = "Failed to execute vdb score function"
        message = f"Exception: {e}"
        _logger.error(title + " " + message)
        pd.set_option("display.max_columns", None)
        _logger.error(input_df)
        pipeline.send_event_sync(
            title, message, ModerationEventTypes.MODERATION_MODEL_SCORING_ERROR
        )
        raise

    score_latency = time.time() - start_time
    pipeline.record_score_latency(score_latency)
    return predictions_df


def vdb_score_wrapper(data: pd.DataFrame, model, pipeline: VDBPipeline, drum_score_fn, **kwargs):
    """
    Run on each prediction, and takes care of running the "score" function as well
    as collecting the metrics for the VDB pipeline.
    """
    _logger.debug(data)

    # clear/allocate memory for reporting metrics
    pipeline.get_new_metrics_payload()

    # NOTE: no "pre-score" calculation on the DataFrame for the predictions

    # perform the main "score" function for this model
    predictions_df = run_vdb_score_function(data, model, pipeline, drum_score_fn, **kwargs)

    # loop through all the metrics scoring for the pipeline with predictions_df that has citations
    for scorer in pipeline.scorers():
        value = scorer.score(predictions_df)
        pipeline.record_aggregate_value(scorer.name, value)

    pipeline.report_custom_metrics()
    return predictions_df


def vdb_init():
    """Initializes a VDB pipeline."""
    return VDBPipeline()


def init(model_dir: str = os.getcwd()):
    """
    Initialize the moderation framework

    Returns:
        pipeline: A Guard pipeline object required to enforce moderations while
            scoring on user data
    """
    disable_moderation_runtime_value = get_runtime_parameter_value_bool(
        param_name=DISABLE_MODERATION_RUNTIME_PARAM_NAME,
        default_value=False,
    )
    if disable_moderation_runtime_value:
        _logger.warning("Moderation is disabled via runtime parameter on the model")
        return None

    guard_config_file = os.path.join(model_dir, MODERATION_CONFIG_FILE_NAME)
    if not os.path.exists(guard_config_file):
        _logger.warning(
            f"Guard config file: {guard_config_file} not found in the model directory,"
            " moderations will not be enforced on this model"
        )
        return None
    pipeline = LLMPipeline(guard_config_file)
    # Lets export the PROMPT_COLUMN_NAME for custom.py
    os.environ["PROMPT_COLUMN_NAME"] = pipeline.get_input_column(GuardStage.PROMPT)
    os.environ["RESPONSE_COLUMN_NAME"] = pipeline.get_input_column(GuardStage.RESPONSE)
    return pipeline


class ModerationPipeline:
    """Base class to simplify interactions with DRUM."""

    def score(self, input_df: pd.DataFrame, model, drum_score_fn, **kwargs):
        """Default score function just runs the DRUM score function."""
        return drum_score_fn(input_df, model, **kwargs)

    def chat(
        self,
        completion_create_params: pd.DataFrame,
        model,
        drum_chat_fn,
        association_id: str = None,
        **kwargs,
    ):
        """Default chat wrapper function just runs the DRUM chat function."""
        return drum_chat_fn(
            completion_create_params, model, association_id=association_id, **kwargs
        )


class LlmModerationPipeline(ModerationPipeline):
    def __init__(self, pipeline: LLMPipeline):
        self._pipeline = pipeline

    def score(self, data: pd.DataFrame, model, drum_score_fn, **kwargs):
        """Calls the standard guard score function."""
        return guard_score_wrapper(data, model, self._pipeline, drum_score_fn, **kwargs)

    def chat(
        self,
        completion_create_params: pd.DataFrame,
        model,
        drum_chat_fn,
        association_id=None,
        **kwargs,
    ):
        """Calls the standard guard chat function."""
        return guard_chat_wrapper(
            completion_create_params,
            model,
            self._pipeline,
            drum_chat_fn,
            association_id=association_id,
            **kwargs,
        )


class VdbModerationPipeline(ModerationPipeline):
    def __init__(self, pipeline: VDBPipeline):
        self._pipeline = pipeline

    def score(self, data: pd.DataFrame, model, drum_score_fn, **kwargs):
        """Calls the VDB score function."""
        return vdb_score_wrapper(data, model, self._pipeline, drum_score_fn, **kwargs)


def moderation_pipeline_factory(
    target_type: str, model_dir: str = os.getcwd()
) -> Optional[ModerationPipeline]:
    # Disable ragas tracking while loading the module.
    os.environ["RAGAS_DO_NOT_TRACK"] = "true"
    if target_type in TargetType.guards():
        pipeline = init(model_dir=model_dir)
        if pipeline:
            return LlmModerationPipeline(pipeline)

    if target_type in TargetType.vdb():
        pipeline = vdb_init()
        if pipeline:
            return VdbModerationPipeline(pipeline)

    _logger.warning(f"Unsupported target type: {target_type}")
    return None
