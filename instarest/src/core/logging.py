
from pydantic import BaseModel
from .config import get_core_settings
import logging
from logging.config import dictConfig

class LogConfig(BaseModel):
    """Logging configuration to be set for the server"""

    LOGGER_NAME: str = "base_logger"
    LOG_FORMAT: str = "%(levelprefix)s | %(asctime)s | %(message)s"
    LOG_LEVEL: str = get_core_settings().log_level

    # Logging config
    version = 1
    disable_existing_loggers = False
    formatters = {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": LOG_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    }
    handlers = {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
    }
    loggers = {
        "base_logger": {"handlers": ["default"], "level": LOG_LEVEL},
    }

    def build_logger(self) -> logging.Logger:
        dictConfig(self.dict())
        logger = logging.getLogger(self.LOGGER_NAME)
        logger.addFilter(SuppressSpecificLogItemFilter(filter_string="this_should_be_filtered_out"))
        return logger


# Define a filter to exclude logs with a specific string
class SuppressSpecificLogItemFilter(logging.Filter):
    def __init__(self, filter_string=""):
        super().__init__()
        self.filter_string = filter_string

    def filter(self, record):
        return self.filter_string not in record.getMessage()