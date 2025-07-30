"""A set of command-line interface (CLI) utilities for bear_utils."""

from .commands import GitCommand, MaskShellCommand, OPShellCommand, UVShellCommand
from .shell._base_command import BaseShellCommand
from .shell._base_shell import SimpleShellSession, shell_session
from .shell._common import DEFAULT_SHELL

__all__ = [
    "DEFAULT_SHELL",
    "BaseShellCommand",
    "GitCommand",
    "MaskShellCommand",
    "OPShellCommand",
    "SimpleShellSession",
    "UVShellCommand",
    "shell_session",
]
