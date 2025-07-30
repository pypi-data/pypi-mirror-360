"""Simple logger implementation with log levels and timestamped output."""

import sys
from typing import TextIO

from bear_utils.logger_manager._log_level import LogLevel, log_levels
from bear_utils.time import EpochTimestamp

STDOUT: TextIO = sys.stdout
STDERR: TextIO = sys.stderr

VERBOSE: LogLevel = log_levels.get("VERBOSE")
DEBUG: LogLevel = log_levels.get("DEBUG")
INFO: LogLevel = log_levels.get("INFO")
WARNING: LogLevel = log_levels.get("WARNING")
ERROR: LogLevel = log_levels.get("ERROR")


class SimpleLogger:
    """A simple logger that writes messages to stderr (or STDOUT if preferred) with a timestamp."""

    def __init__(self, min_level: int | str | LogLevel = INFO, redirect: TextIO = STDERR) -> None:
        """Initialize the logger with a minimum log level."""
        self.min_level: LogLevel = log_levels.get(min_level)
        self.redirect: TextIO = redirect
        self.buffer: list[str] = []

    def _log(self, level: LogLevel, msg: object, end: str = "\n", *args, **kwargs) -> None:
        timestamp: str = EpochTimestamp.now().to_string()
        try:
            self.buffer.append(f"[{timestamp}] {level.value}: {msg}")
            if args:
                self.buffer.append(" ".join(str(arg) for arg in args))
            if kwargs:
                for key, value in kwargs.items():
                    self.buffer.append(f"{key}={value}")
            print(f"{end}".join(self.buffer), file=self.redirect)
        except Exception as e:
            print(f"[{timestamp}] {level.value}: {msg} - Error: {e}", file=self.redirect)
        finally:
            self.buffer.clear()

    def log(self, level: LogLevel, msg: object, *args, **kwargs) -> None:
        """Log a message at the specified level."""
        if level.value >= self.min_level.value:
            self._log(level, msg, *args, **kwargs)

    def verbose(self, msg: object, *args, **kwargs) -> None:
        """Alias for debug level logging."""
        self.log(VERBOSE, msg, *args, **kwargs)

    def debug(self, msg: object, *args, **kwargs) -> None:
        """Log a debug message."""
        self.log(DEBUG, msg, *args, **kwargs)

    def info(self, msg: object, *args, **kwargs) -> None:
        """Log an info message."""
        self.log(INFO, msg, *args, **kwargs)

    def warning(self, msg: object, *args, **kwargs) -> None:
        """Log a warning message."""
        self.log(WARNING, msg, *args, **kwargs)

    def error(self, msg: object, *args, **kwargs) -> None:
        """Log an error message."""
        self.log(ERROR, msg, *args, **kwargs)


# Example usage:
if __name__ == "__main__":
    logger = SimpleLogger()

    logger.verbose(msg="This is a verbose message")
    logger.debug(msg="This is a debug message")
    logger.info(msg="This is an info message")
    logger.warning(msg="This is a warning message")
    logger.error(msg="This is an error message")
