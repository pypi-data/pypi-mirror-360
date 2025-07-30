import json
import os
import sys
import traceback
from contextvars import ContextVar
from threading import Lock
from typing import Dict, Any, Optional

import requests
from loguru import logger
from loguru._handler import Message

# Context variable to store the current request's logger
_contextual_logger = ContextVar('contextual_logger', default=None)


def is_running_on_cloud() -> bool:
    """Check if running on any Google Cloud Platform service.

    Detects:
    - Cloud Run (K_REVISION)
    - Cloud Functions (FUNCTION_NAME)
    - App Engine (GAE_APPLICATION)
    - Cloud Run Jobs (CLOUD_RUN_JOB)
    - GKE (KUBERNETES_SERVICE_HOST)
    - Compute Engine (metadata server)

    Returns:
        bool: True if running on any GCP service, False otherwise.
    """
    # Check environment variables for different GCP services
    gcp_env_vars = [
        "K_REVISION",  # Cloud Run
        "FUNCTION_NAME",  # Cloud Functions
        "GAE_APPLICATION",  # App Engine
        "CLOUD_RUN_JOB",  # Cloud Run Jobs
        "KUBERNETES_SERVICE_HOST",  # GKE
    ]

    if any(var in os.environ for var in gcp_env_vars):
        return True

    # Check for Compute Engine by trying to access metadata server
    try:
        response = requests.get(
            "http://metadata.google.internal/computeMetadata/v1/instance/id",
            headers={"Metadata-Flavor": "Google"},
            timeout=1,
        )
        return response.status_code == 200
    except Exception:
        return False


def serialize(record: Dict[str, Any]) -> str:
    """Serialize a loguru record to JSON for GCP logging."""
    exception = record.get("exception")
    trace = "".join(traceback.format_exception(*exception)) if exception else None

    # Handle loguru's extra data structure - merge bound data with extra data
    extra_data = dict(record["extra"])
    if "extra" in extra_data:
        # Merge nested extra data from log call
        nested_extra = extra_data.pop("extra")
        if isinstance(nested_extra, dict):
            extra_data.update(nested_extra)

    log_data = {
        "severity": record["level"].name,
        "message": record["message"],
        "elapsed": record["elapsed"].total_seconds(),
        "exception": trace,
        "file": {"name": record["file"].name, "path": record["file"].path},
        "function": record["function"],
        "line": record["line"],
        "module": record["module"],
        "name": record["name"],
        "process": {"id": record["process"].id, "name": record["process"].name},
        "thread": {"id": record["thread"].id, "name": record["thread"].name},
        "time": record["time"].isoformat(),
        "extra": extra_data,
    }
    return json.dumps(log_data)


def gcp_sink(message: Message):
    """Serializes messages into JSON format for GCP logging."""
    log = serialize(message.record)
    print(log, file=sys.stderr)


def local_sink(message: Message):
    if message.record["level"].no < 30:
        print(message, file=sys.stdout)
    else:
        # std err is where logging should print to if > INFO level
        print(message, file=sys.stderr)


# Format string for local logging
def format_record(record):
    """Custom formatter that conditionally includes extra data."""
    base_format = "<g>{time:YYYY-MM-DD HH:mm:ss.SSS}</g> | <level>{level: <8}</level> | <c>{name}</c>:<c>{function}</c>:<c>{line}</c> - <level>{message}</level>"
    
    # Check if there's any extra data (excluding the nested 'extra' key from log calls)
    extra_data = dict(record["extra"])
    if "extra" in extra_data:
        extra_data.update(extra_data.pop("extra"))
    
    if extra_data:
        return base_format + " | <y>{extra}</y>\n"
    else:
        return base_format + "\n"


class GCPLogger:
    _instance = None
    _lock = Lock()
    _configured = False

    def __new__(
        cls,
        level: str = os.getenv("LOG_LEVEL", "DEBUG"),
        backtrace: bool = True,
        diagnose: bool = True,
        colorize: bool = True,
        fmt = format_record,
    ) -> logger:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._configure_logger(level, backtrace, diagnose, colorize, fmt)
        return logger

    @classmethod
    def _configure_logger(
        cls,
        level: str,
        backtrace: bool = True,
        diagnose: bool = True,
        colorize: bool = True,
        fmt = format_record,
    ) -> None:
        """Configure the logger with appropriate handlers."""
        if cls._configured:
            return

        try:
            logger.remove()  # Remove all handlers added so far, including the default one.

            # gcp logging
            if is_running_on_cloud():
                logger.add(gcp_sink, level=level, backtrace=True, catch=True)
            else:
                # standard logging
                logger.add(
                    local_sink,
                    level=level,
                    backtrace=backtrace,
                    diagnose=diagnose,
                    colorize=colorize,
                    format=fmt,
                )
            cls._configured = True
        except Exception:
            # Fallback to basic configuration if setup fails
            logger.add(sys.stderr, level="INFO")
            logger.exception("Failed to configure logger")


def set_contextual_logger(bound_logger) -> None:
    """Set a bound logger for the current request context."""
    _contextual_logger.set(bound_logger)


def clear_contextual_logger() -> None:
    """Clear the contextual logger."""
    _contextual_logger.set(None)


def get_logger():
    """Get a configured logger instance for GCP applications.

    Returns the contextual logger if set, otherwise the base logger.
    """
    contextual = _contextual_logger.get()
    if contextual is not None:
        return contextual
    return GCPLogger()


__all__ = ["get_logger", "GCPLogger", "set_contextual_logger", "clear_contextual_logger"]
