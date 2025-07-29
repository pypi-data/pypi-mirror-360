"""A module for Bear Utils, providing various utilities and tools."""

from importlib.metadata import version

from bear_epoch_time import EpochTimestamp, TimeTools

from .cache import CacheWrapper, cache, cache_factory
from .config.settings_manager import SettingsManager, get_settings_manager
from .constants.date_related import DATE_FORMAT, DATE_TIME_FORMAT
from .database import DatabaseManager
from .events import Events
from .files.file_handlers.file_handler_factory import FileHandlerFactory
from .logging.logger_manager._common import VERBOSE_CONSOLE_FORMAT
from .logging.logger_manager._styles import VERBOSE
from .logging.loggers import BaseLogger, BufferLogger, ConsoleLogger, FileLogger

__version__: str = version(distribution_name="bear_utils")

__all__ = [
    "DATE_FORMAT",
    "DATE_TIME_FORMAT",
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
    "SettingsManager",
    "TimeTools",
    "cache",
    "cache_factory",
    "get_settings_manager",
]
