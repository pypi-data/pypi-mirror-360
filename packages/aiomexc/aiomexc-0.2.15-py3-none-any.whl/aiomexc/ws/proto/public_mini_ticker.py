from dataclasses import dataclass
from typing import Annotated

from pure_protobuf.annotations import Field
from pure_protobuf.message import BaseMessage


@dataclass
class PublicMiniTickerMessage(BaseMessage):
    symbol: Annotated[str, Field(1)] = ""
    price: Annotated[str, Field(2)] = ""
    rate: Annotated[str, Field(3)] = ""
    zoned_rate: Annotated[str, Field(4)] = ""
    high: Annotated[str, Field(5)] = ""
    low: Annotated[str, Field(6)] = ""
    volume: Annotated[str, Field(7)] = ""
    quantity: Annotated[str, Field(8)] = ""
    last_close_rate: Annotated[str, Field(9)] = ""
    last_close_zoned_rate: Annotated[str, Field(10)] = ""
    last_close_high: Annotated[str, Field(11)] = ""
    last_close_low: Annotated[str, Field(12)] = ""
