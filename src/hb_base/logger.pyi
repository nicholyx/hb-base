"""Type stubs for hb_base.logger."""

from loguru import Logger


def get_logger(name: str = "hb-base") -> Logger:
    """Get a named logger instance."""
    ...
