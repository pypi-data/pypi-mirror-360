"""Prompt Helpers Module for user input handling."""

from typing import Any, overload

from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.validation import ValidationError, Validator

from bear_utils.constants._exceptions import UserCancelledError
from bear_utils.constants._lazy_typing import LitBool, LitFloat, LitInt, LitStr, OptBool, OptFloat, OptInt, OptStr
from bear_utils.logger_manager import get_console

# TODO: Overhaul this trash, it is written like absolute garbage.


@overload
def ask_question(question: str, expected_type: LitInt, default: OptInt = None, **kwargs) -> int: ...


@overload
def ask_question(question: str, expected_type: LitFloat, default: OptFloat = None, **kwargs) -> float: ...


@overload
def ask_question(question: str, expected_type: LitStr, default: OptStr = None, **kwargs) -> str: ...


@overload
def ask_question(question: str, expected_type: LitBool, default: OptBool = None, **kwargs) -> bool: ...


def ask_question(question: str, expected_type: Any, default: Any = None, **_) -> Any:
    """Ask a question and return the answer, ensuring the entered type is correct and a value is entered.

    This function will keep asking until it gets a valid response or the user cancels with Ctrl+C.
    If the user cancels, a UserCancelledError is raised.

    Args:
        question: The prompt question to display
        expected_type: The expected type of the answer (int, float, str, bool)
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
            response: str = prompt("> ")
            if response == "":
                if default is not None:
                    return default
                continue
            match expected_type:
                case "int":
                    try:
                        result = int(response)
                        sub.verbose("int detected")
                        return result
                    except ValueError:
                        sub.error("Invalid input. Please enter a valid integer.")
                case "float":
                    try:
                        result = float(response)
                        sub.verbose("float detected")
                        return result
                    except ValueError:
                        sub.error("Invalid input. Please enter a valid float.")
                case "str":
                    sub.verbose("str detected")
                    return response
                case "bool":
                    lower_response = response.lower()
                    if lower_response in ("true", "t", "yes", "y", "1"):
                        return True
                    if lower_response in ("false", "f", "no", "n", "0"):
                        return False
                    sub.error("Invalid input. Please enter a valid boolean (true/false, yes/no, etc).")
                case _:
                    raise ValueError(f"Unsupported type: {expected_type}")
    except KeyboardInterrupt:
        raise UserCancelledError("User cancelled input") from None


def ask_yes_no(question: str, default: None | Any = None, **kwargs) -> None | bool:
    """Ask a yes or no question and return the answer.

    Args:
        question: The prompt question to display
        default: Default value if no input is provided

    Returns:
        True for yes, False for no, or None if no valid response is given
    """
    kwargs = kwargs or {}
    sub, console = get_console("prompt_helpers.py")
    try:
        while True:
            console.info(question)
            response = prompt("> ")

            if response == "":
                if default is not None:
                    return default
                continue

            if response.lower() in ["yes", "y"]:
                return True
            if response.lower() in ["no", "n"]:
                return False
            if response.lower() in ["exit", "quit"]:
                return None
            console.error("Invalid input. Please enter 'yes' or 'no' or exit.")
            continue
    except KeyboardInterrupt:
        console.warning("KeyboardInterrupt: Exiting the prompt.")
        return None


def restricted_prompt(question: str, valid_options: list[str], exit_command: str = "exit", **kwargs) -> None | str:
    """Continuously prompt the user until they provide a valid response or exit.

    Args:
        question: The prompt question to display
        valid_options: List of valid responses
        exit_command: Command to exit the prompt (default: "exit")

    Returns:
        The user's response or None if they chose to exit
    """
    kwargs = kwargs or {}
    sub, console = get_console("prompt_helpers.py")
    completer_options: list[str] = [*valid_options, exit_command]
    completer = WordCompleter(completer_options)

    class OptionValidator(Validator):
        def validate(self, document: Any) -> None:
            """Validate the user's input against the valid options."""
            text: str = document.text.lower()
            if text != exit_command and text not in valid_options:
                raise ValidationError(
                    message=f"Invalid option: {text}. Please choose from {', '.join(valid_options)} or type '{exit_command}' to exit.",
                    cursor_position=len(document.text),
                )

    try:
        while True:
            if console is not None:
                console.info(question)
                response = prompt("> ", completer=completer, validator=OptionValidator(), complete_while_typing=True)
                response = response.lower()
            else:
                response = prompt(
                    question, completer=completer, validator=OptionValidator(), complete_while_typing=True
                )
                response = response.lower()

            if response == exit_command:
                return None
            if response == "":
                sub.error("No input provided. Please enter a valid option or exit.")
                continue
            if response in valid_options:
                return response
    except KeyboardInterrupt:
        sub.warning("KeyboardInterrupt: Exiting the prompt.")
        return None
