# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, PositiveInt, field_validator

from ibm_watsonx_gov.entities.credentials import WxGovConsoleCredentials
from ibm_watsonx_gov.entities.foundation_model import FoundationModel


class WxGovConsoleConfiguration(BaseModel):
    model_id: Annotated[
        str,
        Field(
            description="The watsonx Governance Console identifier of the model to store the model risk result."
        ),
    ]
    credentials: Annotated[
        WxGovConsoleCredentials,
        Field(
            description="The watsonx Governance Console credentials."
        ),
    ]
    model_config = ConfigDict(protected_namespaces=())


class ModelRiskConfiguration(BaseModel):
    model_details: Annotated[
        FoundationModel, Field(
            description="The details of the foundation model.")
    ]
    risk_dimensions: Annotated[
        list[str] | None,
        Field(description="The list of risks to be evaluated.", default=None),
    ]
    max_sample_size: Annotated[
        PositiveInt | None,
        Field(description="The maximum sample size used for evaluation.", default=None),
    ]
    wx_gc_configuration: Annotated[
        WxGovConsoleConfiguration | None,
        Field(description="The watsonx Governance Console configuration.", default=None),
    ]
    pdf_report_output_path: Annotated[
        str | None, Field(
            description="The output file path to store the model risk evaluation PDF report.", default=None)
    ]
    thresholds: Annotated[
        tuple[int, int] | None, Field(
            description="A tuple representing the percentile-based threshold configuration used for categorizing LLM performance. The first element is the lower percentile threshold, and the second is the upper percentile threshold", default=(25, 75))
    ]
    model_config = ConfigDict(protected_namespaces=())

    @field_validator("thresholds")
    @classmethod
    def validate_thresholds(cls, v):
        if v is not None:
            low, high = v
            if not (0 <= low < high <= 100):
                raise ValueError(
                    "Thresholds must be between 0 and 100, and the first must be less than the second.")
        return v
