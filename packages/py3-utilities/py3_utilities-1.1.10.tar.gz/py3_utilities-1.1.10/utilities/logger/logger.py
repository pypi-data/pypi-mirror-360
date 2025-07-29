import logging
import os
import threading
import shutil
import tempfile
import contextvars
import queue

from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler, QueueHandler, QueueListener
from colorlog import ColoredFormatter
from pythonjsonlogger import jsonlogger
from typing import Optional, List, Callable
from contextlib import contextmanager


class ContextAwareJsonFormatter(jsonlogger.JsonFormatter):
    """JSON formatter that adds context-specific fields to log records.

    This formatter injects extra fields from a provided `contextvars.ContextVar`
    into each log record.
    """

    def __init__(self, *args, context_var: Optional[contextvars.ContextVar[dict]] = None, **kwargs) -> None:
        """Initialize ContextAwareJsonFormatter.

        Args:
            context_var: Optional ContextVar containing a dict of extra log fields.
        """
        super().__init__(*args, **kwargs)
        self._context_var = context_var

    def add_fields(self, log_record: dict, record: logging.LogRecord, message_dict: dict) -> None:
        """Add base and context-specific fields to the log record.

        Args:
            log_record: The final log record to output.
            record: The original LogRecord instance.
            message_dict: Additional fields from the log message.
        """
        super().add_fields(log_record, record, message_dict)

        if self._context_var:
            context = self._context_var.get()

            for key, value in context.items():
                if key not in log_record:
                    log_record[key] = value


