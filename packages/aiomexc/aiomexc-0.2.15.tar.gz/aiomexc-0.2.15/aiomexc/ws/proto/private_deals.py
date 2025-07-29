from dataclasses import dataclass
from typing import Annotated

from pure_protobuf.annotations import Field
from pure_protobuf.message import BaseMessage


@dataclass
class PrivateDealsMessage(BaseMessage):
    price: Annotated[str, Field(1)] = ""
    quantity: Annotated[str, Field(2)] = ""
    amount: Annotated[str, Field(3)] = ""

    trade_type: Annotated[int, Field(4)] = 0
    is_maker: Annotated[bool, Field(5)] = False
    is_self_trade: Annotated[bool, Field(6)] = False

    trade_id: Annotated[str, Field(7)] = ""
    client_order_id: Annotated[str, Field(8)] = ""
    order_id: Annotated[str, Field(9)] = ""

    fee_amount: Annotated[str, Field(10)] = ""
    fee_currency: Annotated[str, Field(11)] = ""

    time: Annotated[int, Field(12)] = 0
