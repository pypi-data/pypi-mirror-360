from .wrappers.openai import TrackerBatchTraceProcessor, TrackerBackendSpanExporter, get_logger
from typing import Optional
from agents.tracing import add_trace_processor, set_trace_processors


def init(
    app_name: Optional[str] = None,
    env_name: Optional[str] = None,
    endpoint: Optional[str] = None,
    **kwargs,
):
    if app_name != "" and env_name != "":
        get_logger(app_name=app_name, env_name=env_name)
    elif app_name != "":
        get_logger(app_name=app_name)
    elif env_name != "":
        get_logger(env_name=env_name)
    else:
        get_logger()

    _exporter = TrackerBackendSpanExporter(endpoint=endpoint)
    _processor = TrackerBatchTraceProcessor(_exporter)
    set_trace_processors([_processor])
    # add_trace_processor(_processor)