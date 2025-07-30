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
import time
import traceback
from re import match

import tiktoken

from datarobot_dome.constants import AGENTIC_PIPELINE_INTERACTIONS_ATTR
from datarobot_dome.constants import NONE_CUSTOM_PY_RESPONSE
from datarobot_dome.constants import PROMPT_TOKEN_COUNT_COLUMN_NAME_FROM_USAGE
from datarobot_dome.constants import RESPONSE_TOKEN_COUNT_COLUMN_NAME_FROM_USAGE
from datarobot_dome.constants import GuardStage
from datarobot_dome.guard_executor import AsyncGuardExecutor
from datarobot_dome.guard_helpers import calculate_token_counts_for_cost_calculations
from datarobot_dome.guard_helpers import get_citation_columns
from datarobot_dome.guard_helpers import get_rouge_1_score

_logger = logging.getLogger("chat_helper")


def get_all_citation_columns(df):
    citation_columns = []
    for pattern in [
        "CITATION_CONTENT_",
        "CITATION_SOURCE_",
        "CITATION_PAGE_",
        "CITATION_CHUNK_ID_",
        "CITATION_START_INDEX_",
        "CITATION_SIMILARITY_SCORE_",
    ]:
        citation_columns.extend(list(filter(lambda column: match(pattern, column), df.columns)))
    return citation_columns


def build_moderations_attribute_for_completion(pipeline, df):
    """
    Given the dataframe build a moderation attribute to be returned with
    chat completion or chat completion chunk
    """
    if df is None or df.empty:
        return None

    prompt_column_name = pipeline.get_input_column(GuardStage.PROMPT)
    blocked_message_prompt_column_name = f"blocked_message_{prompt_column_name}"
    response_column_name = pipeline.get_input_column(GuardStage.RESPONSE)
    replaced_message_prompt_column_name = f"replaced_message_{prompt_column_name}"
    blocked_message_completion_column_name = f"blocked_message_{response_column_name}"
    replaced_message_response_column_name = f"replaced_message_{response_column_name}"

    moderations = df.to_dict(orient="records")[0]
    columns_to_drop = [
        pipeline.get_input_column(GuardStage.PROMPT),
        # Its already copied as part of the completion.choices[0].message.content
        pipeline.get_input_column(GuardStage.RESPONSE),
        blocked_message_prompt_column_name,
        blocked_message_completion_column_name,
        replaced_message_prompt_column_name,
        replaced_message_response_column_name,
        f"Noneed_{prompt_column_name}",
        f"Noneed_{response_column_name}",
    ]
    citation_columns = get_all_citation_columns(df)
    if len(citation_columns) > 0:
        columns_to_drop += citation_columns
    for column in columns_to_drop:
        if column in moderations:
            moderations.pop(column)

    return moderations


def run_postscore_guards(pipeline, predictions_df, postscore_guards=None):
    """Run postscore guards on the input data."""
    if not postscore_guards:
        postscore_guards = pipeline.get_postscore_guards()
    response_column_name = pipeline.get_input_column(GuardStage.RESPONSE)
    blocked_completion_column_name = f"blocked_{response_column_name}"
    input_df = predictions_df.copy(deep=True)
    if len(postscore_guards) == 0:
        input_df[blocked_completion_column_name] = False
        return input_df, 0

    start_time = time.time()
    try:
        postscore_df, postscore_latency = AsyncGuardExecutor(pipeline).run_guards(
            input_df, postscore_guards, GuardStage.RESPONSE
        )
    except Exception as ex:
        end_time = time.time()
        _logger.error(f"Failed to run postscore guards: {ex}")
        _logger.error(traceback.format_exc())
        postscore_df = input_df
        postscore_df[blocked_completion_column_name] = False
        postscore_latency = end_time - start_time

    # Again ensure the indexing matches the input dataframe indexing
    postscore_df.index = predictions_df.index
    _logger.debug("After passing completions through post score guards")
    _logger.debug(postscore_df)
    _logger.debug(f"Post Score Guard Latency: {postscore_latency} sec")

    return postscore_df, postscore_latency


