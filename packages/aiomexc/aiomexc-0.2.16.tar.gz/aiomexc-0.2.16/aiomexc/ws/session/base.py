import json

from typing import Callable, Any
from abc import ABC, abstractmethod
from dataclasses import dataclass

from aiomexc.ws.proto.message import PushMessage

_JsonLoads = Callable[..., Any]
_JsonDumps = Callable[..., str]


@dataclass
class EventMessage:
    message: PushMessage


@dataclass
class ConnectionMessage:
    message: dict


class BaseWsSession(ABC):
    def __init__(
        self,
        json_loads: _JsonLoads = json.loads,
        json_dumps: _JsonDumps = json.dumps,
    ):
        self.json_loads = json_loads
        self.json_dumps = json_dumps

    def dump_message(self, message: dict) -> str:
        return self.json_dumps(message)

    def load_json_message(self, message: str) -> dict:
        return self.json_loads(message)

    def load_message(self, message: bytes) -> PushMessage:
        return PushMessage.from_bytes(message)

    @abstractmethod
    async def connect(self, url: str) -> None:
        """
        Connect to the websocket
        """
        raise NotImplementedError

    @abstractmethod
    async def receive(self) -> EventMessage | ConnectionMessage:
        """
        Receive a message from the websocket
        """
        raise NotImplementedError

    @abstractmethod
    async def ping(self) -> None:
        """
        Ping the websocket
        """
        raise NotImplementedError

    @abstractmethod
    async def subscribe(self, streams: list[str]) -> None:
        """
        Subscribe to the streams
        """
        raise NotImplementedError

    @abstractmethod
    async def close(self) -> None:
        """
        Close client session
        """
        raise NotImplementedError
