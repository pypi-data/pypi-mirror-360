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
import uuid
from collections.abc import Iterable

import pandas as pd
from openai.types.chat import ChatCompletionChunk
from openai.types.chat.chat_completion import ChatCompletion
from openai.types.chat.chat_completion_chunk import Choice
from openai.types.chat.chat_completion_chunk import ChoiceDelta

from datarobot_dome.chat_helper import add_citations_to_df
from datarobot_dome.chat_helper import build_moderations_attribute_for_completion
from datarobot_dome.chat_helper import calculate_token_counts_and_confidence_score
from datarobot_dome.chat_helper import get_response_message_and_finish_reason
from datarobot_dome.chat_helper import remove_unnecessary_columns
from datarobot_dome.chat_helper import run_postscore_guards
from datarobot_dome.constants import CHAT_COMPLETION_CHUNK_OBJECT
from datarobot_dome.constants import CITATIONS_ATTR
from datarobot_dome.constants import DATAROBOT_MODERATIONS_ATTR
from datarobot_dome.constants import LOGGER_NAME_PREFIX
from datarobot_dome.constants import MODERATION_MODEL_NAME
from datarobot_dome.constants import GuardAction
from datarobot_dome.constants import GuardStage
from datarobot_dome.constants import GuardType
from datarobot_dome.constants import OOTBType
from datarobot_dome.guard import Guard


class StreamingContext:
    """Object maintains the context for later streaming requests"""

    def __init__(self):
        self.pipeline = None
        self.prompt = None
        self.association_id = None
        self.prescore_df = None
        self.prescore_latency = None
        self.input_df = None


class StreamingContextBuilder:
    def __init__(self):
        self.streaming_context = StreamingContext()

    def set_pipeline(self, pipeline):
        self.streaming_context.pipeline = pipeline
        return self

    def set_prompt(self, prompt):
        self.streaming_context.prompt = prompt
        return self

    def set_association_id(self, association_id):
        self.streaming_context.association_id = association_id
        return self

    def set_prescore_df(self, prescore_df):
        self.streaming_context.prescore_df = prescore_df
        return self

    def set_prescore_latency(self, prescore_latency):
        self.streaming_context.prescore_latency = prescore_latency
        return self

    def set_input_df(self, input_df):
        self.streaming_context.input_df = input_df
        return self

    def build(self):
        return self.streaming_context