def get_response_message_and_finish_reason(pipeline, postscore_df, streaming=False):
    response_column_name = pipeline.get_input_column(GuardStage.RESPONSE)
    blocked_completion_column_name = f"blocked_{response_column_name}"
    replaced_response_column_name = f"replaced_{response_column_name}"
    if postscore_df.empty:
        response_message = NONE_CUSTOM_PY_RESPONSE
        finish_reason = "stop"
    elif postscore_df.loc[0, blocked_completion_column_name]:
        blocked_message_completion_column_name = f"blocked_message_{response_column_name}"
        response_message = postscore_df.loc[0, blocked_message_completion_column_name]
        finish_reason = "content_filter"
    elif (
        replaced_response_column_name in postscore_df.columns
        and postscore_df.loc[0, replaced_response_column_name]
    ):
        replaced_message_response_column_name = f"replaced_message_{response_column_name}"
        response_message = postscore_df.loc[0, replaced_message_response_column_name]
        # In case of streaming - if the guard replaces the text, we don't want to
        # stop streaming - so don't put finish_reason in case of streaming
        finish_reason = None if streaming else "content_filter"
    else:
        response_message = postscore_df.loc[0, response_column_name]
        finish_reason = None if streaming else "stop"

    return response_message, finish_reason


def calculate_token_counts_and_confidence_score(pipeline, result_df):
    prompt_column_name = pipeline.get_input_column(GuardStage.PROMPT)
    blocked_prompt_column_name = f"blocked_{prompt_column_name}"
    response_column_name = pipeline.get_input_column(GuardStage.RESPONSE)
    blocked_completion_column_name = f"blocked_{response_column_name}"

    encoding = tiktoken.get_encoding("cl100k_base")

    citation_columns = get_citation_columns(result_df.columns)

    def _get_llm_contexts(index):
        contexts = []
        if len(citation_columns) >= 0:
            for column in citation_columns:
                contexts.append(result_df.loc[index][column])
        return contexts

    for index, row in result_df.iterrows():
        if not (
            row.get(blocked_prompt_column_name, False)
            or row.get(blocked_completion_column_name, False)
        ):
            completion = result_df.loc[index][response_column_name]
            if completion != NONE_CUSTOM_PY_RESPONSE:
                result_df.loc[index, "datarobot_token_count"] = len(
                    encoding.encode(str(completion), disallowed_special=())
                )
                result_df.loc[index, "datarobot_confidence_score"] = get_rouge_1_score(
                    pipeline.rouge_scorer, _get_llm_contexts(index), [completion]
                )
            else:
                result_df.loc[index, "datarobot_confidence_score"] = 0.0
        else:
            # If the row is blocked, set default value
            result_df.loc[index, "datarobot_confidence_score"] = 0.0


def add_citations_to_df(citations, df):
    if not citations:
        return df

    for index, citation in enumerate(citations):
        df[f"CITATION_CONTENT_{index}"] = citation["content"]
    return df


def add_token_count_columns_to_df(pipeline, df, usage=None):
    if not usage:
        prompt_column_name = pipeline.get_input_column(GuardStage.PROMPT)
        response_column_name = pipeline.get_input_column(GuardStage.RESPONSE)
        df = calculate_token_counts_for_cost_calculations(
            prompt_column_name, response_column_name, df
        )
    else:
        df[PROMPT_TOKEN_COUNT_COLUMN_NAME_FROM_USAGE] = [usage.prompt_tokens]
        df[RESPONSE_TOKEN_COUNT_COLUMN_NAME_FROM_USAGE] = [usage.completion_tokens]
    return df


def remove_unnecessary_columns(pipeline, result_df):
    prompt_column_name = pipeline.get_input_column(GuardStage.PROMPT)
    blocked_message_prompt_column_name = f"blocked_message_{prompt_column_name}"
    response_column_name = pipeline.get_input_column(GuardStage.RESPONSE)
    replaced_message_prompt_column_name = f"replaced_message_{prompt_column_name}"
    blocked_message_completion_column_name = f"blocked_message_{response_column_name}"
    replaced_message_response_column_name = f"replaced_message_{response_column_name}"
    # We don't need these columns, because they have already been copied into
    # 'completion' column
    columns_to_remove = [
        blocked_message_prompt_column_name,
        blocked_message_completion_column_name,
        replaced_message_prompt_column_name,
        replaced_message_response_column_name,
        f"Noneed_{prompt_column_name}",
        f"Noneed_{response_column_name}",
        PROMPT_TOKEN_COUNT_COLUMN_NAME_FROM_USAGE,
        RESPONSE_TOKEN_COUNT_COLUMN_NAME_FROM_USAGE,
        AGENTIC_PIPELINE_INTERACTIONS_ATTR,
    ]
    columns_to_remove.extend(get_all_citation_columns(result_df))
    for column in columns_to_remove:
        if column in result_df.columns:
            result_df = result_df.drop(column, axis=1)

    return result_df
