import logging

from enum import StrEnum
from typing import Callable, Coroutine, Any, TypeVar, Generic


logger = logging.getLogger(__name__)


class EventType(StrEnum):
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    MESSAGE = "message"
    ERROR = "error"
    PING = "ping"
    PONG = "pong"
    SUBSCRIPTION = "subscription"
    LISTEN_KEY_EXTENDED = "listen_key_extended"


T = TypeVar("T")


class EventDispatcher(Generic[T]):
    """Generic event dispatcher for handling event callbacks."""

    def __init__(self, event_type: EventType):
        self.event_type = event_type
        self.handlers: list[Callable[..., Coroutine[Any, Any, None]]] = []

    def add(self, handler: Callable[..., Coroutine[Any, Any, None]]) -> None:
        """Add a handler to this event."""
        self.handlers.append(handler)

    async def trigger(self, *args: Any) -> None:
        """Trigger all handlers registered for this event."""
        for handler in self.handlers:
            try:
                await handler(*args)
            except Exception as e:
                logger.exception(f"Error in {self.event_type.value} handler: {e}")
                # We don't trigger error handlers here to avoid potential infinite recursion
