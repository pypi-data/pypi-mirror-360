import asyncio
import logging
import time

from collections import defaultdict
from typing import (
    Callable,
    Coroutine,
    Any,
    Literal,
    TypeVar,
    Generic,
    Type,
    cast,
    AsyncGenerator,
)
from urllib.parse import urljoin

from aiomexc import MexcClient
from aiomexc.exceptions import (
    MexcWsStreamsLimit,
    MexcWsNoStreamsProvided,
    MexcWsNoCredentialsProvided,
    MexcWsInvalidStream,
    MexcWsPrivateStream,
    MexcWsConnectionClosed,
    MexcApiKeyInvalid,
    MexcWsConnectionHandshakeError,
    MexcWsConnectionTimeoutError,
)

from .proto import PushMessage

from .session.base import BaseWsSession, EventMessage, ConnectionMessage
from .credentials import WSCredentials
from .dispatcher import EventType, EventDispatcher
from .messages import (
    ListenKeyExtendedMessage,
    PublicAggreDealsMessage,
    BaseMessage,
    PrivateOrdersMessage,
    PrivateDealsMessage,
)

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseMessage)


class StreamHandler(Generic[T]):
    def __init__(
        self,
        handler: Callable[[T], Coroutine[Any, Any, None]],
        message_type: Type[T],
        handle_as_task: bool = True,
    ):
        self.handler = handler
        self.message_type = message_type
        self.handle_as_task = handle_as_task

    async def __call__(self, msg: PushMessage) -> None:
        if msg.message is None:
            return

        await self.handler(self.message_type.from_proto(msg))


