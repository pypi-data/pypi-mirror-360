from functools import cached_property
from typing import Any, Literal, overload

from pydantic import BaseModel, Field, field_validator

from bear_utils.extras.wrappers.add_methods import add_comparison_methods

FAILURE: Literal[45] = 45
ERROR: Literal[40] = 40
WARNING: Literal[30] = 30
WARN: Literal[30] = WARNING
INFO: Literal[20] = 20
SUCCESS: Literal[15] = 15
DEBUG: Literal[10] = 10
VERBOSE: Literal[5] = 5
NOTSET: Literal[0] = 0


level_to_name = {
    FAILURE: "FAILURE",
    ERROR: "ERROR",
    WARNING: "WARNING",
    INFO: "INFO",
    SUCCESS: "SUCCESS",
    DEBUG: "DEBUG",
    VERBOSE: "VERBOSE",
    NOTSET: "NOTSET",
}

name_to_level = {
    "FAILURE": FAILURE,
    "ERROR": ERROR,
    "WARN": WARNING,
    "WARNING": WARNING,
    "INFO": INFO,
    "SUCCESS": SUCCESS,
    "DEBUG": DEBUG,
    "VERBOSE": VERBOSE,
    "NOTSET": NOTSET,
}


@add_comparison_methods("value")
class LogLevel(BaseModel):
    """Model to represent a logging level."""

    name: str = Field(default="NOTSET", description="Name of the logging level")
    value: int = Field(default=NOTSET, description="Numeric value of the logging level")

    @field_validator("value")
    @classmethod
    def validate_value(cls, value: int) -> int:
        if value not in level_to_name:
            raise ValueError(f"Invalid logging level value: {value!r}. Valid values are: {list(level_to_name.keys())}")
        return value

    @field_validator("name")
    @classmethod
    def validate_name(cls, name: str) -> str:
        if name not in name_to_level:
            raise ValueError(f"Invalid logging level name: {name!r}. Valid names are: {list(name_to_level.keys())}")
        return name


class LogLevels(BaseModel):
    """Model to represent a collection of logging levels."""

    notset: LogLevel = Field(default=LogLevel(name="NOTSET", value=NOTSET))
    verbose: LogLevel = Field(default=LogLevel(name="VERBOSE", value=VERBOSE))
    debug: LogLevel = Field(default=LogLevel(name="DEBUG", value=DEBUG))
    info: LogLevel = Field(default=LogLevel(name="INFO", value=INFO))
    success: LogLevel = Field(default=LogLevel(name="SUCCESS", value=SUCCESS))
    warning: LogLevel = Field(default=LogLevel(name="WARNING", value=WARNING))
    error: LogLevel = Field(default=LogLevel(name="ERROR", value=ERROR))
    failure: LogLevel = Field(default=LogLevel(name="FAILURE", value=FAILURE))

    model_config = {"arbitrary_types_allowed": True, "extra": "forbid"}

    @cached_property
    def keys(self) -> list[str]:
        """Get the names of all logging levels."""
        return [key.upper() for key in LogLevels.model_fields]

    @cached_property
    def levels(self):  # noqa: ANN202
        item_dict: dict[str, Any] = {
            level_name.lower(): getattr(self, level_name.lower()).value for level_name in self.keys
        }
        return item_dict.items()

    def get_int(self, name: str) -> int:
        """Get the integer value of a logging level by name."""
        if not hasattr(self, name):
            raise ValueError(f"Invalid logging level name: {name!r}. Valid names are: {self.keys}")
        return getattr(self, name).value

    @overload
    def get(self, v: LogLevel) -> LogLevel: ...

    @overload
    def get(self, v: str) -> LogLevel: ...

    @overload
    def get(self, v: int) -> LogLevel: ...

    def get(self, v: int | str | LogLevel) -> LogLevel:
        """Get a logging level by name or value."""
        if isinstance(v, LogLevel):
            return v
        if isinstance(v, str) and v.lower() in self.keys:
            return getattr(self, v.lower())
        if isinstance(v, int):
            for level_name, level_value in self.levels:
                if level_value == v:
                    return getattr(self, level_name.lower())
        return self.notset  # Default to NOTSET if no match found

    def get_name(self, value: int) -> str:
        """Get the name of a logging level by its integer value."""
        for level_name, level_value in self.levels:
            if level_value == value:
                return level_name
        raise ValueError(f"Invalid logging level value: {value!r}. Valid values are: {self.keys}")


log_levels = LogLevels()
