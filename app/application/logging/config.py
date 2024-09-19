import logging
from .logger import CustomRootLogger
from .formatters import ColorFormatter
from os import environ


DEFAULT_LOGGING_LEVEL: str = 'DEBUG'
LOGGING_FORMATTER = "{levelname}: {message}"


LOGGING_LEVEL: int = logging._nameToLevel.get(
    environ.get('LOGGING_LEVEL', DEFAULT_LOGGING_LEVEL))


def get_logger() -> logging.StreamHandler:
    # create custom root logger
    logging.root = CustomRootLogger(LOGGING_LEVEL)
    # apply custom config and formatter
    formatter = ColorFormatter(LOGGING_FORMATTER, style="{")
    handler = logging.StreamHandler()
    handler.setLevel(LOGGING_LEVEL)
    handler.setFormatter(formatter)
    # get logger and config
    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(LOGGING_LEVEL)
    return logger
