
from loguru import logger
import sys

def configure_logger():
    """
    Configure the logger for structured logging with context support.
    - Includes timestamp, log level, message, and extra context (e.g., correlation ID).
    - Outputs to stderr.
    """
    logger.remove()  # Remove default handler
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | {message} | {extra}",
        level="INFO",
        serialize=False,
        backtrace=True,
        diagnose=True,
    )

def get_logger_with_correlation_id(correlation_id: str):
    """
    Returns a contextualized logger with the given correlation_id.
    Usage:
        logger = get_logger_with_correlation_id("abcd-1234")
        logger.info("Inside processor")
    """
    return logger.contextualize(correlation_id=correlation_id)

# Example usage:
# configure_logger()
# logger = get_logger_with_correlation_id("abcd-1234")
# logger.info("Inside processor")