class Logger:
    """Flexible logging wrapper supporting configuration, file/JSON output, daily directories, and cleanup.

    Features:
        - Multiple output types: file, console, JSON
        - Time/size-based log rotation
        - Daily log directories
        - Async queue support
        - Contextual logging
        - Log cleanup/compression utilities
    """

    _lock = threading.Lock()

    _internal_logger = logging.getLogger("LoggerInternal")
    _internal_logger.setLevel(logging.WARNING)
    _internal_console_handler = logging.StreamHandler()
    _internal_console_handler.setFormatter(logging.Formatter(
        fmt="%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%dT%H:%M:%S"
    ))
    _internal_logger.addHandler(_internal_console_handler)

    def __init__(
        self,
        name: str,
        base_log_dir: str = "logs",
        clear_handlers: bool = False,
        file_output: bool = False,
        file_extension: str = "log",
        file_formatter: Optional[logging.Formatter] = None,
        file_log_level: int = logging.INFO,
        file_timestamp_format: Optional[str] = None,
        file_rotation_size_based: bool = False,
        file_rotation_max_bytes: int = 10 * 1024 * 1024,
        file_rotation_time_based: bool = False,
        file_rotation_when: str = "midnight",
        file_rotation_interval: int = 1,
        file_rotation_backup_count: int = 7,
        console_output: bool = False,
        console_formatter: Optional[logging.Formatter] = None,
        console_log_level: int = logging.INFO,
        console_timestamp_format: Optional[str] = None,
        json_output: bool = False,
        json_formatter: Optional[logging.Formatter] = None,
        json_log_level: int = logging.INFO,
        json_timestamp_format: Optional[str] = None,
        json_rotation_size_based: bool = False,
        json_rotation_max_bytes: int = 10 * 1024 * 1024,
        json_rotation_time_based: bool = False,
        json_rotation_when: str = "midnight",
        json_rotation_interval: int = 1,
        json_rotation_backup_count: int = 7,
        async_queue_size: int = -1,
        now_func: Optional[Callable[[], datetime]] = None # For testability
    ) -> None:
        """Initialize a Logger instance with multi-output and rotation support.

        Args:
            name: Name of the logger (used in logger identification and log file naming).
            base_log_dir: Base directory for storing log files.
            clear_handlers: If True, removes all existing handlers from the logger before adding new ones.

            file_output: Enables output to a plain text log file.
            file_extension: Extension of the text log file.
            file_formatter: Optional custom formatter instance for file logs. Overrides default formatting.
            file_log_level: Log level for file output (e.g., logging.INFO, logging.DEBUG).
            file_timestamp_format: Optional datetime format string for timestamps in file log messages.
            file_rotation_size_based: If True, enables size-based file rotation for the plain text log file.
            file_rotation_max_bytes: Maximum file size in bytes before rotating (applies only if size-based rotation is enabled).
            file_rotation_time_based: If True, enables time-based file rotation for the plain text log file.
            file_rotation_when: Specifies the type of time interval for rotation (e.g., 'midnight', 'H', 'D', etc.).
            file_rotation_interval: Number of time units between log rotations (used only with time-based rotation).
            file_rotation_backup_count: Number of rotated log files to keep (applies to both size and time-based rotation).

            console_output: Enables logging output to the console (stdout).
            console_formatter: Optional custom formatter instance for console logs. Overrides default formatting.
            console_log_level: Log level for console output.
            console_timestamp_format: Optional datetime format string for console log messages.

            json_output: Enables output to a JSON-formatted log file.
            json_formatter: Optional custom JSON formatter. Overrides default JSON formatting.
            json_log_level: Log level for JSON output.
            json_timestamp_format: Optional datetime format string for timestamps in JSON log messages.
            json_rotation_size_based: If True, enables size-based rotation for JSON log files.
            json_rotation_max_bytes: Maximum file size in bytes before rotating the JSON log (applies only if size-based rotation is enabled).
            json_rotation_time_based: If True, enables time-based rotation for JSON log files.
            json_rotation_when: Specifies the time interval type for JSON rotation (e.g., 'midnight', 'H', 'D', etc.).
            json_rotation_interval: Number of time units between JSON log rotations.
            json_rotation_backup_count: Number of rotated JSON log files to retain.

            async_queue_size: Queue size for the async message queue.
            now_func: Optional callable returning the current datetime (for testability).

        Raises:
            ValueError: If both size-based and time-based rotation are enabled for the same log type.
        """
        if file_rotation_size_based and file_rotation_time_based:
            raise ValueError("Cannot enable both size-based and time-based rotation for file logs.")

        if json_rotation_size_based and json_rotation_time_based:
            raise ValueError("Cannot enable both size-based and time-based rotation for JSON logs.")

        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        # Async logging
        self._log_queue = queue.Queue(async_queue_size)
        self._original_handlers = []
        self._listener = None

        # Create context variables
        self._context_var = contextvars.ContextVar(f"{name}_log_context", default={})

        self._file_formatter = file_formatter or self._get_file_formatter(file_timestamp_format)
        self._json_formatter = json_formatter or self._get_json_formatter(json_timestamp_format)
        self._console_formatter = console_formatter or self._get_console_formatter(console_timestamp_format) 

        self._now = now_func or datetime.now

        with Logger._lock:
            if self.logger.hasHandlers() and clear_handlers:
                self.logger.handlers.clear()

            now = self._now()

            if file_output or json_output:
                day_folder = now.strftime("%Y-%m-%d")
                log_root = os.path.join(base_log_dir, day_folder)
                os.makedirs(log_root, exist_ok=True)

            if file_output:
                log_path = os.path.join(log_root, f"{name}.{file_extension}")
                if file_rotation_time_based:
                    file_handler = TimedRotatingFileHandler(
                        log_path,
                        when=file_rotation_when,
                        interval=file_rotation_interval,
                        backupCount=file_rotation_backup_count
                    )
                elif file_rotation_size_based:
                    file_handler = RotatingFileHandler(
                        log_path,
                        maxBytes=file_rotation_max_bytes,
                        backupCount=file_rotation_backup_count
                    )
                else:
                    file_handler = logging.FileHandler(log_path)

                file_handler.setLevel(file_log_level)
                file_handler.setFormatter(self._file_formatter)
                self._add_handler_once(file_handler)

            if json_output:
                json_path = os.path.join(log_root, f"{name}.json")
                if json_rotation_time_based:
                    json_handler = TimedRotatingFileHandler(
                        json_path,
                        when=json_rotation_when,
                        interval=json_rotation_interval,
                        backupCount=json_rotation_backup_count
                    )
                elif json_rotation_size_based:
                    json_handler = RotatingFileHandler(
                        json_path,
                        maxBytes=json_rotation_max_bytes,
                        backupCount=json_rotation_backup_count
                    )
                else:
                    json_handler = logging.FileHandler(json_path)

                json_handler.setLevel(json_log_level)
                json_handler.setFormatter(self._json_formatter)
                self._add_handler_once(json_handler)

            if console_output:
                console_handler = logging.StreamHandler()
                console_handler.setLevel(console_log_level)
                console_handler.setFormatter(self._console_formatter)
                self._add_handler_once(console_handler)

    def _add_handler_once(self, handler: logging.Handler) -> None:
        """
        Add a logging handler to the logger if a handler of the same type and destination does not already exist.

        Args:
            handler (logging.Handler): The handler to add.
        """
        for existing in self.logger.handlers:
            # Compare stream handlers
            if isinstance(handler, logging.StreamHandler) and isinstance(existing, logging.StreamHandler):
                if getattr(existing, 'stream', None) == getattr(handler, 'stream', None):
                    return

            # Compare all file-based handlers using filename
            if isinstance(handler, logging.FileHandler) and isinstance(existing, logging.FileHandler):
                if getattr(existing, 'baseFilename', None) == getattr(handler, 'baseFilename', None):
                    return

        self.logger.addHandler(handler)

    def get_logger(self) -> logging.Logger:
        """
        Get the configured logger instance.

        Returns:
            logging.Logger: The logger instance.
        """
        return self.logger

    def add_handler(self, handler: logging.Handler) -> None:
        """
        Attach a custom handler to the logger, preventing duplicates.

        Args:
            handler (logging.Handler): The handler object to attach.
        """
        with Logger._lock:
            self._add_handler_once(handler)

    def get_handler_summary(self) -> List[dict]:
        """
        Get a summary of all handlers attached to the logger.

        Returns:
            List[dict]: A list of dictionaries summarizing each handler.
        """
        return [
            {
                "type": type(h).__name__,
                "level": logging.getLevelName(h.level),
                "formatter": type(h.formatter).__name__ if h.formatter else None,
            }
            for h in self.logger.handlers
        ]

    def enable_async_logging(self):
        """
        Enable asynchronous logging using QueueHandler and QueueListener.

        Preserves and restores original handlers if shutdown is called. Does nothing if async logging is already enabled.
        """
        if self._listener:
            Logger._internal_logger.warning("Async logging already enabled.")
            return

        self._original_handlers = self.logger.handlers[:]
        self.logger.handlers.clear()

        self._log_queue = queue.Queue(-1)
        queue_handler = QueueHandler(self._log_queue)
        self.logger.addHandler(queue_handler)

        self._listener = QueueListener(self._log_queue, *self._original_handlers, respect_handler_level=True)
        self._listener.start()

    def shutdown_async_logging(self):
        """
        Stop the async logging listener and restore original handlers.

        No effect if async logging is not enabled.
        """
        if self._listener:
            self._listener.stop()
            self._listener = None
            self.logger.handlers.clear()

            for handler in self._original_handlers:
                self.logger.addHandler(handler)

            self._original_handlers = []
            self._log_queue = None

    @property
    def async_enabled(self):
        """
        bool: Whether asynchronous logging is currently enabled.
        """
        return self._listener is not None

    @contextmanager
    def context_scope(self, **kwargs):
        """
        Context manager for temporarily setting context variables for logging.

        Args:
            **kwargs: Context variables to set within the scope.
        """
        token = self._context_var.set(kwargs)
        try:
            yield
        finally:
            self._context_var.reset(token)

    def set_context(self, **kwargs):
        """
        Set context variables for JSON logging.

        Args:
            **kwargs: Context variables to set.
        """
        self._context_var.set(kwargs)

    def clear_context(self):
        """
        Clear all context variables for logging.
        """
        self._context_var.set({})

    def _get_file_formatter(self, timestamp_format: Optional[str] = None) -> logging.Formatter:
        """
        Create a standard logging formatter for plain text file output.

        Args:
            timestamp_format (Optional[str]): Format string for timestamps. If not provided, defaults to "%Y-%m-%dT%H:%M:%S".

        Returns:
            logging.Formatter: A configured logging.Formatter instance.
        """
        return logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt=timestamp_format or "%Y-%m-%dT%H:%M:%S"
        )

    def _get_json_formatter(self, timestamp_format: Optional[str] = None) -> ContextAwareJsonFormatter:
        """
        Create a context-aware JSON formatter for structured logging.

        Args:
            timestamp_format (Optional[str]): Format string for timestamps. If not provided, defaults to "%Y-%m-%dT%H:%M:%S".

        Returns:
            ContextAwareJsonFormatter: A configured JSON formatter instance.
        """
        return ContextAwareJsonFormatter(
            fmt='{"timestamp": "%(asctime)s", "name": "%(name)s", "level": "%(levelname)s", "message": "%(message)s"}',
            datefmt=timestamp_format or "%Y-%m-%dT%H:%M:%S",
            context_var=self._context_var
        )

    def _get_console_formatter(self, timestamp_format: Optional[str] = None) -> ColoredFormatter:
        """
        Create a colorized formatter for console output.

        Args:
            timestamp_format (Optional[str]): Format string for timestamps. If not provided, defaults to "%Y-%m-%d %H:%M:%S".

        Returns:
            ColoredFormatter: A configured ColoredFormatter instance with level-specific colors.
        """
        default_fmt = (
            "\033[1m[%(name)s]\033[0m "     # Bracketed name
            "\033[2m%(asctime)s\033[0m "    # Dim timestamp
            "%(log_color)s[%(levelname).3s]%(reset)s → "
            "%(message)s"
        )

        return ColoredFormatter(
            fmt=default_fmt,
            datefmt=timestamp_format or "%Y-%m-%d %H:%M:%S",
            log_colors={
                'DEBUG':    'bold_cyan',
                'INFO':     'bold_green',
                'WARNING':  'bold_yellow',
                'ERROR':    'bold_red',
                'CRITICAL': 'bold_white,bg_red',
            },
            style='%'
        )

    @staticmethod
    def cleanup_old_logs(base_log_dir: str, name: str, days: int = 7, verbose: bool = False) -> bool:
        """
        Delete old log files and their daily folders if all contents are expired.

        Args:
            base_log_dir (str): The root directory for logs.
            name (str): Logger name or '*' to process all loggers.
            days (int, optional): Maximum allowed age in days. Defaults to 7.
            verbose (bool, optional): Print details if True. Defaults to False.

        Returns:
            bool: True if any folders were deleted, False otherwise.
        """
        deleted_any = False
        folders = Logger._get_old_log_folders(base_log_dir, name, days)

        for folder in folders:
            try:
                shutil.rmtree(folder)
                deleted_any = True
                if verbose:
                    Logger._internal_logger.warning(f"{name} - Deleted folder: {folder}")
            except Exception as e:
                Logger._internal_logger.warning(f"{name} - Failed to delete {folder}: {e}")

        return deleted_any

    @staticmethod
    def compress_old_logs(base_log_dir: str, name: str, days: int = 7, archive_name: Optional[str] = None, verbose: bool = False) -> Optional[str]:
        """
        Compress all old log folders into a gzip archive, preserving the full folder structure.

        Args:
            base_log_dir (str): Root folder for logs.
            name (str): Logger name or '*' to process all loggers.
            days (int, optional): Archive logs older than this number of days. Defaults to 7.
            archive_name (Optional[str], optional): Name for the archive file. If None, an automatic name is used.
            verbose (bool, optional): Print progress if True. Defaults to False.

        Returns:
            Optional[str]: Path to the archive file, or None if no folders were archived.
        """
        folders = Logger._get_old_log_folders(base_log_dir, name, days)
        if not folders:
            return None

        archive_name = archive_name or f"archived_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        tmp_dir = tempfile.mkdtemp()

        try:
            for folder in folders:
                rel_path = os.path.relpath(folder, base_log_dir)
                dest_path = os.path.join(tmp_dir, rel_path)
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                shutil.copytree(folder, dest_path)

            archive_path = shutil.make_archive(archive_name, 'gztar', tmp_dir)
            if verbose:
                Logger._internal_logger.warning(f"{name} - Created archive: {archive_path}")
            return archive_path
        except Exception as e:
            Logger._internal_logger.error(f"{name} - Compression failed: {e}")
            return None
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

    @staticmethod
    def _get_old_log_folders(base_log_dir: str, name: str, days: int) -> List[str]:
        """
        Identify folders containing logs older than the specified threshold date.

        Args:
            base_log_dir (str): Root logs directory.
            name (str): Logger name or '*' to process all loggers.
            days (int): Days threshold; folders older than this will be included.

        Returns:
            List[str]: List of folder paths to process.
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        result = []
        logger_dirs = []

        if name == "*":
            logger_dirs = [
                os.path.join(base_log_dir, d) for d in os.listdir(base_log_dir)
                if os.path.isdir(os.path.join(base_log_dir, d))
            ]
        else:
            specific_dir = os.path.join(base_log_dir, name)
            if os.path.isdir(specific_dir):
                logger_dirs = [specific_dir]

        for logger_dir in logger_dirs:
            for day_dir in os.listdir(logger_dir):
                full_path = os.path.join(logger_dir, day_dir)
                try:
                    day_date = datetime.strptime(day_dir, "%Y-%m-%d")
                    if day_date < cutoff_date:
                        result.append(full_path)
                except ValueError:
                    Logger._internal_logger.warning(f"{name} - Skipping invalid date folder: {full_path}")
                    continue

        return result