class ModerationIterator:
    def __init__(self, streaming_context, completion):
        self.logger = logging.getLogger(LOGGER_NAME_PREFIX + "." + self.__class__.__name__)
        self.input_df = streaming_context.input_df
        self.original_completion = completion
        self.pipeline = streaming_context.pipeline
        self.prescore_df = streaming_context.prescore_df
        self.latency_so_far = streaming_context.prescore_latency
        self.datarobot_moderations = None
        self.chat_completion = self._build_streaming_chat_completion()
        # Dequeue first chunk
        self.chunk = next(self.chat_completion)
        self.assembled_response = []
        self.postscore_latency = 0
        self.postscore_df_assembled = None
        self.aggregated_metrics_df = None

        # List of postscore guards that can work on chunks
        self.postscore_guards_applied_to_chunks = []

        # List of guards that don't need citations
        for guard in self.pipeline.get_postscore_guards():
            if self._guard_can_work_on_chunk(guard):
                self.postscore_guards_applied_to_chunks.append(guard)

        self.first_chunk = True
        self.last_chunk = False

    def _set_prescore_moderations_info(self, chunk):
        """
        Returning prescore moderations information with the first chunk, so that user
        has access to this information quickly.
        """
        moderations = build_moderations_attribute_for_completion(self.pipeline, self.prescore_df)
        setattr(chunk, DATAROBOT_MODERATIONS_ATTR, moderations)
        self.first_chunk = False

    def _guard_can_work_on_chunk(self, guard):
        if guard.type == GuardType.OOTB and guard.ootb_type in [
            OOTBType.ROUGE_1,
            OOTBType.FAITHFULNESS,
        ]:
            return False
        if guard.type == GuardType.NEMO_GUARDRAILS:
            return False
        return True

    @staticmethod
    def create_chat_completion_chunk(content, finish_reason=None, role=None, citations=None):
        chunk = ChatCompletionChunk(
            id=str(uuid.uuid4()),
            choices=[
                Choice(
                    delta=ChoiceDelta(content=content, role=role),
                    finish_reason=finish_reason,
                    index=0,
                )
            ],
            created=int(time.time()),
            model=MODERATION_MODEL_NAME,
            object=CHAT_COMPLETION_CHUNK_OBJECT,
        )
        if citations:
            setattr(chunk, CITATIONS_ATTR, citations)
        return chunk

    def _build_streaming_chat_completion(self):
        if isinstance(self.original_completion, ChatCompletion):

            def generator():
                yield self.create_chat_completion_chunk("", role="assistant")
                yield self.create_chat_completion_chunk(
                    self.original_completion.choices[0].message.content
                )

                citations = None
                if hasattr(self.original_completion, CITATIONS_ATTR):
                    citations = self.original_completion.citations
                yield self.create_chat_completion_chunk(
                    None,
                    finish_reason=self.original_completion.choices[0].finish_reason,
                    citations=citations,
                )

            return generator()

        elif isinstance(self.original_completion, Iterable):
            return self.original_completion

        raise Exception(f"Unhandled completion type: {type(self.original_completion)}")

    def __iter__(self):
        return self

    def __next__(self):
        """
        The main iterator for streaming response.

        It returns the prescore guard information with first chunk, then information about
        the post score guards that can be run on chunks will be incorporated and the last
        chunk will have information about postscore guard information for the last chunk
        as well as faithfulness - rouge guards information (if configured) on the aseembled
        response.
        """
        if self.last_chunk:
            raise StopIteration

        return_chunk = self.chunk
        try:
            self.chunk = next(self.chat_completion)
        except StopIteration:
            self.last_chunk = True

        if len(self.pipeline.get_postscore_guards()) == 0:
            # No postscore guards, relay the stream we get
            if self.first_chunk:
                self._set_prescore_moderations_info(return_chunk)
            if self.last_chunk:
                self.pipeline.report_custom_metrics(self.prescore_df)
            return return_chunk

        chunk_content = return_chunk.choices[0].delta.content
        if not self.last_chunk:
            if not chunk_content:
                if self.first_chunk:
                    self._set_prescore_moderations_info(return_chunk)
                return return_chunk
            else:
                self.assembled_response.append(chunk_content)
                postscore_df = self._run_postscore_guards_on_chunk(return_chunk)
                self._merge_metrics(postscore_df)
                if return_chunk.choices[0].finish_reason == "content_filter":
                    # If the moderation blocks the chunk - mark it last chunk - the library is not
                    # going to return any further chunks
                    self.last_chunk = True
        else:
            if chunk_content:
                # Typical OpenAI stream would have last chunk = None indicating its the last
                # chunk in the stream.  So, we don't expect it often to have to run postscore
                # guards on the last chunk.  But, "in case" there is a valid last chunk - the
                # library ends up running the postscore guards on chunk and then on the assembled
                # response.  Means -> latency for last chunk.
                #
                # We tried to explore options to make it concurrent using asyncio, threads, but
                # that complicates the overall structure.
                #
                # Because this is not a typical case, we don't want to over optimize it for now.
                self.assembled_response.append(chunk_content)
                postscore_df_chunk = self._run_postscore_guards_on_chunk(return_chunk)
            else:
                postscore_df_chunk = None

            citations = None
            if getattr(return_chunk, CITATIONS_ATTR, None):
                citations = return_chunk.citations
            postscore_df_assembled = self._run_postscore_guards_on_assembled_response(citations)
            if postscore_df_chunk is not None:
                if return_chunk.choices[0].finish_reason == "content_filter":
                    self._merge_metrics(postscore_df_chunk)
                    postscore_df = self._merge_assembled(postscore_df_chunk, postscore_df_assembled)
                    self.aggregated_metrics_df = postscore_df
                else:
                    self.aggregated_metrics_df = postscore_df_assembled
                    postscore_df = postscore_df_assembled
            else:
                self.aggregated_metrics_df = postscore_df_assembled
                postscore_df = postscore_df_assembled

        if self.first_chunk:
            moderations_df = postscore_df.merge(self.prescore_df, on=list(self.input_df.columns))
            self.first_chunk = False
        else:
            moderations_df = postscore_df
        moderations = build_moderations_attribute_for_completion(self.pipeline, moderations_df)
        setattr(return_chunk, DATAROBOT_MODERATIONS_ATTR, moderations)
        if self.last_chunk:
            self._aggregate_guard_latencies()
            self._report_metrics()
        return return_chunk

    def _run_postscore_guards_on_chunk(self, return_chunk):
        chunk_content = return_chunk.choices[0].delta.content
        response_column_name = self.pipeline.get_input_column(GuardStage.RESPONSE)

        predictions_df = self.input_df.copy(deep=True)
        predictions_df[response_column_name] = [chunk_content]

        # Run postscore guards on the chunk content - Note that we are only running
        # the guards which don't need citations or the whole response (eg. NeMo)
        postscore_df_chunk, postscore_latency_chunk = run_postscore_guards(
            self.pipeline, predictions_df, postscore_guards=self.postscore_guards_applied_to_chunks
        )
        self.postscore_latency += postscore_latency_chunk

        final_response_message, final_finish_reason = get_response_message_and_finish_reason(
            self.pipeline, postscore_df_chunk, streaming=True
        )

        postscore_df_chunk = remove_unnecessary_columns(self.pipeline, postscore_df_chunk)
        return_chunk.choices[0].delta.content = final_response_message
        return_chunk.choices[0].finish_reason = final_finish_reason

        return postscore_df_chunk

    def _run_postscore_guards_on_assembled_response(self, citations):
        if len(self.assembled_response) == 0:
            response_column_name = self.pipeline.get_input_column(GuardStage.RESPONSE)
            blocked_completion_column_name = f"blocked_{response_column_name}"
            return pd.DataFrame({blocked_completion_column_name: [False]})

        predictions_df = self.input_df.copy(deep=True)
        response_column_name = self.pipeline.get_input_column(GuardStage.RESPONSE)
        predictions_df[response_column_name] = "".join(self.assembled_response)
        predictions_df = add_citations_to_df(citations, predictions_df)
        postscore_df_assembled, postscore_latency_assembled = run_postscore_guards(
            self.pipeline, predictions_df
        )
        self.postscore_latency += postscore_latency_assembled

        calculate_token_counts_and_confidence_score(self.pipeline, postscore_df_assembled)
        postscore_df_assembled["datarobot_latency"] = self.latency_so_far + self.postscore_latency

        postscore_df_assembled = remove_unnecessary_columns(self.pipeline, postscore_df_assembled)
        return postscore_df_assembled

    def _merge_metrics(self, metrics_df):
        if self.aggregated_metrics_df is None:
            self.aggregated_metrics_df = metrics_df.copy(deep=True)
            return

        response_column_name = self.pipeline.get_input_column(GuardStage.RESPONSE)
        for guard in self.postscore_guards_applied_to_chunks:
            if guard.type == GuardType.MODEL:
                metric_name = guard.model_info.target_name
                column_name = Guard.get_stage_str(GuardStage.RESPONSE) + "_" + metric_name
                # Metric value for the current chunk will be used for reporting.  If the
                # prompt was blocked because metric was higher than threshold, that value
                # should show up in the tracing table and metrics
                self.aggregated_metrics_df[column_name] = metrics_df[column_name]
            elif guard.type == GuardType.OOTB:
                if guard.ootb_type == OOTBType.TOKEN_COUNT:
                    column_name = guard.get_metric_column_name(GuardStage.RESPONSE)
                    self.aggregated_metrics_df[column_name] += metrics_df[column_name]
                else:
                    # Faithfulness, ROUGE-1 can't run on chunks so no merging
                    pass
            elif guard.type == GuardType.NEMO_GUARDRAILS:
                # No average score metric for NeMo
                pass

            if guard.has_latency_custom_metric():
                latency_column_name = f"{guard.name}_latency"
                # Each chunk incurs latency - so just sum it up.
                self.aggregated_metrics_df[latency_column_name] += metrics_df[latency_column_name]

            if guard.intervention:
                enforced_column_name = self.pipeline.get_enforced_column_name(
                    guard, GuardStage.RESPONSE
                )
                # For enforcement column - its simply logical OR of the enforced value of previous
                # chunks and current chunks
                self.aggregated_metrics_df[enforced_column_name] += metrics_df[enforced_column_name]
                action_column_name = f"action_{response_column_name}"
                self.aggregated_metrics_df[action_column_name] = metrics_df[action_column_name]

        for column_name in GuardAction.possible_column_names(response_column_name):
            self.aggregated_metrics_df[column_name] += metrics_df[column_name]

    def _aggregate_guard_latencies(self):
        for guard in self.postscore_guards_applied_to_chunks:
            if guard.has_latency_custom_metric():
                # Aggregate latencies
                latency_column_name = f"{guard.name}_latency"
                self.pipeline.report_guard_latency(
                    guard, self.aggregated_metrics_df.loc[0, latency_column_name]
                )

    def _merge_assembled(self, postscore_df_chunk, postscore_df_assembled):
        """
        Merge metric values from the guards that cannot be run on chunk
        :param postscore_df_assembled:
        :return:
        """
        postscore_df = postscore_df_chunk.copy(deep=True)
        for guard in self.pipeline.get_postscore_guards():
            if not self._guard_can_work_on_chunk(guard):
                metric_column_name = guard.get_metric_column_name(GuardStage.RESPONSE)
                if metric_column_name in postscore_df_assembled.columns:
                    postscore_df[metric_column_name] = postscore_df_assembled[metric_column_name]
                if guard.has_latency_custom_metric():
                    latency_column_name = f"{guard.name}_latency"
                    postscore_df[latency_column_name] = postscore_df_assembled[latency_column_name]
                if guard.intervention:
                    enforced_column_name = self.pipeline.get_enforced_column_name(
                        guard, GuardStage.RESPONSE
                    )
                    postscore_df[enforced_column_name] = postscore_df_assembled[
                        enforced_column_name
                    ]

        for key in ["datarobot_token_count", "datarobot_confidence_score", "datarobot_latency"]:
            if key in postscore_df_assembled.columns:
                postscore_df[key] = postscore_df_assembled[key]
        return postscore_df

    def _report_metrics(self):
        self.pipeline.report_stage_latency(self.postscore_latency, GuardStage.RESPONSE)
        result_df = self.aggregated_metrics_df.merge(
            self.prescore_df, on=list(self.input_df.columns)
        )
        self.pipeline.report_custom_metrics(result_df)
