from collections.abc import Callable
from io import StringIO
from logging import Formatter, Handler, LogRecord
from logging.handlers import BufferingHandler
import threading
from typing import Any

from prompt_toolkit import print_formatted_text
from prompt_toolkit.output.defaults import create_output
from rich.text import Text

from bear_utils.constants.date_related import DATE_TIME_FORMAT

from ._common import SIMPLE_FORMAT, VERBOSE_CONSOLE_FORMAT, ExecValues
from ._styles import LoggerExtraInfo


def get_extra(record: LogRecord) -> LoggerExtraInfo:
    """Get extra information from the log record."""
    extra: LoggerExtraInfo = {
        "style_name": record.__dict__.get("style_name", ""),
        "style": record.__dict__.get("style", ""),
        "log_level": record.__dict__.get("log_level", ""),
        "log_level_style": record.__dict__.get("log_level_style", ""),
        "namespace": record.__dict__.get("namespace", ""),
    }
    return extra


def extract_exec_info(record: LogRecord) -> dict[str, ExecValues] | None:
    """Extract execution info from the log record."""
    exec_values: dict[str, ExecValues] | None = record.__dict__.get("exec_values", {})
    if exec_values is not None:
        return exec_values
    return None


class ConsoleHandler(Handler):
    def __init__(self, print_func: Callable, buffer_output: Callable):
        super().__init__()
        self.print_func: Callable = print_func
        self.buffer_func: Callable = buffer_output

    def emit(self, record: LogRecord, return_str: bool = False) -> Any:
        """Emit a log record either to console or return as string.

        Args:
            record: The LogRecord to emit
            return_str: If True, return formatted string instead of printing

        Returns:
            str if return_str=True, None otherwise
        """
        formatted_msg: str = self.format(record)
        extra: LoggerExtraInfo = get_extra(record)
        exec_values: dict[str, ExecValues] | None = extract_exec_info(record)
        exc_info: bool = bool(exec_values)
        style_name = extra.get("style_name", "")

        print_kwargs = {
            "msg": formatted_msg,
            "style": style_name,
            "exc_info": exc_info if exc_info is not None else False,
            "exec_values": exec_values,
            "return_str": return_str,
        }
        if return_str:
            return self.buffer_func(**print_kwargs)

        return self.print_func(**print_kwargs)


class ConsoleFormatter(Formatter):
    def __init__(self, fmt: str = SIMPLE_FORMAT, datefmt: str = DATE_TIME_FORMAT):
        super().__init__(fmt=fmt, datefmt=datefmt)
        self.log_format: str = fmt

    def format(self, record: LogRecord) -> str:
        extra: LoggerExtraInfo = get_extra(record)
        if self.log_format == VERBOSE_CONSOLE_FORMAT:
            log_level_color: str = extra["log_level_style"]
            style_name: str = extra.get("style_name", "")
            dynamic_format = self.log_format.format(
                log_level_color,
                style_name.upper(),
                log_level_color,
            )
            temp_formatter = Formatter(fmt=dynamic_format, datefmt=self.datefmt)
            return temp_formatter.format(record)

        if self.log_format == SIMPLE_FORMAT:
            record.msg = f"{record.msg}"

        return super().format(record)


class ConsoleBuffering(BufferingHandler):
    def __init__(
        self,
        capacity: int = 9999,
        console_handler: ConsoleHandler | None = None,
        return_auto: bool = False,
    ):
        super().__init__(capacity=capacity)
        # should come with a formatter before getting here
        self.console_handler: ConsoleHandler = console_handler or ConsoleHandler(
            print_func=lambda **kwargs: None, buffer_output=lambda **kwargs: ""
        )
        self._lock = threading.RLock()
        self.flush_auto = return_auto

    def flush_to_output(self) -> Text:
        """Flush all buffered records to the console handler."""
        with self._lock:
            output_buffer = StringIO()
            output = create_output(stdout=output_buffer)
            for record in self.buffer:
                formatted_msg = self.console_handler.emit(record, return_str=True)
                print_formatted_text(formatted_msg, output=output, end="\n")
        output = output_buffer.getvalue()
        output_buffer.close()
        self.buffer.clear()
        return Text.from_ansi(output)

    def trigger_flush(self) -> None:
        """Immediately flush all buffered records to console."""
        self.flush()

    def flush(self) -> None:
        """Flush all buffered records to the console handler."""
        if self.flush_auto:
            with self._lock:
                for record in self.buffer:
                    self.console_handler.emit(record)
                self.buffer.clear()
