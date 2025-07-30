# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------
import json
from typing import Any, List

from pydantic import BaseModel, create_model

from ibm_watsonx_gov.tools.utils import environment
from ibm_watsonx_gov.tools.utils.python_utils import (get_bss_account_id,
                                                      process_result)
from ibm_watsonx_gov.utils.authenticator import Authenticator
from ibm_watsonx_gov.utils.rest_util import RestUtil

TOOL_REGISTRY = {
    "chromadb_retrieval_tool": "ibm_watsonx_gov.tools.ootb.vectordb.chromadb_retriever_tool.ChromaDBRetrievalTool",
    "duckduckgo_search_tool": "ibm_watsonx_gov.tools.ootb.search.duckduckgo_search_tool.DuckDuckGoSearchTool",
    "google_search_tool": "ibm_watsonx_gov.tools.ootb.search.google_search_tool.GoogleSearchTool",
    "weather_tool": "ibm_watsonx_gov.tools.ootb.search.weather_tool.WeatherTool",
    "webcrawler_tool": "ibm_watsonx_gov.tools.ootb.search.web_crawler_tool.WebCrawlerTool",
    "wikipedia_search_tool": "ibm_watsonx_gov.tools.ootb.search.wikipedia_search_tool.WikiPediaSearchTool"
}


def get_pydantic_model(name: str, schema: dict) -> type[BaseModel]:
    """Method to provide a pydantic model with the given schema

    Args:
        name (str): Name of the schema
        schema (dict): schema json

    Returns:
        type[BaseModel]: Pydantic model 
    """
    type_mapping = {
        "string": str,
        "number": float,
        "integer": int,
        "boolean": bool,
        "object": dict,
        "array": list,
        "float": float,
        "dict": dict
    }

    def build_fields(properties, required_fields):
        fields = {}
        for key, val in properties.items():
            typ = val.get("type")
            if typ == "object":
                nested_model = get_pydantic_model(
                    f"{name}_{key.capitalize()}", val)
                fields[key] = (nested_model, ...)
            elif typ == "array":
                item_schema = val.get("items")
                if item_schema["type"] == "object":
                    nested_model = get_pydantic_model(
                        f"{name}_{key.capitalize()}Item", item_schema)
                    fields[key] = (List[nested_model], ...)
                else:
                    item_type = type_mapping[item_schema["type"]]
                    fields[key] = (List[item_type], ...)
            else:
                py_type = type_mapping.get(typ, Any)
                default = ... if key in required_fields else val.get("default")
                fields[key] = (py_type, default)
        return fields

    props = schema.get("properties", {})
    required = schema.get("required", [])
    fields = build_fields(props, required)
    return create_model(name, **fields)


def list_ootb_tools():
    """Helper method to get the list of tools 
       TODO: Replace this method with REST API endpoint
    """
    import pandas as pd
    tools = list(TOOL_REGISTRY.keys())
    df = pd.DataFrame(tools, columns=["tool_name"])
    return df


def get_default_inventory():
    """Method to get the default inventory
      TODO: Need to revisit to cover CPD case
    """
    token = get_token()
    bss_account_id = get_bss_account_id(token)
    base_url = environment.get_platform_url()
    get_default_inventory_url = f"{base_url}/v1/aigov/inventories/default_inventory?bss_account_id={bss_account_id}"
    headers = get_headers(token=token)
    response = RestUtil.request_with_retry(retry_count=3).get(
        url=get_default_inventory_url, headers=headers)
    try:
        response = process_result(response)
        return response["metadata"]["guid"]
    except Exception as e:
        raise Exception("Error while getting default inventory_id: " + str(e))


# Generating user token
def get_token(api_key=None, iam_url=None):
    """Method to generate token based on apikey and iam_url
       TODO: Need to revisit to cover CPD case
    """
    # TODO: Need to enhanced to be able to work with CPD
    api_key = api_key if api_key else environment.get_api_key()
    iam_url = iam_url if iam_url else environment.get_iam_url()
    missing_vars = []
    if not api_key:
        missing_vars.append("WATSONX_APIKEY")
    if not iam_url:
        missing_vars.append("IAM_URL")
    if len(missing_vars) > 0:
        raise Exception(f"Unable to generate token because of the missing details . Details of missing envs: {missing_vars}")
    credentials = {
        "iam_url": iam_url,
        "apikey": api_key
    }
    token = Authenticator(credentials=credentials,
                          use_cpd=False, use_ssl=False).authenticate()
    return token


# Generating header
def get_headers(token: str = None):
    if token is None:
        token = get_token()
    return {
        "Content-Type": "application/json",
        "accept": "application/json",
        "Authorization": f"Bearer {token}"
    }
