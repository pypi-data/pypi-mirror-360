import inspect
from types import TracebackType
from typing import Literal, Required, TypedDict


class ExecValues(TypedDict, total=True):
    exc_type: Required[type[BaseException]]
    exc_value: Required[BaseException]
    exc_traceback: Required[TracebackType]


class StackLevelTracker:
    STACK_LEVEL_OFFSET = 1

    def __init__(self) -> None:
        self.start_depth: int | None = None
        self.end_depth: int | None = None

    @property
    def not_set(self) -> bool:
        """Check if the start depth is not set."""
        return self.start_depth is None

    def record_start(self) -> None:
        """Record the current stack depth as the start depth."""
        self.start_depth = len(inspect.stack())

    def record_end(self) -> int:
        """Record the current stack depth as the end depth and then return the calculated stack level.

        Returns:
            int: The calculated stack level based on the difference between start and end depths.
        """
        self.end_depth = len(inspect.stack())
        return self.calculate_stacklevel()

    def calculate_stacklevel(self) -> int:
        if self.start_depth is None or self.end_depth is None:
            raise ValueError("Start and end depths must be recorded before calculating stack level.")
        return self.end_depth - (self.start_depth + self.STACK_LEVEL_OFFSET)


VERBOSE_FORMAT = "%(asctime)s |%(levelname)s| {%(module)s|%(funcName)s|%(lineno)d} %(message)s"
VERBOSE_CONSOLE_FORMAT = "%(asctime)s <[{}]{}[/{}]> %(message)s"
SIMPLE_FORMAT = "%(message)s"
FIVE_MEGABYTES = 1024 * 1024 * 5

VERBOSE: Literal[5] = 5
SUCCESS: Literal[15] = 15
FAILURE: Literal[45] = 45


__all__ = [
    "FAILURE",
    "FIVE_MEGABYTES",
    "SIMPLE_FORMAT",
    "SUCCESS",
    "VERBOSE",
    "VERBOSE_CONSOLE_FORMAT",
    "VERBOSE_FORMAT",
    "ExecValues",
    "StackLevelTracker",
]
