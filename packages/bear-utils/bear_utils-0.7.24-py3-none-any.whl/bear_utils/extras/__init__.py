"""A module for various utilities in Bear Utils extras."""

from singleton_base import SingletonBase

from ._tools import ClipboardManager, clear_clipboard, copy_to_clipboard, fmt_header, paste_from_clipboard
from .platform_utils import OS, get_platform, is_linux, is_macos, is_windows
from .wrappers.add_methods import add_comparison_methods

__all__ = [
    "OS",
    "ClipboardManager",
    "SingletonBase",
    "add_comparison_methods",
    "clear_clipboard",
    "copy_to_clipboard",
    "fmt_header",
    "get_platform",
    "is_linux",
    "is_macos",
    "is_windows",
    "paste_from_clipboard",
]
