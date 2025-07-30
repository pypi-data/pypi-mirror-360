from logging import Logger
from typing import Any

from tp_helper.functions import get_full_class_name


class BaseLoggingService:
    def __init__(self, logger: Logger = None):
        self.logger = logger

    def set_logger(self, logger: Logger):
        self.logger = logger

    def logging_error(self, exception: Any, message: str):
        self.logger.error(message)
        self.logger.error(f"{get_full_class_name(exception)}: {str(exception)}")
