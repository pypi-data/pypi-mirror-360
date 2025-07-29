from dataclasses import dataclass
from typing import Annotated, Optional

from pure_protobuf.annotations import Field
from pure_protobuf.message import BaseMessage


@dataclass
class PrivateOrdersMessage(BaseMessage):
    id: Annotated[str, Field(1)] = ""
    client_id: Annotated[str, Field(2)] = ""
    price: Annotated[str, Field(3)] = ""
    quantity: Annotated[str, Field(4)] = ""
    amount: Annotated[str, Field(5)] = ""
    avg_price: Annotated[str, Field(6)] = ""
    order_type: Annotated[int, Field(7)] = 0
    trade_type: Annotated[int, Field(8)] = 0
    is_maker: Annotated[bool, Field(9)] = False
    remain_amount: Annotated[str, Field(10)] = ""
    remain_quantity: Annotated[str, Field(11)] = ""
    last_deal_quantity: Annotated[Optional[str], Field(12)] = None
    cumulative_quantity: Annotated[str, Field(13)] = ""
    cumulative_amount: Annotated[str, Field(14)] = ""
    status: Annotated[int, Field(15)] = 0
    create_time: Annotated[int, Field(16)] = 0

    market: Annotated[Optional[str], Field(17)] = None
    trigger_type: Annotated[Optional[int], Field(18)] = None
    trigger_price: Annotated[Optional[str], Field(19)] = None
    state: Annotated[Optional[int], Field(20)] = None
    oco_id: Annotated[Optional[str], Field(21)] = None
    route_factor: Annotated[Optional[str], Field(22)] = None
    symbol_id: Annotated[Optional[str], Field(23)] = None
    market_id: Annotated[Optional[str], Field(24)] = None
    market_currency_id: Annotated[Optional[str], Field(25)] = None
    currency_id: Annotated[Optional[str], Field(26)] = None
