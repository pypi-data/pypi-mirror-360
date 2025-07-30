import asyncio
from asyncio.subprocess import PIPE
from collections import deque
from functools import cached_property
import shutil
from typing import TYPE_CHECKING

from bear_utils.cli.shell._base_command import BaseShellCommand as ShellCommand
from bear_utils.cli.shell._base_shell import AsyncShellSession
from bear_utils.extras.platform_utils import OS, get_platform
from bear_utils.logger_manager.loggers.base_logger import BaseLogger

if TYPE_CHECKING:
    from subprocess import CompletedProcess


class TextHelper:
    @cached_property
    def local_console(self) -> BaseLogger:
        from bear_utils.logger_manager import BaseLogger  # noqa: PLC0415

        init: bool = not BaseLogger.has_instance()
        return BaseLogger.get_instance(init=init)

    def print_header(
        self,
        title: str,
        sep: str = "#",
        length: int = 60,
        s1: str = "bold red",
        s2: str = "bold blue",
        return_txt: bool = False,
    ) -> str:
        """Generate a header string"""
        # FIXME: There are probably better ways to do this, but this is OK.
        fill: str = sep * length
        title = f" {title} ".center(length, sep).replace(title, f"[{s1}]{title}[/{s1}]")
        output_text: str = f"\n{fill}\n{title}\n{fill}\n"
        if not return_txt:
            self.local_console.print(output_text, style=s2)
        return output_text


class ClipboardManager:
    """A class to manage clipboard operations such as copying, pasting, and clearing.

    This class provides methods to interact with the system clipboard.
    """

    def __init__(self, maxlen: int = 10) -> None:
        """Initialize the ClipboardManager with a maximum history length."""
        self.clipboard_history: deque[str] = deque(maxlen=maxlen)
        self.shell = AsyncShellSession(env={"LANG": "en_US.UTF-8"}, verbose=False)
        self._copy: ShellCommand[str]
        self._paste: ShellCommand[str]

        platform: OS = get_platform()
        match platform:
            case OS.DARWIN:
                self._copy = ShellCommand.adhoc(name="pbcopy")
                self._paste = ShellCommand.adhoc(name="pbpaste")
            case OS.LINUX:
                if shutil.which(cmd="wl-copy") and shutil.which(cmd="wl-paste"):
                    self._copy = ShellCommand.adhoc(name="wl-copy")
                    self._paste = ShellCommand.adhoc(name="wl-paste")
                elif shutil.which(cmd="xclip"):
                    self._copy = ShellCommand.adhoc(name="xclip").sub("-selection", "clipboard")
                    self._paste = ShellCommand.adhoc(name="xclip").sub("-selection", "clipboard").value("-o")
                else:
                    raise RuntimeError("No clipboard command found on Linux")
            case OS.WINDOWS:
                self._copy = ShellCommand.adhoc(name="clip")
                self._paste = ShellCommand.adhoc(name="powershell").sub("Get-Clipboard")
            case _:
                raise RuntimeError(f"Unsupported platform: {platform}")

    def _copy_cmd(self) -> ShellCommand[str]:
        """Get the copy command based on the platform."""
        return self._copy

    def _paste_cmd(self) -> ShellCommand[str]:
        """Get the paste command based on the platform."""
        return self._paste

    def get_history(self) -> deque:
        """Get the clipboard history.

        Returns:
            deque: The history of clipboard entries.
        """
        return self.clipboard_history

    async def copy(self, output: str) -> int:
        """A function that copies the output to the clipboard.

        Args:
            output (str): The output to copy to the clipboard.

        Returns:
            int: The return code of the command.
        """
        await self.shell.run(cmd=self._copy, stdin=PIPE)
        result: CompletedProcess[str] = await self.shell.communicate(stdin=output)
        if result.returncode == 0:
            self.clipboard_history.append(output)  # Only append to history if the copy was successful
        return result.returncode

    async def paste(self) -> str:
        """Paste the output from the clipboard.

        Returns:
            str: The content of the clipboard.

        Raises:
            RuntimeError: If the paste command fails.
        """
        try:
            await self.shell.run(cmd=self._paste)
            result: CompletedProcess[str] = await self.shell.communicate()
        except Exception as e:
            raise RuntimeError(f"Error pasting from clipboard: {e}") from e
        if result.returncode != 0:
            raise RuntimeError(f"{self._paste.cmd} failed with return code {result.returncode}")
        return result.stdout

    async def clear(self) -> int:
        """A function that clears the clipboard.

        Returns:
            int: The return code of the command.
        """
        return await self.copy(output="")


def copy_to_clipboard(output: str) -> int:
    """Copy the output to the clipboard.

    Args:
        output (str): The output to copy to the clipboard.

    Returns:
        int: The return code of the command.
    """
    clipboard_manager = ClipboardManager()
    loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    return loop.run_until_complete(future=clipboard_manager.copy(output))


async def copy_to_clipboard_async(output: str) -> int:
    """Asynchronously copy the output to the clipboard.

    Args:
        output (str): The output to copy to the clipboard.

    Returns:
        int: The return code of the command.
    """
    clipboard_manager = ClipboardManager()
    return await clipboard_manager.copy(output=output)


def paste_from_clipboard() -> str:
    """Paste the output from the clipboard.

    Returns:
        str: The content of the clipboard.
    """
    clipboard_manager = ClipboardManager()
    loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    return loop.run_until_complete(future=clipboard_manager.paste())


async def paste_from_clipboard_async() -> str:
    """Asynchronously paste the output from the clipboard.

    Returns:
        str: The content of the clipboard.
    """
    clipboard_manager = ClipboardManager()
    return await clipboard_manager.paste()


def clear_clipboard() -> int:
    """Clear the clipboard.

    Returns:
        int: The return code of the command.
    """
    clipboard_manager = ClipboardManager()
    loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    return loop.run_until_complete(clipboard_manager.clear())


async def clear_clipboard_async() -> int:
    """Asynchronously clear the clipboard.

    Returns:
        int: The return code of the command.
    """
    clipboard_manager = ClipboardManager()
    return await clipboard_manager.clear()


def fmt_header(
    title: str,
    sep: str = "#",
    length: int = 60,
    style1: str = "bold red",
    style2: str = "bold blue",
    print_out: bool = True,
) -> str:
    """Generate a header string for visual tests.

    Args:
        title (str): The title to display in the header.
        sep (str): The character to use for the separator. Defaults to '#'.
        length (int): The total length of the header line. Defaults to 60.
        style1 (str): The style for the title text. Defaults to 'bold red'.
        style2 (str): The style for the separator text. Defaults to 'bold blue'.
    """
    text_helper = TextHelper()
    if print_out:
        text_helper.print_header(title=title, sep=sep, length=length, s1=style1, s2=style2, return_txt=False)
        return ""
    return text_helper.print_header(title=title, sep=sep, length=length, s1=style1, s2=style2, return_txt=True)
