"""Simple logger implementation with log levels and timestamped output."""

import sys
from typing import TextIO

from bear_utils.logger_manager._common import DEBUG, ERROR, INFO, VERBOSE, WARNING, LogLevel
from bear_utils.time import EpochTimestamp

STDOUT: TextIO = sys.stdout
STDERR: TextIO = sys.stderr


class SimpleLogger:
    """A simple logger that writes messages to stderr (or STDOUT if preferred) with a timestamp."""

    def __init__(self, min_level: LogLevel = INFO, redirect: TextIO = STDERR) -> None:
        """Initialize the logger with a minimum log level."""
        self.min_level: LogLevel = min_level
        self.redirect: TextIO = redirect

    def _log(self, level: LogLevel, msg: object, *args, **kwargs) -> None:
        if isinstance(level, LogLevel) and level.value >= self.min_level.value:
            timestamp: str = EpochTimestamp.now().to_string()
            print(f"[{timestamp}] {level.value}: {msg}", file=self.redirect)
        if args:
            print(" ".join(str(arg) for arg in args), file=self.redirect)
        if kwargs:
            for key, value in kwargs.items():
                print(f"{key}={value}", file=self.redirect)

    def verbose(self, msg: object, *args, **kwargs) -> None:
        """Alias for debug level logging."""
        self._log(VERBOSE, msg, *args, **kwargs)

    def debug(self, msg: object, *args, **kwargs) -> None:
        """Log a debug message."""
        self._log(DEBUG, msg, *args, **kwargs)

    def info(self, msg: object, *args, **kwargs) -> None:
        """Log an info message."""
        self._log(INFO, msg, *args, **kwargs)

    def warning(self, msg: object, *args, **kwargs) -> None:
        """Log a warning message."""
        self._log(WARNING, msg, *args, **kwargs)

    def error(self, msg: object, *args, **kwargs) -> None:
        """Log an error message."""
        self._log(ERROR, msg, *args, **kwargs)


# Example usage:
if __name__ == "__main__":
    logger = SimpleLogger()

    logger.verbose(msg="This is a verbose message")
    logger.debug(msg="This is a debug message")
    logger.info(msg="This is an info message")
    logger.warning(msg="This is a warning message")
    logger.error(msg="This is an error message")
