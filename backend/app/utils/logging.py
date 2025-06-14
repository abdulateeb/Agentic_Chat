"""
Logging configuration for the Agentic SRE backend.
Provides structured logging for easy parsing and analysis in production environments.
"""

import logging
import sys

from pythonjsonlogger import jsonlogger

from app.core.config import Settings


def setup_logging(settings: Settings) -> None:
    """Configure the root logger for the application."""

    log_level = settings.LOG_LEVEL.upper()

    # Create a custom JSON formatter
    formatter = jsonlogger.JsonFormatter("%(asctime)s %(name)s %(levelname)s %(message)s")

    # Get the root logger and remove existing handlers
    logger = logging.getLogger()

    # Avoid adding duplicate handlers if this function is called multiple times
    if logger.hasHandlers():
        logger.handlers.clear()

    # Create a handler to stream logs to standard output
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    # Add the handler to the root logger
    logger.addHandler(handler)
    logger.setLevel(log_level)

    # Suppress noisy loggers from common libraries
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    logger.info("Logging configured with level: %s", log_level)


def get_logger(name: str) -> logging.Logger:
    """Retrieve a logger instance with the specified name."""

    return logging.getLogger(name)
