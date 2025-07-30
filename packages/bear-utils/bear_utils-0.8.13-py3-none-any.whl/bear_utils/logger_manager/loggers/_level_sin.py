"""This is some terrible sinning that should not exist, don't look at it. It doesn't exist if you don't look at it."""

from logging import addLevelName
import threading
from typing import Literal

ERROR: Literal[40] = 40
WARNING: Literal[30] = 30
WARN: Literal[30] = WARNING
INFO: Literal[20] = 20
DEBUG: Literal[10] = 10
NOTSET: Literal[0] = 0

level_to_name = {
    ERROR: "ERROR",
    WARNING: "WARNING",
    INFO: "INFO",
    DEBUG: "DEBUG",
    NOTSET: "NOTSET",
}

name_to_level = {
    "ERROR": ERROR,
    "WARN": WARNING,
    "WARNING": WARNING,
    "INFO": INFO,
    "DEBUG": DEBUG,
    "NOTSET": NOTSET,
}

_lock = threading.RLock()


def lvl_exists(level: int | str) -> bool:
    """Check if a logging level already exists."""
    with _lock:
        level = check_level(level, fail=False)
        return level in level_to_name


def add_level_name(level: int, name: str) -> None:
    """Add a custom logging level name."""
    with _lock:
        if level in level_to_name:
            raise ValueError(f"Level {level} already exists with name {level_to_name[level]}")
        level_to_name[level] = name.upper()
        name_to_level[name.upper()] = level
        addLevelName(level=level, levelName=name)


def check_level(level: int | str | None, fail: bool = True) -> int:
    """Validate and normalize logging level to integer."""
    if isinstance(level, str) and level.upper() in name_to_level:
        return name_to_level[level.upper()]
    if isinstance(level, int) and level in level_to_name:
        return level
    if fail:
        if not isinstance(level, (int | str)):
            raise TypeError(f"Level must be int or str, got {type(level).__name__}: {level!r}")
        raise ValueError(f"Invalid logging level: {level!r}. Valid levels are: {list(name_to_level.keys())}")
    return 999  # Return a high value to indicate invalid level
