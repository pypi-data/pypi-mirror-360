"""Module for logging functionality."""

import sys
import pathlib

import loguru


LOG_LEVEL: str = "DEBUG"

LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green>"
    " | <level>{level: <4}</level>"
    " | <cyan>Line {line: >4} ({file}):</cyan> <b>{message}</b>"
)


def add_file_sink(file: pathlib.Path) -> None:
    """Adds a file sink to the logger."""
    loguru.logger.add(
        file,
        level=LOG_LEVEL,
        format=LOG_FORMAT,
        colorize=False,
        backtrace=True,
        diagnose=True,
    )


def _initialize() -> None:
    """Initializes the logger."""

    # Clear default logger
    loguru.logger.remove()

    # Add custom sinks
    loguru.logger.add(
        sys.stderr,
        level=LOG_LEVEL,
        format=LOG_FORMAT,
        colorize=True,
        backtrace=True,
        diagnose=True,
    )

    return loguru.logger


logger = _initialize()
global_logger = logger
