import logging
import os
import sys
from pathlib import Path
from typing import Literal

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


def setup_logger(
    name: str = "qcog",
    level: LogLevel | None = None,
    log_file: str | Path | None = None,
    format_string: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    propagate: bool = True,
) -> logging.Logger:
    """
    Configure and return a logger instance.

    Parameters
    ----------
    name : str, optional
        Name of the logger, by default "qcog"
    level : LogLevel, optional
        Logging level, by default "INFO"
    log_file : Optional[str | Path], optional
        Path to log file. If None, logs only to console, by default None
    format_string : str, optional
        Format string for log messages
    propagate : bool, optional
        Whether to propagate messages to parent loggers, by default True

    Returns
    -------
    logging.Logger
        Configured logger instance
    """
    logger = logging.getLogger(name)

    level = level or os.getenv("QCOG_LOG_LEVEL", "INFO")  # type: ignore

    if level not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
        raise ValueError(f"Invalid log level: {level}")

    # Set the level for both the logger and the root logger to ensure consistency
    log_level = getattr(logging, level)
    logger.setLevel(log_level)

    # If this is the root qcog logger, also set the root logging level
    if name == "qcog":
        logging.getLogger().setLevel(log_level)

    logger.propagate = propagate

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter(format_string)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)  # Set handler level explicitly
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Create file handler if log_file is specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)  # Set handler level explicitly
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(
    module_name: str,
    level: LogLevel | None = None,
) -> logging.Logger:
    """
    Get a module-specific logger that inherits from the root qcog logger.

    Parameters
    ----------
    module_name : str
        Name of the module (typically __name__)
    level : LogLevel | None, optional
        Optional specific level for this module logger.
        If None, inherits from parent logger.

    Returns
    -------
    logging.Logger
        Module-specific logger instance

    Examples
    --------
    >>> # In my_module.py
    >>> logger = get_logger(__name__)
    >>> logger.info("Message")  # Will log as "qcog.my_module - Message"
    """
    if not module_name.startswith("qcog"):
        logger_name = f"qcog.{module_name}"
    else:
        logger_name = module_name

    logger = logging.getLogger(logger_name)
    level = level or os.getenv("QCOG_LOG_LEVEL", "INFO")  # type: ignore

    if level not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
        raise ValueError(f"Invalid log level: {level}")

    logger.setLevel(getattr(logging, level))

    return logger


# Setup root logger with default configuration
root_logger = setup_logger(name="qcog")
