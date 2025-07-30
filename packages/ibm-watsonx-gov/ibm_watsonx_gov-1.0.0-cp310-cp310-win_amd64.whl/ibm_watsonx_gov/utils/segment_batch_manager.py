# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

import asyncio
import os

from ibm_watsonx_gov.clients.segment_client import SegmentClient
from ibm_watsonx_gov.tools.utils.constants import (
    SEGMENT_AUTO_TRIGGER_INTERVAL, SEGMENT_BATCH_LIMIT)
from ibm_watsonx_gov.utils.gov_sdk_logger import GovSDKLogger

logger = GovSDKLogger.get_logger(__name__)


class Singleton(type):
    """
    Define an Instance operation that lets clients access its unique
    instance.
    """

    def __init__(cls, name, bases, attrs, **kwargs):
        super().__init__(name, bases, attrs)
        cls._instance = None

    def __call__(cls, *args, **kwargs):
        """
        Called when the instance is “called” as a function
        """
        if cls._instance is None:
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance


class SegmentBatchManager(metaclass=Singleton):

    shared_list = []
    lock = asyncio.Lock()
    auto_trigger = False

    async def add_segment_event(self, api_client, data):
        if os.getenv("WATSONX_SERVER") in ["WXO", "WXAI"]:
            return
        if not self.auto_trigger:
            asyncio.create_task(self.auto_trigger_function(api_client))
            self.auto_trigger = True
        async with self.lock:
            self.shared_list.append(data)
            if len(self.shared_list) >= SEGMENT_BATCH_LIMIT:
                await self.send_segment_events(api_client)

    async def send_segment_events(self, api_client):
        batch_data = self.shared_list[:]
        self.shared_list.clear()
        try:
            segment_client = SegmentClient(api_client)
            segment_client.trigger_segment_endpoint(batch_data)
        except Exception as e:
            logger.error("Failed to send segment events.")

    async def auto_trigger_function(self, api_client):
        while True:
            await asyncio.sleep(SEGMENT_AUTO_TRIGGER_INTERVAL)
            if self.shared_list:
                await self.send_segment_events(api_client)

    async def add_event_to_shared_list(self, wos_client, properties):
        data = {
            "event": "API Call",
            "properties": properties,
            "integrations": {
                "Amplitude": {
                    "groups": {
                        "Instance": wos_client.service_instance_id
                    }
                }
            }
        }
        await self.add_segment_event(wos_client, data)
