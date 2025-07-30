# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

from functools import partial
from time import time
from typing import Annotated, Any, Callable, Optional, Set

import pandas as pd
from deprecated.sphinx import deprecated
from ibm_watsonx_gov.clients.api_client import APIClient
from ibm_watsonx_gov.config import AgenticAIConfiguration
from ibm_watsonx_gov.entities.credentials import Credentials
from ibm_watsonx_gov.entities.enums import EvaluatorFields, MetricGroup
from ibm_watsonx_gov.entities.evaluation_result import ToolMetricResult
from ibm_watsonx_gov.entities.metric import GenAIMetric
from ibm_watsonx_gov.evaluate.impl.evaluate_metrics_impl import (
    _evaluate_metrics, _resolve_metric_dependencies)
from ibm_watsonx_gov.metrics import (
    AnswerRelevanceMetric, AnswerSimilarityMetric, AveragePrecisionMetric,
    ContextRelevanceMetric, FaithfulnessMetric, HitRateMetric, NDCGMetric,
    ReciprocalRankMetric, RetrievalPrecisionMetric, ToolCallAccuracyMetric,
    ToolCallIntentAccuracyMetric, ToolCallOrderAccuracyMetric,
    ToolCallParameterAccuracyMetric, ToolCallParameterAlignmentMetric,
    ToolCallParameterConsistencyMetric, ToolCallParameterGroundednessMetric,
    ToolCallParameterHallucinationMetric,
    ToolCallParameterInformationSufficiencyMetric,
    ToolCallSyntacticAccuracyMetric, ToolSelectionAccuracyMetric,
    UnsuccessfulRequestsMetric)
from ibm_watsonx_gov.utils.python_utils import (add_if_unique,
                                                get_argument_value)
from ibm_watsonx_gov.visualizations import ModelInsights
from pydantic import BaseModel, Field, PrivateAttr
from wrapt import decorator


