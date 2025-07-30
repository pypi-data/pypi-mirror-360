# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------
try:
    from ibm_watsonx_gov.entities.evaluation_result import MetricsEvaluationResult
except ImportError:
    MetricsEvaluationResult = None

try:
    from ibm_watsonx_gov.entities.model_risk_result import ModelRiskResult
except ImportError:
    ModelRiskResult = None

try:
    from ibm_watsonx_gov.evaluate.agentic_evaluation import AgenticEvaluation
except ImportError:
    AgenticEvaluation = None

try:
    from ibm_watsonx_gov.evaluate.evaluate_metrics import evaluate_metrics
except ImportError:
    evaluate_metrics = None

try:
    from ibm_watsonx_gov.evaluate.evaluate_model_risk import evaluate_model_risk
except ImportError:
    evaluate_model_risk = None
