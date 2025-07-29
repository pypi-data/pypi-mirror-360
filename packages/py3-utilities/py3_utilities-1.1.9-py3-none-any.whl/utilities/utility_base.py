import logging

from abc import ABC
from typing import Optional, Union

from .logger import Logger, LogWrapper


class UtilityBase(ABC):
    """Base class for the utility types."""

    def __init__(
            self, 
            verbose: bool = False,
            logger: Optional[Union[logging.Logger, Logger, LogWrapper]] = None,
            log_level: Optional[int] = None
        ):
        """Initialize the UtilityBase.

        Args:
            verbose (bool): If True, logs will be provided with the configured level.
            logger (Logger): Optional logger instance. If not provided, a default logger is used.
            log_level (int): Optional log level. If not provided, INFO level will be used for logging.
        """
        self.verbose = verbose
        self.log_level = log_level or logging.INFO

        if logger is None:
            self.logger = logging.getLogger("null")
            if not self.logger.handlers:
                self.logger.addHandler(logging.NullHandler())
        else:
            if isinstance(logger, Logger) or isinstance(logger, LogWrapper):
                self.logger = logger.get_logger()
            else:
                self.logger = logger

    def _log(self, message: str) -> None:
        """Log a message using the provided or null logger.

        Args:
            message (str): The message to log.
        """
        if self.verbose:
            self.logger.log(self.log_level, message)

    def _log_debug(self, message: str) -> None:
        """
        Log a debug message.

        Args:
            message (str): The message to log.
        """
        if self.verbose:
            self.logger.debug(message)

    def _log_info(self, message: str) -> None:
        """
        Log an info message.

        Args:
            message (str): The message to log.
        """
        if self.verbose:
            self.logger.info(message)

    def _log_warning(self, message: str) -> None:
        """
        Log a warning message.

        Args:
            message (str): The message to log.
        """
        if self.verbose:
            self.logger.warning(message)

    def _log_error(self, message: str) -> None:
        """
        Log an error message.

        Args:
            message (str): The message to log.
        """
        self.logger.error(message)

    def _log_critical(self, message: str) -> None:
        """
        Log a critical message.

        Args:
            message (str): The message to log.
        """
        self.logger.critical(message)

    def _log_exception(self, message: str) -> None:
        """
        Log a critical message with stack trace.

        Args:
            message (str): The message to log.
        """
        self.logger.critical(message, exc_info=True)
