"""A module for Bear Utils, providing various utilities and tools."""

from bear_utils.cache import CacheWrapper, cache, cache_factory
from bear_utils.config.settings_manager import SettingsManager, get_settings_manager
from bear_utils.database import DatabaseManager
from bear_utils.events import Events
from bear_utils.extras.responses import FAILURE, SUCCESS, FunctionResponse
from bear_utils.files.file_handlers.file_handler_factory import FileHandlerFactory
from bear_utils.logger_manager import BaseLogger, BufferLogger, ConsoleLogger, FileLogger
from bear_utils.logger_manager._common import VERBOSE_CONSOLE_FORMAT
from bear_utils.logger_manager._styles import VERBOSE
from bear_utils.time import (
    DATE_FORMAT,
    DATE_TIME_FORMAT,
    EpochTimestamp,
    TimeTools,
    convert_to_milliseconds,
    seconds_to_time,
)

__all__ = [
    "DATE_FORMAT",
    "DATE_TIME_FORMAT",
    "FAILURE",
    "SUCCESS",
    "VERBOSE",
    "VERBOSE_CONSOLE_FORMAT",
    "BaseLogger",
    "BufferLogger",
    "CacheWrapper",
    "ConsoleLogger",
    "DatabaseManager",
    "EpochTimestamp",
    "Events",
    "FileHandlerFactory",
    "FileLogger",
    "FunctionResponse",
    "SettingsManager",
    "TimeTools",
    "cache",
    "cache_factory",
    "convert_to_milliseconds",
    "get_settings_manager",
    "seconds_to_time",
]
