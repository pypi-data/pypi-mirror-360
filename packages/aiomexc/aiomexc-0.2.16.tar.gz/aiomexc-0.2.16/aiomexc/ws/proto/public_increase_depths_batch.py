from typing import Annotated, List

from dataclasses import dataclass, field
from pure_protobuf.annotations import Field
from pure_protobuf.message import BaseMessage

from .public_increase_depths import PublicIncreaseDepthsMessage


@dataclass
class PublicIncreaseDepthsBatchMessage(BaseMessage):
    items: Annotated[List[PublicIncreaseDepthsMessage], Field(1)] = field(
        default_factory=list
    )
