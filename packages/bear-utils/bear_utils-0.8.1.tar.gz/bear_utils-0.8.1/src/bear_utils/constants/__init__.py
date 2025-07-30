"""Constants Module for Bear Utils."""

from pathlib import Path

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
