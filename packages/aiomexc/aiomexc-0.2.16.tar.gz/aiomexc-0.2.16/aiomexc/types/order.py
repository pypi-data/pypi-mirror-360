from decimal import Decimal
from dataclasses import dataclass
from datetime import datetime

from aiomexc.enums import OrderStatus, OrderType, OrderSide


@dataclass
class Order:
    symbol: str
    order_id: str
    order_list_id: int | None
    client_order_id: str | None
    price: Decimal
    orig_qty: Decimal
    executed_qty: Decimal
    cummulative_quote_qty: Decimal
    status: OrderStatus
    time_in_force: int | None
    type: OrderType
    side: OrderSide
    stop_price: Decimal | None
    time: datetime
    update_time: datetime | None
    is_working: bool
    orig_quote_order_qty: Decimal | None


@dataclass
class CreatedOrder:
    symbol: str
    order_id: str
    order_list_id: int
    price: Decimal
    orig_qty: Decimal
    type: OrderType
    side: OrderSide
    transact_time: datetime


@dataclass
class CanceledOrder:
    symbol: str
    order_id: str
    price: Decimal
    orig_qty: Decimal
    executed_qty: Decimal
    cummulative_quote_qty: Decimal
    status: OrderStatus
    type: OrderType
    side: OrderSide
