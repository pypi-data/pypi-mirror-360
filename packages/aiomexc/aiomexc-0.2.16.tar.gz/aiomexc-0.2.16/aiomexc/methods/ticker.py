from dataclasses import dataclass
from http import HTTPMethod

from aiomexc.types import TickerPrice
from .base import MexcMethod


@dataclass(kw_only=True)
class GetTickerPrice(MexcMethod):
    __returning__ = TickerPrice
    __api_http_method__ = HTTPMethod.GET
    __api_method__ = "ticker/price"
    __requires_auth__ = False

    symbol: str
