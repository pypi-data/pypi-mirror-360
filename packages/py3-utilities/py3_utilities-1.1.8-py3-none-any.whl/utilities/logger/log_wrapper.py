from typing import Callable
from .log_decorator import LogDecorator
from .logger import Logger

class LogWrapper:
    def __init__(self, decorator: LogDecorator, logger: Logger):
        """
        Wraps both the logger and its associated decorator.

        Args:
            decorator (LogDecorator): LoggingDecorator instance for decorating functions.
            logger (Logger): Actual Python logger instance for logging messages directly.
        """
        self._decorator = decorator
        self._logger = logger

    def __call__(self, func: Callable):
        """
        Enables using this object as a decorator.

        Args:
            func (Callable): The function to wrap.

        Returns:
            Callable: Decorated function.
        """
        return self._decorator(func)

    def __getattr__(self, name: str):
        """
        Delegates attribute access to the underlying Logger or the logging.Logger instance
        based on the attribute name.

        For example: log.logger.info(...), log.logger.warning(...)

        Args:
            name (str): Attribute or method name.

        Returns:
            Any: Logger method or property.
        """
        if any(keyword in name for keyword in ("context", "async", "get_logger")):
            return getattr(self._logger, name)
        else:
            return getattr(self._logger.get_logger(), name)