class WSConnection:
    STREAM_TYPES = {
        "spot@public.aggre.deals.v3.api.pb": PublicAggreDealsMessage,
        "spot@private.orders.v3.api.pb": PrivateOrdersMessage,
        "spot@private.deals.v3.api.pb": PrivateDealsMessage,
    }

    def __init__(
        self,
        client: MexcClient,
        session: BaseWsSession,
        credentials: WSCredentials | None = None,
        base_url: str = "wss://wbs-api.mexc.com/ws",
    ):
        self._client = client
        self._streams = []
        self._credentials = credentials
        self._is_private = credentials is not None
        self._ping_task: asyncio.Task | None = None
        self._listen_key_update_task: asyncio.Task | None = None
        self._base_url = base_url
        self._session = session
        self._is_listening = False
        self._shutdown_event = asyncio.Event()

        self._events: dict[EventType, EventDispatcher] = {
            event_type: EventDispatcher(event_type) for event_type in EventType
        }

        self._stream_handlers: defaultdict[str, list[StreamHandler]] = defaultdict(list)
        self._active_tasks: set[asyncio.Task] = set()
        self._connected = False

    def on_connect(self, handler: Callable[[], Coroutine[Any, Any, None]]) -> None:
        self._events[EventType.CONNECT].add(handler)

    def on_listen_key_extended(
        self, handler: Callable[[ListenKeyExtendedMessage], Coroutine[Any, Any, None]]
    ) -> None:
        self._events[EventType.LISTEN_KEY_EXTENDED].add(handler)

    def on_subscription(
        self, handler: Callable[[dict], Coroutine[Any, Any, None]]
    ) -> None:
        self._events[EventType.SUBSCRIPTION].add(handler)

    def on_disconnect(self, handler: Callable[[], Coroutine[Any, Any, None]]) -> None:
        self._events[EventType.DISCONNECT].add(handler)

    def on_message(
        self, handler: Callable[[PushMessage], Coroutine[Any, Any, None]]
    ) -> None:
        self._events[EventType.MESSAGE].add(handler)

    def on_error(
        self, handler: Callable[[Exception], Coroutine[Any, Any, None]]
    ) -> None:
        self._events[EventType.ERROR].add(handler)

    def on_ping(self, handler: Callable[[], Coroutine[Any, Any, None]]) -> None:
        self._events[EventType.PING].add(handler)

    def on_pong(self, handler: Callable[[], Coroutine[Any, Any, None]]) -> None:
        self._events[EventType.PONG].add(handler)

    def _get_message_type(self, stream: str) -> Type[BaseMessage] | None:
        """Get the message type for a given stream."""
        for pattern, msg_type in self.STREAM_TYPES.items():
            if pattern in stream:
                return msg_type
        return None

    def _cancel_service_tasks(self):
        if self._ping_task:
            self._ping_task.cancel()
        if self._listen_key_update_task:
            self._listen_key_update_task.cancel()

    def _start_service_tasks(self):
        self._ping_task = asyncio.create_task(self.keepalive_ping())
        if self._is_private:
            self._listen_key_update_task = asyncio.create_task(
                self.keepalive_extend_listen_key()
            )

    def _restart_service_tasks(self):
        self._cancel_service_tasks()
        self._start_service_tasks()

    def _register_channel_handler(
        self,
        stream: str,
        handler: Callable[[T], Coroutine[Any, Any, None]],
        private: bool = False,
        handle_as_task: bool = True,
    ) -> Callable[[T], Coroutine[Any, Any, None]]:
        """Register a handler for a specific channel and add the channel to streams."""
        if len(self._streams) + 1 > 30:
            raise MexcWsStreamsLimit(
                stream_count=len(self._streams) + 1, max_streams=30
            )

        if private and not self._is_private:
            raise MexcWsPrivateStream(stream=stream)

        message_type = self._get_message_type(stream)
        if message_type is None:
            raise MexcWsInvalidStream(stream=stream)

        self._streams.append(stream)
        self._stream_handlers[stream].append(
            StreamHandler(handler, cast(Type[T], message_type), handle_as_task)
        )
        return handler

    def aggre_deals(
        self,
        symbol: str,
        interval: Literal["10ms", "100ms"] = "10ms",
        handle_as_task: bool = True,
    ):
        def decorator(
            handler: Callable[[PublicAggreDealsMessage], Coroutine[Any, Any, None]],
        ) -> Callable[[PublicAggreDealsMessage], Coroutine[Any, Any, None]]:
            channel = f"spot@public.aggre.deals.v3.api.pb@{interval}@{symbol}"
            return self._register_channel_handler(channel, handler, handle_as_task)

        return decorator

    def private_orders(self, handle_as_task: bool = True):
        def decorator(
            handler: Callable[[PrivateOrdersMessage], Coroutine[Any, Any, None]],
        ) -> Callable[[PrivateOrdersMessage], Coroutine[Any, Any, None]]:
            channel = "spot@private.orders.v3.api.pb"
            return self._register_channel_handler(
                channel, handler, private=True, handle_as_task=handle_as_task
            )

        return decorator

    def private_deals(self, handle_as_task: bool = True):
        def decorator(
            handler: Callable[[PrivateDealsMessage], Coroutine[Any, Any, None]],
        ) -> Callable[[PrivateDealsMessage], Coroutine[Any, Any, None]]:
            channel = "spot@private.deals.v3.api.pb"
            return self._register_channel_handler(
                channel, handler, private=True, handle_as_task=handle_as_task
            )

        return decorator

    def _add_task(self, coro: Coroutine[Any, Any, None]) -> None:
        """Add a task to the active tasks set and remove it when done."""
        task = asyncio.create_task(coro)
        self._active_tasks.add(task)
        task.add_done_callback(self._active_tasks.discard)

    async def _trigger_event(self, event: EventType, *args: Any) -> None:
        """Trigger handlers for a specific event in separate tasks."""
        for handler in self._events[event].handlers:
            self._add_task(handler(*args))

        # If this isn't an error event, and there was an exception, trigger error handlers
        if event != EventType.ERROR and args and isinstance(args[0], Exception):
            await self._trigger_event(EventType.ERROR, args[0])

    async def _trigger_channel_handlers(
        self, channel: str, message: PushMessage
    ) -> None:
        """Trigger channel handlers in separate tasks."""
        for handler in self._stream_handlers.get(channel, []):
            handle_update = handler(message)
            if handler.handle_as_task:
                self._add_task(handle_update)
            else:
                await handle_update

        await self._trigger_event(EventType.MESSAGE, message)

    def is_sub_message(self, message: dict) -> bool:
        if messages := message.get("msg"):
            return all(param in self._streams for param in messages.split(","))
        return False

    def is_pong_message(self, message: dict) -> bool:
        return message.get("msg") == "PONG"

    async def keepalive_ping(self):
        """
        Function to send keepalive ping every 30 seconds
        30 seconds is recommended by MEXC API docs: https://mexcdevelop.github.io/apidocs/spot_v3_en/#websocket-market-streams
        """
        while not self._shutdown_event.is_set():
            await asyncio.sleep(30)
            await self._session.ping()
            await self._trigger_event(EventType.PING)
            logger.debug("Keepalive ping sent")

    async def keepalive_extend_listen_key(self):
        """
        Function to update listen key dynamically based on its expiration time
        We update the key 5 minutes before it expires to avoid connection issues
        """
        if self._credentials is None or self._credentials.listen_key is None:
            raise MexcWsNoCredentialsProvided()

        while not self._shutdown_event.is_set():
            # Calculate time until expiration minus 5 minutes buffer
            now = int(time.time())
            if self._credentials.expires_at is None:
                # If expires_at is None, use default 30 minutes
                sleep_time = 1800 - 300  # 30 minutes - 5 minutes buffer
            else:
                time_until_expiry = self._credentials.expires_at - now
                sleep_time = max(
                    0, time_until_expiry - 300
                )  # 300 seconds = 5 minutes buffer

            if sleep_time > 0:
                logger.debug("Sleeping for %s seconds to extend listen key", sleep_time)
                await asyncio.sleep(sleep_time)

            response = await self._client.extend_listen_key(
                credentials=self._credentials, listen_key=self._credentials.listen_key
            )
            self._credentials.update(response.listen_key)
            await self._trigger_event(
                EventType.LISTEN_KEY_EXTENDED,
                ListenKeyExtendedMessage(
                    listen_key=self._credentials.listen_key,
                    expires_at=cast(int, self._credentials.expires_at),
                ),
            )
            logger.debug("Listen key extended")

    async def get_listen_key(self) -> str | None:
        """
        Get listen key for subscription to private streams
        If listen key is not provided, it will be created, else extended
        """
        if self._credentials is None:
            raise MexcWsNoCredentialsProvided()

        if self._credentials.is_expired():
            response = await self._client.create_listen_key(
                credentials=self._credentials
            )
            self._credentials.update(response.listen_key)
            await self._trigger_event(
                EventType.LISTEN_KEY_EXTENDED,
                ListenKeyExtendedMessage(
                    listen_key=cast(str, self._credentials.listen_key),
                    expires_at=cast(int, self._credentials.expires_at),
                ),
            )

        return self._credentials.listen_key

    async def connect(self):
        """
        Connect to MEXC WebSocket Server and subscribe to streams
        If this is private connection, connections will be created with listen key
        """
        if len(self._streams) == 0:
            raise MexcWsNoStreamsProvided()

        url = self._base_url
        if self._is_private:
            listen_key = await self.get_listen_key()
            url = urljoin(url, f"?listenKey={listen_key}")

        while True:
            try:
                await self._session.connect(url)
                break
            except MexcWsConnectionHandshakeError as e:
                logger.error("Connection handshake failed: %s", e)
                await asyncio.sleep(1)

            except MexcWsConnectionTimeoutError as e:
                logger.error("Connection timeout: %s", e)
                await asyncio.sleep(1)

        await self._session.subscribe(self._streams)

        self._restart_service_tasks()

        await self._trigger_event(EventType.CONNECT)

    async def _listen_updates(
        self,
    ) -> AsyncGenerator[EventMessage | ConnectionMessage, None]:
        while not self._shutdown_event.is_set():
            try:
                if not self._connected:
                    await self.connect()
                    self._connected = True

                msg = await self._session.receive()

            except MexcWsConnectionClosed:
                logger.debug("Connection closed")
                self._connected = False
                continue

            except MexcApiKeyInvalid:
                logger.warning("MexcApiKeyInvalid, closing connection")
                await self.close()
                break

            except Exception as e:
                logger.error(
                    "Error listening to updates: %s: %s",
                    e.__class__.__name__,
                    e,
                )
                await self._trigger_event(EventType.ERROR, e)
                if not self._shutdown_event.is_set():
                    raise

            yield msg

    async def _listening(self):
        try:
            self._is_listening = True
            async for msg in self._listen_updates():
                if isinstance(msg, EventMessage):
                    await self._trigger_channel_handlers(
                        msg.message.channel, msg.message
                    )
                elif isinstance(msg, ConnectionMessage):
                    if self.is_sub_message(msg.message):
                        await self._trigger_event(EventType.SUBSCRIPTION, msg.message)
                    elif self.is_pong_message(msg.message):
                        await self._trigger_event(EventType.PONG)

        finally:
            self._is_listening = False
            logger.info("Listening stopped")

    async def start_listening(self):
        """Start listening to WebSocket updates."""
        if self._is_listening:
            logger.warning("Already listening")
            return

        self._shutdown_event.clear()
        await self._listening()

    async def stop_listening(self):
        """Gracefully stop listening to WebSocket updates."""
        if not self._is_listening:
            logger.warning("Not listening")
            return

        self._shutdown_event.set()

        # Cancel all active tasks
        for task in self._active_tasks:
            if not task.done():
                task.cancel()

        # Wait for all tasks to complete
        if self._active_tasks:
            await asyncio.gather(*self._active_tasks, return_exceptions=True)

        # Close the WebSocket connection
        await self.close()

    async def close(self):
        try:
            if self._ping_task and not self._ping_task.done():
                self._ping_task.cancel()

            if self._listen_key_update_task and not self._listen_key_update_task.done():
                self._listen_key_update_task.cancel()

            await self._session.close()
            await self._trigger_event(EventType.DISCONNECT)
        except Exception as e:
            await self._trigger_event(EventType.ERROR, e)
            raise
