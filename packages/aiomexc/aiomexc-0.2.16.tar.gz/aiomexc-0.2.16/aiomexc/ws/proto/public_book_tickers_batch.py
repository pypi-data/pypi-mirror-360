from typing import Annotated, List

from dataclasses import dataclass, field
from pure_protobuf.annotations import Field
from pure_protobuf.message import BaseMessage

from .public_book_ticker import PublicBookTickerMessage


@dataclass
class PublicBookTickersBatchMessage(BaseMessage):
    items: Annotated[List[PublicBookTickerMessage], Field(1)] = field(
        default_factory=list
    )
