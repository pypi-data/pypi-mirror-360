from dataclasses import dataclass
from typing import Annotated

from pure_protobuf.annotations import Field
from pure_protobuf.message import BaseMessage


@dataclass
class PrivateAccountMessage(BaseMessage):
    v_coin_name: Annotated[str, Field(1)] = ""
    coin_id: Annotated[str, Field(2)] = ""
    balance_amount: Annotated[str, Field(3)] = ""
    balance_amount_change: Annotated[str, Field(4)] = ""
    frozen_amount: Annotated[str, Field(5)] = ""
    frozen_amount_change: Annotated[str, Field(6)] = ""
    type: Annotated[str, Field(7)] = ""
    timestamp: Annotated[int, Field(8)] = 0
