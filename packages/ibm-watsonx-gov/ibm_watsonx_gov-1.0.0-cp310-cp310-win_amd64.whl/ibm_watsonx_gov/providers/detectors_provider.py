# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------
import json
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
import requests

from ibm_watsonx_gov.clients.usage_client import validate_usage_client
from ibm_watsonx_gov.config import GenAIConfiguration
from ibm_watsonx_gov.entities.base_classes import Error
from ibm_watsonx_gov.entities.enums import (EvaluationProvider,
                                            GraniteGuardianRisks, MetricGroup)
from ibm_watsonx_gov.entities.evaluation_result import (AggregateMetricResult,
                                                        RecordMetricResult)
from ibm_watsonx_gov.entities.metric_threshold import MetricThreshold


class DetectorsProvider():

    def __init__(
        self,
        configuration: GenAIConfiguration,
        metric_name: str,
        metric_method: str,
        metric_group: MetricGroup = None,
        thresholds: list[MetricThreshold] = [],
        **kwargs,
    ) -> None:
        self.base_url = "{}/ml/v1/text/detection?version=2023-10-25".format(
            self.get_detector_url(kwargs.get("api_client")))
        self.configuration: GenAIConfiguration = configuration
        self.configuration_: dict[str, any] = {}
        self.metric_name = metric_name
        self.metric_method = metric_method
        self.metric_group = metric_group
        self.service_instance_id = self.get_service_instance_id(
            kwargs.get("api_client"))
        self.thresholds = thresholds
        self.detector_params = kwargs.get("detector_params", None)
        validate_usage_client(kwargs.get("usage_client"))

    def evaluate(self, data: pd.DataFrame) -> AggregateMetricResult:
        """
        Entry point method to compute the configured detectors-based metrics.
        Args:
            data: Input test data
        """
        try:
            json_payloads, record_ids = self.__pre_process_data(data=data)
            result = self.__compute_metric(json_payloads)
            aggregated_result = self.__post_process(result, record_ids)
            return aggregated_result

        except Exception as e:
            raise Exception(
                f"Error while computing metrics: {self.metric_name}. Reason: {str(e)}")

    def __pre_process_data(self, data: pd.DataFrame):
        """
        Creates payload for each row in the test data.
        """
        input_content = data[self.configuration.input_fields[0]].to_list()
        payloads_json = self.__get_json_payloads(input_content)
        record_ids = data[self.configuration.record_id_field].to_list()
        return payloads_json, record_ids

    def __compute_metric(self, api_payloads: list):
        """
        Calls the detections API and returns the response.
        """
        responses = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            responses = list(executor.map(self.send_request, api_payloads))
        return responses

    def __post_process(self, results: list, record_ids: list) -> AggregateMetricResult:
        """
        Process the responses and aggregate the results.
        """
        record_level_metrics: list[RecordMetricResult] = []
        values = []
        errors = []
        for result, record_id in zip(results, record_ids):
            record_data = {
                "name": self.metric_name,
                "method": self.metric_method,
                "provider": EvaluationProvider.DETECTORS.value,
                "group": self.metric_group,
                "record_id": record_id,
                "thresholds": self.thresholds,
            }

            if "error" in result:
                record_level_metrics.append(RecordMetricResult(
                    **record_data,
                    value=None,
                    errors=[result["error"]]
                ))
                errors.append(result["error"])
            else:
                value = 0
                if len(result["detections"]) > 0:
                    value = result["detections"][0]["score"]
                record_level_metrics.append(RecordMetricResult(
                    **record_data,
                    value=value
                ))
                values.append(value)

        # creating AggregateMetricResult
        if values:
            mean_val = round(sum(values) / len(values), 4)
            min_val = min(values)
            max_val = max(values)
            value = mean_val
            error_info = {}
        else:
            mean_val = min_val = max_val = None
            value = "Error"
            error_info = {"errors": errors}

        aggregated_result = AggregateMetricResult(
            name=self.metric_name,
            method=self.metric_method,
            group=self.metric_group,
            provider=EvaluationProvider.DETECTORS.value,
            value=value,
            total_records=len(results),
            record_level_metrics=record_level_metrics,
            min=min_val,
            max=max_val,
            mean=mean_val,
            thresholds=self.thresholds,
            **error_info
        )

        # return the aggregated result
        return aggregated_result

    def __get_json_payloads(self, contents: list) -> list:
        # Method to create the request payload.
        json_payloads = []
        for content in contents:
            metric_name = self.set_metric_name(self.metric_name)
            payload_json = {
                "detectors": {
                    metric_name: self.detector_params or {}
                },
                "input": content
            }
            json_payloads.append(json.dumps(payload_json))
        return json_payloads

    def __get_headers(self):
        # Method to create request headers
        headers = {}
        headers["Content-Type"] = "application/json"
        headers["Authorization"] = f"Bearer {self.wos_client.authenticator.token_manager.get_token()}"
        headers["x-governance-instance-id"] = self.service_instance_id
        return headers

    def send_request(self, api_payload):
        response = requests.post(
            url=self.base_url, headers=self.__get_headers(), data=api_payload)
        response_status = response.status_code
        if response_status != 200:
            response = response.text if not isinstance(
                response, str) else response
            return {"error": Error(code=str(response_status),
                                   message_en=str(json.loads(str(response))))}
        else:
            return json.loads(response.text)

    def get_detector_url(self, api_client):
        """
        Sets the wos_client and returns the service url
        """
        from ibm_watsonx_gov.utils.url_mapping import WOS_URL_MAPPING

        self.wos_client = api_client.wos_client
        urls = WOS_URL_MAPPING.get(api_client.credentials.url)
        return urls.wml_url

    def get_service_instance_id(self, api_client):
        """
        Sets the wos_client and returns the service instance id
        """

        self.wos_client = api_client.wos_client
        return self.wos_client.service_instance_id

    def set_metric_name(self, metric_name):
        """
        Sets metric name as 'granite guardian' for Granite Guardian risks
        """
        metric_name = "granite_guardian" if metric_name in GraniteGuardianRisks.values() else metric_name
        return metric_name
