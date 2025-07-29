from dataclasses import dataclass, field
from typing import Annotated, List

from pure_protobuf.annotations import Field
from pure_protobuf.message import BaseMessage


@dataclass
class PublicAggreDepthItemMessage(BaseMessage):
    price: Annotated[str, Field(1)] = ""
    quantity: Annotated[str, Field(2)] = ""


@dataclass
class PublicAggreDepthsMessage(BaseMessage):
    asks: Annotated[List[PublicAggreDepthItemMessage], Field(1)] = field(
        default_factory=list
    )
    bids: Annotated[List[PublicAggreDepthItemMessage], Field(2)] = field(
        default_factory=list
    )
    eventType: Annotated[str, Field(3)] = ""
    fromVersion: Annotated[str, Field(4)] = ""
    toVersion: Annotated[str, Field(5)] = ""
