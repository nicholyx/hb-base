"""Logging utilities using loguru."""

import sys

from loguru import logger

logger.remove()
logger.add(sys.stderr, level="DEBUG", format="{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {name}:{function}:{line} - {message}")


def get_logger(name: str = "hb-base"):
    """Get a named logger instance."""
    return logger.bind(name=name)
