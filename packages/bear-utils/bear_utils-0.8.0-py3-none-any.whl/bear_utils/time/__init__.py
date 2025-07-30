"""A module for Bear Epoch Time utilities centering around the EpochTimestamp class."""

from importlib.metadata import version

from bear_epoch_time import EpochTimestamp, TimerData, TimeTools, add_ord_suffix, create_timer, timer
from bear_epoch_time.constants.date_related import (
    DATE_FORMAT,
    DATE_TIME_FORMAT,
    DT_FORMAT_WITH_SECONDS,
    DT_FORMAT_WITH_TZ,
    DT_FORMAT_WITH_TZ_AND_SECONDS,
    ET_TIME_ZONE,
    PT_TIME_ZONE,
    TIME_FORMAT_WITH_SECONDS,
    UTC_TIME_ZONE,
)

__version__: str = version(distribution_name="bear_epoch_time")

__all__ = [
    "DATE_FORMAT",
    "DATE_TIME_FORMAT",
    "DT_FORMAT_WITH_SECONDS",
    "DT_FORMAT_WITH_TZ",
    "DT_FORMAT_WITH_TZ_AND_SECONDS",
    "ET_TIME_ZONE",
    "PT_TIME_ZONE",
    "TIME_FORMAT_WITH_SECONDS",
    "UTC_TIME_ZONE",
    "EpochTimestamp",
    "TimeTools",
    "TimerData",
    "__version__",
    "add_ord_suffix",
    "create_timer",
    "timer",
]
