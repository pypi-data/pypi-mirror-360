from abc import (
    ABC,
    abstractmethod,
)
from typing import TYPE_CHECKING, ClassVar, Generic
from http import HTTPMethod

from aiomexc.types import MexcType


class MexcMethod(Generic[MexcType], ABC):
    if TYPE_CHECKING:
        __returning__: ClassVar[type]
        __api_http_method__: ClassVar[HTTPMethod]
        __api_method__: ClassVar[str]
        __requires_auth__: ClassVar[bool]
    else:

        @property
        @abstractmethod
        def __returning__(self) -> type:
            pass

        @property
        @abstractmethod
        def __api_http_method__(self) -> HTTPMethod:
            pass

        @property
        @abstractmethod
        def __api_method__(self) -> str:
            pass

        @property
        @abstractmethod
        def __requires_auth__(self) -> bool:
            pass
