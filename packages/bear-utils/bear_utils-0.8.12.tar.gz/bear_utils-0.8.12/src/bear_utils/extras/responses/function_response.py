"""Function Response Class for handling function call results."""

from __future__ import annotations

from collections.abc import Callable
import json
from subprocess import CompletedProcess
from types import SimpleNamespace as Namespace
from typing import Any, Literal, Self, overload

from pydantic import BaseModel, Field, field_validator

from bear_utils.logger_manager.logger_protocol import (
    LoggerProtocol,  # noqa: TC001 # DO NOT PUT INTO A TYPE_CHECKING BLOCK
)

SUCCESS: list[str] = ["name", "success"]
FAILURE: list[str] = ["name"]


class FunctionResponse(BaseModel):
    """A class to represent the response of a function call, including success status, content, and error messages."""

    name: str = Field(default="", description="Name of the function that was called.")
    returncode: int = Field(default=0, description="Return code of the function, 0 for success, !=0 for failure.")
    extra: dict = Field(default_factory=dict, description="Additional metadata or information related to the response.")
    content: list[str] = Field(default=[], description="Content returned by the function call")
    error: list[str] = Field(default=[], description="Error message if the function call failed")
    sub_tasks: list[FunctionResponse] = Field(default_factory=list, description="List of sub-tasks.")
    number_of_tasks: int = Field(default=0, description="Number of tasks processed in this response.")
    logger: LoggerProtocol | None = Field(default=None, description="Logger instance for logging messages.")
    attrs: Namespace = Field(default_factory=Namespace, description="Storing additional attributes dynamically.")

    model_config = {
        "arbitrary_types_allowed": True,
    }

    def __getattr__(self, key: str, default: Any = None) -> Any:
        if key in FunctionResponse.model_fields:
            raise AttributeError(f"This should never be called, {key} is a model field.")
        if hasattr(self.attrs, key):
            return getattr(self.attrs, key)
        return default

    def __setattr__(self, key: str, value: Any) -> None:
        if key in FunctionResponse.model_fields:
            object.__setattr__(self, key, value)
            return
        setattr(self.attrs, key, value)

    def __repr__(self) -> str:
        """Return a string representation of Response."""
        parts: list[str] = []

        def add(k: str, v: Any, _bool: bool = True, formatter: Callable | None = None) -> None:
            if _bool:
                formatted_value: str = formatter(v) if formatter else repr(v)
                parts.append(f"{k}={formatted_value}")

        add("name", self.name, bool(self.name))
        add("returncode", self.returncode, self.returncode != 0)
        add("success", self.success, bool(self.returncode))
        add("content", ", ".join(self.content), bool(self.content))
        add("error", ", ".join(self.error), bool(self.error))
        add("extra", self.extra, bool(self.extra), json.dumps)
        add("number_of_tasks", self.number_of_tasks, self.number_of_tasks > 0)

        return f"Response({', '.join(parts)})"

    def __str__(self) -> str:
        """Return a string representation of Response."""
        return self.__repr__()

    @field_validator("name", mode="before")
    @classmethod
    def validate_name(cls, value: str | Any) -> str:
        """Ensure name is a string, lowercased, and without spaces."""
        if value is None:
            return ""
        if not isinstance(value, str):
            try:
                value = str(value)
            except Exception as e:
                raise TypeError(f"Name must be a string, got {type(value).__name__}.") from e
        return value.lower().replace(" ", "_")

    @field_validator("returncode")
    @classmethod
    def validate_returncode(cls, value: int) -> int:
        """Ensure returncode is an integer above or equal to zero."""
        if not isinstance(value, int) or value < 0:
            raise ValueError("Return code must be a non-negative integer.")
        return value

    @field_validator("extra", mode="before")
    @classmethod
    def validate_extra(cls, value: dict | Any) -> dict:
        """Ensure extra is always a dictionary."""
        if value is None:
            return {}
        if not isinstance(value, dict):
            raise TypeError("Extra must be a dictionary.")
        return value

    @field_validator("content", mode="before")
    @classmethod
    def validate_content(cls, value: str | list[str] | Any) -> list[str]:
        """Ensure content is always a list of strings."""
        if isinstance(value, str):
            return [value]
        if isinstance(value, list):
            if not all(isinstance(item, str) for item in value):
                raise TypeError("Content must be a list of strings.")
            return value
        raise TypeError("Content must be a string or a list of strings.")

    @field_validator("error", mode="before")
    @classmethod
    def validate_error(cls, value: str | list[str] | Any) -> list[str]:
        """Ensure error is always a list of strings."""
        if isinstance(value, str):
            return [value]
        if isinstance(value, list):
            if not all(isinstance(item, str) for item in value):
                raise TypeError("Error must be a list of strings.")
            return value
        raise TypeError("Error must be a string or a list of strings.")

    @classmethod
    def from_process(cls, process: CompletedProcess[str], **kwargs) -> Self:
        """Create a FunctionResponse from a CompletedProcess object."""
        returncode: int = process.returncode if process.returncode is not None else 0
        content: str = process.stdout.strip() if process.stdout else ""
        error: str = process.stderr.strip() if process.stderr else ""

        if returncode == 0 and not content and error:
            error, content = content, error

        return cls().add(returncode=returncode, content=content, error=error, **kwargs)

    def from_response(self, response: FunctionResponse | Any, **kwargs) -> Self:
        """Create a FunctionResponse from another FunctionResponse object."""
        if not isinstance(response, FunctionResponse):
            raise TypeError("Expected a FunctionResponse instance.")
        self.sub_tasks.append(response)
        return self.add(
            content=response.content,
            error=response.error,
            returncode=response.returncode,
            log_output=kwargs.pop("log_output", False),
            **kwargs,
        )

    @property
    def success(self) -> bool:
        """Check if the response indicates success."""
        return self.returncode == 0

    def sub_task(
        self,
        name: str = "",
        content: str | list[str] = "",
        error: str | list[str] = "",
        extra: dict[str, Any] | None = None,
        returncode: int | None = None,
        log_output: bool = False,
    ) -> Self:
        """Add a sub-task response to the FunctionResponse."""
        func_response: FunctionResponse = FunctionResponse(name=name, logger=self.logger).add(
            content=content,
            error=error,
            returncode=returncode or self.returncode,
            log_output=log_output,
            extra=extra,
        )
        self.add(content=func_response)
        self.sub_tasks.append(func_response)
        return self

    def successful(
        self,
        content: str | list[str] | CompletedProcess,
        error: str | list[str] = "",
        returncode: int | None = None,
        **kwargs,
    ) -> Self:
        """Set the response to a success state with optional content."""
        self.add(content=content, error=error, returncode=returncode or 0, **kwargs)
        return self

    def fail(
        self,
        content: list[str] | str | CompletedProcess = "",
        error: str | list[str] = "",
        returncode: int | None = None,
        **kwargs,
    ) -> Self:
        """Set the response to a failure state with an error message."""
        self.add(content=content, error=error, returncode=returncode or 1, **kwargs)
        return self

    def _add_item(self, item: str, target_list: list[str]) -> None:
        """Append an item to the target list if not empty."""
        if item != "":
            target_list.append(item)

    def _add_to_list(self, items: str | list[str], target_list: list[str], name: str | None = None) -> None:
        """Append items to the target list with optional name prefix."""
        try:
            if isinstance(items, list):
                for item in items:
                    self._add_item(f"{name}: {item}" if name else item, target_list)
            elif isinstance(items, str):
                self._add_item(f"{name}: {items}" if name else items, target_list)
        except Exception as e:
            raise ValueError(f"Failed to add items: {e!s}") from e

    def _add_content(self, content: str | list[str], name: str | None = None) -> None:
        """Append content to the existing content."""
        self._add_to_list(content, self.content, name)

    def _add_error(self, error: str | list[str], name: str | None = None) -> None:
        """Append error to the existing error."""
        self._add_to_list(error, self.error, name)

    def _handle_function_response(self, func_response: FunctionResponse) -> None:
        """Handle a FunctionResponse object and update the current response."""
        if func_response.extra:
            self.extra.update(func_response.extra)
        self._add_error(error=func_response.error, name=func_response.name)
        self._add_content(content=func_response.content, name=func_response.name)

    def _handle_completed_process(self, result: CompletedProcess[str]) -> None:
        """Handle a CompletedProcess object and update the FunctionResponse."""
        self._add_content(content=result.stdout.strip() if result.stdout else "")
        self._add_error(error=result.stderr.strip() if result.stderr else "")
        self.returncode = result.returncode

    def add(
        self,
        content: list[str] | str | FunctionResponse | CompletedProcess | None = None,
        error: str | list[str] | None = None,
        returncode: int | None = None,
        log_output: bool = False,
        extra: dict[str, Any] | None = None,
    ) -> Self:
        """Append additional content to the existing content.

        Args:
            content (list[str] | str | FunctionResponse | CompletedProcess): The content to add.
            error (str | list[str] | None): The error message(s) to add.
            returncode (int | None): The return code of the function call.
            log_output (bool): Whether to log the output using the logger.
            **kwargs: Additional metadata to include in the response.

        Returns:
            Self: The updated FunctionResponse instance.
        """
        try:
            match content:
                case FunctionResponse():
                    self._handle_function_response(func_response=content)
                    self.number_of_tasks += 1
                case CompletedProcess():
                    self._handle_completed_process(result=content)
                    self.number_of_tasks += 1
                case str() | list() if content:
                    self._add_content(content=content)
                    self.number_of_tasks += 1
                case None:
                    content = None
                case _:
                    content = None
            self._add_error(error=error) if isinstance(error, (str | list)) else None
            self.returncode = returncode if returncode is not None else self.returncode
            self.extra.update(extra) if isinstance(extra, dict) else None
            if log_output and self.logger is not None and (content is not None or error is not None):
                self._log_handling(content=content, error=error, logger=self.logger)
        except Exception as e:
            raise ValueError(f"Failed to add content: {e!s}") from e
        return self

    def _log_handling(
        self,
        content: list[str] | str | FunctionResponse | CompletedProcess | None,
        error: str | list[str] | None,
        logger: LoggerProtocol,
    ) -> None:
        """Log the content and error messages if they exist."""

        def _log_messages(messages: str | list[str], log_func: Callable) -> None:
            if isinstance(messages, str):
                messages = [messages]
            if isinstance(messages, list):
                for msg in messages:
                    log_func(f"{self.name}: {msg}" if self.name else msg)

        if content and isinstance(content, (str | list)):
            _log_messages(content, logger.info)

        if error and isinstance(error, (str | list)):
            _log_messages(error, logger.error)

    @overload
    def done(self, to_dict: Literal[True], suppress: list[str] | None = None) -> dict[str, Any]: ...

    @overload
    def done(self, to_dict: Literal[False], suppress: list[str] | None = None) -> Self: ...

    def done(self, to_dict: bool = False, suppress: list[str] | None = None) -> dict[str, Any] | Self:
        """Convert the FunctionResponse to a dictionary or return the instance itself.

        Args:
            to_dict (bool): If True, return a dictionary representation.
            If False, return the FunctionResponse instance.

        Returns:
            dict[str, Any] | Self: The dictionary representation or the FunctionResponse instance.
        """
        if not to_dict:
            return self

        if suppress is None:
            suppress = []

        result: dict[str, Any] = {}

        def add(k: str, v: Any, _bool: bool = True) -> None:
            if k not in suppress and _bool:
                result[k] = v

        add("name", self.name, bool(self.name))
        add("success", self.success)
        add("returncode", self.returncode, self.returncode > 0)
        add("number_of_tasks", self.number_of_tasks, self.number_of_tasks > 0)
        add("content", self.content, bool(self.content))
        add("error", self.error, bool(self.error))
        result.update(self.extra)
        return result


def success(
    content: str | list[str] | CompletedProcess[str] | FunctionResponse,
    error: str = "",
    **kwargs,
) -> FunctionResponse:
    """Create a successful FunctionResponse."""
    return FunctionResponse().add(content=content, error=error, **kwargs)


def fail(
    content: str | list[str] | CompletedProcess[str] = "",
    error: str | list[str] = "",
    returncode: int | None = None,
    **kwargs,
) -> FunctionResponse:
    """Create a failed FunctionResponse."""
    return FunctionResponse().fail(content=content, error=error, returncode=returncode, **kwargs)


if __name__ == "__main__":
    # Example usage
    from rich import inspect

    response = FunctionResponse(name="example_function", returncode=0, content=["Task completed successfully."])
    response.task_id = 124

    inspect(response)
    print(response)
    print(response.done(to_dict=True))
    print(response.done(to_dict=False))
