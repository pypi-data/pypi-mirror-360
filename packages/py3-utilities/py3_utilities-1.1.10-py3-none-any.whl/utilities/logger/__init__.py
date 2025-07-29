import logging
from types import SimpleNamespace
from typing import Optional, Any
from .logger import Logger
from .log_decorator import LogDecorator
from .log_wrapper import LogWrapper

# Expose public classes/interfaces
__all__ = [
    "Logger", 
    "LogDecorator", 
    "LogWrapper", 
    "log"
]

# Object to hold logger access: log.app, etc.
log = type("LoggerRegistry", (), {})()

# Load config
try: 
    from ..config import parse_config
    _config = parse_config()
except (ImportError, ModuleNotFoundError):
    _config = None

def flatten_loggers(config_section: SimpleNamespace, prefix: Optional[str] = None):
    """
    Recursively flattens a nested SimpleNamespace logger configuration into a flat dictionary.

    Parameters
    ----------
    config_section : SimpleNamespace
        The logger configuration section to flatten.
    prefix : str, optional
        The prefix to prepend to each logger name.

    Returns
    -------
    dict
        A flat dictionary mapping full logger names to their configuration objects.
    """
    flat = {}
    for key, val in config_section.__dict__.items():
        full_key = f"{prefix}.{key}" if prefix else key

        if hasattr(val, "__dict__"):
            flat.update(flatten_loggers(val, full_key))
        else:
            flat[prefix] = config_section
            break

    return flat

def set_nested_attr(obj: SimpleNamespace, path: str, value: Any):
    """
    Sets a value on a nested attribute path within a SimpleNamespace object, creating intermediate namespaces as needed.

    Parameters
    ----------
    obj : SimpleNamespace
        The root object to set the attribute on.
    path : str
        Dot-separated path specifying the nested attribute to set.
    value : Any
        The value to set at the specified attribute path.

    Returns
    -------
    None
    """
    parts = path.split(".")
    current = obj

    for part in parts[:-1]:
        if not hasattr(current, part):
            setattr(current, part, SimpleNamespace())
        current = getattr(current, part)

    setattr(current, parts[-1], value)

# Make sure logging section exists and is structured properly
if hasattr(_config, "logging"):
    logging_config = _config.logging

    # --- Global ---
    root_folder = getattr(logging_config, "root_folder", "logs")
    cleanup_old_logs = getattr(logging_config, "cleanup_old_logs", False)
    cleanup_days = getattr(logging_config, "cleanup_days", 7)

     # Clean-up old logs
    if cleanup_old_logs:
        Logger.cleanup_old_logs(
            base_log_dir=root_folder,
            name="*",
            days=cleanup_days,
            verbose=False
        )

    if hasattr(logging_config, "loggers"):
        loggers_list = flatten_loggers(logging_config.loggers)

        for logger_name, cfg in loggers_list.items():
            enabled = getattr(cfg, "enabled", False)

            # Create loggers

            clear_handlers = getattr(cfg, "clear_handlers", False)
            
            # --- Console ---
            console_output = getattr(cfg, "console_output", True)
            console_log_level_str = getattr(cfg, "console_log_level", "DEBUG").upper()
            console_log_level = getattr(logging, console_log_level_str, logging.INFO)
            console_timestamp_format = getattr(cfg, "console_timestamp_format", None)

            # --- File ---
            file_output = getattr(cfg, "file_output", False)
            file_log_level_str = getattr(cfg, "file_log_level", "INFO").upper()
            file_log_level = getattr(logging, file_log_level_str, logging.INFO)
            file_rotation_time_based = getattr(cfg, "file_rotation_time", True)
            file_rotation_when = getattr(cfg, "file_rotation_when", "midnight")
            file_rotation_interval = getattr(cfg, "file_rotation_interval", 1)
            file_rotation_backup_count = getattr(cfg, "file_rotation_backup_count", 7)
            file_timestamp_format = getattr(cfg, "file_timestamp_format", None)

            # --- JSON ---
            json_output = getattr(cfg, "json_output", False)
            json_log_level_str = getattr(cfg, "json_log_level", "INFO").upper()
            json_log_level = getattr(logging, json_log_level_str, logging.INFO)
            json_rotation_time_based = getattr(cfg, "json_rotation_time", True)
            json_rotation_when = getattr(cfg, "json_rotation_when", "midnight")
            json_rotation_interval = getattr(cfg, "json_rotation_interval", 1)
            json_rotation_backup_count = getattr(cfg, "json_rotation_backup_count", 7)
            json_timestamp_format = getattr(cfg, "json_timestamp_format", None)

            # --- Decorator ---
            decorator_sensitive_params = getattr(cfg, "decorator_sensitive_params", [])
            decorator_raise_exception = getattr(cfg, "decorator_raise_exception", False)
            decorator_log_level_str = getattr(cfg, "decorator_log_level", "DEBUG").upper()
            decorator_log_level = getattr(logging, decorator_log_level_str, logging.INFO)
            decorator_max_log_length = getattr(cfg, "decorator_max_log_length", 500)
            decorator_log_arguments = getattr(cfg, "decorator_log_arguments", False)
            decorator_tag = getattr(cfg, "decorator_tag", "decorator")
            decorator_warn_duration = getattr(cfg, "decorator_warn_duration", None)
            decorator_log_stack = getattr(cfg, "decorator_log_stack", False)
            decorator_log_return_value = getattr(cfg, "decorator_log_return_value", False)
            decorator_log_execution_time = getattr(cfg, "decorator_log_execution_time", False)

            if not enabled:
                file_output = False
                json_output = False
                console_output = False
                clear_handlers = False

            # Init logger
            logger = Logger(
                name=logger_name,
                base_log_dir=root_folder,
                clear_handlers=clear_handlers,

                # Console
                console_output=console_output,
                console_log_level=console_log_level,
                console_timestamp_format=console_timestamp_format,

                # File
                file_output=file_output,
                file_log_level=file_log_level,
                file_rotation_time_based=file_rotation_time_based,
                file_rotation_when=file_rotation_when,
                file_rotation_interval=file_rotation_interval,
                file_rotation_backup_count=file_rotation_backup_count,
                file_timestamp_format=file_timestamp_format,

                # JSON
                json_output=json_output,
                json_log_level=json_log_level,
                json_rotation_time_based=json_rotation_time_based,
                json_rotation_when=json_rotation_when,
                json_rotation_interval=json_rotation_interval,
                json_rotation_backup_count=json_rotation_backup_count,
                json_timestamp_format=json_timestamp_format,
            )

            # Create the decorator
            decorator = LogDecorator(
                logger=logger.get_logger(),
                raise_exception=decorator_raise_exception,
                log_level=decorator_log_level,
                max_log_length=decorator_max_log_length,
                sensitive_params=decorator_sensitive_params,
                default_return=None,
                log_arguments=decorator_log_arguments,
                tag=decorator_tag,
                warn_duration=decorator_warn_duration,
                log_stack=decorator_log_stack,
                log_return=decorator_log_return_value,
                log_execution_time=decorator_log_execution_time
            )

            # Wrap and expose logger + decorator together
            wrapper = LogWrapper(decorator=decorator, logger=logger)
            set_nested_attr(log, logger_name, wrapper)
