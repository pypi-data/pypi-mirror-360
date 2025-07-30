# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

import os

from .platform_url_mapping import ALLOWED_PLATFORM_URL, PROD_PLATFORM_URL


def get_property_value(property_name, default=None):
    if os.environ.get(property_name):
        return os.environ.get(property_name)
    else:
        return default


def get_platform_url():
    platform_url = get_property_value(property_name="PLATFORM_URL")

    if not platform_url:
        raise Exception(
            "The platform URL cannot be empty. "
            f"Supported platform URLs are: {', '.join(PROD_PLATFORM_URL.keys())}."
        )

    if platform_url not in ALLOWED_PLATFORM_URL:
        raise Exception(
            f"The platform URL '{platform_url}' is invalid or not supported. "
            f"Supported platform URLs are: {', '.join(PROD_PLATFORM_URL.keys())}."
        )

    return platform_url


def get_iam_url():
    platform_url = get_platform_url()
    return ALLOWED_PLATFORM_URL.get(platform_url)


def get_api_key():
    return get_property_value(property_name="WATSONX_APIKEY")
