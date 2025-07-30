# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------


import json
import os
import threading
from concurrent.futures import ThreadPoolExecutor

try:
    from google.protobuf.json_format import MessageToDict
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import \
        OTLPSpanExporter as HTTPSpanExporter
    from opentelemetry.proto.trace.v1.trace_pb2 import TracesData
    from opentelemetry.sdk.trace.export import SpanExportResult
except:
    pass


from pathlib import Path
from typing import Optional


class WxGovSpanExporter(HTTPSpanExporter):
    def __init__(
        self,
        enable_local_traces: Optional[bool] = False,
        enable_server_traces: Optional[bool] = False,
        file_name: Optional[str] = None,
        storage_path: Optional[str] = None,
        max_workers: int = 2,
        *args, **kwargs
    ):
        """
        Initialize a HTTPSpan exporter which additionally store traces to a local log file

        Args:
            enable_local_traces: For storing traces locally
            enable_server_traces: For forwarding traces to tracing service
            file_name: Base name for the trace file (without extension)
            storage_path: Directory to store trace files
            *args, **kwargs: default inputs of HTTPSpanExporter
        """
        super().__init__(*args, **kwargs)
        self.enable_local_traces = enable_local_traces
        self.enable_server_traces = enable_server_traces
        self.storage_path = Path(storage_path)
        self.file_path = self.storage_path / f"{file_name}.log"
        self._lock = threading.Lock()
        self._executor = ThreadPoolExecutor(max_workers=max_workers)

        # Ensure storage directory exists
        if enable_local_traces:
            self.storage_path.mkdir(parents=True, exist_ok=True)
            self._initialize_trace_file()

    def _initialize_trace_file(self) -> None:
        """Initialize the trace file with file"""
        with self._lock, self.file_path.open("w") as f:
            pass

    def _store_locally(self, spans: bytes) -> None:
        """Append spans to the trace file in a thread-safe manner."""
        try:
            traces = TracesData.FromString(spans)
            traces_dict = MessageToDict(traces)
            with self._lock, self.file_path.open("a") as f:
                json.dump(traces_dict, f)
                f.write("\n")
        except Exception as e:
            return SpanExportResult.FAILURE

    def export(self, spans) -> SpanExportResult:
        if self._shutdown:
            return SpanExportResult.FAILURE

        serialized_data = self._serialize_spans(spans)

        if self.enable_server_traces and os.getenv(
                "WATSONX_TRACING_ENABLED", "true").lower() == "true":
            self._export_serialized_spans(serialized_data)
        if self.enable_local_traces:
            self._store_locally(serialized_data)
