"""Logging configuration for DataRush."""

from __future__ import annotations

import logging
import sys
import time
from typing import Any, Optional


def setup_logging(
    level: str = "INFO",
    format_string: Optional[str] = None,
    log_file: Optional[str] = None,
) -> None:
    """Set up logging configuration for DataRush.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_string: Custom format string for log messages
        log_file: Optional file path to write logs to
    """
    # Try to get config if available, otherwise use parameters
    try:
        from datarush.config import get_datarush_config

        config = get_datarush_config()
        logging_config = config.logging

        # Use config values if not explicitly provided
        if level == "INFO" and logging_config.level != "INFO":
            level = logging_config.level
        if log_file is None and logging_config.log_file is not None:
            log_file = logging_config.log_file
        if format_string is None and logging_config.format_string is not None:
            format_string = logging_config.format_string
    except LookupError:
        # Config not set up yet, use parameters as-is
        pass

    # Default format for DataRush
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Clear existing handlers to avoid duplicates
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create handlers
    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]
    if log_file:
        handlers.append(logging.FileHandler(log_file))

    # Determine log level
    try:
        log_level = getattr(logging, level.upper())
    except AttributeError:
        log_level = logging.INFO
        level = "INFO"  # fallback for downstream loggers

    # Set root logger level and handlers
    root_logger.setLevel(log_level)
    for handler in handlers:
        handler.setFormatter(logging.Formatter(format_string))
        root_logger.addHandler(handler)

    # Set specific loggers
    loggers = [
        "datarush.core.dataflow",
        "datarush.core.operations",
        "datarush.core.templates",
        "datarush.run",
        "datarush.utils",
        "datarush.config",
    ]

    for logger_name in loggers:
        logger = logging.getLogger(logger_name)
        try:
            logger.setLevel(getattr(logging, level.upper()))
        except AttributeError:
            logger.setLevel(logging.INFO)


class OperationLogger:
    """Context manager for logging operation execution."""

    def __init__(self, operation_name: str, operation_title: str, logger: logging.Logger) -> None:
        """Initialize operation logger.

        Args:
            operation_name: Name of the operation
            operation_title: Human-readable title of the operation
            logger: Logger instance to use
        """
        self.operation_name = operation_name
        self.operation_title = operation_title
        self.logger = logger
        self.start_time: float | None = None

    def __enter__(self) -> OperationLogger:
        """Log operation start."""
        self.start_time = time.time()
        self.logger.info(f"Starting operation: {self.operation_title} ({self.operation_name})")
        return self

    def __exit__(
        self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: Any
    ) -> None:
        """Log operation completion or failure."""
        if self.start_time:
            duration = time.time() - self.start_time
            if exc_type is None:
                self.logger.info(
                    f"Completed operation: {self.operation_title} ({self.operation_name}) "
                    f"in {duration:.2f}s"
                )
            else:
                self.logger.error(
                    f"Failed operation: {self.operation_title} ({self.operation_name}) "
                    f"after {duration:.2f}s - {exc_type.__name__}: {exc_val}"
                )


class DataflowLogger:
    """Context manager for logging dataflow execution."""

    def __init__(self, template_name: str, template_version: str, logger: logging.Logger) -> None:
        """Initialize dataflow logger.

        Args:
            template_name: Name of the template being executed
            template_version: Version of the template
            logger: Logger instance to use
        """
        self.template_name = template_name
        self.template_version = template_version
        self.logger = logger
        self.start_time: float | None = None

    def __enter__(self) -> DataflowLogger:
        """Log template start."""
        self.start_time = time.time()
        self.logger.info(
            f"Starting template execution: {self.template_name} {self.template_version}"
        )
        return self

    def __exit__(
        self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: Any
    ) -> None:
        """Log template completion or failure."""
        if self.start_time:
            duration = time.time() - self.start_time
            if exc_type is None:
                self.logger.info(
                    f"Completed template execution: {self.template_name} {self.template_version} "
                    f"in {duration:.2f}s"
                )
            else:
                self.logger.error(
                    f"Failed template execution: {self.template_name} {self.template_version} "
                    f"after {duration:.2f}s - {exc_type.__name__}: {exc_val}"
                )
