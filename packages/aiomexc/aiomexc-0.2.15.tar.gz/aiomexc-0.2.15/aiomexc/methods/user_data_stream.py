from dataclasses import dataclass
from http import HTTPMethod

from aiomexc.types import ListenKey, ListenKeys
from .base import MexcMethod


@dataclass(kw_only=True)
class CreateListenKey(MexcMethod):
    __returning__ = ListenKey
    __api_http_method__ = HTTPMethod.POST
    __api_method__ = "userDataStream"
    __requires_auth__ = True


@dataclass(kw_only=True)
class GetListenKeys(MexcMethod):
    __returning__ = ListenKeys
    __api_http_method__ = HTTPMethod.GET
    __api_method__ = "userDataStream"
    __requires_auth__ = True


@dataclass
class ExtendListenKey(MexcMethod):
    __returning__ = ListenKey
    __api_http_method__ = HTTPMethod.PUT
    __api_method__ = "userDataStream"
    __requires_auth__ = True

    listen_key: str


@dataclass(kw_only=True)
class DeleteListenKey(MexcMethod):
    __returning__ = ListenKey
    __api_http_method__ = HTTPMethod.DELETE
    __api_method__ = "userDataStream"
    __requires_auth__ = True

    listen_key: str
