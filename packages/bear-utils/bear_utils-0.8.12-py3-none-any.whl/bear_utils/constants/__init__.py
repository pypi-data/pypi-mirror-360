"""Constants Module for Bear Utils."""

from pathlib import Path

from .server import BAD_REQUEST, CONFLICT, FORBIDDEN, PAGE_NOT_FOUND, SERVER_ERROR, SERVER_OK, UNAUTHORIZED

VIDEO_EXTS = [".mp4", ".mov", ".avi", ".mkv"]
"""Extensions for video files."""
IMAGE_EXTS = [".jpg", ".jpeg", ".png", ".gif"]
"""Extensions for image files."""
FILE_EXTS = IMAGE_EXTS + VIDEO_EXTS
"""Extensions for both image and video files."""

PATH_TO_DOWNLOADS = Path.home() / "Downloads"
"""Path to the Downloads folder."""
PATH_TO_PICTURES = Path.home() / "Pictures"
"""Path to the Pictures folder."""
GLOBAL_VENV = Path.home() / ".global_venv"
"""Path to the global virtual environment."""

__all__ = [
    "BAD_REQUEST",
    "CONFLICT",
    "FILE_EXTS",
    "FORBIDDEN",
    "GLOBAL_VENV",
    "IMAGE_EXTS",
    "PAGE_NOT_FOUND",
    "PATH_TO_DOWNLOADS",
    "PATH_TO_PICTURES",
    "SERVER_ERROR",
    "SERVER_OK",
    "UNAUTHORIZED",
    "VIDEO_EXTS",
]
