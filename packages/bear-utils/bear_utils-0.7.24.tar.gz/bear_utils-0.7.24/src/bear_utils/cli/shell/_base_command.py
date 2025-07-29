from typing import TYPE_CHECKING, Any, ClassVar, LiteralString, Self, cast

if TYPE_CHECKING:
    from subprocess import CompletedProcess


class BaseShellCommand[T: str]:
    """Base class for typed shell commands compatible with session systems"""

    command_name: ClassVar[str] = ""

    def __init__(self, *args, **kwargs) -> None:
        self.sub_command: str = kwargs.get("sub_command", "")
        self.args = args
        self.kwargs: dict[str, Any] = kwargs
        self.suffix = kwargs.get("suffix", "")
        self.result: CompletedProcess[str] | None = None

    def __str__(self) -> str:
        """String representation of the command"""
        return self.cmd

    def value(self, v: str) -> Self:
        """Add value to the export command"""
        self.suffix: str = v
        return self

    @classmethod
    def adhoc(cls, name: T, *args, **kwargs) -> "BaseShellCommand[T]":
        """Create an ad-hoc command class for a specific command

        Args:
            name (str): The name of the command to create

        Returns:
            BaseShellCommand: An instance of the ad-hoc command class.
        """
        return type(
            f"AdHoc{name.title()}Command",
            (cls,),
            {"command_name": name},
        )(*args, **kwargs)

    @classmethod
    def sub(cls, s: str, *args, **kwargs) -> Self:
        """Set a sub-command for the shell command"""
        return cls(s, *args, **kwargs)

    @property
    def cmd(self) -> str:
        """Return the full command as a string"""
        cmd_parts = [self.command_name, self.sub_command, *self.args]
        cmd_parts = [part for part in cmd_parts if part]
        joined: LiteralString = " ".join(cmd_parts).strip()
        if self.suffix:
            return f"{joined} {self.suffix}"
        return joined

    def do(self, **kwargs) -> Self:
        """Run the command using subprocess"""
        from ._base_shell import shell_session  # noqa: PLC0415

        with shell_session(**kwargs) as session:
            result = session.add(self.cmd).run()
        if result is not None:
            self.result = cast("CompletedProcess[str]", result)
        return self

    def get(self) -> str:
        """Get the result of the command execution"""
        if self.result is None:
            self.do()
        if self.result is None:
            raise RuntimeError("Command execution failed for some reason.")
        return str(self.result.stdout).strip()
