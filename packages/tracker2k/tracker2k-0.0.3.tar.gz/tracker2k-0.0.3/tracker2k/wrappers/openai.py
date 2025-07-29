'''
@description openai.py
@author liupoyang
@date 2025-05-09 10:23:47
'''

import sys, os

from agents.tracing.processor_interface import TracingExporter
from agents.tracing.spans import Span
from agents.tracing.traces import Trace
from typing import Any
from agents.tracing.processors import BatchTraceProcessor, BackendSpanExporter
import httpx
import random
import time
import json

import logging
from logging import handlers
import datetime
import threading
import uuid

import socket



class TrackerFormatter(logging.Formatter):

    def __init__(self, fmt, datefmt=None, app_name="noapp", env_name="noenv"):
        super().__init__(fmt, datefmt)
        self.local_ip = self.get_local_ip()
        self.app_name = app_name
        self.env_name = env_name

    def formatTime(self, record, datefmt=None):
        ct = datetime.datetime.fromtimestamp(record.created)
        s = ct.strftime("%Y-%m-%dT%H:%M:%S")
        ms = f"{int(ct.microsecond / 1000):03d}"
        return f"{s}.{ms}"

    def get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
        finally:
            s.close()
        return ip

    def format(self, record):
        record.local_ip = self.local_ip
        record.app_name = self.app_name
        record.env_name = self.env_name
        record.trace_id = get_trace_id()
        record.dltag = get_dltag()
        return super().format(record)


class NoWriteFilter(logging.Filter):
    def filter(self, record):
        return not record.getMessage().startswith('nowrite')


class TrackerLogHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.payload = []
        super().setFormatter(get_logger().get_tracker_formatter())


    def emit(self, record):
        if record.getMessage().startswith('nowrite'):
            log_entry = self.format(record)
            log_entry = log_entry.replace("nowrite:", "", 1)
            self.payload.append( {"log": log_entry})


    def get_payload(self):
        return self.payload

class Logger(object):
    base_dir = '/'
    level_relations = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'crit': logging.CRITICAL
    }

    def __init__(self, log_path, app_name="noapp", env_name="noenv", level='info', when='D', back_count=3,
                 fmt='[%(levelname)s][%(asctime)s][%(filename)s:%(lineno)d] %(dltag)s||traceid=%(trace_id)s||app=%(app_name)s||env=%(env_name)s||pod_ip=%(local_ip)s||_msg=%(message)s'):
        if not os.path.exists(log_path):
            os.makedirs(log_path, exist_ok=True)
        filename = log_path + "default.log"
        self.log_path = log_path
        self.logger = logging.getLogger(filename)
        # format_str = logging.Formatter(fmt, datefmt=datefmt)
        self.app_name = app_name
        self.env_name = env_name
        self.fmt = fmt
        format_str = self.get_tracker_formatter()
        self.logger.setLevel(self.level_relations.get(level))
        # sh = logging.StreamHandler()
        # sh.setFormatter(format_str)
        th = handlers.TimedRotatingFileHandler(filename=filename, when=when, backupCount=back_count, encoding='utf-8')
        th.setFormatter(format_str)
        th.addFilter(NoWriteFilter())
        # self.logger.addHandler(sh)
        self.logger.addHandler(th)


    def get_tracker_formatter(self):
        return TrackerFormatter(fmt=self.fmt, app_name=self.app_name, env_name=self.env_name)



logger_list = list()

def get_logger(log_path="./logs/tracker2k/", app_name="noapp", env_name="noenv"):
    for item in logger_list:
        if item.log_path == log_path:
            return item
    logger_init = Logger(log_path, app_name, env_name)
    logger_list.append(logger_init)
    return logger_init


thread_local = threading.local()

def get_trace_id():
    if not hasattr(thread_local, 'trace_id'):
        thread_local.trace_id = str(uuid.uuid4())
    return thread_local.trace_id

def set_trace_id(trace_id):
    thread_local.trace_id = trace_id

def get_dltag():
    if not hasattr(thread_local, 'dltag'):
        thread_local.dltag = "_undef"
    return thread_local.dltag

def set_dltag(dltag):
    thread_local.dltag = dltag


class TrackerBatchTraceProcessor(BatchTraceProcessor):

    def __init__(
        self,
        exporter: TracingExporter,
        max_queue_size: int = 8192,
        max_batch_size: int = 128,
        schedule_delay: float = 5.0,
        export_trigger_ratio: float = 0.7,
    ) -> None:
        super().__init__(exporter, max_queue_size, max_batch_size, schedule_delay, export_trigger_ratio)


class TrackerBackendSpanExporter(BackendSpanExporter):

    def __init__(
        self,
        api_key: str | None = None,
        organization: str | None = None,
        project: str | None = None,
        endpoint: str = "your data server url",
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 30.0,
    ):
        super().__init__(api_key, organization, project, endpoint, max_retries, base_delay, max_delay)




    def export(self, items: list[Trace | Span[Any]]) -> None:
        if not items:
            return

        _logger = get_logger().logger
        if not self.api_key:
            _logger.debug("API_KEY is not set, skipping trace export")
            # return

        # example
        # [INFO][2025-05-13T17:37:51.120][openai.py:216] _undef||traceid=trace_9d030e991c224732a8c56043e90529d7||app=chuxing-assistant||env=dev||pod_ip=10.84.144.2||_msg={"object": "trace.span", "id": "span_d9f018c386654a98aa1a8d65", "trace_id": "trace_9d030e991c224732a8c56043e90529d7", "parent_id": "span_ed86fcb50f284b61b04f852d", "started_at": "2025-05-13T09:37:46.993053+00:00", "ended_at": "2025-05-13T09:37:46.993707+00:00", "span_data": {"type": "handoff", "from_agent": "llab_agent", "to_agent": "chatbot_agent"}, "error": null}

        tracker_handler = TrackerLogHandler()
        _logger.addHandler(tracker_handler)
        for item in items:
            if item.export():
                set_trace_id(item.trace_id)
                if isinstance(item, Trace):
                    set_dltag("_trace")
                else:
                    set_dltag("_span")

                obj = item.export()
                msg = json.dumps(obj, ensure_ascii=False)

                if "metadata" in obj and obj["metadata"] is not None and len(obj["metadata"]) > 0:
                    for key, value in obj["metadata"].items():
                        msg = f"{msg}||{key}={value}"

                _logger.info("nowrite:" + msg)

        payload = tracker_handler.get_payload()
        set_dltag("_undef")
        _logger.removeHandler(tracker_handler)

        headers = {
            "Content-Type": "application/json",
            "OpenAI-Beta": "traces=v1",
        }

        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        attempt = 0
        delay = self.base_delay
        while True:
            attempt += 1
            try:
                response = self._client.post(url=self.endpoint, headers=headers, json=payload)

                if response.status_code < 300:
                    _logger.debug(f"Exported {len(items)} items")
                    return

                if 400 <= response.status_code < 500:
                    _logger.error(
                        f"[non-fatal] Tracing client error {response.status_code}: {response.text}"
                    )
                    return

                _logger.warning(
                    f"[non-fatal] Tracing: server error {response.status_code}, retrying."
                )
            except httpx.RequestError as exc:
                _logger.warning(f"[non-fatal] Tracing: request failed: {exc}")

            if attempt >= self.max_retries:
                _logger.error("[non-fatal] Tracing: max retries reached, giving up on this batch.")
                return

            sleep_time = delay + random.uniform(0, 0.1 * delay)
            time.sleep(sleep_time)
            delay = min(delay * 2, self.max_delay)

