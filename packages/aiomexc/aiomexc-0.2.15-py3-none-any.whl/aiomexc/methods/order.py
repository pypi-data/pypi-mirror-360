from dataclasses import dataclass
from decimal import Decimal
from http import HTTPMethod

from aiomexc.types import Order, CreateOrder as CreateOrderType
from aiomexc.enums import OrderSide, OrderType

from .base import MexcMethod


@dataclass(kw_only=True)
class QueryOrder(MexcMethod):
    __returning__ = Order
    __api_http_method__ = HTTPMethod.GET
    __api_method__ = "order"
    __requires_auth__ = True

    symbol: str
    order_id: str | None
    orig_client_order_id: str | None


@dataclass(kw_only=True)
class GetOpenOrders(MexcMethod):
    __returning__ = list[Order]
    __api_http_method__ = HTTPMethod.GET
    __api_method__ = "openOrders"
    __requires_auth__ = True

    symbol: str


@dataclass(kw_only=True)
class CreateOrder(MexcMethod):
    __returning__ = CreateOrderType
    __api_http_method__ = HTTPMethod.POST
    __api_method__ = "order"
    __requires_auth__ = True

    symbol: str
    side: OrderSide
    type: OrderType
    quantity: Decimal | None
    quote_order_qty: Decimal | None
    price: Decimal | None
    new_client_order_id: str | None
