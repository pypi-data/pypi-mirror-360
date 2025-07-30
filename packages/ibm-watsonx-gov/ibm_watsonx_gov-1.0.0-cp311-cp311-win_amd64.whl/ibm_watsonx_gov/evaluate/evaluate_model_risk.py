# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

from deprecated.sphinx import deprecated

from ibm_watsonx_gov.clients.api_client import APIClient
from ibm_watsonx_gov.config import ModelRiskConfiguration
from ibm_watsonx_gov.entities.credentials import Credentials
from ibm_watsonx_gov.evaluate import ModelRiskResult


@deprecated(version="1.0.0")
def evaluate_model_risk(
        configuration: ModelRiskConfiguration,
        credentials: Credentials | None = None,
) -> ModelRiskResult:
    """
    Evaluate the risk of a Foundation model model.

    Parameters:
    - configuration (ModelRiskConfiguration): The configuration for 
    the model risk evaluation engine.
    - credentials (Credentials | None): The credentials for watsonx.governance.
    Returns:
    - ModelRiskResult: The result of the model risk evaluation.
    """
    from .impl.evaluate_model_risk_impl import _evaluate_model_risk

    if credentials:
        api_client = APIClient(credentials)
    else:
        api_client = None
    return _evaluate_model_risk(
        configuration=configuration,
        api_client=api_client,
    )
