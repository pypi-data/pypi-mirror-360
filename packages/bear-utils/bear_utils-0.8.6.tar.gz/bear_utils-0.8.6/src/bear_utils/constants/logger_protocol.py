"""A protocol for logging classes for general use."""

from typing import Protocol, runtime_checkable


@runtime_checkable
class LoggerProtocol(Protocol):
    """A protocol for logging classes."""

    def debug(self, msg: object, *args, **kwargs) -> None:
        """Log a debug message."""
        ...

    def info(self, msg: object, *args, **kwargs) -> None:
        """Log an info message."""
        ...

    def warning(self, msg: object, *args, **kwargs) -> None:
        """Log a warning message."""
        ...

    def error(self, msg: object, *args, **kwargs) -> None:
        """Log an error message."""
        ...

    def verbose(self, msg: object, *args, **kwargs) -> None:
        """Log a verbose message."""
        ...
