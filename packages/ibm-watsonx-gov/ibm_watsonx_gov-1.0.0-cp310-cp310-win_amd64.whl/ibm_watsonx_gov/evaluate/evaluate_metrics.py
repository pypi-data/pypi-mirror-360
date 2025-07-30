# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

from typing import Literal, overload

import pandas as pd
from deprecated.sphinx import deprecated

from ibm_watsonx_gov.clients.api_client import APIClient
from ibm_watsonx_gov.config import AgenticAIConfiguration, GenAIConfiguration
from ibm_watsonx_gov.entities.credentials import Credentials
from ibm_watsonx_gov.entities.evaluation_result import MetricsEvaluationResult
from ibm_watsonx_gov.entities.metric import GenAIMetric
from ibm_watsonx_gov.evaluate import MetricsEvaluationResult


@deprecated(version="1.0.0")
@overload
def evaluate_metrics(
    configuration: GenAIConfiguration,
    data: pd.DataFrame,
    metrics: list[GenAIMetric] = [],
    credentials: Credentials | None = None,
    output_format: Literal["object", "dict", "dataframe"] = "object",
    **kwargs,
) -> MetricsEvaluationResult: ...


@deprecated(version="1.0.0")
@overload
def evaluate_metrics(
    configuration: GenAIConfiguration,
    data: pd.DataFrame | dict,
    credentials: Credentials | None = None,
    output_format: Literal["object", "dict", "dataframe"] = "dict",
    **kwargs,
) -> dict: ...


@deprecated(version="1.0.0")
@overload
def evaluate_metrics(
    configuration: GenAIConfiguration,
    data: pd.DataFrame | dict,
    credentials: Credentials | None = None,
    output_format: Literal["object", "dict", "dataframe"] = "dataframe",
    **kwargs,
) -> pd.DataFrame: ...


@deprecated(version="1.0.0")
@overload
def evaluate_metrics(
    configuration: AgenticAIConfiguration,
    data: dict,
    credentials: Credentials | None = None,
    output_format: Literal["object", "dict", "dataframe"] = "dict",
    **kwargs,
) -> pd.DataFrame: ...


@deprecated(version="1.0.0")
def evaluate_metrics(
    configuration: GenAIConfiguration | AgenticAIConfiguration,
    data: pd.DataFrame | dict,
    metrics: list[GenAIMetric] = [],
    credentials: Credentials | None = None,
    output_format: Literal["object", "dict", "dataframe"] = "object",
    **kwargs,
):
    from .impl.evaluate_metrics_impl import _evaluate_metrics

    if credentials:
        api_client = APIClient(credentials=credentials)
    else:
        api_client = None

    result = _evaluate_metrics(configuration=configuration,
                               data=data,
                               metrics=metrics,
                               api_client=api_client,
                               **kwargs)

    if output_format == "dict":
        return result.to_dict()
    elif output_format == "dataframe":
        return result.to_df()
    else:
        return result
