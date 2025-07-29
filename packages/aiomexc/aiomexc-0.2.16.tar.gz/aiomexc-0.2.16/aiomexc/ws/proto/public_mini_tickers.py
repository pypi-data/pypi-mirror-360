from typing import Annotated, List

from dataclasses import dataclass, field
from pure_protobuf.annotations import Field
from pure_protobuf.message import BaseMessage

from .public_mini_ticker import PublicMiniTickerMessage


@dataclass
class PublicMiniTickersMessage(BaseMessage):
    items: Annotated[List[PublicMiniTickerMessage], Field(1)] = field(
        default_factory=list
    )
