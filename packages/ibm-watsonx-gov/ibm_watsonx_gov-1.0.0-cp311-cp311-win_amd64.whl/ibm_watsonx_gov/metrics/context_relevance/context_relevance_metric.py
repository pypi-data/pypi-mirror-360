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
from pydantic import Field, model_validator
from typing_extensions import Self

from ibm_watsonx_gov.config.agentic_ai_configuration import \
    AgenticAIConfiguration
from ibm_watsonx_gov.config.gen_ai_configuration import GenAIConfiguration
from ibm_watsonx_gov.entities.enums import (EvaluationProvider, MetricGroup,
                                            TaskType)
from ibm_watsonx_gov.entities.evaluation_result import (AggregateMetricResult,
                                                        RecordMetricResult)
from ibm_watsonx_gov.entities.llm_judge import LLMJudge
from ibm_watsonx_gov.entities.metric import GenAIMetric
from ibm_watsonx_gov.entities.metric_threshold import MetricThreshold
from ibm_watsonx_gov.providers.unitxt_provider import UnitxtProvider
from ibm_watsonx_gov.utils.python_utils import transform_str_to_list
from ibm_watsonx_gov.utils.validation_util import (validate_context,
                                                   validate_input,
                                                   validate_llm_as_judge,
                                                   validate_unitxt_method)

CONTEXT_RELEVANCE = "context_relevance"


class ContextRelevanceResult(RecordMetricResult):
    name: str = CONTEXT_RELEVANCE
    group: MetricGroup = MetricGroup.RETRIEVAL_QUALITY
    additional_info: dict[Literal["contexts_values"],
                          list[float]] = {"context_values": []}


unitxt_methods = [
    "sentence_bert_bge",
    "sentence_bert_mini_lm",
    "llm_as_judge",
]


class ContextRelevanceMetric(GenAIMetric):
    """
    Defines the Context Relevance metric class.

    The Context Relevance metric measures the relevance of the contexts to the given input query.
    It can be computed using the below methods:
        1. sentence_bert_bge
        2. sentence_bert_mini_lm (default)
        3. llm_as_judge

    Examples:
        1. Create Context Relevance metric with default parameters and compute using metrics evaluator.
            .. code-block:: python

                metric = ContextRelevanceMetric()
                result = MetricsEvaluator().evaluate(data={"input_text": "...", "context": "..."}, 
                                                    metrics=[metric])
                * A list of contexts can also be passed as shown below
                result = MetricsEvaluator().evaluate(data={"input_text": "...", "context": ["...", "..."]}, 
                                                    metrics=[metric])

        2. Create Context Relevance metric with a custom threshold and method.
            .. code-block:: python

                threshold  = MetricThreshold(type="lower_limit", value=0.5)
                method = "sentence_bert_bge"
                metric = ContextRelevanceMetric(method=method, threshold=threshold)

        3. Create Context Relevance metric with llm_as_judge method.
            .. code-block:: python

                * Define LLM Judge using watsonx.ai
                * To use other frameworks and models as llm_judge, see :module:`ibm_watsonx_gov.entities.foundation_model`
                llm_judge = LLMJudge(model=WxAIFoundationModel(
                                            model_id="google/flan-ul2",
                                            project_id="<PROJECT_ID>"
                                    ))
                metric = ContextRelevanceMetric(llm_judge=llm_judge)
    """
    name: Annotated[Literal["context_relevance"],
                    Field(title="Name",
                          description="The context relevance metric name.",
                          default=CONTEXT_RELEVANCE, frozen=True)]
    tasks: Annotated[list[TaskType],
                     Field(title="Tasks",
                           description="The list of supported tasks.",
                           default=[TaskType.RAG])]
    thresholds: Annotated[list[MetricThreshold],
                          Field(title="Thresholds",
                                description="The metric thresholds.",
                                default=[MetricThreshold(type="lower_limit", value=0.7)])]
    method: Annotated[Literal["sentence_bert_bge", "sentence_bert_mini_lm", "llm_as_judge"],
                      Field(title="Method",
                            description="The method used to compute the metric. This field is optional and when `llm_judge` is provided, the method would be set to `llm_as_judge`.",
                            default="sentence_bert_mini_lm")]
    group: Annotated[MetricGroup,
                     Field(title="Group",
                           description="The metric group.",
                           default=MetricGroup.RETRIEVAL_QUALITY, frozen=True)]
    llm_judge: Annotated[LLMJudge | None,
                         Field(title="LLM Judge",
                               description="The LLM judge used to compute the metric.",
                               default=None)]

    @model_validator(mode="after")
    def set_llm_judge_default_method(self) -> Self:
        # If llm_judge is set, set the method to llm_as_judge
        if self.llm_judge:
            self.method = "llm_as_judge"
        return self

    def evaluate(self, data: pd.DataFrame | dict, configuration: GenAIConfiguration | AgenticAIConfiguration, **kwargs) -> AggregateMetricResult:

        data_cols = data.columns.to_list()
        validate_input(data_cols, configuration)
        validate_context(data_cols, configuration)
        validate_unitxt_method(self.name, self.method, unitxt_methods)
        validate_llm_as_judge(self.name, self.method,
                              self.llm_judge, configuration.llm_judge)

        context_fields = configuration.context_fields

        # Check if we need to expand the contexts column:
        if len(configuration.context_fields) == 1:
            context = context_fields[0]
            data[context] = data[context].apply(transform_str_to_list)
            contexts_count = len(data[context].iloc[0])
            context_fields = [f"context_{i}" for i in range(contexts_count)]
            data[context_fields] = pd.DataFrame(
                data[context].to_list(), index=data.index)

        contexts_result: list[AggregateMetricResult] = []
        for context in context_fields:
            context_config = configuration.model_copy()
            context_config.context_fields = [context]
            context_provider = UnitxtProvider(
                configuration=context_config,
                metric_name=self.name,
                metric_method=self.method,
                metric_group=self.group,
                metric_prefix="metrics.rag.external_rag",
                llm_judge=self.llm_judge,
                thresholds=self.thresholds,
                **kwargs
            )
            res = context_provider.evaluate(data=data)
            contexts_result.append(res)

        final_res: list[ContextRelevanceResult] = []
        for record_metric in zip(*[context_result.record_level_metrics for context_result in contexts_result]):
            values = [context_value.value for context_value in record_metric]
            record_result = ContextRelevanceResult(
                method=self.method,
                provider=EvaluationProvider.UNITXT.value,
                value=max(values),
                record_id=record_metric[0].record_id,
                additional_info={"contexts_values": values},
                thresholds=self.thresholds
            )
            final_res.append(record_result)

        # Create the aggregate result
        values = [record.value for record in final_res]
        mean = sum(values) / len(values)
        aggregate_result = AggregateMetricResult(
            name=self.name,
            method=self.method,
            provider=EvaluationProvider.UNITXT.value,
            group=MetricGroup.RETRIEVAL_QUALITY,
            value=mean,
            total_records=len(final_res),
            record_level_metrics=final_res,
            min=min(values),
            max=max(values),
            mean=mean,
            thresholds=self.thresholds
        )

        return aggregate_result
