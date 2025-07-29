from typing import cast
from dataclasses import dataclass

from aiomexc.ws.proto import PushMessage
from aiomexc.ws.proto.public_aggre_deals import (
    PublicAggreDealItemMessage as ProtoPublicAggreDealItemMessage,
)

from .base import BaseMessage


@dataclass
class PublicAggreDealItemMessage(BaseMessage):
    price: str
    quantity: str
    trade_type: int
    time: int

    @classmethod
    def from_proto(
        cls, message: ProtoPublicAggreDealItemMessage
    ) -> "PublicAggreDealItemMessage":
        return cls(
            price=message.price,
            quantity=message.quantity,
            trade_type=message.trade_type,
            time=message.time,
        )


@dataclass
class PublicAggreDealsMessage(BaseMessage):
    deals: list[PublicAggreDealItemMessage]
    symbol: str
    time: int

    @classmethod
    def from_proto(cls, message: PushMessage) -> "PublicAggreDealsMessage":
        assert message.public_aggre_deals is not None, "public_aggre_deals is None"

        return cls(
            deals=[
                PublicAggreDealItemMessage.from_proto(deal)
                for deal in message.public_aggre_deals.deals
            ],
            symbol=cast(str, message.symbol),
            time=cast(int, message.send_time),
        )
