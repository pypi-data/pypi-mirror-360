"""Prompt Helpers Module for user input handling."""

from typing import Any, overload

from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.validation import ValidationError, Validator

from bear_utils.constants._exceptions import UserCancelledError
from bear_utils.constants._lazy_typing import OptBool, OptFloat, OptInt, OptStr
from bear_utils.logger_manager import get_console

# TODO: ehhhhhhhh, it is okay


def _parse_bool(value: str) -> bool:
    """Parse a string into a boolean value."""
    lower_value: str = value.lower().strip()
    if lower_value in ("true", "t", "yes", "y", "1"):
        return True
    if lower_value in ("false", "f", "no", "n", "0"):
        return False
    raise ValueError(f"Cannot convert '{value}' to boolean")


def _convert_value(value: str, target_type: type) -> str | int | float | bool:
    """Convert a string value to the target type."""
    if target_type is str:
        return value
    if target_type is int:
        return int(value)
    if target_type is float:
        return float(value)
    if target_type is bool:
        return _parse_bool(value)
    raise ValueError(f"Unsupported type: {target_type}")


@overload
def ask_question(question: str, expected_type: type[bool], default: OptBool = None) -> bool: ...


@overload
def ask_question(question: str, expected_type: type[int], default: OptInt = None) -> int: ...


@overload
def ask_question(question: str, expected_type: type[float], default: OptFloat = None) -> float: ...


@overload
def ask_question(question: str, expected_type: type[str], default: OptStr = None) -> str: ...


def ask_question(question: str, expected_type: type, default: Any = None) -> Any:
    """Ask a question and return the answer, ensuring the entered type is correct.

    This function will keep asking until it gets a valid response or the user cancels with Ctrl+C.
    If the user cancels, a UserCancelledError is raised.

    Args:
        question: The prompt question to display
        expected_type: The expected type class (int, float, str, bool)
        default: Default value if no input is provided

    Returns:
        The user's response in the expected type

    Raises:
        UserCancelledError: If the user cancels input with Ctrl+C
        ValueError: If an unsupported type is specified
    """
    console, sub = get_console("prompt_helpers.py")

    try:
        while True:
            console.print(question)
            response = prompt("> ").strip()

            if not response:
                if default is not None:
                    return default
                sub.error("Input required. Please enter a value.")
                continue
            try:
                result: str | int | float | bool = _convert_value(response, expected_type)
                sub.verbose(f"{expected_type.__name__} detected")
                return result
            except ValueError as e:
                sub.error(f"Invalid input: {e}. Please enter a valid {expected_type.__name__}.")

    except KeyboardInterrupt:
        raise UserCancelledError("User cancelled input") from None


def ask_yes_no(question: str, default: bool | None = None) -> bool | None:
    """Ask a yes or no question and return the answer.

    Args:
        question: The prompt question to display
        default: Default value if no input is provided

    Returns:
        True for yes, False for no, or None if user exits
    """
    console, sub = get_console("prompt_helpers.py")

    try:
        while True:
            console.print(question)
            response = prompt("> ").strip().lower()

            if not response:
                if default is not None:
                    return default
                sub.error("Please enter 'yes', 'no', or 'exit'.")
                continue

            if response in ("exit", "quit"):
                return None
            try:
                return _parse_bool(response)
            except ValueError:
                sub.error("Invalid input. Please enter 'yes', 'no', or 'exit'.")
    except KeyboardInterrupt:
        sub.warning("KeyboardInterrupt: Exiting the prompt.")
        return None


def restricted_prompt(
    question: str, valid_options: list[str], exit_command: str = "exit", case_sensitive: bool = False
) -> str | None:
    """Continuously prompt the user until they provide a valid response or exit.

    Args:
        question: The prompt question to display
        valid_options: List of valid responses
        exit_command: Command to exit the prompt (default: "exit")
        case_sensitive: Whether options are case-sensitive (default: False)

    Returns:
        The user's response or None if they chose to exit
    """
    console, sub = get_console("prompt_helpers.py")
    completer_options = [*valid_options, exit_command]
    completer = WordCompleter(completer_options)

    comparison_options = valid_options if case_sensitive else [opt.lower() for opt in valid_options]
    comparison_exit = exit_command if case_sensitive else exit_command.lower()

    class OptionValidator(Validator):
        def validate(self, document: Any) -> None:
            """Validate the user's input against the valid options."""
            text: Any = document.text if case_sensitive else document.text.lower()
            if text and text != comparison_exit and text not in comparison_options:
                raise ValidationError(
                    message=f"Invalid option. Choose from: {', '.join(valid_options)} or '{exit_command}'",
                    cursor_position=len(document.text),
                )

    try:
        while True:
            console.print(question)
            response: str = prompt(
                "> ", completer=completer, validator=OptionValidator(), complete_while_typing=True
            ).strip()
            comparison_response: str = response if case_sensitive else response.lower()
            if not response:
                sub.error("Please enter a valid option or 'exit'.")
                continue
            if comparison_response == comparison_exit:
                return None
            if comparison_response in comparison_options:
                if not case_sensitive:
                    idx: int = comparison_options.index(comparison_response)
                    return valid_options[idx]
                return response

    except KeyboardInterrupt:
        sub.warning("KeyboardInterrupt: Exiting the prompt.")
        return None
