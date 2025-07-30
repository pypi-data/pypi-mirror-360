"""A module for Bear Utils, providing various utilities and tools."""

from bear_epoch_time import EpochTimestamp, TimeTools

from bear_utils.cache import CacheWrapper, cache, cache_factory
from bear_utils.config.settings_manager import SettingsManager, get_settings_manager
from bear_utils.constants.date_related import DATE_FORMAT, DATE_TIME_FORMAT
from bear_utils.database import DatabaseManager
from bear_utils.events import Events
from bear_utils.extras.responses import FAILURE, SUCCESS, FunctionResponse
from bear_utils.files.file_handlers.file_handler_factory import FileHandlerFactory
from bear_utils.logger_manager import BaseLogger, BufferLogger, ConsoleLogger, FileLogger
from bear_utils.logger_manager._common import VERBOSE_CONSOLE_FORMAT
from bear_utils.logger_manager._styles import VERBOSE

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
    "get_settings_manager",
]
