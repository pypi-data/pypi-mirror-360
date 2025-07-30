import logging
import os
from typing import Optional


def setup_logging(level: Optional[str] = None, log_file: Optional[str] = None) -> None:
    """Configure basic logging for Terraback.

    The log level defaults to ``TERRABACK_LOG_LEVEL`` and logs can be written
    to a file defined by ``TERRABACK_LOG_FILE``.
    """
    level_name = level or os.environ.get("TERRABACK_LOG_LEVEL", "INFO")
    log_level = getattr(logging, level_name.upper(), logging.INFO)

    handlers = [logging.StreamHandler()]
    log_file = log_file or os.environ.get("TERRABACK_LOG_FILE")
    if log_file:
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=handlers,
    )


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the configured settings."""
    return logging.getLogger(name)

