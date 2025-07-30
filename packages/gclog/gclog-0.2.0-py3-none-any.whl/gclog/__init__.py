# GCLog package
from .gclog import (
    get_logger, 
    GCPLogger,
    is_running_on_cloud,
    serialize,
    gcp_sink,
    local_sink,
    set_contextual_logger,
    clear_contextual_logger,
)

__version__ = "0.1.1"
__all__ = ["get_logger", "GCPLogger", "set_contextual_logger", "clear_contextual_logger"]