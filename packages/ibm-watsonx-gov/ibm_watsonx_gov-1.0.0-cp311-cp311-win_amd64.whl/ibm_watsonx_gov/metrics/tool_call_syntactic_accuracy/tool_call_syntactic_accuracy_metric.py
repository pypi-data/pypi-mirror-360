# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

from typing import Annotated, Literal

import pandas as pd
from ibm_watsonx_gov.config import AgenticAIConfiguration, GenAIConfiguration
from ibm_watsonx_gov.entities.enums import MetricGroup, TaskType
from ibm_watsonx_gov.entities.evaluation_result import AggregateMetricResult
from ibm_watsonx_gov.entities.metric import GenAIMetric
from ibm_watsonx_gov.entities.metric_threshold import MetricThreshold
from ibm_watsonx_gov.providers.tool_call_metric_provider import \
    ToolCallMetricProvider
from ibm_watsonx_gov.utils.validation_util import validate_tool_calls
from llmevalkit.function_calling.pipeline.pipeline import ReflectionPipeline
from llmevalkit.function_calling.pipeline.types import ToolCall, ToolSpec
from pydantic import Field

TOOL_CALLING_SYNTACTIC_ACCURACY = "tool_call_syntactic_accuracy"


class ToolCallSyntacticAccuracyMetric(GenAIMetric):
    """
    ToolCallSyntacticAccuracyMetric compute the tool call syntactic correctness 
    by validating tool call against the schema of the list of available tools.

    The ToolCallSyntacticAccuracy metric will be computed by performing the syntactic checks.

    Examples:
        1. Create ToolCallSyntacticAccuracy metric by passing the basic configuration.
            .. code-block:: python

                config = GenAIConfiguration(tools = [get_weather,fetch_stock_price])
                evaluator = MetricsEvaluator(configuration=config)
                df = pd.read_csv("")
                metrics = [ToolCallSyntacticAccuracyMetric()]
                result = evaluator.evaluate(data=df, metrics=metrics)

        2. Create ToolCallSyntacticAccuracy metric by passing custom tool calls field in configuration.
            .. code-block:: python

                config = GenAIConfiguration(tools = [get_weather,fetch_stock_price],
                                            tool_calls_field="tools_used")
                evaluator = MetricsEvaluator(configuration=config)
                df = pd.read_csv("")
                metrics = [ToolCallSyntacticAccuracyMetric()]
                result = evaluator.evaluate(data=df, metrics=metrics)

        3. Create ToolCallSyntacticAccuracy metric with a custom threshold.
            .. code-block:: python

                threshold  = MetricThreshold(type="upper_limit", value=0.8)
                metric = ToolCallSyntacticAccuracyMetric(threshold=threshold)
    """

    name: Annotated[Literal["tool_call_syntactic_accuracy"], Field(title="Metric Name",
                                                                   description="The name of metric.",
                                                                   default=TOOL_CALLING_SYNTACTIC_ACCURACY)]

    tasks: Annotated[list[TaskType], Field(title="Task Type",
                                           description="The generative task type.",
                                           default=[TaskType.RAG])]
    group: Annotated[MetricGroup, Field(title="Group",
                                        description="The metric group.",
                                        default=MetricGroup.TOOL_CALL_QUALITY, frozen=True)]
    method: Annotated[Literal["syntactic_check"], Field(title="Computation Method",
                                                        description="The method used to compute the metric.",
                                                        default="syntactic_check")]
    thresholds: Annotated[list[MetricThreshold], Field(title="Metric threshold",
                                                       description="Value that defines the violation limit for the metric",
                                                       default=[MetricThreshold(
                                                           type="upper_limit", value=0.7)]
                                                       )]

    def evaluate(self, data: pd.DataFrame | dict,
                 configuration: GenAIConfiguration | AgenticAIConfiguration,
                 **kwargs) -> AggregateMetricResult:
        """
        Evaluate the data for ToolCallSyntacticAccuracyMetric
        Args:
            data (pd.DataFrame | dict): Data to be evaluated
            configuration (GenAIConfiguration | AgenticAIConfiguration): Metrics configuration

        Returns:
            AggregateMetricResult: The computed metrics
        """
        # Validate tool calls field in data and tools in configuration
        data_cols = data.columns.to_list()
        validate_tool_calls(data_cols, configuration)

        tool_call_provider = ToolCallMetricProvider()
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
        Compute the ToolCallSyntacticAccuracyMetric metrics for the given data

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
            tool_calls_field = configuration.tool_calls_field
            record_id_field = configuration.record_id_field
            record_level_metrics = []
            tool_call_level_explanation = []

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
                        "explanations": "Agent did not make any tool calls"
                    })
                    continue

                for call in tool_calls:
                    explanations = ReflectionPipeline.static_only(
                        inventory=configuration.tools, call=ToolCall.model_validate(call))
                    explanations = explanations.model_dump()
                    if explanations.get("final_decision") is False:
                        tool_call_level_explanation.append({
                            "tool_name": call.get("function").get("name"),
                            "hallucinations": {
                                key: val for key, val in explanations["metrics"].items() if not val["valid"]
                            }
                        })
                record_level_metrics.append({
                    "value": 1.0 if tool_call_level_explanation else 0.0,
                    "record_id": row[record_id_field],
                    "explanations": tool_call_level_explanation
                })
            return record_level_metrics
        except Exception as ex:
            raise Exception(
                f"Error while computing metrics: '{self.name}' using '{self.method}'. Reason: {str(ex)}")
