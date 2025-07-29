from dataclasses import dataclass
from decimal import Decimal
from http import HTTPMethod

from aiomexc.types import Order, CreatedOrder, CanceledOrder
from aiomexc.enums import OrderSide, OrderType

from ..exceptions import (
    MexcBadRequestEitherParamsRequiredError,
    MexcBadRequestParamsRequiredError,
)
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
    __returning__ = CreatedOrder
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

    def __post_init__(self):
        if self.type == OrderType.LIMIT:
            if self.quantity is None or self.price is None:
                raise MexcBadRequestParamsRequiredError(
                    method=self,
                    required_params=["quantity", "price"],
                )
        elif self.type == OrderType.MARKET:
            if self.quote_order_qty is None:
                raise MexcBadRequestParamsRequiredError(
                    method=self,
                    required_params=["quote_order_qty"],
                )


@dataclass(kw_only=True)
class CancelOrder(MexcMethod):
    __returning__ = CanceledOrder
    __api_http_method__ = HTTPMethod.DELETE
    __api_method__ = "order"
    __requires_auth__ = True

    symbol: str
    order_id: str | None
    orig_client_order_id: str | None
    new_client_order_id: str | None

    def __post_init__(self):
        if (
            self.order_id is None
            and self.orig_client_order_id is None
            and self.new_client_order_id is None
        ):
            raise MexcBadRequestEitherParamsRequiredError(
                method=self,
                optional_params=[
                    "order_id",
                    "orig_client_order_id",
                    "new_client_order_id",
                ],
            )
