"""ConsoleLogger: A comprehensive console logger that combines Python's logging framework with Rich console styling."""

# region Imports
from contextlib import suppress
from functools import cached_property
from logging import DEBUG, Formatter, Handler, Logger
from logging.handlers import QueueHandler, QueueListener, RotatingFileHandler
from queue import Queue
from typing import TYPE_CHECKING, override

from prompt_toolkit import PromptSession
from rich.text import Text
from rich.theme import Theme

from bear_utils.constants.date_related import DATE_TIME_FORMAT
from bear_utils.logger_manager._common import FIVE_MEGABYTES, VERBOSE_CONSOLE_FORMAT, VERBOSE_FORMAT, ExecValues
from bear_utils.logger_manager._console_junk import ConsoleBuffering, ConsoleFormatter, ConsoleHandler

from .base_logger import BaseLogger

if TYPE_CHECKING:
    from rich.traceback import Traceback

# endregion Imports


class ConsoleLogger(Logger, BaseLogger):
    """A comprehensive console logger that combines Python's logging framework with Rich console styling.

    This logger provides styled console output with configurable file logging, queue handling,
    buffering, and interactive input capabilities. It dynamically creates logging methods
    (info, error, debug, etc.) that forward to Rich's styled console printing.

    Features:
    - Rich styled console output with themes
    - Optional file logging with rotation
    - Queue-based async logging
    - Message buffering capabilities
    - Interactive prompt integration
    - Exception tracebacks with local variables

    Example:
        logger = ConsoleLogger.get_instance(init=True, verbose=True, name="MyLogger", level=DEBUG)
        logger.info("This is styled info")
        logger.error("This is styled error")
        logger.success("This is styled success")
    """

    # region Setup
    def __init__(
        self,
        theme: Theme | None = None,
        name: str = "ConsoleLogger",
        level: int = DEBUG,
        disabled: bool = True,
        console: bool = True,
        file: bool = False,
        queue_handler: bool = False,
        buffering: bool = False,
        *_,
        **kwargs,
    ) -> None:
        """Initialize the ConsoleLogger with optional file, console, and buffering settings."""
        Logger.__init__(self, name=name, level=level)
        BaseLogger.__init__(
            self,
            output_handler=self._console_output,
            theme=theme,
            style_disabled=kwargs.get("style_disabled", False),
            logger_mode=kwargs.get("logger_mode", True),
            level=level,
        )
        self.name = name
        self.level = level
        self.setLevel(level)
        self.session = None
        self.disabled = disabled
        self._handlers: list[Handler] = []
        self.logger_mode: bool = kwargs.pop("logger_mode", True)
        if self.logger_mode:
            self.disabled = False
            self._handle_enable_booleans(
                file=file,
                console=console,
                buffering=buffering,
                queue_handler=queue_handler,
                **kwargs,
            )

    def _handle_enable_booleans(
        self,
        file: bool,
        console: bool,
        buffering: bool,
        queue_handler: bool,
        **kwargs,
    ) -> None:
        """Configure logging handlers based on initialization parameters."""
        if console or buffering:
            self.console_handler: ConsoleHandler = ConsoleHandler(self.print, self.output_buffer)
            self.console_handler.setFormatter(ConsoleFormatter(fmt=VERBOSE_CONSOLE_FORMAT, datefmt=DATE_TIME_FORMAT))
            self.console_handler.setLevel(self.level)
            if console:
                self._handlers.append(self.console_handler)
            if buffering:
                self.buffer_handler: ConsoleBuffering = ConsoleBuffering(console_handler=self.console_handler)
                self.addHandler(self.buffer_handler)
        if file:
            self.file_handler: RotatingFileHandler = RotatingFileHandler(
                filename=kwargs.get("file_path", "console.log"),
                maxBytes=kwargs.get("max_bytes", FIVE_MEGABYTES),
                backupCount=kwargs.get("backup_count", 5),
            )
            self.file_handler.setFormatter(Formatter(fmt=VERBOSE_FORMAT, datefmt=DATE_TIME_FORMAT))
            self.file_handler.setLevel(self.level)
            self._handlers.append(self.file_handler)
        if queue_handler:
            self.queue = Queue()
            self.queue_handler = QueueHandler(self.queue)
            self.addHandler(self.queue_handler)
            self.listener = QueueListener(self.queue, *self._handlers)
            self.listener.start()
        else:
            for handler in self._handlers:
                self.addHandler(handler)

    def stop_queue_listener(self) -> None:
        """Stop the queue listener if it exists and clean up resources."""
        if hasattr(self, "listener"):
            self.verbose("ConsoleLogger: QueueListener stopped and cleaned up.")
            self.listener.stop()
            del self.listener
            del self.queue
            del self.queue_handler

    def trigger_buffer_flush(self) -> Text:
        """Flush buffered messages to console output."""
        if hasattr(self, "buffer_handler"):
            return self.buffer_handler.flush_to_output()
        return Text("No buffering handler available.", style="bold red")

    def set_base_level(self, level: int) -> None:
        """Set the base logging level for the console logger."""
        super().set_base_level(level)
        self.setLevel(level)
        if hasattr(self, "console_handler"):
            self.console_handler.setLevel(level)
        if hasattr(self, "buffer_handler"):
            self.buffer_handler.setLevel(level)
        if hasattr(self, "queue_handler"):
            self.queue_handler.setLevel(level)

    def _console_output(self, msg: object, extra: dict, *args, **kwargs) -> None:
        """Console-specific output handler that integrates with logging module."""
        if not self.logger_mode:
            self.print(msg, *args, **kwargs)
        else:
            kwargs.pop("style", None)
            self.log(
                extra.get("log_level", DEBUG),
                msg,
                *args,
                extra=extra,
                **kwargs,
            )

    # endregion Setup

    # region Utility Methods

    async def input(self, msg: str, style: str = "info", **kwargs) -> str:
        """Display a styled prompt and return user input asynchronously."""
        if not self.session:
            self.session = PromptSession(**kwargs)
        self.print(msg, style=style)
        return await self.session.prompt_async()

    def output_buffer(
        self,
        msg: object,
        end: str = "\n",
        exc_info: str | None = None,
        exec_values: ExecValues | None = None,
        *_,
        **kwargs,
    ) -> str:
        """Capture console output to a string buffer without printing to terminal."""
        if exc_info and exec_values:
            exception: Traceback = self._get_exception(manual=True, exec_values=exec_values)
            self.console.print(exception, end=end)
        self.console.print(msg, end="", style=kwargs.get("style", "info"))
        output = self.console_buffer.getvalue()
        self._reset_buffer()
        return output

    # endregion Utility Methods

    # region Enhanced Print Methods

    def print(
        self,
        msg: object,
        end: str = "\n",
        exc_info: str | None = None,
        extra: dict | None = None,
        *args,
        **kwargs,
    ) -> None | str:
        """Print styled messages with enhanced exception handling and JSON support.

        Extends the base print method with proper exception tracebacks and
        integrated JSON printing for structured data output.
        """
        if exc_info is not None:
            with suppress(ValueError):
                self._print(self._get_exception(), end=end, width=100, show_locals=True, **kwargs)

        self._print(msg, end, *args, **kwargs)

        if extra:
            self._print(msg=extra, end=end, json=True, indent=4)

    @cached_property
    def stack_level(self) -> int:
        """Cached property to retrieve the current stack level."""
        return self.stack_tracker.record_end()

    @override
    def _log(  # type: ignore[override]
        self,
        level: int,
        msg: object,
        args: tuple,
        exc_info: str | None = None,
        extra: dict | None = None,
        stack_info: bool = False,
        stacklevel: int | None = None,
    ) -> None:
        """Custom logging implementation with enhanced exception handling.

        Overrides the standard logging._log method to provide better exception
        value extraction for Rich traceback integration while respecting log levels.
        """
        stacklevel = stacklevel or self.stack_level
        try:
            fn, lno, func, sinfo = self.findCaller(stack_info, stacklevel)
        except ValueError:
            fn, lno, func, sinfo = "(unknown file)", 0, "(unknown function)", None
        final_extra = extra or {}
        if exc_info is not None:
            exec_values = self._extract_exception_values(exc_info)
            if exec_values:
                final_extra = {**final_extra, "exec_values": exec_values}

        record = self.makeRecord(
            name=self.name,
            level=level,
            fn=fn,
            lno=lno,
            msg=msg,
            args=args,
            exc_info=None,
            func=func,
            extra=final_extra,
            sinfo=sinfo,
        )

        self.handle(record)

    def exit(self) -> None:
        """Clean up resources including queue listeners and console buffers."""
        if hasattr(self, "queue_handler"):
            self.queue_handler.flush()
            self.stop_queue_listener()

        self.console_buffer.close()

    # endregion Enhanced Print Methods
