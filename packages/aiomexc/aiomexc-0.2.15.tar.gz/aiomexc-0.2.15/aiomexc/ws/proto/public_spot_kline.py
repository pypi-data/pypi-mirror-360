from dataclasses import dataclass
from typing import Annotated

from pure_protobuf.annotations import Field
from pure_protobuf.message import BaseMessage


@dataclass
class PublicSpotKlineMessage(BaseMessage):
    interval: Annotated[str, Field(1)] = ""
    window_start: Annotated[int, Field(2)] = 0
    opening_price: Annotated[str, Field(3)] = ""
    closing_price: Annotated[str, Field(4)] = ""
    highest_price: Annotated[str, Field(5)] = ""
    lowest_price: Annotated[str, Field(6)] = ""
    volume: Annotated[str, Field(7)] = ""
    amount: Annotated[str, Field(8)] = ""
    window_end: Annotated[int, Field(9)] = 0
