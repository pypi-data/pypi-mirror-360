from typing import NotRequired, Required, TypedDict

from rich.theme import Theme

from bear_utils.logger_manager._log_level import (
    DEBUG,
    ERROR,
    FAILURE,
    INFO,
    SUCCESS,
    VERBOSE,
    WARNING,
)


class LoggerExtraInfo(TypedDict):
    """Type definition for extra info that can be added to log records."""

    style_name: Required[str]
    style: Required[str]
    namespace: NotRequired[str]
    log_level: Required[int]
    log_level_style: Required[str]


LOGGER_METHODS: dict[str, LoggerExtraInfo] = {
    "info": {
        "style_name": "info",
        "style": "dim green",
        "log_level": INFO,
        "log_level_style": "black on white",
    },
    "debug": {
        "style_name": "debug",
        "style": "bold blue",
        "log_level": DEBUG,
        "log_level_style": "black on blue",
    },
    "warning": {
        "style_name": "warning",
        "style": "bold yellow",
        "log_level": WARNING,
        "log_level_style": "yellow on black",
    },
    "error": {
        "style_name": "error",
        "style": "bold red",
        "log_level": ERROR,
        "log_level_style": "bold white on red",
    },
    "exception": {
        "style_name": "exception",
        "style": "bold red",
        "log_level": ERROR,
        "log_level_style": "bold white on red",
    },
    "success": {
        "style_name": "success",
        "style": "bold green",
        "log_level": SUCCESS,
        "log_level_style": "black on bright_green",
    },
    "failure": {
        "style_name": "failure",
        "style": "bold red underline",
        "log_level": FAILURE,
        "log_level_style": "bold red on white",
    },
    "verbose": {
        "style_name": "verbose",
        "style": "bold blue",
        "log_level": VERBOSE,
        "log_level_style": "black on bright_blue",
    },
}


def get_method(name: str) -> LoggerExtraInfo:
    """Get the name info from the logger methods.

    Args:
        name (str): The name of the logger method.

    Returns:
        LoggerExtraInfo | dict: The info of the logger method or an empty dict if not found.
    """
    if not LOGGER_METHODS.get(name):
        raise ValueError(f"Logger method '{name}' does not exist. Available methods: {list(LOGGER_METHODS.keys())}")
    return LOGGER_METHODS[name]


DEFAULT_STYLES: dict[str, str] = {**{method: info["style"] for method, info in LOGGER_METHODS.items()}}
"""Just the styles of the logger methods, used to create the theme."""

DEFAULT_THEME = Theme(styles=DEFAULT_STYLES)
