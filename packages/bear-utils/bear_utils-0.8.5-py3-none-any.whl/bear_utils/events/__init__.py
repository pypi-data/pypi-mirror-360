"""A module for event handling in Bear Utils."""

from .events_class import Events
from .events_module import clear_all, clear_handlers_for_event, dispatch_event, event_handler, set_handler

subscribe = event_handler
publish = dispatch_event

__all__ = [
    "Events",
    "clear_all",
    "clear_handlers_for_event",
    "dispatch_event",
    "event_handler",
    "publish",
    "set_handler",
    "subscribe",
]
