# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

import os
from typing import Annotated

from pydantic import BaseModel, Field

from ibm_watsonx_gov.utils.python_utils import get_environment_variable_value
from ibm_watsonx_gov.utils.url_mapping import WOS_URL_MAPPING


class Credentials(BaseModel):
    api_key: Annotated[str, Field(title="Api Key",
                                  description="The user api key.",
                                  strip_whitespace=True)]
    url: Annotated[str, Field(title="watsonx.governance url",
                              description="The watsonx.governance url. By default the url for dallas region is used.",
                              default="https://api.aiopenscale.cloud.ibm.com")]
    service_instance_id:  Annotated[str | None, Field(title="Service instance id",
                                                      description="The watsonx.governance service instance id.",
                                                      default=None)]
    username: Annotated[str | None, Field(title="User name",
                                          description="The user name.",
                                          default=None)]
    version: Annotated[str | None, Field(title="Version",
                                         description="The watsonx.governance version.",
                                         default=None)]
    disable_ssl: Annotated[bool, Field(title="Disable ssl",
                                       description="The flag to disable ssl.",
                                       default=False)]
    dai_url: Annotated[str, Field(title="watsonx.ai platform url",
                                  description="The watsonx.ai platform url. Defaults to None. This is required for users without a valid watsonx.governance instance.",
                                  default=None)]

    @classmethod
    def create_from_env(cls):
        # possible API key environment variable names
        api_key = get_environment_variable_value(
            ["WXG_API_KEY", "WATSONX_APIKEY"])

        if not api_key:
            raise ValueError("Missing API key environment variable")

        username = get_environment_variable_value(
            ["WXG_USERNAME", "WATSONX_USERNAME"])

        version = get_environment_variable_value(
            ["WXG_VERSION", "WATSONX_VERSION"])

        return Credentials(
            api_key=api_key,
            url=os.getenv("WXG_URL", "https://api.aiopenscale.cloud.ibm.com"),
            service_instance_id=os.getenv("WXG_SERVICE_INSTANCE_ID"),
            username=username,
            version=version,
            disable_ssl=os.getenv("WXG_DISABLE_SSL", False)
        )


class WxAICredentials(BaseModel):
    """
    Defines the WxAICredentials class to specify the watsonx.ai server details.

    Examples:
        1. Create WxAICredentials with default parameters. By default Dallas region is used.
            .. code-block:: python

                wxai_credentials = WxAICredentials(api_key="...")

        2. Create WxAICredentials by specifying region url.
            .. code-block:: python

                wxai_credentials = WxAICredentials(api_key="...",
                                                   url="https://au-syd.ml.cloud.ibm.com")

        3. Create WxAICredentials by reading from environment variables.
            .. code-block:: python

                os.environ["WATSONX_APIKEY"] = "..."
                # [Optional] Specify watsonx region specific url. Default is https://us-south.ml.cloud.ibm.com .
                os.environ["WATSONX_URL"] = "https://eu-gb.ml.cloud.ibm.com"
                wxai_credentials = WxAICredentials.create_from_env()
    """
    url: Annotated[str, Field(
        title="watsonx.ai url",
        description="The url for watsonx ai service",
        default="https://us-south.ml.cloud.ibm.com",
        examples=[
            "https://us-south.ml.cloud.ibm.com",
            "https://eu-de.ml.cloud.ibm.com",
            "https://eu-gb.ml.cloud.ibm.com",
            "https://jp-tok.ml.cloud.ibm.com",
            "https://au-syd.ml.cloud.ibm.com",
        ]
    )]
    api_key: Annotated[str, Field(title="Api Key",
                                  description="The user api key.",
                                  strip_whitespace=True)]
    version: Annotated[str | None, Field(title="Version",
                                         description="The watsonx.ai version.",
                                         default=None)]
    username: Annotated[str | None, Field(title="User name",
                                          description="The user name.",
                                          default=None)]

    @classmethod
    def create_from_env(cls):
        # possible API key environment variable names
        api_key = get_environment_variable_value(
            ["WXAI_API_KEY", "WATSONX_APIKEY", "WXG_API_KEY"])

        if not api_key:
            raise ValueError("Missing API key environment variable")

        username = get_environment_variable_value(
            ["WXAI_USERNAME", "WATSONX_USERNAME", "WXG_USERNAME"])

        version = get_environment_variable_value(
            ["WXAI_VERSION", "WATSONX_VERSION", "WXG_VERSION"])

        url = get_environment_variable_value(
            ["WXAI_URL", "WATSONX_URL"])

        # Check the url & update it
        if url in WOS_URL_MAPPING.keys():
            url = WOS_URL_MAPPING.get(url).wml_url

        # If the url environment variable is not found, use the default
        if not url:
            url = "https://us-south.ml.cloud.ibm.com"

        credentials = {
            "url": url,
            "api_key": api_key,
            "version": version,
            "username": username,
        }

        return WxAICredentials(
            **credentials
        )


class WxGovConsoleCredentials(BaseModel):
    url: str
    username: str
    password: str
    api_key: str | None = None

    @classmethod
    def create_from_env(cls):
        return WxGovConsoleCredentials(
            url=os.getenv("WXGC_URL"),
            username=os.getenv("WXGC_USERNAME"),
            password=os.getenv("WXGC_PASSWORD"),
            api_key=os.getenv("WXGC_API_KEY"),
        )


class RITSCredentials(BaseModel):
    hostname: Annotated[
        str | None,
        Field(description="The rits hostname",
              default="https://inference-3scale-apicast-production.apps.rits.fmaas.res.ibm.com"),
    ]
    api_key: str

    @classmethod
    def create_from_env(cls):
        api_key = os.getenv("RITS_API_KEY")
        rits_host = os.getenv(
            "RITS_HOST", "https://inference-3scale-apicast-production.apps.rits.fmaas.res.ibm.com")

        return RITSCredentials(
            hostname=rits_host,
            api_key=api_key,
        )


class OpenAICredentials(BaseModel):
    """
    Defines the OpenAICredentials class to specify the OpenAI server details.

    Examples:
        1. Create OpenAICredentials with default parameters. By default Dallas region is used.
            .. code-block:: python

                openai_credentials = OpenAICredentials(api_key=api_key,
                                                       url=openai_url)

        2. Create OpenAICredentials by reading from environment variables.
            .. code-block:: python

                os.environ["OPENAI_API_KEY"] = "..."
                os.environ["OPENAI_URL"] = "..."
                openai_credentials = OpenAICredentials.create_from_env()
    """
    url: str | None
    api_key: str | None

    @classmethod
    def create_from_env(cls):
        return OpenAICredentials(
            url=os.getenv("OPENAI_URL"),
            api_key=os.getenv("OPENAI_API_KEY"),
        )


class AzureOpenAICredentials(BaseModel):
    url: Annotated[str | None, Field(
        description="Azure OpenAI url. This attribute can be read from `AZURE_OPENAI_HOST` environment variable.",
        serialization_alias="azure_openai_host")]
    api_key: Annotated[str | None, Field(
        description="API key for Azure OpenAI. This attribute can be read from `AZURE_OPENAI_API_KEY` environment variable.")]
    api_version: Annotated[str | None, Field(
        description="The model API version from Azure OpenAI. This attribute can be read from `AZURE_OPENAI_API_VERSION` environment variable.")]

    @classmethod
    def create_from_env(cls):
        return AzureOpenAICredentials(
            url=os.getenv("AZURE_OPENAI_HOST"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        )
