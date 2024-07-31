import logging
from .config import get_logger  # noqa: F401


# include logging levels
CRITICAL = logging.CRITICAL
FATAL = logging.FATAL
ERROR = logging.ERROR
WARNING = logging.WARNING
WARN = logging.WARN
INFO = logging.INFO
DEBUG = logging.DEBUG
NOTSET = logging.NOTSET


# FLAGS: config logger
logger_config = False

logger = get_logger()
