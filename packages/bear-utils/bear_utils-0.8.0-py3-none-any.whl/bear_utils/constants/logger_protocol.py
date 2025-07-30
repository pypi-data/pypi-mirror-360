"""A protocol for logging classes for general use."""

from typing import Protocol, runtime_checkable


@runtime_checkable
class LoggerProtocol(Protocol):
    """A protocol for logging classes."""

    def debug(self, message: object, *args, **kwargs) -> None:
        """Log a debug message."""
        ...

    def info(self, message: object, *args, **kwargs) -> None:
        """Log an info message."""
        ...

    def warning(self, message: object, *args, **kwargs) -> None:
        """Log a warning message."""
        ...

    def error(self, message: object, *args, **kwargs) -> None:
        """Log an error message."""
        ...

    def verbose(self, message: object, *args, **kwargs) -> None:
        """Log a verbose message."""
        ...
