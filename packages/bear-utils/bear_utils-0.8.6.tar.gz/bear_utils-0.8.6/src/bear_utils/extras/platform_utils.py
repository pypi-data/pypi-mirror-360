"""A module for detecting the current operating system."""

from enum import StrEnum
import platform


class OS(StrEnum):
    """Enumeration of operating systems."""

    DARWIN = "Darwin"
    LINUX = "Linux"
    WINDOWS = "Windows"
    OTHER = "Other"


DARWIN = OS.DARWIN
LINUX = OS.LINUX
WINDOWS = OS.WINDOWS
OTHER = OS.OTHER


def get_platform() -> OS:
    """Return the current operating system as an :class:`OS` enum.

    Returns:
        OS: The current operating system as an enum member, or `OS.OTHER` if the platform is not recognized.
    """
    system = platform.system()
    return OS(system) if system in OS.__members__.values() else OS.OTHER


def is_macos() -> bool:
    """Return ``True`` if running on macOS."""
    return get_platform() == DARWIN


def is_windows() -> bool:
    """Return ``True`` if running on Windows."""
    return get_platform() == WINDOWS


def is_linux() -> bool:
    """Return ``True`` if running on Linux."""
    return get_platform() == LINUX


if __name__ == "__main__":
    detected_platform: OS = get_platform()
    match detected_platform:
        case OS.DARWIN:
            print("Detected macOS")
        case OS.LINUX:
            print("Detected Linux")
        case OS.WINDOWS:
            print("Detected Windows")
        case _:
            print(f"Detected unsupported platform: {detected_platform}")
