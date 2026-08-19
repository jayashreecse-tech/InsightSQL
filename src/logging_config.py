from __future__ import annotations

import logging
import os


_LOGGER_NAME = "insightsql"


def configure_logging() -> logging.Logger:
    """Configure one redacted, process-wide application logger."""
    logger = logging.getLogger(_LOGGER_NAME)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
        logger.addHandler(handler)
    logger.setLevel(os.getenv("INSIGHTSQL_LOG_LEVEL", "INFO").upper())
    logger.propagate = False
    return logger


def get_logger() -> logging.Logger:
    return logging.getLogger(_LOGGER_NAME)
