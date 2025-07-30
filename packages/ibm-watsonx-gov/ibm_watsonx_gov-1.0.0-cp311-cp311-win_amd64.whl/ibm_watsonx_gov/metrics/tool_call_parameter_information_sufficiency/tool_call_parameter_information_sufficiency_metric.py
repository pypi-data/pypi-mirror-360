# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

import asyncio
import json
import os
from typing import Annotated, Literal

import pandas as pd
from llmevalkit.function_calling.pipeline.pipeline import ReflectionPipeline
from llmevalkit.function_calling.pipeline.types import (FunctionCallMetric,
                                                        ToolCall, ToolSpec)
from pydantic import Field

from ibm_watsonx_gov.config import AgenticAIConfiguration, GenAIConfiguration
from ibm_watsonx_gov.entities.enums import MetricGroup, TaskType
from ibm_watsonx_gov.entities.evaluation_result import (AggregateMetricResult,
                                                        RecordMetricResult)
from ibm_watsonx_gov.entities.llm_judge import LLMJudge
from ibm_watsonx_gov.entities.metric import GenAIMetric
from ibm_watsonx_gov.entities.metric_threshold import MetricThreshold
from ibm_watsonx_gov.providers.tool_call_metric_provider import \
    ToolCallMetricProvider
from ibm_watsonx_gov.utils.python_utils import get

TOOL_CALLING_PARAMETER_INFORMATION_SUFFICIENCY = "tool_call_parameter_information_sufficiency"


class ToolCallParameterInformationSufficiencyMetric(GenAIMetric):
    """
    Implementation class for ToolCallParameterInformationSufficiencyMetric.
    Determine if the value is unambiguous or if more detail is needed.

    The following methods are supported:
    1. llm_as_judge
    """

    name: Annotated[Literal["tool_call_parameter_information_sufficiency"], Field(title="Metric Name",
                                                                                  description="The name of metric.",
                                                                                  default=TOOL_CALLING_PARAMETER_INFORMATION_SUFFICIENCY)]

    tasks: Annotated[list[TaskType], Field(title="Task Type",
                                           description="The generative task type.",
                                           default=[TaskType.RAG])]
    group: Annotated[MetricGroup, Field(
        default=MetricGroup.TOOL_CALL_QUALITY, frozen=True)]

    llm_judge: Annotated[LLMJudge | None, Field(
        description="The LLM judge used to compute the metric.", default=None)]

    method: Annotated[Literal["llm_as_judge"], Field(title="Computation Method",
                                                           description="The method used to compute the metric.",
                                                           default="llm_as_judge")]
    thresholds: Annotated[list[MetricThreshold], Field(title="Metric threshold",
                                                       description="Value that defines the violation limit for the metric",
                                                       default=[MetricThreshold(
                                                           type="upper_limit", value=0.7)]
                                                       )]
    metric_mapping_name: Annotated[Literal["parameter_info_sufficiency"], Field(title="Metric Mapping Name",
                                                                                description="The mapping name of metric with semantic evaluator.",
                                                                                default="parameter_info_sufficiency")]

    def evaluate(self, data: pd.DataFrame | dict,
                 configuration: GenAIConfiguration | AgenticAIConfiguration,
                 **kwargs) -> AggregateMetricResult:
        """
        Evaluate the data for ToolCallParameterInformationSufficiencyMetric
        Args:
            data (pd.DataFrame | dict): Data to be evaluated
            configuration (GenAIConfiguration | AgenticAIConfiguration): Metrics configuration

        Returns:
            AggregateMetricResult: The computed metrics
        """

        tool_call_provider = ToolCallMetricProvider()
        # Validate the configuration to compute the TCH
        tool_call_provider.validate_configuration(data, configuration)

        # Pre-process the data for the TCH Computation
        data = tool_call_provider.pre_process(data, configuration)

        # Compute the metrics
        metric_result = self._compute_metrics(
            data, configuration=configuration, provider=tool_call_provider)

        # Post process to make the aggregated and record level metrics results
        metric_result = tool_call_provider.post_process(
            metric_result, configuration, self)

        return metric_result

    def _compute_metrics(self, data: pd.DataFrame, configuration: GenAIConfiguration | AgenticAIConfiguration, provider: ToolCallMetricProvider):
        """
        Compute the ToolCallParameterInformationSufficiencyMetric metrics for the given data

        Args:
            data (pd.DataFrame): Input data including the tools used for the application
            configuration (GenAIConfiguration | AgenticAIConfiguration): Metrics configuration
            provider (ToolCallMetricProvider): Metric Provider object

        Raises:
            Exception: When the computation is failed

        Returns:
            list: List of metrics calculated for each records
        """

        try:
            question_field = configuration.input_fields[0]
            tool_calls_field = configuration.tool_calls_field
            record_id_field = configuration.record_id_field
            record_level_metrics = []
            tool_call_level_explanation = []

            if not self.llm_judge:
                return

            if not all(isinstance(t, ToolSpec) for t in configuration.tools):
                configuration.tools = [ToolSpec.model_validate(
                    func) for func in configuration.tools]

            for _, row in data.iterrows():
                tool_calls = provider.extract_tool_calls_from_response(
                    row[tool_calls_field])

                if not tool_calls:
                    record_level_metrics.append({
                        "value": 0.0,  # Treat no tool calls as 0 score
                        "record_id": row[record_id_field],
                        "explanations": "LLM did not make any tool calls"
                    })
                    continue

                prompt_json = provider.get_semantic_metric_json(
                    self.metric_mapping_name)

                for call in tool_calls:
                    pipeline = ReflectionPipeline(
                        metrics_client=provider.get_llm_metric_client(
                            self.llm_judge),
                        general_metrics=None,
                        function_metrics=None,
                        parameter_metrics=[FunctionCallMetric(**prompt_json)],
                        transform_enabled=False
                    )
                    result = asyncio.run(pipeline.semantic_async(
                        conversation=row[question_field],
                        inventory=configuration.tools,
                        call=ToolCall.model_validate(call),
                        retries=2
                    ))
                    explanations = provider.extract_parameter_info(
                        result.model_dump(), self.metric_mapping_name)

                    if explanations:
                        tool_call_level_explanation.append({
                            "tool_name": get(call, "function.name"),
                            "is_issue": get(explanations, "is_issue"),
                            "response": get(explanations, "raw_response")
                        })
                record_level_metrics.append({
                    "value": 1.0 if any(
                        entry.get("is_issue") is True
                        for entry in tool_call_level_explanation
                    ) else 0.0,
                    "record_id": row[record_id_field],
                    "explanations": tool_call_level_explanation
                })
            return record_level_metrics
        except Exception as ex:
            raise Exception(
                f"Error while computing metrics: '{self.name}' using '{self.method}'. Reason: {str(ex)}")
