"""Function Response Class for handling function call results."""

from __future__ import annotations

from io import StringIO
import json
from subprocess import CompletedProcess
from typing import Any, Literal, Self, overload

from pydantic import BaseModel, Field, field_validator

from bear_utils.constants.logger_protocol import LoggerProtocol  # noqa: TC001 # DO NOT PUT INTO A TYPE_CHECKING BLOCK

SUCCESS: list[str] = ["name", "success"]
FAILURE: list[str] = ["name"]


class FunctionResponse(BaseModel):
    """A class to represent the response of a function call, including success status, content, and error messages."""

    name: str = Field(default="", description="Name of the function that was called.")
    returncode: int = Field(default=0, description="Return code of the function, 0 for success, !=0 for failure.")
    extra: dict = Field(default_factory=dict, description="Additional metadata or information related to the response.")
    content: list[str] = Field(default=[], description="Content returned by the function call")
    error: list[str] = Field(default=[], description="Error message if the function call failed")
    number_of_tasks: int = Field(default=0, description="Number of tasks processed in this response.")
    logger: LoggerProtocol | None = Field(default=None, description="Logger instance for logging messages.")

    model_config = {
        "arbitrary_types_allowed": True,
    }

    def __repr__(self) -> str:
        """Return a string representation of Response."""
        result = StringIO()
        result.write("Response(")
        if self.name:
            result.write(f"name={self.name!r}, ")
        if self.returncode:
            result.write(f"success={self.success!r}, ")
        if self.content:
            content: str = ", ".join(self.content)
            result.write(f"content={content!r}, ")
        if self.error:
            error: str = ", ".join(self.error)
            result.write(f"error={error!r}, ")
        if self.extra:
            result.write(f"extra={json.dumps(self.extra)!r}, ")
        if self.number_of_tasks > 0:
            result.write(f"number_of_tasks={self.number_of_tasks!r}, ")
        result.write(")")
        returned_result: str = result.getvalue().replace(", )", ")")
        result.close()
        return returned_result

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
    ) -> None:
        """Add a sub-task response to the FunctionResponse."""
        func_response: FunctionResponse = FunctionResponse(name=name, logger=self.logger).add(
            content=content,
            error=error,
            returncode=returncode or self.returncode,
            log_output=log_output,
            extra=extra,
        )
        self.add(content=func_response)

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

    def _add_error(self, error: str) -> None:
        """Append an error message to the existing error."""
        if error != "":
            self.error.append(error)

    def _add_to_error(self, error: str | list[str], name: str | None = None) -> None:
        """Append additional error messages to the existing error."""
        try:
            if isinstance(error, list):
                for err in error:
                    self._add_error(error=f"{name}: {err}" if name else err)
            elif isinstance(error, str):
                self._add_error(error=f"{name}: {error}" if name else error)
        except Exception as e:
            raise ValueError(f"Failed to add error: {e!s}") from e

    def _add_content(self, content: str) -> None:
        """Append content to the existing content."""
        if content != "":
            self.content.append(content)

    def _add_to_content(self, content: str | list[str], name: str | None = None) -> None:
        """Append additional content to the existing content."""
        try:
            if isinstance(content, list):
                for item in content:
                    self._add_content(content=f"{name}: {item}" if name else item)
            elif isinstance(content, str):
                self._add_content(content=f"{name}: {content}" if name else content)
        except Exception as e:
            raise ValueError(f"Failed to add content: {e!s}") from e

    def _handle_function_response(self, func_response: FunctionResponse) -> None:
        """Handle a FunctionResponse object and update the current response."""
        if func_response.extra:
            self.extra.update(func_response.extra)
        self._add_to_error(error=func_response.error, name=func_response.name)
        self._add_to_content(content=func_response.content, name=func_response.name)

    def _handle_completed_process(self, result: CompletedProcess[str]) -> None:
        """Handle a CompletedProcess object and update the FunctionResponse."""
        self._add_to_content(content=result.stdout.strip() if result.stdout else "")
        self._add_to_error(error=result.stderr.strip() if result.stderr else "")
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
                    self._add_to_content(content=content)
                    self.number_of_tasks += 1
                case None:
                    content = None
                case _:
                    content = None
            self._add_to_error(error=error) if isinstance(error, (str | list)) else None
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
        if content is not None and error is None:
            if isinstance(content, list):
                for item in content:
                    logger.info(message=f"{self.name}: {item}" if self.name else item)
            elif isinstance(content, str):
                logger.info(message=f"{self.name}: {content}" if self.name else content)
        elif error is not None and content is None:
            if isinstance(error, list):
                for err in error:
                    logger.error(message=f"{self.name}: {err}" if self.name else err)
            elif isinstance(error, str):
                logger.error(message=f"{self.name}: {error}" if self.name else error)

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
        if suppress is None:
            suppress = []
        if to_dict:
            result: dict[str, Any] = {}
            if self.name and "name" not in suppress:
                result["name"] = self.name
            if "success" not in suppress:
                result.update({"success": self.success})
            if self.returncode > 0 and "returncode" not in suppress:
                result["returncode"] = self.returncode
            if self.number_of_tasks > 0 and "number_of_tasks" not in suppress:
                result["number_of_tasks"] = self.number_of_tasks
            if self.content and "content" not in suppress:
                result["content"] = self.content
            if self.error and "error" not in suppress:
                result["error"] = self.error
            if self.extra:
                result.update(self.extra)
            return result
        return self


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
