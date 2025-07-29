"""
Sherlock AI - Your AI assistant package
"""

__version__ = "1.2.0"
# __author__ = "Pranaw Mishra"
# __email__ = "pranawmishra73@gmail.com"

# Import main components for easy access
from .performance import log_performance, PerformanceTimer
from .logging_setup import setup_logging, get_logger
from .config import LoggingConfig, LoggingPresets, LogFileConfig, LoggerConfig
from .utils import set_request_id, get_request_id, clear_request_id
from .monitoring import (
    monitor_memory,
    monitor_resources,
    MemoryTracker,
    ResourceTracker,
    ResourceMonitor,
)

# ✅ Logger name constants 
class LoggerNames:
    """Available logger names for use with get_logger()"""
    API = "ApiLogger"
    DATABASE = "DatabaseLogger"
    SERVICES = "ServiceLogger"
    PERFORMANCE = "PerformanceLogger"
    MONITORING = "MonitoringLogger"

# ✅ Convenience function
def list_available_loggers():
    """Get list of all available logger names"""
    return [
        LoggerNames.API,
        LoggerNames.DATABASE,
        LoggerNames.SERVICES,
        LoggerNames.PERFORMANCE,
        LoggerNames.MONITORING
    ]

__all__ = [
    # Performance Logging
    "log_performance", 
    "PerformanceTimer",

    # Memory and Resource Monitoring
    "monitor_memory",
    "monitor_resources",
    "MemoryTracker",
    "ResourceTracker",
    "ResourceMonitor",

    # Logging Configuration
    "setup_logging",
    "get_logger",
    "LoggingConfig",
    "LoggingPresets",
    "LogFileConfig",
    "LoggerConfig",

    # Request ID
    "set_request_id",
    "get_request_id",
    "clear_request_id",
    
    # Logger utilities
    "LoggerNames",
    "list_available_loggers",

    # Package info
    "__version__",
]