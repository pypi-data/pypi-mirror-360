from typing import cast
from dataclasses import dataclass

from aiomexc.ws.proto import PushMessage

from .base import BaseMessage


@dataclass
class PrivateOrdersMessage(BaseMessage):
    symbol: str
    id: str
    client_id: str
    price: str
    quantity: str
    amount: str
    avg_price: str
    order_type: int
    trade_type: int
    is_maker: bool
    remain_amount: str
    remain_quantity: str
    last_deal_quantity: str | None
    cumulative_quantity: str
    cumulative_amount: str
    status: int
    create_time: int

    @classmethod
    def from_proto(cls, message: PushMessage) -> "PrivateOrdersMessage":
        assert message.private_orders is not None, "private_orders is None"

        return cls(
            symbol=cast(str, message.symbol),
            id=message.private_orders.id,
            client_id=message.private_orders.client_id,
            price=message.private_orders.price,
            quantity=message.private_orders.quantity,
            amount=message.private_orders.amount,
            avg_price=message.private_orders.avg_price,
            order_type=message.private_orders.order_type,
            trade_type=message.private_orders.trade_type,
            is_maker=message.private_orders.is_maker,
            remain_amount=message.private_orders.remain_amount,
            remain_quantity=message.private_orders.remain_quantity,
            last_deal_quantity=message.private_orders.last_deal_quantity,
            cumulative_quantity=message.private_orders.cumulative_quantity,
            cumulative_amount=message.private_orders.cumulative_amount,
            status=message.private_orders.status,
            create_time=message.private_orders.create_time,
        )
