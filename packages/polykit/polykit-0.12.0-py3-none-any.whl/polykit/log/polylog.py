"""Classes for setting up and formatting loggers.

PolyLog and related classes provide methods for setting up a logger with a console handler,
defining console color codes for use in the formatter to colorize messages by log level, and more.
"""

from __future__ import annotations

import contextlib
import functools
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypeVar

from polykit.core.singleton import Singleton
from polykit.log.formatters import CustomFormatter, FileFormatter
from polykit.log.types import LogLevel

if TYPE_CHECKING:
    from collections.abc import Callable

    from polykit.env.polyenv import PolyEnv

T = TypeVar("T")


class PolyLog(metaclass=Singleton):
    """A powerful, colorful logger for Python applications. The logical choice for Python logging.

    PolyLog provides easy configuration of Python's standard logging with sensible defaults and
    features like automatic context detection, color-coded output, and datetime formatting.

    Usage:
        from polykit.log import PolyLog

        # Basic usage with automatic name detection
        logger = PolyLog.get_logger()
        logger.info("Application started.")

        # With explicit name and options
        logger = PolyLog.get_logger("MyComponent", level="DEBUG", show_context=True)

        # With datetime formatting
        from datetime import datetime
        time_logger = PolyLog.get_logger(time_aware=True)
        time_logger.info("Event occurred at %s", datetime.now())  # Formats datetime nicely
    """

    @classmethod
    def get_logger(
        cls,
        logger_name: str | None = None,
        level: int | str = "INFO",
        simple: bool = False,
        show_context: bool = False,
        color: bool = True,
        log_file: Path | None = None,
        time_aware: bool = False,
        env: PolyEnv | None = None,
    ) -> logging.Logger:
        """Get a configured logger instance.

        Args:
            logger_name: The name of the logger. If None, automatically determined from the calling
                         class, module, or file name.
            level: The log level as string ("DEBUG", "INFO", etc.) or a logging constant.
                   Defaults to "INFO".
            simple: If True, use a simplified format that shows only the message. Defaults to False.
            show_context: If True, include the function/method name in log messages.
                          Defaults to False.
            color: If True, use color-coded output based on log level. Defaults to True.
            log_file: Optional path to a log file. If provided, logs will be written to this file in
                      addition to the console. Defaults to None, which means no file logging.
            time_aware: If True, returns a TimeAwareLogger that automatically formats datetime
                        objects in log messages. Defaults to False.
            env: An optional PolyEnv instance. Useful for easily parsing log level, but additional
                 environment-specific functionality may be added in future. Defaults to None.

        Returns:
            A configured standard Logger or TimeAwareLogger instance.
        """
        logger_name = PolyLog._get_logger_name(logger_name)
        logger = logging.getLogger(logger_name)

        if not logger.handlers:
            log_level = env.log_level if env is not None else LogLevel.get_level(level)
            logger.setLevel(log_level)

            log_formatter = CustomFormatter(simple=simple, color=color, show_context=show_context)

            console_handler = logging.StreamHandler()
            console_handler.setFormatter(log_formatter)
            console_handler.setLevel(log_level)
            logger.addHandler(console_handler)

            if log_file:
                PolyLog._add_file_handler(logger, log_file)

            logger.propagate = False

        if time_aware:
            from polykit.log.time_aware import TimeAwareLogger

            return TimeAwareLogger(logger)

        return logger

    @staticmethod
    def _get_logger_name(logger_name: str | None = None) -> str:
        """Generate a logger identifier based on the provided parameters and calling context."""
        if logger_name is not None:
            return logger_name

        import inspect

        # Try to get the calling frame
        frame = inspect.currentframe()
        if frame is not None:
            frame = frame.f_back  # get_logger's frame
            if frame is not None:
                frame = frame.f_back  # get_logger's caller's frame

        # If we have a valid frame, try to identify it
        if frame is not None:
            # Try to get class name first
            if "self" in frame.f_locals:
                return frame.f_locals["self"].__class__.__name__
            if "cls" in frame.f_locals:
                return frame.f_locals["cls"].__name__

            # Get the module name if we can't get the class name
            module = inspect.getmodule(frame)
            if module is not None and hasattr(module, "__name__"):
                return module.__name__.split(".")[-1]

            # Get the filename if we can't get the module name
            filename = frame.f_code.co_filename
            if filename:
                base_filename = Path(filename).name
                return Path(base_filename).stem

        # If we really can't find our place in the universe
        return "unknown"

    @staticmethod
    def _add_file_handler(logger: logging.Logger, log_file: Path) -> None:
        """Add a file handler to the given logger."""
        formatter = FileFormatter()
        log_dir = Path(log_file).parent

        if not log_dir.exists():
            log_dir.mkdir(parents=True, exist_ok=True)

        if not log_file.is_file():
            log_file.touch()

        file_handler = RotatingFileHandler(log_file, maxBytes=512 * 1024)
        file_handler.setFormatter(formatter)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)

    @classmethod
    def exception(
        cls,
        logger: logging.Logger | str | None = None,
        exc_info: bool = True,
        message: str = "An exception occurred:",
        level: str = "error",
    ) -> None:
        """Log an exception with full traceback information.

        Args:
            logger: Logger object or logger name to use. If None, creates a new logger.
            exc_info: Exception info to log. True uses current exception from sys.exc_info().
            message: Custom message to log with the exception.
            level: Log level to use.
        """
        if logger is None:
            # Create a default logger if none provided
            logger = PolyLog.get_logger()
        elif isinstance(logger, str):
            logger = PolyLog.get_logger(logger_name=logger)

        log_level = LogLevel.get_level(level)

        # Log at the appropriate level with exception info
        if log_level >= logging.ERROR:
            logger.error(message, exc_info=exc_info)
        elif log_level >= logging.WARNING:
            logger.warning(message, exc_info=exc_info)
        elif log_level >= logging.INFO:
            logger.info(message, exc_info=exc_info)
        else:
            logger.debug(message, exc_info=exc_info)

    @classmethod
    @contextlib.contextmanager
    def catch(
        cls,
        logger: logging.Logger | str | None = None,
        message: str = "An exception occurred:",
        level: str = "error",
        reraise: bool = True,
    ):
        """Context manager to catch and log exceptions.

        Args:
            logger: Logger object or logger name to use. If None, creates a new logger.
            message: Custom message to log with the exception.
            level: Log level to use.
            reraise: Whether to re-raise the exception after logging.

        Example:
            ```python
            with PolyLog.catch(logger, "Error processing data"):
                # code that might raise an exception
            ```
        """
        try:
            yield
        except Exception as e:
            cls.exception(logger, True, f"{message} {e!s}", level)
            if reraise:
                raise

    @classmethod
    def decorate(
        cls,
        logger: logging.Logger | str | None = None,
        message: str = "Exception in {func_name}:",
        level: str = "error",
        reraise: bool = True,
    ) -> Callable[[Callable[..., T]], Callable[..., T]]:
        """Decorator to log exceptions raised in functions.

        Args:
            logger: Logger object or logger name to use.
            message: Message template to use ({func_name} will be replaced).
            level: Log level to use.
            reraise: Whether to re-raise the exception after logging.

        Example:
            ```python
            @PolyLog.decorate(logger, "Error in data processing")
            def process_data():
                # code that might raise an exception
            ```
        """

        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            @functools.wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                formatted_message = message.format(func_name=func.__name__)
                with cls.catch(logger, formatted_message, level, reraise):
                    return func(*args, **kwargs)

            return wrapper

        return decorator


class LogLevelOverride:
    """Temporarily override the log level of a logger.

    This context manager allows you to change the log level of a logger for the duration of a
    context. It can be useful for debugging or temporarily silencing log messages.

    Example:
        ```python
        with LogLevelOverride(logger, logging.ERROR):
            logger.info("This will not be logged.")
            logger.error("This will be logged.")
        ```
    """

    def __init__(self, logger: logging.Logger, new_level: int | str):
        self.logger = logger
        self.new_level = LogLevel.get_level(new_level)
        self.original_level = logger.getEffectiveLevel()

    def __enter__(self) -> None:
        """Set the new log level."""
        if self.new_level != self.original_level:
            self.logger.setLevel(self.new_level)
            setattr(self.logger, "temporary_override", True)

    def __exit__(self, exc_type: Exception, exc_val: Exception, exc_tb: Exception) -> None:
        """Revert to the original log level."""
        if self.new_level != self.original_level:
            setattr(self.logger, "temporary_override", False)
