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
import asyncio
import json
import logging
import operator
import time
import traceback

import nest_asyncio
import pandas as pd
import requests.exceptions
from opentelemetry import trace

from datarobot_dome.constants import AGENTIC_PIPELINE_INTERACTIONS_ATTR
from datarobot_dome.constants import LOGGER_NAME_PREFIX
from datarobot_dome.constants import PROMPT_TOKEN_COUNT_COLUMN_NAME_FROM_USAGE
from datarobot_dome.constants import RESPONSE_TOKEN_COUNT_COLUMN_NAME_FROM_USAGE
from datarobot_dome.constants import GuardAction
from datarobot_dome.constants import GuardOperatorType
from datarobot_dome.constants import GuardStage
from datarobot_dome.constants import GuardTimeoutAction
from datarobot_dome.constants import GuardType
from datarobot_dome.constants import ModerationEventTypes
from datarobot_dome.constants import OOTBType
from datarobot_dome.guard import AgentGoalAccuracyGuard
from datarobot_dome.guard import FaithfulnessGuard
from datarobot_dome.guard import ModelGuard
from datarobot_dome.guard import NeMoGuard
from datarobot_dome.guard import OOTBCostMetric
from datarobot_dome.guard import OOTBGuard
from datarobot_dome.guard import TaskAdherenceGuard
from datarobot_dome.guard_helpers import calculate_agent_goal_accuracy
from datarobot_dome.guard_helpers import calculate_faithfulness
from datarobot_dome.guard_helpers import calculate_task_adherence
from datarobot_dome.guard_helpers import calculate_token_counts_for_cost_calculations
from datarobot_dome.guard_helpers import get_citation_columns
from datarobot_dome.guard_helpers import get_rouge_1_score
from datarobot_dome.guard_helpers import get_token_count
from datarobot_dome.guard_helpers import nemo_response_stage_input_formatter
from datarobot_dome.guard_helpers import nemo_response_stage_output_formatter

tracer = trace.get_tracer(__name__)


def get_operator_comparator(comparator):  # noqa: PLR0911
    if comparator == GuardOperatorType.GREATER_THAN:
        return operator.gt
    elif comparator == GuardOperatorType.LESS_THAN:
        return operator.lt
    elif comparator == GuardOperatorType.EQUALS:
        return operator.eq
    elif comparator == GuardOperatorType.NOT_EQUALS:
        return operator.ne
    # IS and IS_NOT are identical to EQUALS and NOT_EQUALS
    # this is because the "==" operator can be used for comparands of any type
    elif comparator == GuardOperatorType.IS:
        return operator.eq
    elif comparator == GuardOperatorType.IS_NOT:
        return operator.ne
    # MATCHES and DOES_NOT_MATCH are used for string comparands
    elif comparator == GuardOperatorType.MATCHES:
        return lambda x, y: [str(__x) in y for __x in x]
    elif comparator == GuardOperatorType.DOES_NOT_MATCH:
        return lambda x, y: [str(__x) not in y for __x in x]
    # CONTAINS and DOES_NOT_CONTAIN are used for list of strings comparands
    elif comparator == GuardOperatorType.CONTAINS:
        return lambda x, y: [all(item in str(__x) for item in y) for __x in x]
    elif comparator == GuardOperatorType.DOES_NOT_CONTAIN:
        return lambda x, y: [not all(item in str(__x) for item in y) for __x in x]
    else:
        raise NotImplementedError(f"Comparator {comparator} not implemented")


