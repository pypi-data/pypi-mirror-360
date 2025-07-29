# app > core > logging_config.py
from typing import Optional
import logging
import logging.handlers
from pathlib import Path
from sherlock_ai.config.logging import LoggingConfig
from sherlock_ai.utils import request_id_var

class RequestIdFormatter(logging.Formatter):
    """Custom formatter that includes request ID in log messages"""

    def format(self, record):
        """Add request ID to log message"""
        # get current request ID from context
        record.request_id = request_id_var.get("") or "-"
        return super().format(record)


def setup_logging(config: Optional[LoggingConfig] = None):
    """
    Set up logging configuration with full customization support

    Args:
        config: LoggingConfig object. If None, uses default configuration.
    """
    if config is None:
        config = LoggingConfig()

    # Create logs directory if it doesn't exist
    # logs_dir = Path("logs")
    logs_dir = Path(config.logs_dir)
    logs_dir.mkdir(exist_ok=True)

    # Configure logging format
    # log_format = "%(asctime)s - %(request_id)s - %(name)s - %(levelname)s - %(message)s"
    # date_format = "%Y-%m-%d %H:%M:%S"

    # Create custom formatter with request ID support
    formatter = RequestIdFormatter(config.log_format, datefmt=config.date_format)

    # Clear existing handlers to avoid duplicates
    logging.root.handlers.clear()

    # Clear handlers from all existing loggers
    for logger_name in list(logging.Logger.manager.loggerDict.keys()):
        logger = logging.getLogger(logger_name)
        if hasattr(logger, 'handlers'):
            logger.handlers.clear()

    # 1. Console Handler - prints to terminal
    if config.console_enabled:
        console_handler = logging.StreamHandler()
        # console_handler.setLevel(logging.INFO)
        console_handler.setLevel(config.console_level)
        console_handler.setFormatter(formatter)
        logging.root.addHandler(console_handler)

    # Create file handlers
    file_handlers = {}
    for name, file_config in config.log_files.items():
        if file_config.enabled:
            handler = logging.handlers.RotatingFileHandler(
                file_config.filename,
                maxBytes=file_config.max_bytes,
                backupCount=file_config.backup_count,
                encoding=file_config.encoding
            )
            handler.setLevel(file_config.level)
            handler.setFormatter(formatter)
            file_handlers[name] = handler

    # Configure root logger
    logging.root.setLevel(config.root_level)

    # Add main app and error handlers to root by default
    if "app" in file_handlers:
        logging.root.addHandler(file_handlers["app"])
    if "errors" in file_handlers:
        logging.root.addHandler(file_handlers["errors"])
    
    # Configure specific loggers
    for name, logger_config in config.loggers.items():
        if logger_config.enabled:
            logger = logging.getLogger(logger_config.name)
            logger.setLevel(logger_config.level)
            logger.propagate = logger_config.propagate

            # Add specified file handlers to this logger
            for file_name in logger_config.log_files:
                if file_name in file_handlers:
                    logger.addHandler(file_handlers[file_name])
    
    # Configure external library loggers
    for logger_name, level in config.external_loggers.items():
        logging.getLogger(logger_name).setLevel(level)

# Helper function to get logger (optional, but clean)
def get_logger(name: str = None):
    """Get a logger. If no name provided, uses the caller's __name__."""
    return logging.getLogger(name) if name else logging.getLogger(__name__)
