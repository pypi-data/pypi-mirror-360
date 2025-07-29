from dataclasses import dataclass
from typing import Annotated

from pure_protobuf.annotations import Field
from pure_protobuf.message import BaseMessage


@dataclass
class PublicBookTickerMessage(BaseMessage):
    bid_price: Annotated[str, Field(1)] = ""
    bid_quantity: Annotated[str, Field(2)] = ""
    ask_price: Annotated[str, Field(3)] = ""
    ask_quantity: Annotated[str, Field(4)] = ""
