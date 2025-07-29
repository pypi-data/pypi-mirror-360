from dataclasses import dataclass
from typing import cast

from aiomexc.ws.proto import PushMessage
from .base import BaseMessage


@dataclass
class PrivateDealsMessage(BaseMessage):
    symbol: str
    price: str
    quantity: str
    amount: str
    trade_type: int
    is_maker: bool
    is_self_trade: bool
    trade_id: str
    client_order_id: str
    order_id: str
    fee_amount: str
    fee_currency: str
    time: int

    @classmethod
    def from_proto(cls, message: PushMessage) -> "PrivateDealsMessage":
        assert message.private_deals is not None, "private_deals is None"

        return cls(
            symbol=cast(str, message.symbol),
            price=message.private_deals.price,
            quantity=message.private_deals.quantity,
            amount=message.private_deals.amount,
            trade_type=message.private_deals.trade_type,
            is_maker=message.private_deals.is_maker,
            is_self_trade=message.private_deals.is_self_trade,
            trade_id=message.private_deals.trade_id,
            client_order_id=message.private_deals.client_order_id,
            order_id=message.private_deals.order_id,
            fee_amount=message.private_deals.fee_amount,
            fee_currency=message.private_deals.fee_currency,
            time=message.private_deals.time,
        )
