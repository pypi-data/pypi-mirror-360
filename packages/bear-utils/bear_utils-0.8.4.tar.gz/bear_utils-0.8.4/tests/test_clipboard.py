from unittest.mock import patch

import pytest

from bear_utils.extras._tools import ClipboardManager
from bear_utils.extras.platform_utils import OS


def mock_which_func(cmd: str) -> None | str:
    """Mock function to simulate shutil.which behavior for testing."""
    if cmd == "wl-copy":
        return "/usr/bin/wl-copy"
    if cmd == "wl-paste":
        return "/usr/bin/wl-paste"
    if cmd == "xclip":
        return "/usr/bin/xclip"

    return None


@patch("bear_utils.extras._tools.get_platform", return_value=OS.DARWIN)
def test_macos_commands(mock_platform) -> None:
    manager = ClipboardManager()
    assert manager._copy.command_name == "pbcopy"
    assert manager._paste.command_name == "pbpaste"


@patch("bear_utils.extras._tools.shutil.which")
@patch("bear_utils.extras._tools.get_platform", return_value=OS.LINUX)
def test_linux_wayland(mock_platform, mock_which) -> None:
    mock_which.side_effect = mock_which_func
    manager = ClipboardManager()
    assert manager._copy.command_name == "wl-copy"
    assert manager._paste.command_name == "wl-paste"


@patch("bear_utils.extras._tools.shutil.which", return_value=None)
@patch("bear_utils.extras._tools.get_platform", return_value=OS.LINUX)
def test_linux_no_clipboard(mock_platform, mock_which) -> None:
    with pytest.raises(RuntimeError):
        ClipboardManager()


@patch("bear_utils.extras._tools.get_platform", return_value=OS.WINDOWS)
def test_windows_commands(mock_platform) -> None:
    manager = ClipboardManager()
    assert manager._copy.cmd == "clip"
    assert manager._paste.cmd == "powershell Get-Clipboard"
