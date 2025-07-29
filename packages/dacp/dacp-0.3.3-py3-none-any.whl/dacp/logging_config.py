"""
DACP Logging Configuration

Utilities for configuring logging for DACP components.
"""

import logging
import sys
from typing import Optional


def setup_dacp_logging(
    level: str = "INFO",
    format_style: str = "detailed",
    include_timestamp: bool = True,
    log_file: Optional[str] = None,
) -> None:
    """
    Set up logging for DACP components.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_style: Log format style ('simple', 'detailed', 'emoji')
        include_timestamp: Whether to include timestamps in logs
        log_file: Optional file path to also log to a file
    """
    # Define format styles
    if format_style == "simple":
        if include_timestamp:
            log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        else:
            log_format = "%(name)s - %(levelname)s - %(message)s"
    elif format_style == "detailed":
        if include_timestamp:
            log_format = (
                "%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s"
            )
        else:
            log_format = "%(name)s:%(lineno)d - %(levelname)s - %(message)s"
    elif format_style == "emoji":
        # Emoji format doesn't include logger name since emojis provide context
        if include_timestamp:
            log_format = "%(asctime)s - %(message)s"
        else:
            log_format = "%(message)s"
    else:
        raise ValueError(f"Unknown format_style: {format_style}")

    # Configure root logger for DACP components
    logger = logging.getLogger("dacp")
    logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create formatter
    formatter = logging.Formatter(
        log_format, datefmt="%Y-%m-%d %H:%M:%S" if include_timestamp else None
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Optional file handler
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Prevent propagation to root logger to avoid duplicate messages
    logger.propagate = False

    logger.info(f"🚀 DACP logging configured: level={level}, style={format_style}")


def set_dacp_log_level(level: str) -> None:
    """
    Set the log level for all DACP components.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    logger = logging.getLogger("dacp")
    logger.setLevel(getattr(logging, level.upper()))
    logger.info(f"📊 DACP log level changed to {level}")


def disable_dacp_logging() -> None:
    """Disable all DACP logging."""
    logger = logging.getLogger("dacp")
    logger.disabled = True


def enable_dacp_logging() -> None:
    """Re-enable DACP logging."""
    logger = logging.getLogger("dacp")
    logger.disabled = False


def get_dacp_logger(name: str) -> logging.Logger:
    """
    Get a logger for a DACP component.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Configured logger
    """
    return logging.getLogger(f"dacp.{name}")


# Convenience functions for quick setup
def enable_debug_logging(log_file: Optional[str] = None) -> None:
    """Enable debug logging with detailed format."""
    setup_dacp_logging(level="DEBUG", format_style="detailed", log_file=log_file)


def enable_info_logging(log_file: Optional[str] = None) -> None:
    """Enable info logging with emoji format."""
    setup_dacp_logging(level="INFO", format_style="emoji", log_file=log_file)


def enable_quiet_logging() -> None:
    """Enable only error and critical logging."""
    setup_dacp_logging(level="ERROR", format_style="simple", include_timestamp=False)