@deprecated(version="1.0.0")
class AgenticEvaluation(BaseModel):

    credentials: Annotated[Optional[Credentials], Field(
        name="watsonx.governance Credentials", default=None)]
    experiment_id: Annotated[Optional[str], Field(name="Experiment ID",
                                                  description="An id for the experiment.",
                                                  default="1", examples=[
                                                      "experiment_1", "experiment_2"])]
    configuration: Annotated[Optional[AgenticAIConfiguration],
                             Field(name="Configuration object", default=None)]
    __metrics: Annotated[list[GenAIMetric],
                         PrivateAttr(default=[])]
    __metric_results: Annotated[list[ToolMetricResult],
                                PrivateAttr(default=[])]
    """__metric_results holds the results of all the evaluations done for a particular evaluation instance."""
    __execution_counts: Annotated[dict[str, dict[str, int]],
                                  PrivateAttr(default={})]
    """__execution_counts holds the execution count for a particular tool, for a given record_id."""
    __tools_being_run: Annotated[dict[str, Set[str]],
                                 PrivateAttr(default={})]
    """__tools_being_run holds the name of the current tools being run for a given record_id. Multiple decorators can be applied on a single tool using chaining. We don't want to hold multiple copies of same tool here."""

    def __validate(self, *, func: Callable, metrics: list[GenAIMetric], valid_metric_types: tuple[Any]):
        if not metrics:
            raise ValueError(
                "The 'metrics' argument can not be empty.")

        invalid_metrics = [metric.name for metric in metrics if not isinstance(
            metric, valid_metric_types)]
        if len(invalid_metrics):
            raise ValueError(
                f"The evaluator '{func.__name__}' is not applicable for "
                f"computing the metrics: {', '.join(invalid_metrics)}")

    def __compute_helper(self, *, func: Callable,
                         args: tuple,
                         kwargs: dict[str, Any],
                         configuration: AgenticAIConfiguration,
                         metrics: list[GenAIMetric],
                         metric_inputs: list[EvaluatorFields],
                         metric_outputs: list[EvaluatorFields],
                         metric_references: list[EvaluatorFields] = [],
                         metric_groups: list[MetricGroup] = []) -> dict:
        """
        Helper method for computing metrics.

        Does the following:
            1. Computes tool latency metric, and appends the result to the :py:attr:`AgenticEvaluation.metric_results` attribute.
            2. Calls the original tool. 
            3. Computes the list of metrics given, and appends the result to the :py:attr:`AgenticEvaluation.metric_results` attribute.
            4. Returns the result of the original tool without any changes.

        Args:
            func (Callable): The tool on which the metric is to be computed
            args (tuple): The tuple of positional arguments passed to the tool
            kwargs (dict[str, Any]): The dictionary of keyword arguments passed to the tool
            configuration (AgenticAIConfiguration): The tool specific configuration
            metrics (list[GenAIMetric]): The list of metrics to compute.
            metric_inputs (list[EvaluatorFields]): The list of inputs for the metric.
            metric_outputs (list[EvaluatorFields]): The list of outputs for the metric.
            metric_references (list[EvaluatorFields], optional): The optional list of references for the metric. Defaults to [].

        Raises:
            ValueError: If the record id field is missing from the tool inputs.

        Returns:
            dict: The result of the wrapped tool.
        """

        get_arg_value = partial(
            get_argument_value, func=func, args=args, kwargs=kwargs)

        defaults = metric_inputs + metric_outputs + metric_references
        _configuration = AgenticAIConfiguration.create_configuration(app_config=self.configuration,
                                                                     method_config=configuration,
                                                                     defaults=defaults)
        _data = {}
        for field in metric_inputs + metric_references:
            _field = getattr(_configuration, field.value)
            if not (isinstance(_field, list)):
                _field = [_field]
            _data.update(dict(map(lambda f: (
                f, get_arg_value(param_name=f)), _field)))

        # Add record id to the data
        _field = getattr(_configuration, EvaluatorFields.RECORD_ID_FIELD.value,
                         EvaluatorFields.get_default_fields_mapping()[EvaluatorFields.RECORD_ID_FIELD])
        _record_id_value = get_arg_value(param_name=_field)
        if _record_id_value is None:
            raise ValueError(
                f"The {_field} is required for evaluation. Please add it while invoking the application.")
        _data[_field] = _record_id_value

        if _record_id_value not in self.__tools_being_run:
            self.__tools_being_run[_record_id_value] = set()
        if _record_id_value not in self.__execution_counts:
            self.__execution_counts[_record_id_value] = dict()

        if func.__name__ not in self.__tools_being_run[_record_id_value]:
            self.__tools_being_run[_record_id_value].add(func.__name__)
            self.__execution_counts[_record_id_value][func.__name__] = self.__execution_counts[_record_id_value].get(
                func.__name__, 0) + 1

        start_time = time()
        original_result = func(*args, **kwargs)
        latency = time() - start_time

        tool_mr = {
            "tool_name": func.__name__,
            "execution_count": self.__execution_counts[_record_id_value].get(func.__name__),
            "name": "tool_latency (s)",
            "method": "",
            "provider": "",
            "record_id": _record_id_value,
            "value": latency
        }

        add_if_unique(ToolMetricResult(**tool_mr), self.__metric_results,
                      ["tool_name", "execution_count", "name", "record_id"])

        if func.__name__ in self.__tools_being_run[_record_id_value]:
            self.__tools_being_run[_record_id_value].remove(func.__name__)

        for field in metric_outputs:
            _field = getattr(_configuration, field.value)
            if not (isinstance(_field, list)):
                _field = [_field]
            _data.update(dict(map(lambda f: (
                f, original_result.get(f)), _field)))

        if self.credentials:
            api_client = APIClient(self.credentials)
        else:
            api_client = None
        final_metrics = _resolve_metric_dependencies(
            metrics=metrics, metric_groups=metric_groups)
        metric_result = _evaluate_metrics(configuration=_configuration, data=_data,
                                          metrics=final_metrics,
                                          api_client=api_client).to_dict()
        self.__metrics.extend(final_metrics)

        for mr in metric_result:
            tool_result = {
                "tool_name": func.__name__,
                "execution_count": self.__execution_counts[_record_id_value].get(func.__name__),
                **mr
            }
            tmr = ToolMetricResult(**tool_result)
            self.__metric_results.append(tmr)

        return original_result

    def evaluate_context_relevance(self,
                                   func: Optional[Callable] = None,
                                   *,
                                   configuration: Optional[AgenticAIConfiguration] = None,
                                   metrics: list[GenAIMetric] = [
                                       ContextRelevanceMetric()
                                   ]
                                   ) -> dict:
        """
        An evaluation decorator for computing context relevance metric on an agentic tool.

        For more details, see :class:`ibm_watsonx_gov.metrics.ContextRelevanceMetric`

        Args:
            func (Optional[Callable], optional): The tool on which the metric is to be computed.
            configuration (Optional[AgenticAIConfiguration], optional): The configuration specific to this evaluator. Defaults to None.
            metrics (list[GenAIMetric], optional): The list of metrics to compute as part of this evaluator. Defaults to [ ContextRelevanceMetric() ].

        Raises:
            Exception: If there is any error while evaluation.

        Returns:
            dict: The result of the wrapped tool.

        Example:
            1. Basic usage
                .. code-block:: python

                    evaluator = AgenticEvaluation()
                    @evaluator.evaluate_context_relevance
                    def agentic_tool(*args, *kwargs):
                        pass

            2. Usage with different thresholds and methods
                .. code-block:: python

                    metric_1 = ContextRelevanceMetric(method="sentence_bert_bge", threshold=MetricThreshold(type="lower_limit", value=0.5))
                    metric_2 = ContextRelevanceMetric(method="sentence_bert_mini_lm", threshold=MetricThreshold(type="lower_limit", value=0.6))

                    evaluator = AgenticEvaluation()
                    @evaluator.evaluate_context_relevance(metrics=[metric_1, metric_2])
                    def agentic_tool(*args, *kwargs):
                        pass
        """
        if func is None:
            return partial(self.evaluate_context_relevance, configuration=configuration, metrics=metrics)

        @decorator
        def wrapper(func, instance, args, kwargs):

            try:
                self.__validate(func=func, metrics=metrics,
                                valid_metric_types=(ContextRelevanceMetric,))

                metric_inputs = [EvaluatorFields.INPUT_FIELDS]
                metric_outputs = [EvaluatorFields.CONTEXT_FIELDS]

                original_result = self.__compute_helper(func=func, args=args, kwargs=kwargs,
                                                        configuration=configuration,
                                                        metrics=metrics,
                                                        metric_inputs=metric_inputs,
                                                        metric_outputs=metric_outputs)

                return original_result
            except Exception as ex:
                raise Exception(
                    f"There was an error while evaluating context relevance metric on {func.__name__},") from ex

        return wrapper(func)

    def evaluate_answer_similarity(self,
                                   func: Optional[Callable] = None,
                                   *,
                                   configuration: Optional[AgenticAIConfiguration] = None,
                                   metrics: list[GenAIMetric] = [
                                       AnswerSimilarityMetric()
                                   ]
                                   ) -> dict:
        """
        An evaluation decorator for computing answer similarity metric on an agentic tool.

        For more details, see :class:`ibm_watsonx_gov.metrics.AnswerSimilarityMetric`

        Args:
            func (Optional[Callable], optional): The tool on which the metric is to be computed.
            configuration (Optional[AgenticAIConfiguration], optional): The configuration specific to this evaluator. Defaults to None.
            metrics (list[GenAIMetric], optional): The list of metrics to compute as part of this evaluator. Defaults to [ AnswerSimilarityMetric() ].

        Raises:
            Exception: If there is any error while evaluation.

        Returns:
            dict: The result of the wrapped tool.

        Example:
            1. Basic usage
                .. code-block:: python

                    evaluator = AgenticEvaluation()
                    @evaluator.evaluate_answer_similarity
                    def agentic_tool(*args, *kwargs):
                        pass


            2. Usage with different thresholds and methods
                .. code-block:: python

                    metric_1 = AnswerSimilarityMetric(method="token_k_precision", threshold=MetricThreshold(type="lower_limit", value=0.5))
                    metric_2 = AnswerSimilarityMetric(method="sentence_bert_mini_lm", threshold=MetricThreshold(type="lower_limit", value=0.6))

                    evaluator = AgenticEvaluation()
                    @evaluator.evaluate_answer_similarity(metrics=[metric_1, metric_2])
                    def agentic_tool(*args, *kwargs):
                        pass

        """

        if func is None:
            return partial(self.evaluate_answer_similarity, configuration=configuration, metrics=metrics)

        @decorator
        def wrapper(func, instance, args, kwargs):

            try:
                self.__validate(func=func, metrics=metrics,
                                valid_metric_types=(AnswerSimilarityMetric,))

                metric_inputs = [
                    EvaluatorFields.INPUT_FIELDS,
                    EvaluatorFields.CONTEXT_FIELDS
                ]
                metric_references = [EvaluatorFields.REFERENCE_FIELDS]
                metric_outputs = [EvaluatorFields.OUTPUT_FIELDS]

                original_result = self.__compute_helper(func=func, args=args, kwargs=kwargs,
                                                        configuration=configuration,
                                                        metrics=metrics,
                                                        metric_inputs=metric_inputs,
                                                        metric_outputs=metric_outputs,
                                                        metric_references=metric_references)

                return original_result
            except Exception as ex:
                raise Exception(
                    f"There was an error while evaluating answer similarity metric on {func.__name__},") from ex

        return wrapper(func)

    def evaluate_faithfulness(self,
                              func: Optional[Callable] = None,
                              *,
                              configuration: Optional[AgenticAIConfiguration] = None,
                              metrics: list[GenAIMetric] = [
                                  FaithfulnessMetric()
                              ]
                              ) -> dict:
        """
        An evaluation decorator for computing faithfulness metric on an agentic tool.

        For more details, see :class:`ibm_watsonx_gov.metrics.FaithfulnessMetric`

        Args:
            func (Optional[Callable], optional): The tool on which the metric is to be computed.
            configuration (Optional[AgenticAIConfiguration], optional): The configuration specific to this evaluator. Defaults to None.
            metrics (list[GenAIMetric], optional): The list of metrics to compute as part of this evaluator. Defaults to [ FaithfulnessMetric() ].

        Raises:
            Exception: If there is any error while evaluation.

        Returns:
            dict: The result of the wrapped tool.

        Example:
            1. Basic usage
                .. code-block:: python

                    evaluator = AgenticEvaluation()
                    @evaluator.evaluate_faithfulness
                    def agentic_tool(*args, *kwargs):
                        pass

            2. Usage with different thresholds and methods
                .. code-block:: python

                    metric_1 = FaithfulnessMetric(method="token_k_precision", threshold=MetricThreshold(type="lower_limit", value=0.5))
                    metric_2 = FaithfulnessMetric(method="sentence_bert_mini_lm", threshold=MetricThreshold(type="lower_limit", value=0.6))

                    evaluator = AgenticEvaluation()
                    @evaluator.evaluate_faithfulness(metrics=[metric_1, metric_2])
                    def agentic_tool(*args, *kwargs):
                        pass
        """

        if func is None:
            return partial(self.evaluate_faithfulness, configuration=configuration, metrics=metrics)

        @decorator
        def wrapper(func, instance, args, kwargs):

            try:
                self.__validate(func=func, metrics=metrics,
                                valid_metric_types=(FaithfulnessMetric,))

                metric_inputs = [
                    EvaluatorFields.INPUT_FIELDS,
                    EvaluatorFields.CONTEXT_FIELDS
                ]
                metric_outputs = [EvaluatorFields.OUTPUT_FIELDS]

                original_result = self.__compute_helper(func=func, args=args, kwargs=kwargs,
                                                        configuration=configuration,
                                                        metrics=metrics,
                                                        metric_inputs=metric_inputs,
                                                        metric_outputs=metric_outputs)

                return original_result
            except Exception as ex:
                raise Exception(
                    f"There was an error while evaluating faithfulness metric on {func.__name__},") from ex

        return wrapper(func)

    def evaluate_tool_call_syntactic_accuracy(self,
                                              func: Optional[Callable] = None,
                                              *,
                                              configuration: Optional[AgenticAIConfiguration] = None,
                                              metrics: list[GenAIMetric] = [
                                                  ToolCallSyntacticAccuracyMetric()
                                              ]
                                              ) -> dict:
        """
        An evaluation decorator for computing tool_call_syntactic_accuracy metric on an agentic tool.

        For more details, see :class:`ibm_watsonx_gov.metrics.ToolCallSyntacticAccuracyMetric`

        Args:
            func (Optional[Callable], optional): The tool on which the metric is to be computed.
            configuration (Optional[AgenticAIConfiguration], optional): The configuration specific to this evaluator. Defaults to None.
            metrics (list[GenAIMetric], optional): The list of metrics to compute as part of this evaluator. Defaults to [ ToolCallSyntacticAccuracyMetric() ].

        Raises:
            Exception: If there is any error while evaluation.

        Returns:
            dict: The result of the wrapped tool.

        Example:
            1. Basic usage
                .. code-block:: python

                    evaluator = AgenticEvaluation()
                    @evaluator.evaluate_tool_call_syntactic_accuracy
                    def agentic_tool(*args, *kwargs):
                        pass

            2. Usage with different thresholds
                .. code-block:: python

                    metric_1 = ToolCallSyntacticAccuracyMetric(threshold=MetricThreshold(type="upper_limit", value=0.7))
                    evaluator = AgenticEvaluation()
                    @evaluator.evaluate_tool_call_syntactic_accuracy(metrics=[metric_1])
                    def agentic_tool(*args, *kwargs):
                        pass
        """

        if func is None:
            return partial(self.evaluate_tool_call_syntactic_accuracy, configuration=configuration, metrics=metrics)

        @decorator
        def wrapper(func, instance, args, kwargs):

            try:
                self.__validate(func=func, metrics=metrics,
                                valid_metric_types=(ToolCallSyntacticAccuracyMetric,))

                metric_outputs = [
                    EvaluatorFields.TOOL_CALLS_FIELD, EvaluatorFields.OUTPUT_FIELDS]

                original_result = self.__compute_helper(func=func, args=args, kwargs=kwargs,
                                                        configuration=configuration,
                                                        metrics=metrics,
                                                        metric_inputs=[],
                                                        metric_outputs=metric_outputs)

                return original_result
            except Exception as ex:
                raise Exception(
                    f"There was an error while evaluating tool_call_syntactic_accuracy metric on {func.__name__},") from ex

        return wrapper(func)

    def evaluate_tool_call_intent_accuracy(self,
                                           func: Optional[Callable] = None,
                                           *,
                                           configuration: Optional[AgenticAIConfiguration] = None,
                                           metrics: list[GenAIMetric] = [
                                               ToolCallIntentAccuracyMetric()
                                           ]
                                           ) -> dict:
        """
        An evaluation decorator for computing tool_call_intent_accuracy metric on an agentic tool.

        For more details, see :class:`ibm_watsonx_gov.metrics.ToolCallIntentAccuracyMetric`

        Args:
            func (Optional[Callable], optional): The tool on which the metric is to be computed.
            configuration (Optional[AgenticAIConfiguration], optional): The configuration specific to this evaluator. Defaults to None.
            metrics (list[GenAIMetric], optional): The list of metrics to compute as part of this evaluator. Defaults to [ ToolCallIntentAccuracyMetric() ].

        Raises:
            Exception: If there is any error while evaluation.

        Returns:
            dict: The result of the wrapped tool.

        Example:
            1. Usage with llm_judge
                .. code-block:: python

                    llm_judge = LLMJudge(
                        model=WxAIFoundationModel(
                            model_id="meta-llama/llama-3-3-70b-instruct",
                            project_id=os.getenv("WATSONX_PROJECT_ID"),
                        )
                    )
                    metric_1 = ToolCallIntentAccuracyMetric(llm_judge=llm_judge)
                    evaluator = AgenticEvaluation()
                    @evaluator.evaluate_tool_call_intent_accuracy(metrics=[metric_1])
                    def agentic_tool(*args, *kwargs):
                        pass
        """

        if func is None:
            return partial(self.evaluate_tool_call_intent_accuracy, configuration=configuration, metrics=metrics)

        @decorator
        def wrapper(func, instance, args, kwargs):

            try:
                self.__validate(func=func, metrics=metrics,
                                valid_metric_types=(ToolCallIntentAccuracyMetric,))

                metric_inputs = [
                    EvaluatorFields.INPUT_FIELDS
                ]

                metric_outputs = [
                    EvaluatorFields.TOOL_CALLS_FIELD, EvaluatorFields.OUTPUT_FIELDS]

                original_result = self.__compute_helper(func=func, args=args, kwargs=kwargs,
                                                        configuration=configuration,
                                                        metrics=metrics,
                                                        metric_inputs=metric_inputs,
                                                        metric_outputs=metric_outputs)

                return original_result
            except Exception as ex:
                raise Exception(
                    f"There was an error while evaluating tool call_intent accuracy metric on {func.__name__},") from ex

        return wrapper(func)

    def evaluate_tool_call_accuracy(self,
                                    func: Optional[Callable] = None,
                                    *,
                                    configuration: Optional[AgenticAIConfiguration] = None,
                                    metrics: list[GenAIMetric] = [
                                        ToolCallAccuracyMetric()
                                    ]
                                    ) -> dict:
        """
        An evaluation decorator for computing tool_call_accuracy metric on an agentic tool.

        For more details, see :class:`ibm_watsonx_gov.metrics.ToolCallAccuracyMetric`

        Args:
            func (Optional[Callable], optional): The tool on which the metric is to be computed.
            configuration (Optional[AgenticAIConfiguration], optional): The configuration specific to this evaluator. Defaults to None.
            metrics (list[GenAIMetric], optional): The list of metrics to compute as part of this evaluator. Defaults to [ ToolCallAccuracyMetric() ].

        Raises:
            Exception: If there is any error while evaluation.

        Returns:
            dict: The result of the wrapped tool.

        Example:
            1. Usage with llm_judge
                .. code-block:: python

                    llm_judge = LLMJudge(
                        model=WxAIFoundationModel(
                            model_id="meta-llama/llama-3-3-70b-instruct",
                            project_id=os.getenv("WATSONX_PROJECT_ID"),
                        )
                    )
                    metric_1 = ToolCallAccuracyMetric(llm_judge=llm_judge)
                    evaluator = AgenticEvaluation()
                    @evaluator.evaluate_tool_call_accuracy(metrics=[metric_1])
                    def agentic_tool(*args, *kwargs):
                        pass
        """

        if func is None:
            return partial(self.evaluate_tool_call_accuracy, configuration=configuration, metrics=metrics)

        @decorator
        def wrapper(func, instance, args, kwargs):

            try:
                self.__validate(func=func, metrics=metrics,
                                valid_metric_types=(ToolCallAccuracyMetric,))

                metric_inputs = [
                    EvaluatorFields.INPUT_FIELDS
                ]

                metric_outputs = [
                    EvaluatorFields.TOOL_CALLS_FIELD, EvaluatorFields.OUTPUT_FIELDS]

                original_result = self.__compute_helper(func=func, args=args, kwargs=kwargs,
                                                        configuration=configuration,
                                                        metrics=metrics,
                                                        metric_inputs=metric_inputs,
                                                        metric_outputs=metric_outputs)

                return original_result
            except Exception as ex:
                raise Exception(
                    f"There was an error while evaluating tool_call_accuracy metric on {func.__name__},") from ex

        return wrapper(func)

    def evaluate_tool_selection_accuracy(self,
                                         func: Optional[Callable] = None,
                                         *,
                                         configuration: Optional[AgenticAIConfiguration] = None,
                                         metrics: list[GenAIMetric] = [
                                             ToolSelectionAccuracyMetric()
                                         ]
                                         ) -> dict:
        """
        An evaluation decorator for computing tool_selection_accuracy metric on an agentic tool.

        For more details, see :class:`ibm_watsonx_gov.metrics.ToolSelectionAccuracyMetric`

        Args:
            func (Optional[Callable], optional): The tool on which the metric is to be computed.
            configuration (Optional[AgenticAIConfiguration], optional): The configuration specific to this evaluator. Defaults to None.
            metrics (list[GenAIMetric], optional): The list of metrics to compute as part of this evaluator. Defaults to [ ToolSelectionAccuracyMetric() ].

        Raises:
            Exception: If there is any error while evaluation.

        Returns:
            dict: The result of the wrapped tool.

        Example:
            1. Usage with llm_judge
                .. code-block:: python

                    llm_judge = LLMJudge(
                        model=WxAIFoundationModel(
                            model_id="meta-llama/llama-3-3-70b-instruct",
                            project_id=os.getenv("WATSONX_PROJECT_ID"),
                        )
                    )
                    metric_1 = ToolSelectionAccuracyMetric(llm_judge=llm_judge)
                    evaluator = AgenticEvaluation()
                    @evaluator.evaluate_tool_selection_accuracy(metrics=[metric_1])
                    def agentic_tool(*args, *kwargs):
                        pass
        """

        if func is None:
            return partial(self.evaluate_tool_selection_accuracy, configuration=configuration, metrics=metrics)

        @decorator
        def wrapper(func, instance, args, kwargs):

            try:
                self.__validate(func=func, metrics=metrics,
                                valid_metric_types=(ToolSelectionAccuracyMetric,))

                metric_inputs = [
                    EvaluatorFields.INPUT_FIELDS
                ]

                metric_outputs = [
                    EvaluatorFields.TOOL_CALLS_FIELD, EvaluatorFields.OUTPUT_FIELDS]

                original_result = self.__compute_helper(func=func, args=args, kwargs=kwargs,
                                                        configuration=configuration,
                                                        metrics=metrics,
                                                        metric_inputs=metric_inputs,
                                                        metric_outputs=metric_outputs)

                return original_result
            except Exception as ex:
                raise Exception(
                    f"There was an error while evaluating tool_selection_accuracy metric on {func.__name__},") from ex

        return wrapper(func)

    def evaluate_tool_call_parameter_consistency(self,
                                                 func: Optional[Callable] = None,
                                                 *,
                                                 configuration: Optional[AgenticAIConfiguration] = None,
                                                 metrics: list[GenAIMetric] = [
                                                     ToolCallParameterConsistencyMetric()
                                                 ]
                                                 ) -> dict:
        """
        An evaluation decorator for computing tool_call_parameter_consistency metric on an agentic tool.

        For more details, see :class:`ibm_watsonx_gov.metrics.ToolCallParameterConsistencyMetric`

        Args:
            func (Optional[Callable], optional): The tool on which the metric is to be computed.
            configuration (Optional[AgenticAIConfiguration], optional): The configuration specific to this evaluator. Defaults to None.
            metrics (list[GenAIMetric], optional): The list of metrics to compute as part of this evaluator. Defaults to [ ToolCallParameterConsistencyMetric() ].

        Raises:
            Exception: If there is any error while evaluation.

        Returns:
            dict: The result of the wrapped tool.

        Example:
            1. Usage with llm_judge
                .. code-block:: python

                    llm_judge = LLMJudge(
                        model=WxAIFoundationModel(
                            model_id="meta-llama/llama-3-3-70b-instruct",
                            project_id=os.getenv("WATSONX_PROJECT_ID"),
                        )
                    )
                    metric_1 = ToolCallParameterConsistencyMetric(llm_judge=llm_judge)
                    evaluator = AgenticEvaluation()
                    @evaluator.evaluate_tool_call_parameter_consistency(metrics=[metric_1])
                    def agentic_tool(*args, *kwargs):
                        pass
        """

        if func is None:
            return partial(self.evaluate_tool_call_parameter_consistency, configuration=configuration, metrics=metrics)

        @decorator
        def wrapper(func, instance, args, kwargs):

            try:
                self.__validate(func=func, metrics=metrics,
                                valid_metric_types=(ToolCallParameterConsistencyMetric,))

                metric_inputs = [
                    EvaluatorFields.INPUT_FIELDS
                ]

                metric_outputs = [
                    EvaluatorFields.TOOL_CALLS_FIELD, EvaluatorFields.OUTPUT_FIELDS]

                original_result = self.__compute_helper(func=func, args=args, kwargs=kwargs,
                                                        configuration=configuration,
                                                        metrics=metrics,
                                                        metric_inputs=metric_inputs,
                                                        metric_outputs=metric_outputs)

                return original_result
            except Exception as ex:
                raise Exception(
                    f"There was an error while evaluating tool_call_parameter_consistency metric on {func.__name__},") from ex

        return wrapper(func)

    def evaluate_tool_call_parameter_alignment(self,
                                               func: Optional[Callable] = None,
                                               *,
                                               configuration: Optional[AgenticAIConfiguration] = None,
                                               metrics: list[GenAIMetric] = [
                                                   ToolCallParameterAlignmentMetric()
                                               ],
                                               compute_online: Optional[bool] = True) -> dict:
        """
        An evaluation decorator for computing tool_call_parameter_alignment metric on an agentic tool.

        For more details, see :class:`ibm_watsonx_gov.metrics.ToolCallParameterAlignmentMetric`

        Args:
            func (Optional[Callable], optional): The tool on which the metric is to be computed.
            configuration (Optional[AgenticAIConfiguration], optional): The configuration specific to this evaluator. Defaults to None.
            metrics (list[GenAIMetric], optional): The list of metrics to compute as part of this evaluator. Defaults to [ ToolCallParameterAlignmentMetric() ].

        Raises:
            Exception: If there is any error while evaluation.

        Returns:
            dict: The result of the wrapped tool.

        Example:
            1. Usage with llm_judge
                .. code-block:: python

                    llm_judge = LLMJudge(
                        model=WxAIFoundationModel(
                            model_id="meta-llama/llama-3-3-70b-instruct",
                            project_id=os.getenv("WATSONX_PROJECT_ID"),
                        )
                    )
                    metric_1 = ToolCallParameterAlignmentMetric(llm_judge=llm_judge)
                    evaluator = AgenticEvaluation()
                    @evaluator.evaluate_tool_call_parameter_alignment(metrics=[metric_1])
                    def agentic_tool(*args, *kwargs):
                        pass
        """

        if func is None:
            return partial(self.evaluate_tool_call_parameter_alignment, configuration=configuration, metrics=metrics)

        @decorator
        def wrapper(func, instance, args, kwargs):

            try:
                self.__validate(func=func, metrics=metrics,
                                valid_metric_types=(ToolCallParameterAlignmentMetric,))

                metric_inputs = [
                    EvaluatorFields.INPUT_FIELDS
                ]

                metric_outputs = [
                    EvaluatorFields.TOOL_CALLS_FIELD, EvaluatorFields.OUTPUT_FIELDS]

                original_result = self.__compute_helper(func=func, args=args, kwargs=kwargs,
                                                        configuration=configuration,
                                                        metrics=metrics,
                                                        metric_inputs=metric_inputs,
                                                        metric_outputs=metric_outputs)

                return original_result
            except Exception as ex:
                raise Exception(
                    f"There was an error while evaluating tool_call_parameter_alignment metric on {func.__name__},") from ex

        return wrapper(func)

    def evaluate_tool_call_parameter_hallucination(self,
                                                   func: Optional[Callable] = None,
                                                   *,
                                                   configuration: Optional[AgenticAIConfiguration] = None,
                                                   metrics: list[GenAIMetric] = [
                                                       ToolCallParameterHallucinationMetric()
                                                   ],
                                                   compute_online: Optional[bool] = True) -> dict:
        """
        An evaluation decorator for computing tool_call_parameter_hallucination metric on an agentic tool.

        For more details, see :class:`ibm_watsonx_gov.metrics.ToolCallParameterHallucinationMetric`

        Args:
            func (Optional[Callable], optional): The tool on which the metric is to be computed.
            configuration (Optional[AgenticAIConfiguration], optional): The configuration specific to this evaluator. Defaults to None.
            metrics (list[GenAIMetric], optional): The list of metrics to compute as part of this evaluator. Defaults to [ ToolCallParameterHallucinationMetric() ].

        Raises:
            Exception: If there is any error while evaluation.

        Returns:
            dict: The result of the wrapped tool.

        Example:
            1. Usage with llm_judge
                .. code-block:: python

                    llm_judge = LLMJudge(
                        model=WxAIFoundationModel(
                            model_id="meta-llama/llama-3-3-70b-instruct",
                            project_id=os.getenv("WATSONX_PROJECT_ID"),
                        )
                    )
                    metric_1 = ToolCallParameterHallucinationMetric(llm_judge=llm_judge)
                    evaluator = AgenticEvaluation()
                    @evaluator.evaluate_tool_call_parameter_hallucination(metrics=[metric_1])
                    def agentic_tool(*args, *kwargs):
                        pass
        """

        if func is None:
            return partial(self.evaluate_tool_call_parameter_hallucination, configuration=configuration, metrics=metrics)

        @decorator
        def wrapper(func, instance, args, kwargs):

            try:
                self.__validate(func=func, metrics=metrics,
                                valid_metric_types=(ToolCallParameterHallucinationMetric,))

                metric_inputs = [
                    EvaluatorFields.INPUT_FIELDS
                ]

                metric_outputs = [
                    EvaluatorFields.TOOL_CALLS_FIELD, EvaluatorFields.OUTPUT_FIELDS]

                original_result = self.__compute_helper(func=func, args=args, kwargs=kwargs,
                                                        configuration=configuration,
                                                        metrics=metrics,
                                                        metric_inputs=metric_inputs,
                                                        metric_outputs=metric_outputs)

                return original_result
            except Exception as ex:
                raise Exception(
                    f"There was an error while evaluating tool_call_parameter_hallucination metric on {func.__name__},") from ex

        return wrapper(func)

    def evaluate_tool_call_parameter_information_sufficiency(self,
                                                             func: Optional[Callable] = None,
                                                             *,
                                                             configuration: Optional[AgenticAIConfiguration] = None,
                                                             metrics: list[GenAIMetric] = [
                                                                 ToolCallParameterInformationSufficiencyMetric()
                                                             ],
                                                             compute_online: Optional[bool] = True) -> dict:
        """
        An evaluation decorator for computing tool_call_parameter_information_sufficiency metric on an agentic tool.

        For more details, see :class:`ibm_watsonx_gov.metrics.ToolCallParameterInformationSufficiencyMetric`

        Args:
            func (Optional[Callable], optional): The tool on which the metric is to be computed.
            configuration (Optional[AgenticAIConfiguration], optional): The configuration specific to this evaluator. Defaults to None.
            metrics (list[GenAIMetric], optional): The list of metrics to compute as part of this evaluator. Defaults to [ ToolCallParameterInformationSufficiencyMetric() ].

        Raises:
            Exception: If there is any error while evaluation.

        Returns:
            dict: The result of the wrapped tool.

        Example:
            1. Usage with llm_judge
                .. code-block:: python

                    llm_judge = LLMJudge(
                        model=WxAIFoundationModel(
                            model_id="meta-llama/llama-3-3-70b-instruct",
                            project_id=os.getenv("WATSONX_PROJECT_ID"),
                        )
                    )
                    metric_1 = ToolCallParameterInformationSufficiencyMetric(llm_judge=llm_judge)
                    evaluator = AgenticEvaluation()
                    @evaluator.evaluate_tool_call_parameter_information_sufficiency(metrics=[metric_1])
                    def agentic_tool(*args, *kwargs):
                        pass
        """

        if func is None:
            return partial(self.evaluate_tool_call_parameter_information_sufficiency, configuration=configuration, metrics=metrics)

        @decorator
        def wrapper(func, instance, args, kwargs):

            try:
                self.__validate(func=func, metrics=metrics,
                                valid_metric_types=(ToolCallParameterInformationSufficiencyMetric,))

                metric_inputs = [
                    EvaluatorFields.INPUT_FIELDS
                ]

                metric_outputs = [
                    EvaluatorFields.TOOL_CALLS_FIELD, EvaluatorFields.OUTPUT_FIELDS]

                original_result = self.__compute_helper(func=func, args=args, kwargs=kwargs,
                                                        configuration=configuration,
                                                        metrics=metrics,
                                                        metric_inputs=metric_inputs,
                                                        metric_outputs=metric_outputs)

                return original_result
            except Exception as ex:
                raise Exception(
                    f"There was an error while evaluating tool_call_parameter_information_sufficiency metric on {func.__name__},") from ex

        return wrapper(func)

    def evaluate_tool_call_parameter_accuracy(self,
                                              func: Optional[Callable] = None,
                                              *,
                                              configuration: Optional[AgenticAIConfiguration] = None,
                                              metrics: list[GenAIMetric] = [
                                                  ToolCallParameterAccuracyMetric()
                                              ],
                                              compute_online: Optional[bool] = True) -> dict:
        """
        An evaluation decorator for computing tool_call_parameter_accuracy metric on an agentic tool.

        For more details, see :class:`ibm_watsonx_gov.metrics.ToolCallParameterAccuracyMetric`

        Args:
            func (Optional[Callable], optional): The tool on which the metric is to be computed.
            configuration (Optional[AgenticAIConfiguration], optional): The configuration specific to this evaluator. Defaults to None.
            metrics (list[GenAIMetric], optional): The list of metrics to compute as part of this evaluator. Defaults to [ ToolCallParameterAccuracyMetric() ].

        Raises:
            Exception: If there is any error while evaluation.

        Returns:
            dict: The result of the wrapped tool.

        Example:
            1. Usage with llm_judge
                .. code-block:: python

                    llm_judge = LLMJudge(
                        model=WxAIFoundationModel(
                            model_id="meta-llama/llama-3-3-70b-instruct",
                            project_id=os.getenv("WATSONX_PROJECT_ID"),
                        )
                    )
                    metric_1 = ToolCallParameterAccuracyMetric(llm_judge=llm_judge)
                    evaluator = AgenticEvaluation()
                    @evaluator.evaluate_tool_call_parameter_accuracy(metrics=[metric_1])
                    def agentic_tool(*args, *kwargs):
                        pass
        """

        if func is None:
            return partial(self.evaluate_tool_call_parameter_accuracy, configuration=configuration, metrics=metrics)

        @decorator
        def wrapper(func, instance, args, kwargs):

            try:
                self.__validate(func=func, metrics=metrics,
                                valid_metric_types=(ToolCallParameterAccuracyMetric,))

                metric_inputs = [
                    EvaluatorFields.INPUT_FIELDS
                ]

                metric_outputs = [
                    EvaluatorFields.TOOL_CALLS_FIELD, EvaluatorFields.OUTPUT_FIELDS]

                original_result = self.__compute_helper(func=func, args=args, kwargs=kwargs,
                                                        configuration=configuration,
                                                        metrics=metrics,
                                                        metric_inputs=metric_inputs,
                                                        metric_outputs=metric_outputs)

                return original_result
            except Exception as ex:
                raise Exception(
                    f"There was an error while evaluating tool_call_parameter_accuracy metric on {func.__name__},") from ex

        return wrapper(func)

    def evaluate_tool_call_parameter_groundedness(self,
                                                  func: Optional[Callable] = None,
                                                  *,
                                                  configuration: Optional[AgenticAIConfiguration] = None,
                                                  metrics: list[GenAIMetric] = [
                                                      ToolCallParameterGroundednessMetric()
                                                  ]
                                                  ) -> dict:
        """
        An evaluation decorator for computing tool_call_parameter_groundedness metric on an agentic tool.

        For more details, see :class:`ibm_watsonx_gov.metrics.ToolCallParameterGroundednessMetric`

        Args:
            func (Optional[Callable], optional): The tool on which the metric is to be computed.
            configuration (Optional[AgenticAIConfiguration], optional): The configuration specific to this evaluator. Defaults to None.
            metrics (list[GenAIMetric], optional): The list of metrics to compute as part of this evaluator. Defaults to [ ToolCallParameterGroundednessMetric() ].

        Raises:
            Exception: If there is any error while evaluation.

        Returns:
            dict: The result of the wrapped tool.

        Example:
            1. Usage with llm_judge
                .. code-block:: python

                    llm_judge = LLMJudge(
                        model=WxAIFoundationModel(
                            model_id="meta-llama/llama-3-3-70b-instruct",
                            project_id=os.getenv("WATSONX_PROJECT_ID"),
                        )
                    )
                    metric_1 = ToolCallParameterGroundednessMetric(llm_judge=llm_judge)
                    evaluator = AgenticEvaluation()
                    @evaluator.evaluate_tool_call_parameter_groundedness(metrics=[metric_1])
                    def agentic_tool(*args, *kwargs):
                        pass
        """

        if func is None:
            return partial(self.evaluate_tool_call_parameter_groundedness, configuration=configuration, metrics=metrics)

        @decorator
        def wrapper(func, instance, args, kwargs):

            try:
                self.__validate(func=func, metrics=metrics,
                                valid_metric_types=(ToolCallParameterGroundednessMetric,))

                metric_inputs = [
                    EvaluatorFields.INPUT_FIELDS
                ]

                metric_outputs = [
                    EvaluatorFields.TOOL_CALLS_FIELD, EvaluatorFields.OUTPUT_FIELDS]

                original_result = self.__compute_helper(func=func, args=args, kwargs=kwargs,
                                                        configuration=configuration,
                                                        metrics=metrics,
                                                        metric_inputs=metric_inputs,
                                                        metric_outputs=metric_outputs)

                return original_result
            except Exception as ex:
                raise Exception(
                    f"There was an error while evaluating tool_call_parameter_groundedness metric on {func.__name__},") from ex

        return wrapper(func)

    def evaluate_tool_call_order_accuracy(self,
                                          func: Optional[Callable] = None,
                                          *,
                                          configuration: Optional[AgenticAIConfiguration] = None,
                                          metrics: list[GenAIMetric] = [
                                              ToolCallOrderAccuracyMetric()
                                          ]
                                          ) -> dict:
        """
        An evaluation decorator for computing tool_call_order_accuracy metric on an agentic tool.

        For more details, see :class:`ibm_watsonx_gov.metrics.ToolCallOrderAccuracyMetric`

        Args:
            func (Optional[Callable], optional): The tool on which the metric is to be computed.
            configuration (Optional[AgenticAIConfiguration], optional): The configuration specific to this evaluator. Defaults to None.
            metrics (list[GenAIMetric], optional): The list of metrics to compute as part of this evaluator. Defaults to [ ToolCallOrderAccuracyMetric() ].

        Raises:
            Exception: If there is any error while evaluation.

        Returns:
            dict: The result of the wrapped tool.

        Example:
            1. Usage with llm_judge
                .. code-block:: python

                    llm_judge = LLMJudge(
                        model=WxAIFoundationModel(
                            model_id="meta-llama/llama-3-3-70b-instruct",
                            project_id=os.getenv("WATSONX_PROJECT_ID"),
                        )
                    )
                    metric_1 = ToolCallOrderAccuracyMetric(llm_judge=llm_judge)
                    evaluator = AgenticEvaluation()
                    @evaluator.evaluate_tool_call_order_accuracy(metrics=[metric_1])
                    def agentic_tool(*args, *kwargs):
                        pass
        """

        if func is None:
            return partial(self.evaluate_tool_call_order_accuracy, configuration=configuration, metrics=metrics)

        @decorator
        def wrapper(func, instance, args, kwargs):

            try:
                self.__validate(func=func, metrics=metrics,
                                valid_metric_types=(ToolCallOrderAccuracyMetric,))

                metric_inputs = [
                    EvaluatorFields.INPUT_FIELDS
                ]

                metric_outputs = [
                    EvaluatorFields.TOOL_CALLS_FIELD, EvaluatorFields.OUTPUT_FIELDS]

                original_result = self.__compute_helper(func=func, args=args, kwargs=kwargs,
                                                        configuration=configuration,
                                                        metrics=metrics,
                                                        metric_inputs=metric_inputs,
                                                        metric_outputs=metric_outputs)

                return original_result
            except Exception as ex:
                raise Exception(
                    f"There was an error while evaluating tool_call_order_accuracy metric on {func.__name__},") from ex

        return wrapper(func)

    def evaluate_answer_relevance(self,
                                  func: Optional[Callable] = None,
                                  *,
                                  configuration: Optional[AgenticAIConfiguration] = None,
                                  metrics: list[GenAIMetric] = [
                                      AnswerRelevanceMetric()
                                  ]
                                  ) -> dict:
        """
        An evaluation decorator for computing answer relevance metric on an agentic tool.

        For more details, see :class:`ibm_watsonx_gov.metrics.AnswerRelevanceMetric`

        Args:
            func (Optional[Callable], optional): The tool on which the metric is to be computed.
            configuration (Optional[AgenticAIConfiguration], optional): The configuration specific to this evaluator. Defaults to None.
            metrics (list[GenAIMetric], optional): The list of metrics to compute as part of this evaluator. Defaults to [ AnswerRelevanceMetric() ].

        Raises:
            Exception: If there is any error while evaluation.

        Returns:
            dict: The result of the wrapped tool.

        Example:
            1. Basic usage
                .. code-block:: python

                    evaluator = AgenticEvaluation()
                    @evaluator.evaluate_answer_relevance
                    def agentic_tool(*args, *kwargs):
                        pass

            2. Usage with different thresholds and methods
                .. code-block:: python

                    metric_1 = AnswerRelevanceMetric(method="token_recall", threshold=MetricThreshold(type="lower_limit", value=0.5))

                    evaluator = AgenticEvaluation()
                    @evaluator.evaluate_answer_relevance(metrics=[metric_1])
                    def agentic_tool(*args, *kwargs):
                        pass
        """

        if func is None:
            return partial(self.evaluate_answer_relevance, configuration=configuration, metrics=metrics)

        @decorator
        def wrapper(func, instance, args, kwargs):

            try:
                self.__validate(func=func, metrics=metrics,
                                valid_metric_types=(AnswerRelevanceMetric,))

                metric_inputs = [
                    EvaluatorFields.INPUT_FIELDS
                ]
                metric_outputs = [EvaluatorFields.OUTPUT_FIELDS]

                original_result = self.__compute_helper(func=func, args=args, kwargs=kwargs,
                                                        configuration=configuration,
                                                        metrics=metrics,
                                                        metric_inputs=metric_inputs,
                                                        metric_outputs=metric_outputs)

                return original_result
            except Exception as ex:
                raise Exception(
                    f"There was an error while evaluating answer relevance metric on {func.__name__},") from ex

        return wrapper(func)

    def evaluate_unsuccessful_requests(self,
                                       func: Optional[Callable] = None,
                                       *,
                                       configuration: Optional[AgenticAIConfiguration] = None,
                                       metrics: list[GenAIMetric] = [
                                           UnsuccessfulRequestsMetric()
                                       ]
                                       ) -> dict:
        """
        An evaluation decorator for computing unsuccessful requests metric on an agentic tool.

        For more details, see :class:`ibm_watsonx_gov.metrics.UnsuccessfulRequestsMetric`

        Args:
            func (Optional[Callable], optional): The tool on which the metric is to be computed.
            configuration (Optional[AgenticAIConfiguration], optional): The configuration specific to this evaluator. Defaults to None.
            metrics (list[GenAIMetric], optional): The list of metrics to compute as part of this evaluator. Defaults to [ UnsuccessfulRequestsMetric() ].

        Raises:
            Exception: If there is any error while evaluation.

        Returns:
            dict: The result of the wrapped tool.

        Example:
            1. Basic usage
                .. code-block:: python

                    evaluator = AgenticEvaluation()
                    @evaluator.evaluate_unsuccessful_requests
                    def agentic_tool(*args, *kwargs):
                        pass

            2. Usage with different thresholds and methods
                .. code-block:: python

                    metric_1 = UnsuccessfulRequestsMetric(threshold=MetricThreshold(type="lower_limit", value=0.5))

                    evaluator = AgenticEvaluation()
                    @evaluator.evaluate_unsuccessful_requests(metrics=[metric_1])
                    def agentic_tool(*args, *kwargs):
                        pass
        """

        if func is None:
            return partial(self.evaluate_unsuccessful_requests, configuration=configuration, metrics=metrics)

        @decorator
        def wrapper(func, instance, args, kwargs):

            try:
                self.__validate(func=func, metrics=metrics,
                                valid_metric_types=(UnsuccessfulRequestsMetric,))

                metric_inputs = []
                metric_outputs = [EvaluatorFields.OUTPUT_FIELDS]

                original_result = self.__compute_helper(func=func, args=args, kwargs=kwargs,
                                                        configuration=configuration,
                                                        metrics=metrics,
                                                        metric_inputs=metric_inputs,
                                                        metric_outputs=metric_outputs)

                return original_result
            except Exception as ex:
                raise Exception(
                    f"There was an error while evaluating unsuccessful metric on {func.__name__},") from ex

        return wrapper(func)

    def evaluate_average_precision(self,
                                   func: Optional[Callable] = None,
                                   *,
                                   configuration: Optional[AgenticAIConfiguration] = None,
                                   metrics: list[GenAIMetric] = [
                                       AveragePrecisionMetric()
                                   ]
                                   ) -> dict:
        """
        An evaluation decorator for computing average precision metric on an agentic tool.
        This metric uses context relevance values for computation, context relevance metric would be computed as a prerequisite.

        For more details, see :class:`ibm_watsonx_gov.metrics.AveragePrecisionMetric`

        Args:
            func (Optional[Callable], optional): The tool on which the metric is to be computed.
            configuration (Optional[AgenticAIConfiguration], optional): The configuration specific to this evaluator. Defaults to None.
            metrics (list[GenAIMetric], optional): The list of metrics to compute as part of this evaluator. Defaults to [ AveragePrecisionMetric() ].

        Raises:
            Exception: If there is any error while evaluation.

        Returns:
            dict: The result of the wrapped tool.

        Example:
            1. Basic usage
                .. code-block:: python

                    evaluator = AgenticEvaluation()
                    @evaluator.evaluate_average_precision
                    def agentic_tool(*args, *kwargs):
                        pass

            2. Usage with different thresholds and methods
                .. code-block:: python

                    metric_1 = AveragePrecisionMetric(threshold=MetricThreshold(type="lower_limit", value=0.5))
                    metric_2 = ContextRelevanceMetric(method="sentence_bert_mini_lm", threshold=MetricThreshold(type="lower_limit", value=0.6))

                    evaluator = AgenticEvaluation()
                    @evaluator.evaluate_average_precision(metrics=[metric_1, metric_2])
                    def agentic_tool(*args, *kwargs):
                        pass
        """

        if func is None:
            return partial(self.evaluate_average_precision, configuration=configuration, metrics=metrics)

        @decorator
        def wrapper(func, instance, args, kwargs):

            try:
                self.__validate(func=func, metrics=metrics,
                                valid_metric_types=(AveragePrecisionMetric, ContextRelevanceMetric))

                metric_inputs = [EvaluatorFields.INPUT_FIELDS]
                metric_outputs = [EvaluatorFields.CONTEXT_FIELDS]

                is_metric_present = False
                for m in metrics:
                    if isinstance(m, AveragePrecisionMetric):
                        is_metric_present = True
                        break
                if not is_metric_present:
                    metrics.append(AveragePrecisionMetric())

                original_result = self.__compute_helper(func=func, args=args, kwargs=kwargs,
                                                        configuration=configuration,
                                                        metrics=metrics,
                                                        metric_inputs=metric_inputs,
                                                        metric_outputs=metric_outputs)

                return original_result
            except Exception as ex:
                raise Exception(
                    f"There was an error while evaluating average precision metric on {func.__name__},") from ex

        return wrapper(func)

    def evaluate_retrieval_precision(self,
                                     func: Optional[Callable] = None,
                                     *,
                                     configuration: Optional[AgenticAIConfiguration] = None,
                                     metrics: list[GenAIMetric] = [
                                         RetrievalPrecisionMetric()
                                     ]
                                     ) -> dict:
        """
        An evaluation decorator for computing retrieval precision metric on an agentic tool.
        This metric uses context relevance values for computation, context relevance metric would be computed as a prerequisite.

        For more details, see :class:`ibm_watsonx_gov.metrics.RetrievalPrecisionMetric`

        Args:
            func (Optional[Callable], optional): The tool on which the metric is to be computed.
            configuration (Optional[AgenticAIConfiguration], optional): The configuration specific to this evaluator. Defaults to None.
            metrics (list[GenAIMetric], optional): The list of metrics to compute as part of this evaluator. Defaults to [ RetrievalPrecisionMetric() ].

        Raises:
            Exception: If there is any error while evaluation.

        Returns:
            dict: The result of the wrapped tool.

        Example:
            1. Basic usage
                .. code-block:: python

                    evaluator = AgenticEvaluation()
                    @evaluator.evaluate_retrieval_precision
                    def agentic_tool(*args, *kwargs):
                        pass

            2. Usage with different thresholds and methods
                .. code-block:: python

                    metric_1 = AveragePrecisionMetric(threshold=MetricThreshold(type="lower_limit", value=0.5))
                    metric_2 = ContextRelevanceMetric(method="sentence_bert_mini_lm", threshold=MetricThreshold(type="lower_limit", value=0.6))

                    evaluator = AgenticEvaluation()
                    @evaluator.evaluate_retrieval_precision(metrics=[metric_1, metric_2])
                    def agentic_tool(*args, *kwargs):
                        pass
        """

        if func is None:
            return partial(self.evaluate_retrieval_precision, configuration=configuration, metrics=metrics)

        @decorator
        def wrapper(func, instance, args, kwargs):

            try:
                self.__validate(func=func, metrics=metrics,
                                valid_metric_types=(RetrievalPrecisionMetric, ContextRelevanceMetric))

                metric_inputs = [EvaluatorFields.INPUT_FIELDS]
                metric_outputs = [EvaluatorFields.CONTEXT_FIELDS]

                is_metric_present = False
                for m in metrics:
                    if isinstance(m, RetrievalPrecisionMetric):
                        is_metric_present = True
                        break
                if not is_metric_present:
                    metrics.append(RetrievalPrecisionMetric())

                original_result = self.__compute_helper(func=func, args=args, kwargs=kwargs,
                                                        configuration=configuration,
                                                        metrics=metrics,
                                                        metric_inputs=metric_inputs,
                                                        metric_outputs=metric_outputs)

                return original_result
            except Exception as ex:
                raise Exception(
                    f"There was an error while evaluating retrieval precision metric on {func.__name__},") from ex

        return wrapper(func)

    def evaluate_reciprocal_rank(self,
                                 func: Optional[Callable] = None,
                                 *,
                                 configuration: Optional[AgenticAIConfiguration] = None,
                                 metrics: list[GenAIMetric] = [
                                     ReciprocalRankMetric()
                                 ]
                                 ) -> dict:
        """
        An evaluation decorator for computing reciprocal precision metric on an agentic tool.
        This metric uses context relevance values for computation, context relevance metric would be computed as a prerequisite.

        For more details, see :class:`ibm_watsonx_gov.metrics.ReciprocalRankMetric`

        Args:
            func (Optional[Callable], optional): The tool on which the metric is to be computed.
            configuration (Optional[AgenticAIConfiguration], optional): The configuration specific to this evaluator. Defaults to None.
            metrics (list[GenAIMetric], optional): The list of metrics to compute as part of this evaluator. Defaults to [ ReciprocalRankMetric() ].

        Raises:
            Exception: If there is any error while evaluation.

        Returns:
            dict: The result of the wrapped tool.

        Example:
            1. Basic usage
                .. code-block:: python

                    evaluator = AgenticEvaluation()
                    @evaluator.evaluate_reciprocal_rank
                    def agentic_tool(*args, *kwargs):
                        pass

            2. Usage with different thresholds and methods
                .. code-block:: python

                    metric_1 = ReciprocalRankMetric(threshold=MetricThreshold(type="lower_limit", value=0.5))
                    metric_2 = ContextRelevanceMetric(method="sentence_bert_mini_lm", threshold=MetricThreshold(type="lower_limit", value=0.6))

                    evaluator = AgenticEvaluation()
                    @evaluator.evaluate_reciprocal_rank(metrics=[metric_1, metric_2])
                    def agentic_tool(*args, *kwargs):
                        pass
        """

        if func is None:
            return partial(self.evaluate_reciprocal_rank, configuration=configuration, metrics=metrics)

        @decorator
        def wrapper(func, instance, args, kwargs):

            try:
                self.__validate(func=func, metrics=metrics,
                                valid_metric_types=(ReciprocalRankMetric, ContextRelevanceMetric))

                metric_inputs = [EvaluatorFields.INPUT_FIELDS]
                metric_outputs = [EvaluatorFields.CONTEXT_FIELDS]

                is_metric_present = False
                for m in metrics:
                    if isinstance(m, ReciprocalRankMetric):
                        is_metric_present = True
                        break
                if not is_metric_present:
                    metrics.append(ReciprocalRankMetric())

                original_result = self.__compute_helper(func=func, args=args, kwargs=kwargs,
                                                        configuration=configuration,
                                                        metrics=metrics,
                                                        metric_inputs=metric_inputs,
                                                        metric_outputs=metric_outputs)

                return original_result
            except Exception as ex:
                raise Exception(
                    f"There was an error while evaluating reciprocal rank metric on {func.__name__},") from ex

        return wrapper(func)

    def evaluate_hit_rate(self,
                          func: Optional[Callable] = None,
                          *,
                          configuration: Optional[AgenticAIConfiguration] = None,
                          metrics: list[GenAIMetric] = [
                              HitRateMetric()
                          ]
                          ) -> dict:
        """
        An evaluation decorator for computing hit rate metric on an agentic tool.
        This metric uses context relevance values for computation, context relevance metric would be computed as a prerequisite.

        For more details, see :class:`ibm_watsonx_gov.metrics.HitRateMetric`

        Args:
            func (Optional[Callable], optional): The tool on which the metric is to be computed.
            configuration (Optional[AgenticAIConfiguration], optional): The configuration specific to this evaluator. Defaults to None.
            metrics (list[GenAIMetric], optional): The list of metrics to compute as part of this evaluator. Defaults to [ HitRateMetric() ].

        Raises:
            Exception: If there is any error while evaluation.

        Returns:
            dict: The result of the wrapped tool.

        Example:
            1. Basic usage
                .. code-block:: python

                    evaluator = AgenticEvaluation()
                    @evaluator.evaluate_hit_rate
                    def agentic_tool(*args, *kwargs):
                        pass

            2. Usage with different thresholds and methods
                .. code-block:: python

                    metric_1 = HitRateMetric(threshold=MetricThreshold(type="lower_limit", value=0.5))
                    metric_2 = ContextRelevanceMetric(method="sentence_bert_mini_lm", threshold=MetricThreshold(type="lower_limit", value=0.6))

                    evaluator = AgenticEvaluation()
                    @evaluator.evaluate_hit_rate(metrics=[metric_1, metric_2])
                    def agentic_tool(*args, *kwargs):
                        pass
        """

        if func is None:
            return partial(self.evaluate_hit_rate, configuration=configuration, metrics=metrics)

        @decorator
        def wrapper(func, instance, args, kwargs):

            try:
                self.__validate(func=func, metrics=metrics,
                                valid_metric_types=(HitRateMetric, ContextRelevanceMetric))

                metric_inputs = [EvaluatorFields.INPUT_FIELDS]
                metric_outputs = [EvaluatorFields.CONTEXT_FIELDS]

                is_metric_present = False
                for m in metrics:
                    if isinstance(m, HitRateMetric):
                        is_metric_present = True
                        break
                if not is_metric_present:
                    metrics.append(HitRateMetric())

                original_result = self.__compute_helper(func=func, args=args, kwargs=kwargs,
                                                        configuration=configuration,
                                                        metrics=metrics,
                                                        metric_inputs=metric_inputs,
                                                        metric_outputs=metric_outputs)

                return original_result
            except Exception as ex:
                raise Exception(
                    f"There was an error while evaluating hit rate metric on {func.__name__},") from ex

        return wrapper(func)

    def evaluate_ndcg(self,
                      func: Optional[Callable] = None,
                      *,
                      configuration: Optional[AgenticAIConfiguration] = None,
                      metrics: list[GenAIMetric] = [
                          NDCGMetric()
                      ]
                      ) -> dict:
        """
        An evaluation decorator for computing ndcg metric on an agentic tool.
        This metric uses context relevance values for computation, context relevance metric would be computed as a prerequisite.

        For more details, see :class:`ibm_watsonx_gov.metrics.NDCGMetric`

        Args:
            func (Optional[Callable], optional): The tool on which the metric is to be computed.
            configuration (Optional[AgenticAIConfiguration], optional): The configuration specific to this evaluator. Defaults to None.
            metrics (list[GenAIMetric], optional): The list of metrics to compute as part of this evaluator. Defaults to [ NDCGMetric() ].

        Raises:
            Exception: If there is any error while evaluation.

        Returns:
            dict: The result of the wrapped tool.

        Example:
            1. Basic usage
                .. code-block:: python

                    evaluator = AgenticEvaluation()
                    @evaluator.evaluate_ndcg
                    def agentic_tool(*args, *kwargs):
                        pass

            2. Usage with different thresholds and methods
                .. code-block:: python

                    metric_1 = NDCGMetric(threshold=MetricThreshold(type="lower_limit", value=0.5))
                    metric_2 = ContextRelevanceMetric(method="sentence_bert_mini_lm", threshold=MetricThreshold(type="lower_limit", value=0.6))

                    evaluator = AgenticEvaluation()
                    @evaluator.evaluate_ndcg(metrics=[metric_1, metric_2])
                    def agentic_tool(*args, *kwargs):
                        pass
        """

        if func is None:
            return partial(self.evaluate_ndcg, configuration=configuration, metrics=metrics)

        @decorator
        def wrapper(func, instance, args, kwargs):

            try:
                self.__validate(func=func, metrics=metrics,
                                valid_metric_types=(NDCGMetric, ContextRelevanceMetric))

                metric_inputs = [EvaluatorFields.INPUT_FIELDS]
                metric_outputs = [EvaluatorFields.CONTEXT_FIELDS]

                is_metric_present = False
                for m in metrics:
                    if isinstance(m, NDCGMetric):
                        is_metric_present = True
                        break
                if not is_metric_present:
                    metrics.append(NDCGMetric())

                original_result = self.__compute_helper(func=func, args=args, kwargs=kwargs,
                                                        configuration=configuration,
                                                        metrics=metrics,
                                                        metric_inputs=metric_inputs,
                                                        metric_outputs=metric_outputs)

                return original_result
            except Exception as ex:
                raise Exception(
                    f"There was an error while evaluating ndcg metric on {func.__name__},") from ex

        return wrapper(func)

    def evaluate_retrieval_quality(self,
                                   func: Optional[Callable] = None,
                                   *,
                                   configuration: Optional[AgenticAIConfiguration] = None,
                                   metrics: list[GenAIMetric] = MetricGroup.RETRIEVAL_QUALITY.get_metrics(
                                   )
                                   ) -> dict:
        """
        An evaluation decorator for computing retrieval quality metrics on an agentic tool.
        Retrieval Quality metrics include Context Relevance, Retrieval Precision, Average Precision, Hit Rate, Reciprocal Rank, NDCG

        For more details, see :class:`ibm_watsonx_gov.metrics.ContextRelevanceMetric`, :class:`ibm_watsonx_gov.metrics.RetrievalPrecisionMetric`, 
        :class:`ibm_watsonx_gov.metrics.AveragePrecisionMetric`, :class:`ibm_watsonx_gov.metrics.ReciprocalRankMetric`, :class:`ibm_watsonx_gov.metrics.HitRateMetric`,
        :class:`ibm_watsonx_gov.metrics.NDCGMetric`

        Args:
            func (Optional[Callable], optional): The tool on which the metric is to be computed.
            configuration (Optional[AgenticAIConfiguration], optional): The configuration specific to this evaluator. Defaults to None.
            metrics (list[GenAIMetric], optional): The list of metrics to compute as part of this evaluator. Defaults to MetricGroup.RETRIEVAL_QUALITY.get_metrics().

        Raises:
            Exception: If there is any error while evaluation.

        Returns:
            dict: The result of the wrapped tool.

        Example:
            1. Basic usage
                .. code-block:: python

                    evaluator = AgenticEvaluation()
                    @evaluator.evaluate_retrieval_quality
                    def agentic_tool(*args, *kwargs):
                        pass

            2. Usage with different thresholds and methods for some of the metrics in the group
                .. code-block:: python

                    metric_1 = NDCGMetric(threshold=MetricThreshold(type="lower_limit", value=0.5))
                    metric_2 = ContextRelevanceMetric(method="sentence_bert_mini_lm", threshold=MetricThreshold(type="lower_limit", value=0.6))

                    evaluator = AgenticEvaluation()
                    @evaluator.retrieval_quality(metrics=[metric_1, metric_2])
                    def agentic_tool(*args, *kwargs):
                        pass
        """

        if func is None:
            return partial(self.evaluate_retrieval_quality, configuration=configuration, metrics=metrics)

        @decorator
        def wrapper(func, instance, args, kwargs):

            try:
                self.__validate(func=func, metrics=metrics,
                                valid_metric_types=(NDCGMetric, ContextRelevanceMetric, ReciprocalRankMetric, RetrievalPrecisionMetric, AveragePrecisionMetric, HitRateMetric))

                metric_inputs = [EvaluatorFields.INPUT_FIELDS]
                metric_outputs = [EvaluatorFields.CONTEXT_FIELDS]

                original_result = self.__compute_helper(func=func, args=args, kwargs=kwargs,
                                                        configuration=configuration,
                                                        metrics=metrics,
                                                        metric_inputs=metric_inputs,
                                                        metric_outputs=metric_outputs,
                                                        metric_groups=[MetricGroup.RETRIEVAL_QUALITY])

                return original_result
            except Exception as ex:
                raise Exception(
                    f"There was an error while evaluating retrieval quality metrics on {func.__name__},") from ex

        return wrapper(func)

    def evaluate_answer_quality(self,
                                func: Optional[Callable] = None,
                                *,
                                configuration: Optional[AgenticAIConfiguration] = None,
                                metrics: list[GenAIMetric] = MetricGroup.ANSWER_QUALITY.get_metrics(
                                )
                                ) -> dict:
        """
        An evaluation decorator for computing answer quality metrics on an agentic tool.
        Answer Quality metrics include Answer Relevance, Faithfulness, Answer Similarity, Unsuccessful Requests

        For more details, see :class:`ibm_watsonx_gov.metrics.AnswerRelevanceMetric`, :class:`ibm_watsonx_gov.metrics.FaithfulnessMetric`, 
        :class:`ibm_watsonx_gov.metrics.UnsuccessfulRequestsMetric`, see :class:`ibm_watsonx_gov.metrics.AnswerSimilarityMetric`,

        Args:
            func (Optional[Callable], optional): The tool on which the metric is to be computed.
            configuration (Optional[AgenticAIConfiguration], optional): The configuration specific to this evaluator. Defaults to None.
            metrics (list[GenAIMetric], optional): The list of metrics to compute as part of this evaluator. Defaults to MetricGroup.ANSWER_QUALITY.get_metrics().

        Raises:
            Exception: If there is any error while evaluation.

        Returns:
            dict: The result of the wrapped tool.

        Example:
            1. Basic usage
                .. code-block:: python

                    evaluator = AgenticEvaluation()
                    @evaluator.evaluate_answer_quality
                    def agentic_tool(*args, *kwargs):
                        pass

            2. Usage with different thresholds and methods for some of the metrics in the group
                .. code-block:: python

                    metric_1 = FaithfulnessMetric(threshold=MetricThreshold(type="lower_limit", value=0.5))
                    metric_2 = AnswerRelevanceMetric(method="token_recall", threshold=MetricThreshold(type="lower_limit", value=0.5))

                    evaluator = AgenticEvaluation()
                    @evaluator.evaluate_answer_quality(metrics=[metric_1, metric_2])
                    def agentic_tool(*args, *kwargs):
                        pass
        """

        if func is None:
            return partial(self.evaluate_answer_quality, configuration=configuration, metrics=metrics)

        @decorator
        def wrapper(func, instance, args, kwargs):

            try:
                self.__validate(func=func, metrics=metrics,
                                valid_metric_types=(AnswerRelevanceMetric, FaithfulnessMetric, UnsuccessfulRequestsMetric, AnswerSimilarityMetric))

                metric_inputs = [EvaluatorFields.INPUT_FIELDS,
                                 EvaluatorFields.CONTEXT_FIELDS]
                metric_outputs = [EvaluatorFields.OUTPUT_FIELDS]
                metric_references = [EvaluatorFields.REFERENCE_FIELDS]

                original_result = self.__compute_helper(func=func, args=args, kwargs=kwargs,
                                                        configuration=configuration,
                                                        metrics=metrics,
                                                        metric_inputs=metric_inputs,
                                                        metric_outputs=metric_outputs,
                                                        metric_references=metric_references,
                                                        metric_groups=[MetricGroup.ANSWER_QUALITY])

                return original_result
            except Exception as ex:
                raise Exception(
                    f"There was an error while evaluating answer quality metrics on {func.__name__},") from ex

        return wrapper(func)

    def get_metric_results(self, node_name: Optional[str] = None, metric_name: Optional[str] = None, record_id: Optional[str] = None) -> list[ToolMetricResult]:
        """
        Get the tool metrics results as a list

        Args:
            node_name (Optional[str], optional): Name of the node or tool used to filter the metric results. Defaults to None.
            metric_name (Optional[str], optional): Name of metric used to filter the metric results. Defaults to None.
            record_id (Optional[str], optional): Record id used to filter the metric results. Defaults to None.
        Returns:
            list[ToolMetricResult]: The list of metric results
        """
        metric_results = sorted(self.__metric_results)

        # If node_name and metric_name is not given
        # return the metrics results as it is
        if node_name is None and metric_name is None:
            return metric_results

        # Filter the metric results if node_name or
        # metric_name is provided
        metric_results = [
            r for r in metric_results
            if (node_name is None or r.tool_name == node_name)
            and (metric_name is None or r.name == metric_name)
            and (record_id is None or r.record_id == record_id)
        ]

        return metric_results

    def get_metrics_df(self, input_data: Optional[pd.DataFrame] = None,
                       record_id_field: str = "record_id",  wide_format: bool = True) -> pd.DataFrame:
        """
        Get metrics dataframe.

        If the input dataframe is provided, it will be merged with the metrics dataframe.

        Args:
            input_data (Optional[pd.DataFrame], optional): Input data to merge with metrics dataframe.. Defaults to None.
            record_id_field (str, optional): Field to use for merging input data and metrics dataframe.. Defaults to "record_id".
            wide_format (bool): Determines whether to display the results in a pivot table format. Defaults to True

        Returns:
            pd.DataFrame: Metrics dataframe.
        """

        results = sorted(self.__metric_results)

        def converter(m): return m.model_dump(
            exclude={"provider"}, exclude_none=True)

        metrics_df = pd.DataFrame(list(map(converter, results)))
        if input_data is not None:
            metrics_df = input_data.merge(metrics_df, on=record_id_field)

        # Return the metric result dataframe
        # if the wide_format is False
        if not wide_format:
            return metrics_df

        # Prepare the dataframe for pivot table view
        metrics_df["idx"] = metrics_df.apply(
            lambda row: f"{row['tool_name']}.{row['name']}", axis=1
        )

        # Pivot the table
        metrics_df_wide = metrics_df.pivot_table(
            index="record_id",
            columns="idx",
            values="value"
        ).reset_index().rename_axis("", axis=1)

        # if input_data is provided add
        # it to the pivot table
        if input_data is not None:
            metrics_df_wide = input_data.merge(
                metrics_df_wide, on=record_id_field)
        return metrics_df_wide

    def visualize(self):
        """
        Display the metrics result in a venn diagram based on the metrics threshold.
        """
        model_insights = ModelInsights(
            configuration=self.configuration, metrics=self.__metrics)
        model_insights.display_metrics(
            metrics_result=self.get_model_insights_dataframe(self.get_metric_results()))

    def get_model_insights_dataframe(self, metrics_result: list[ToolMetricResult] = None) -> pd.DataFrame:
        """
        Transform the metrics evaluation result to a dataframe required for visualisation.

        Args:
            data (list): The ToolMetricResult for the evaluation

        Returns:
            pd.DataFrame: new dataframe for the model insights
        """
        if not metrics_result:
            return pd.DataFrame()

        # Filtering the required metric records
        metric_names = {metric.name for metric in self.__metrics}
        filtered_data = [
            obj for obj in metrics_result if obj.name in metric_names]

        # Transforming data into a dictionary structure
        records = [
            {
                "record_id": obj.record_id,
                f"{obj.name}.{obj.method}": obj.value
            }
            for obj in filtered_data
        ]

        # Convert to DataFrame
        df = pd.DataFrame(records)

        # Group by 'record_id' to consolidate multiple metric columns in the same row
        df = df.groupby("record_id").first().reset_index()

        return df
