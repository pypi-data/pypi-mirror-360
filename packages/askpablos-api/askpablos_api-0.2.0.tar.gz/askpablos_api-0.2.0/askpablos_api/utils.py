"""
askpablos_api.utils

Utility functions for the AskPablos API client.

This module provides helper functions for logging configuration.
"""

import logging
from typing import Optional


def configure_logging(
    level: str = "INFO",
    format_string: Optional[str] = None
) -> None:
    """
    Configure logging for the AskPablos API client.

    Args:
        level: Logging level ("DEBUG", "INFO", "WARNING", "ERROR")
        format_string: Custom log format string

    Example:
        >>> from askpablos_api import configure_logging
        >>> configure_logging(level="DEBUG")
    """
    # Convert string level to logging constant
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR
    }

    log_level = level_map.get(level.upper(), logging.INFO)

    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    logging.basicConfig(
        level=log_level,
        format=format_string,
        datefmt="%Y-%m-%d %H:%M:%S"
    )