class AsyncGuardExecutor:
    guard_executor_map = {
        GuardType.MODEL: "run_model_guard",
        GuardType.OOTB: "run_ootb_guard",
        GuardType.NEMO_GUARDRAILS: "run_nemo_guard",
    }

    def __init__(self, pipeline):
        self._logger = logging.getLogger(LOGGER_NAME_PREFIX + "." + self.__class__.__name__)
        self.pipeline = pipeline
        self.async_http_client = self.pipeline.get_async_http_client()
        self.loop = asyncio.get_event_loop()
        self.loop.set_debug(True)
        nest_asyncio.apply(loop=self.loop)

    async def run_guard(self, guard, copy_df, stage):
        start_time = time.time()
        with tracer.start_as_current_span(f"DataRobot Guard: {guard.name}") as span:
            span.set_attribute("datarobot.moderation.guard.name", guard.name)
            span.set_attribute("datarobot.moderation.guard.type", guard.type)
            span.set_attribute("datarobot.moderation.guard.description", guard.description)
            span.set_attribute("datarobot.moderation.guard.stage", stage)

            executor = getattr(self, self.guard_executor_map[guard.type])
            df = await executor(guard, copy_df, stage)
            end_time = time.time()

            latency = end_time - start_time
            span.set_attribute("datarobot.moderation.guard.latency", latency)
            if guard.has_latency_custom_metric():
                self.pipeline.report_guard_latency(guard, latency)
            if guard.has_average_score_custom_metric():
                metric_column_name = guard.get_metric_column_name(stage)
                if metric_column_name in df.columns:
                    span.set_attribute(
                        guard.get_span_attribute_name(stage),
                        df[metric_column_name].tolist()[0],
                    )
            if guard.get_intervention_action():
                (
                    enforced_column_name,
                    _,
                    _,
                ) = self._get_enforced_and_action_column_names(
                    guard.get_intervention_action(), self.pipeline.get_input_column(stage)
                )
                span.set_attribute(
                    guard.get_enforced_span_attribute_name(stage),
                    df[enforced_column_name].tolist()[0],
                )

        return df, latency

    def _should_intervene(self, guard):
        if (
            guard.intervention
            and guard.intervention.threshold is not None
            and guard.intervention.comparator is not None
        ):
            return True
        return False

    @classmethod
    def _get_enforced_and_action_column_names(cls, intervention_action, input_column):
        action_column_name = "action_" + input_column
        if intervention_action == GuardAction.REPLACE:
            enforced_column_name = f"replaced_{input_column}"
        else:
            enforced_column_name = f"{intervention_action}ed_{input_column}"
        enforced_message_column_name = None
        if intervention_action == GuardAction.BLOCK:
            enforced_message_column_name = f"blocked_message_{input_column}"
        elif intervention_action == GuardAction.REPLACE:
            enforced_message_column_name = f"replaced_message_{input_column}"

        return enforced_column_name, enforced_message_column_name, action_column_name

    @classmethod
    def _initialize_enforced_and_action_columns(
        cls, df, enforced_column_name, enforced_message_column_name, action_column_name
    ):
        df[enforced_column_name] = False
        df[action_column_name] = ""
        if enforced_message_column_name:
            df[enforced_message_column_name] = ""

    async def run_model_guard(self, guard, copy_df, stage):
        if not isinstance(guard, ModelGuard):
            raise ValueError(f"Guard object should be of type ModelGuard, got: {type(guard)}")
        metric_column = guard.model_info.target_name

        llm_input_column = self.pipeline.get_input_column(stage)
        guard_input_column = guard.get_input_column(stage)

        intervene = self._should_intervene(guard)
        try:
            if llm_input_column not in copy_df.columns:
                raise ValueError(
                    f"Expecting column {llm_input_column} in DF, but is missing. Stage: {stage}"
                )

            # Copy and rename only the column guard needs, we don't need
            # to send rest of data to the guard model
            input_df_to_guard = copy_df[[llm_input_column]].copy()
            input_df_to_guard.rename(columns={llm_input_column: guard_input_column}, inplace=True)

            result_df = await self.async_http_client.predict(guard.deployment, input_df_to_guard)
            if metric_column not in result_df.columns:
                # This is caught anyways in the exception handling code and masked
                raise ValueError(
                    f"Missing output column {metric_column} in the model guard response"
                    f"Columns obtained: {result_df.columns}"
                )
            if (
                intervene
                and guard.intervention.action == GuardAction.REPLACE
                and guard.model_info.replacement_text_column_name not in result_df.columns
            ):
                # In case of "replace" intervention we expect the guard to send the
                # replacement as well
                raise ValueError(
                    f"Missing replacement column {guard.model_info.replacement_text_column_name} "
                    f"in the model guard response Columns obtained: {result_df.columns}"
                )
            # Ensure that index of result and copy dfs are same, so that concat will work
            # correctly
            result_df.index = copy_df.index
            columns_to_concat = [metric_column]
            if intervene and guard.intervention.action == GuardAction.REPLACE:
                columns_to_concat.append(guard.model_info.replacement_text_column_name)

            copy_df = pd.concat([copy_df, result_df[columns_to_concat]], axis="columns")

            if intervene:
                copy_df, _ = self._intervene(guard, copy_df, stage, metric_column)
            else:
                copy_df = self._dont_intervene(guard, copy_df, stage)
            # eg. toxicity_toxic_PREDICTION should be renamed to "Prompts_toxicity_toxic_PREDICTION"
            # and "Response_toxicity_toxic_PREDICTION", if toxicity is configured for both
            # prompts and responses
            copy_df.rename(
                columns={metric_column: guard.get_metric_column_name(stage)},
                inplace=True,
            )
        except Exception as ex:
            if isinstance(ex, asyncio.TimeoutError):
                title = "Model Guard timeout"
                message = f'Timed out waiting for guard "{guard.name}" to predict'
                if self.pipeline.guard_timeout_action == GuardTimeoutAction.BLOCK:
                    copy_df = self._timeout_intervention(guard, copy_df, stage)
                else:
                    # No intervention - continue scoring / returning response
                    copy_df = self._dont_intervene(guard, copy_df, stage)
            else:
                title = "Model guard predictions failed"
                message = f'Guard "{guard.name}": Exception {ex}'
                self._logger.error(traceback.format_exc())
                # No intervention
                copy_df = self._dont_intervene(guard, copy_df, stage)
            self._logger.error(title + " " + message)
            await self.pipeline.send_event_async(
                title,
                message,
                ModerationEventTypes.MODERATION_MODEL_RUNTIME_ERROR,
                guard_name=guard.name,
            )
        return copy_df

    def _timeout_intervention(self, guard, copy_df, stage):
        timeout_action = self.pipeline.guard_timeout_action
        input_column = self.pipeline.get_input_column(stage)
        (
            enforced_column_name,
            enforced_message_column_name,
            action_column_name,
        ) = self._get_enforced_and_action_column_names(timeout_action, input_column)
        copy_df[enforced_column_name] = True
        copy_df[action_column_name] = self.pipeline.guard_timeout_action
        if enforced_message_column_name:
            copy_df[enforced_message_column_name] = (
                f"DataRobot Moderation system {self.pipeline.guard_timeout_action}ing "
                f"it due to timeout on {guard.name} guard"
            )
        return copy_df

    def _dont_intervene(self, guard, copy_df, stage):
        input_column = self.pipeline.get_input_column(stage)
        (
            enforced_column_name,
            enforced_message_column_name,
            action_column_name,
        ) = self._get_enforced_and_action_column_names(
            guard.get_intervention_action(), input_column
        )
        self._initialize_enforced_and_action_columns(
            copy_df,
            enforced_column_name,
            enforced_message_column_name,
            action_column_name,
        )
        return copy_df

    @classmethod
    def intervene(cls, guard, copy_df, input_column, metric_column):
        intervention_action = guard.get_intervention_action()
        (
            enforced_column_name,
            enforced_message_column_name,
            action_column_name,
        ) = cls._get_enforced_and_action_column_names(intervention_action, input_column)
        cls._initialize_enforced_and_action_columns(
            copy_df,
            enforced_column_name,
            enforced_message_column_name,
            action_column_name,
        )

        # Do intervention
        threshold = guard.get_comparand()
        comparator = get_operator_comparator(guard.intervention.comparator)
        # update new tracking columns for this guard
        copy_df[action_column_name] = copy_df[action_column_name].mask(
            comparator(copy_df[metric_column], threshold),
            intervention_action,
        )
        copy_df[enforced_column_name] = copy_df[enforced_column_name].mask(
            comparator(copy_df[metric_column], threshold),
            True,
        )
        if guard.intervention.action == GuardAction.REPLACE:
            copy_df[enforced_message_column_name] = copy_df[enforced_message_column_name].mask(
                comparator(copy_df[metric_column], threshold),
                copy_df[guard.model_info.replacement_text_column_name],
            )
        elif guard.intervention.action == GuardAction.BLOCK:
            if guard.intervention.message:
                copy_df[enforced_message_column_name] = copy_df[enforced_message_column_name].mask(
                    comparator(copy_df[metric_column], threshold),
                    guard.intervention.message,
                )

        num_intervened = int(
            copy_df[copy_df[action_column_name] == guard.intervention.action][
                action_column_name
            ].count()
        )

        return copy_df, num_intervened

    def _intervene(self, guard, copy_df, stage, metric_column):
        input_column = self.pipeline.get_input_column(stage)
        return self.intervene(guard, copy_df, input_column, metric_column)

    async def _handle_faithfulness(self, guard, copy_df, stage, intervene):
        if not isinstance(guard, FaithfulnessGuard):
            raise ValueError(
                f"Guard object should be of type FaithfulnessGuard, got: {type(guard)}"
            )
        if stage == GuardStage.PROMPT:
            raise ValueError("Faithfulness only supports evaluating the response")

        citation_columns = get_citation_columns(copy_df.columns)
        if len(citation_columns) == 0:
            # For now, let us simply log the error.  In future, we can add new error
            # custom metrics to track it
            title = "Faithfulness guard configured without citation columns"
            message = f"Input Column Names: {copy_df.columns}"
            self._logger.error(title + " " + message)
            await self.pipeline.send_event_async(
                title,
                message,
                ModerationEventTypes.MODERATION_MODEL_CONFIG_ERROR,
                guard_name=guard.name,
            )
            intervene = False
        else:
            prompt_column_name = self.pipeline.get_input_column(GuardStage.PROMPT)
            response_column_name = self.pipeline.get_input_column(GuardStage.RESPONSE)
            metric_column_name = guard.get_metric_column_name(stage)

            try:
                copy_df[metric_column_name] = copy_df.apply(
                    lambda x: calculate_faithfulness(
                        evaluator=guard.faithfulness_evaluator,
                        llm_query=x[prompt_column_name],
                        llm_context=[x[col] for col in citation_columns],
                        llm_response=x[response_column_name],
                    ),
                    axis=1,
                )
            except Exception as e:
                title = "Faithfulness calculation failed"
                message = f"Exception: {e}"
                self._logger.error(title + " " + message)
                self._logger.error(traceback.format_exc())
                await self.pipeline.send_event_async(
                    title,
                    message,
                    ModerationEventTypes.MODERATION_MODEL_RUNTIME_ERROR,
                    guard_name=guard.name,
                )
                intervene = False

        return copy_df, intervene

    async def _handle_agent_goal_accuracy(self, guard, copy_df, stage):
        if not isinstance(guard, AgentGoalAccuracyGuard):
            raise ValueError(
                f"Guard object should be of type AgentGoalAccuracyGuard, got: {type(guard)}"
            )
        if stage == GuardStage.PROMPT:
            raise ValueError("Agent Goal Accuracy only supports evaluating the response")

        if AGENTIC_PIPELINE_INTERACTIONS_ATTR not in copy_df.columns:
            title = "Agent goal accuracy cannot be calculated without pipeline interactions"
            message = f"Input Column Names: {copy_df.columns}"
            self._logger.error(title + " " + message)
            await self.pipeline.send_event_async(
                title,
                message,
                ModerationEventTypes.MODERATION_MODEL_CONFIG_ERROR,
                guard_name=guard.name,
            )
        else:
            prompt_column_name = self.pipeline.get_input_column(GuardStage.PROMPT)
            response_column_name = self.pipeline.get_input_column(GuardStage.RESPONSE)
            metric_column_name = guard.get_metric_column_name(stage)

            try:
                copy_df[metric_column_name] = copy_df.apply(
                    lambda x: calculate_agent_goal_accuracy(
                        scorer=guard.accuracy_scorer,
                        prompt=x[prompt_column_name],
                        interactions=x[AGENTIC_PIPELINE_INTERACTIONS_ATTR],
                        response=x[response_column_name],
                    ),
                    axis=1,
                )
            except Exception as e:
                title = "Agent Goal accuracy calculation failed"
                message = f"Exception: {e}"
                self._logger.error(title + " " + message)
                self._logger.error(traceback.format_exc())
                await self.pipeline.send_event_async(
                    title,
                    message,
                    ModerationEventTypes.MODERATION_MODEL_RUNTIME_ERROR,
                    guard_name=guard.name,
                )

        return copy_df

    async def _handle_task_adherence(self, guard, copy_df, stage):
        if not isinstance(guard, TaskAdherenceGuard):
            raise ValueError(
                f"Guard object should be of type TaskAdherenceGuard, got: {type(guard)}"
            )
        if stage == GuardStage.PROMPT:
            raise ValueError("Task Adherence only supports evaluating the response")

        if AGENTIC_PIPELINE_INTERACTIONS_ATTR not in copy_df.columns:
            title = "Task adherence cannot be calculated without pipeline interactions"
            message = f"Input Column Names: {copy_df.columns}"
            self._logger.error(title + " " + message)
            await self.pipeline.send_event_async(
                title,
                message,
                ModerationEventTypes.MODERATION_MODEL_CONFIG_ERROR,
                guard_name=guard.name,
            )
        else:
            prompt_column_name = self.pipeline.get_input_column(GuardStage.PROMPT)
            response_column_name = self.pipeline.get_input_column(GuardStage.RESPONSE)
            metric_column_name = guard.get_metric_column_name(stage)

            try:
                copy_df[metric_column_name] = copy_df.apply(
                    lambda x: calculate_task_adherence(
                        scorer=guard.task_adherence_scorer,
                        prompt=x[prompt_column_name],
                        interactions=x[AGENTIC_PIPELINE_INTERACTIONS_ATTR],
                        response=x[response_column_name],
                    ),
                    axis=1,
                )
            except Exception as e:
                title = "Task Adherence calculation failed"
                message = f"Exception: {e}"
                self._logger.error(title + " " + message)
                self._logger.error(traceback.format_exc())
                await self.pipeline.send_event_async(
                    title,
                    message,
                    ModerationEventTypes.MODERATION_MODEL_RUNTIME_ERROR,
                    guard_name=guard.name,
                )

        return copy_df

    async def _handle_rouge_1(self, guard, copy_df, stage, intervene):
        if not isinstance(guard, OOTBGuard):
            raise ValueError(f"Guard object should be of type OOTBGuard, got: {type(guard)}")

        citation_columns = get_citation_columns(copy_df.columns)
        if len(citation_columns) == 0:
            # For now, let us simply log the error.  In future, we can add new error custom
            # metrics to track it
            title = "ROUGE-1 guard configured without citation columns"
            message = f"Input Column Names: {copy_df.columns}"
            await self.pipeline.send_event_async(
                title,
                message,
                ModerationEventTypes.MODERATION_MODEL_CONFIG_ERROR,
                guard_name=guard.name,
            )
            self._logger.error(title + " " + message)
            intervene = False
        else:
            input_column = self.pipeline.get_input_column(stage)
            metric_column_name = guard.get_metric_column_name(stage)
            copy_df[metric_column_name] = copy_df.apply(
                lambda x: get_rouge_1_score(
                    scorer=self.pipeline.rouge_scorer,
                    llm_context=[x[col] for col in citation_columns],
                    llm_response=[x[input_column]],
                ),
                axis=1,
            )
        return copy_df, intervene

    async def _handle_cost(self, guard, copy_df, stage):
        if not isinstance(guard, OOTBCostMetric):
            raise ValueError(f"Guard object should be of type OOTBCostMetric, got: {type(guard)}")

        prompt_column_name = self.pipeline.get_input_column(GuardStage.PROMPT)
        response_column_name = self.pipeline.get_input_column(GuardStage.RESPONSE)
        metric_column_name = guard.get_metric_column_name(stage)
        if (
            PROMPT_TOKEN_COUNT_COLUMN_NAME_FROM_USAGE not in copy_df.columns
            or RESPONSE_TOKEN_COUNT_COLUMN_NAME_FROM_USAGE not in copy_df.columns
        ):
            # In case cost is configured with the score interface, we can try our best
            # to get the token count numbers
            copy_df = calculate_token_counts_for_cost_calculations(
                prompt_column_name, response_column_name, copy_df
            )

        copy_df[metric_column_name] = copy_df.apply(
            lambda x: x[PROMPT_TOKEN_COUNT_COLUMN_NAME_FROM_USAGE] * guard.input_multiplier
            + x[RESPONSE_TOKEN_COUNT_COLUMN_NAME_FROM_USAGE] * guard.output_multiplier,
            axis=1,
        )
        return copy_df

    async def run_ootb_guard(self, guard, copy_df, stage):
        if not isinstance(guard, OOTBGuard):
            raise ValueError(f"Guard object should be of type OOTBGuard, got: {type(guard)}")
        input_column = self.pipeline.get_input_column(stage)
        metric_column_name = guard.get_metric_column_name(stage)
        intervene = self._should_intervene(guard)

        if guard.ootb_type == OOTBType.TOKEN_COUNT:
            copy_df[metric_column_name] = copy_df[input_column].apply(lambda x: get_token_count(x))
        elif guard.ootb_type == OOTBType.ROUGE_1:
            copy_df, intervene = await self._handle_rouge_1(guard, copy_df, stage, intervene)
        elif guard.ootb_type == OOTBType.FAITHFULNESS:
            copy_df, intervene = await self._handle_faithfulness(guard, copy_df, stage, intervene)
        elif guard.ootb_type == OOTBType.COST:
            copy_df = await self._handle_cost(guard, copy_df, stage)
            # No intervention for cost metric
            intervene = False
        elif guard.ootb_type == OOTBType.AGENT_GOAL_ACCURACY:
            copy_df = await self._handle_agent_goal_accuracy(guard, copy_df, stage)
            # No intervention for agent goal accuracy
            intervene = False
        elif guard.ootb_type == OOTBType.TASK_ADHERENCE:
            copy_df = await self._handle_task_adherence(guard, copy_df, stage)
            # No intervention for task adherence
            intervene = False
        elif guard.ootb_type == OOTBType.CUSTOM_METRIC:
            body = {
                "df": copy_df.to_dict(),
                "stage": stage,
                "metric_column_name": metric_column_name,
                "input_column": input_column,
            }
            response = requests.post(
                guard.faas_url,
                data=json.dumps(body),
                headers={"Content-Type": "application/json"},
            )
            if response.status_code == 200:
                copy_df = pd.DataFrame.from_dict(response.json()["df"])
            else:
                status_code = response.status_code
                err_message = response.json().get("err_message")
                self._logger.error(
                    "Custom metric guard calculation failed with"
                    f" status code {status_code}: {err_message}"
                )
                intervene = False

        if intervene:
            copy_df, _ = self._intervene(guard, copy_df, stage, metric_column_name)
        else:
            copy_df = self._dont_intervene(guard, copy_df, stage)
        return copy_df

    async def run_nemo_guard(self, guard, copy_df, stage):
        if not isinstance(guard, NeMoGuard):
            raise ValueError(f"Guard object should be of type NeMoGuard, got: {type(guard)}")

        input_column = self.pipeline.get_input_column(stage)
        metric_column_name = guard.get_metric_column_name(stage)
        intervene = self._should_intervene(guard)

        try:
            if stage == GuardStage.PROMPT:
                result_series = await asyncio.gather(
                    *(guard.nemo_llm_rails.generate_async(x) for x in copy_df[input_column])
                )
            else:
                nemo_assistant_output = await asyncio.gather(
                    *(
                        guard.nemo_llm_rails.generate_async(
                            messages=nemo_response_stage_input_formatter(x)
                        )
                        for x in copy_df[input_column]
                    )
                )
                result_series = [
                    nemo_response_stage_output_formatter(x) for x in nemo_assistant_output
                ]
            copy_df[metric_column_name] = result_series
        except Exception as e:
            title = "NeMo guard calculation failed"
            message = f"Exception: {e}"
            self._logger.error(title + " " + message)
            self._logger.error(traceback.format_exc())
            await self.pipeline.send_event_async(
                title,
                message,
                ModerationEventTypes.MODERATION_MODEL_RUNTIME_ERROR,
                guard_name=guard.name,
            )
            intervene = False

        if intervene:
            copy_df, _ = self._intervene(guard, copy_df, stage, metric_column_name)
        else:
            copy_df = self._dont_intervene(guard, copy_df, stage)
        return copy_df

    def run_guards(self, input_df, guards, stage):
        start_time = time.time()
        df = self.loop.run_until_complete(self.async_guard_executor(input_df, guards, stage))
        end_time = time.time()
        latency = end_time - start_time
        self.pipeline.report_stage_latency(latency, stage)
        self.pipeline.report_stage_total_inputs(stage, input_df.shape[0])
        return df, latency

    def _merge_moderation_columns(self, final_df, result_df, join_columns, guard, stage):
        final_df = final_df.merge(result_df, on=list(join_columns))
        # Ensure that the index of result matches final, because merge resets
        # index
        final_df.index = result_df.index
        input_column = self.pipeline.get_input_column(stage)
        (
            enforced_column_name,
            enforced_message_column_name,
            action_column_name,
        ) = self._get_enforced_and_action_column_names(
            guard.get_intervention_action(), input_column
        )
        # This is logical OR on 'enforced' column
        final_df[enforced_column_name] = (
            final_df[enforced_column_name + "_x"] + final_df[enforced_column_name + "_y"]
        )
        final_df[action_column_name] = final_df[
            [action_column_name + "_x", action_column_name + "_y"]
        ].apply(lambda x: ",".join(filter(None, x.dropna())), axis=1)
        if enforced_message_column_name:
            final_df[enforced_message_column_name] = final_df[
                [
                    enforced_message_column_name + "_x",
                    enforced_message_column_name + "_y",
                ]
            ].apply(lambda x: ",".join(filter(None, x.dropna())), axis=1)
        column_list_to_drop = [
            enforced_column_name + "_x",
            enforced_column_name + "_y",
            action_column_name + "_x",
            action_column_name + "_y",
        ]
        if enforced_message_column_name:
            column_list_to_drop.extend(
                [
                    enforced_message_column_name + "_x",
                    enforced_message_column_name + "_y",
                ]
            )
        final_df.drop(columns=column_list_to_drop, inplace=True)
        # We need to capture the information of which prompts were blocked specifically
        # by this guard.
        if guard.get_intervention_action() != GuardAction.NONE:
            final_df[self.pipeline.get_enforced_column_name(guard, stage)] = result_df[
                enforced_column_name
            ]
        return final_df

    def _get_input_df_for_the_guard(self, _input_df, join_columns, guard, stage):
        if stage == GuardStage.RESPONSE and isinstance(guard, OOTBGuard):
            if guard.ootb_type in [OOTBType.ROUGE_1, OOTBType.FAITHFULNESS] or guard.copy_citations:
                join_columns = join_columns.union(set(get_citation_columns(_input_df.columns)))
            if guard.ootb_type in [
                OOTBType.FAITHFULNESS,
                OOTBType.COST,
                OOTBType.AGENT_GOAL_ACCURACY,
                OOTBType.TASK_ADHERENCE,
            ]:
                join_columns.add(self.pipeline.get_input_column(GuardStage.PROMPT))
            if guard.ootb_type in [OOTBType.AGENT_GOAL_ACCURACY, OOTBType.TASK_ADHERENCE]:
                join_columns.add(AGENTIC_PIPELINE_INTERACTIONS_ATTR)
        copy_df = _input_df[list(join_columns)].copy(deep=True)
        return copy_df, join_columns

    async def async_guard_executor(self, input_df, guards, stage):
        tasks = list()

        _input_df = input_df.copy(deep=True)

        final_df = _input_df.copy(deep=True)
        input_column = self.pipeline.get_input_column(stage)
        for intervention_action in GuardAction.ALL:
            (
                enforced_column_name,
                enforced_message_column_name,
                action_column_name,
            ) = self._get_enforced_and_action_column_names(intervention_action, input_column)
            self._initialize_enforced_and_action_columns(
                final_df,
                enforced_column_name,
                enforced_message_column_name,
                action_column_name,
            )

        for guard in guards:
            join_columns = {input_column}
            association_id_column_name = self.pipeline.get_association_id_column_name()
            if association_id_column_name:
                if association_id_column_name not in _input_df.columns:
                    self._logger.warning(
                        f"Association ID Column {association_id_column_name} is missing in the "
                        "input dataframe, custom metrics won't be available"
                    )
                else:
                    join_columns.add(association_id_column_name)

            copy_df, join_columns = self._get_input_df_for_the_guard(
                _input_df, join_columns, guard, stage
            )
            task_name = f"{guard.name}_{guard.stage}"
            task = asyncio.create_task(self.run_guard(guard, copy_df, stage), name=task_name)
            task.context = {
                "join_columns": join_columns,
                "guard": guard,
                "df": copy_df,
                "stage": stage,
            }
            tasks.append(task)

        while len(tasks) > 0:
            done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            for task in done:
                guard = task.context["guard"]
                try:
                    await task
                except Exception as e:
                    # Task Cancellation is also handled here - CancelledError exception is raised
                    self._logger.error(f"Exception in the task {task}: {e}")
                    self._logger.error(traceback.format_exc())
                    result_df = self._dont_intervene(
                        guard, task.context["df"], task.context["stage"]
                    )
                    latency = 0
                else:
                    result_df, latency = task.result()
                final_df = self._merge_moderation_columns(
                    final_df, result_df, task.context["join_columns"], guard, stage
                )

                # If there are multiple prompts, we don't have way to detect guard latency for
                # each prompt (DataRobot `predict` does not return that).  So, we use the same
                # guard latency for each prompt.  However, our typical use case is one prompt /
                # response
                final_df[f"{guard.name}_latency"] = latency / final_df.shape[0]
            tasks = pending

        return final_df
