"""Logging utilities for Bear Utils."""

from bear_utils.logger_manager._common import VERBOSE_CONSOLE_FORMAT
from bear_utils.logger_manager._styles import VERBOSE
from bear_utils.logger_manager.loggers._base_logger import BaseLogger
from bear_utils.logger_manager.loggers._buffer_logger import BufferLogger
from bear_utils.logger_manager.loggers._console_logger import ConsoleLogger
from bear_utils.logger_manager.loggers._file_logger import FileLogger
from bear_utils.logger_manager.loggers._sub_logger import SubConsoleLogger

AllLoggers = BaseLogger | ConsoleLogger | SubConsoleLogger
Loggers = BaseLogger | ConsoleLogger


def get_logger(
    console: bool = True,
    file: bool = False,
    queue_handler: bool = False,
    buffering: bool = False,
    **kwargs,
) -> BaseLogger | ConsoleLogger | BufferError | FileLogger:
    """Get a logger instance based on the specified parameters.

    Args:
        name (str): The name of the logger.
        level (int): The logging level.
        console (bool): Whether to enable console logging.
        file (bool): Whether to enable file logging.
        queue_handler (bool): Whether to use a queue handler.
        buffering (bool): Whether to enable buffering.
        style_disabled (bool): Whether to disable styling.
        logger_mode (bool): Whether the logger is in logger mode.
        **kwargs: Additional keyword arguments for customization.

    Returns:
        BaseLogger | ConsoleLogger | BufferLogger| FileLogger: An instance of the appropriate logger.
    """
    if (not console and not file) and buffering:
        return BufferLogger(queue_handler=queue_handler, **kwargs)
    if (console and file) or (console and buffering):
        return ConsoleLogger(queue_handler=queue_handler, buffering=buffering, **kwargs)
    if not console and not buffering and file:
        return FileLogger(queue_handler=queue_handler, **kwargs)
    return BaseLogger(**kwargs)


def get_console(namespace: str) -> tuple[BaseLogger, SubConsoleLogger]:
    """Get a console logger and a sub-logger for a specific namespace.

    Args:
        namespace (str): The namespace for the sub-logger.

    Returns:
        tuple[BaseLogger, SubConsoleLogger]: A tuple containing the base logger and the sub-logger.
    """
    base_logger = BaseLogger.get_instance(init=True)
    sub_logger = SubConsoleLogger(logger=base_logger, namespace=namespace)
    return base_logger, sub_logger


def get_sub_logger(logger: BaseLogger | ConsoleLogger, namespace: str) -> SubConsoleLogger[BaseLogger | ConsoleLogger]:
    """Get a sub-logger for a specific namespace.

    Args:
        logger (BaseLogger): The parent logger.
        namespace (str): The namespace for the sub-logger.

    Returns:
        SubConsoleLogger: A sub-logger instance.
    """
    if not isinstance(logger, (BaseLogger | ConsoleLogger)):
        raise TypeError("Expected logger to be an instance of BaseLogger or ConsoleLogger")

    return SubConsoleLogger(logger=logger, namespace=namespace)


__all__ = [
    "VERBOSE",
    "VERBOSE_CONSOLE_FORMAT",
    "BaseLogger",
    "BufferLogger",
    "ConsoleLogger",
    "FileLogger",
    "SubConsoleLogger",
    "get_console",
    "get_logger",
    "get_sub_logger",
]
