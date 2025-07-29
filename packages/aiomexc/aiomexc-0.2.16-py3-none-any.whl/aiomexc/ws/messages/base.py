from abc import ABC, abstractmethod

from aiomexc.ws.proto import PushMessage


class BaseMessage(ABC):
    @classmethod
    @abstractmethod
    def from_proto(cls, proto: PushMessage) -> type:
        raise NotImplementedError
