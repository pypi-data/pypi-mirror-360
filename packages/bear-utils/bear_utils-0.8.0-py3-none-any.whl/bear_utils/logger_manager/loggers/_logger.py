from logging import Logger

from ._base_logger import BaseLogger


class ExtraBaseLogger(Logger, BaseLogger):
    """Base logger class that extends the standard logging.Logger and BaseLogger.

    This class is intended to be used as a base for custom loggers that require
    additional functionality or attributes.
    """

    def __init__(self, name: str, level: int = 0, **kwargs):
        """Initialize the ExtraBaseLogger with a name and level."""
        super().__init__(name, level)
        BaseLogger.__init__(self, **kwargs)
