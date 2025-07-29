from dataclasses import dataclass, field
from typing import Annotated, List

from pure_protobuf.annotations import Field
from pure_protobuf.message import BaseMessage


@dataclass
class PublicIncreaseDepthItemMessage(BaseMessage):
    price: Annotated[str, Field(1)] = ""
    quantity: Annotated[str, Field(2)] = ""


@dataclass
class PublicIncreaseDepthsMessage(BaseMessage):
    asks: Annotated[List[PublicIncreaseDepthItemMessage], Field(1)] = field(
        default_factory=list
    )
    bids: Annotated[List[PublicIncreaseDepthItemMessage], Field(2)] = field(
        default_factory=list
    )
    event_type: Annotated[str, Field(3)] = ""
    version: Annotated[str, Field(4)] = ""
