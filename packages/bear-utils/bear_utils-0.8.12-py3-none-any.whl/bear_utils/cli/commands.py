"""Shell Commands Module for Bear Utils."""

from typing import Self

from .shell._base_command import BaseShellCommand


class OPShellCommand(BaseShellCommand):
    """OP command for running 1Password CLI commands"""

    command_name = "op"

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the OPShellCommand with the op command."""
        super().__init__(*args, **kwargs)

    @classmethod
    def read(cls, *args, **kwargs) -> Self:
        """Create a read command for 1Password"""
        return cls.sub("read", *args, **kwargs)


class UVShellCommand(BaseShellCommand):
    """UV command for running Python scripts with uv"""

    command_name = "uv"

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the UVShellCommand with the uv command."""
        super().__init__(*args, **kwargs)

    @classmethod
    def pip(cls, s: str = "", *args, **kwargs) -> Self:
        """Create a piped command for uv"""
        if s:
            return cls.sub(f"pip {s}", *args, **kwargs)
        return cls.sub("pip", *args, **kwargs)


class MaskShellCommand(BaseShellCommand):
    """Mask command for running masked commands"""

    command_name = "mask"

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the MaskShellCommand with the mask command."""
        super().__init__(*args, **kwargs)

    @classmethod
    def maskfile(cls, maskfile: str, *args, **kwargs) -> Self:
        """Create a maskfile command with the specified maskfile"""
        return cls.sub("--maskfile", *args, **kwargs).value(maskfile)

    @classmethod
    def init(cls, *args, **kwargs) -> Self:
        """Create an init command for mask"""
        return cls.sub("init", *args, **kwargs)


class GitCommand(BaseShellCommand):
    """Base class for Git commands"""

    command_name = "git"

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the GitCommand with the git command."""
        super().__init__(*args, **kwargs)

    @classmethod
    def init(cls, *args, **kwargs) -> "GitCommand":
        """Initialize a new Git repository"""
        return cls.sub("init", *args, **kwargs)

    @classmethod
    def status(cls, *args, **kwargs) -> "GitCommand":
        """Get the status of the Git repository"""
        return cls.sub("status", *args, **kwargs)

    @classmethod
    def log(cls, *args, **kwargs) -> "GitCommand":
        """Show the commit logs"""
        return cls.sub("log", *args, **kwargs)

    @classmethod
    def add(cls, files: str, *args, **kwargs) -> "GitCommand":
        """Add files to the staging area"""
        return cls.sub("add", *args, **kwargs).value(files)

    @classmethod
    def diff(cls, *args, **kwargs) -> "GitCommand":
        """Show changes between commits, commit and working tree, etc."""
        return cls.sub("diff", *args, **kwargs)

    @classmethod
    def commit(cls, message: str, *args, **kwargs) -> "GitCommand":
        """Commit changes with a message"""
        return cls.sub("commit -m", *args, **kwargs).value(f"'{message}'")


__all__ = [
    "GitCommand",
    "MaskShellCommand",
    "OPShellCommand",
    "UVShellCommand",
]
