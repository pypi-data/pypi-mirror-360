"""Event handling module for Bear Utils."""

import asyncio
from collections import defaultdict
from collections.abc import Callable
from functools import wraps
from types import MethodType
from typing import Any
import weakref
from weakref import WeakMethod, ref

from bear_utils.extras._async_helpers import is_async_function

Callback = Callable[..., Any]

_event_registry: dict[str, weakref.WeakSet[Callback]] = defaultdict(weakref.WeakSet)


def clear_handlers_for_event(event_name: str) -> None:
    """Remove all handlers associated with a specific event."""
    _event_registry.pop(event_name, None)


def clear_all() -> None:
    """Remove all registered event handlers."""
    _event_registry.clear()


def _make_callback(name: str) -> Callable[[Any], None]:
    """Create an internal callback to remove dead handlers."""

    def callback(weak_method: Any) -> None:
        _event_registry[name].remove(weak_method)
        if not _event_registry[name]:
            del _event_registry[name]

    return callback


def set_handler(name: str, func: Callback) -> None:
    """Register a function as a handler for a specific event."""
    if isinstance(func, MethodType):
        _event_registry[name].add(WeakMethod(func, _make_callback(name)))
    else:
        _event_registry[name].add(ref(func, _make_callback(name)))


def dispatch_event(name: str, *args, **kwargs) -> Any | None:
    """Dispatch an event to all registered handlers."""
    results: list[Any] = []
    for func in _event_registry.get(name, []):
        if is_async_function(func):
            result: Any = asyncio.run(func(*args, **kwargs))
        else:
            result: Any = func(*args, **kwargs)
            results.append(result)
    if not results:
        return None
    return results[0] if len(results) == 1 else results


def event_handler(event_name: str) -> Callable[[Callback], Callback]:
    """Decorator to register a callback as an event handler for a specific event."""

    def decorator(callback: Callback) -> Callback:
        @wraps(callback)
        def wrapper(*args, **kwargs) -> Any:
            """Wrapper to register the callback and call it."""
            return callback(*args, **kwargs)

        set_handler(event_name, wrapper)
        return wrapper

    return decorator
