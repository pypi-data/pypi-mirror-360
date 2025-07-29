from dataclasses import dataclass
from typing import Optional, Annotated, ClassVar

from pure_protobuf.annotations import Field
from pure_protobuf.message import BaseMessage
from pure_protobuf.one_of import OneOf

from .private_account import PrivateAccountMessage
from .private_deals import PrivateDealsMessage
from .public_deals import PublicDealsMessage
from .public_increase_depths import PublicIncreaseDepthsMessage
from .public_limit_depths import PublicLimitDepthsMessage
from .private_orders import PrivateOrdersMessage
from .public_book_ticker import PublicBookTickerMessage
from .public_spot_kline import PublicSpotKlineMessage
from .public_mini_ticker import PublicMiniTickerMessage
from .public_mini_tickers import PublicMiniTickersMessage
from .public_book_tickers_batch import PublicBookTickersBatchMessage
from .public_increase_depths_batch import PublicIncreaseDepthsBatchMessage
from .public_aggre_depths import PublicAggreDepthsMessage
from .public_aggre_deals import PublicAggreDealsMessage
from .public_aggre_book_ticker import PublicAggreBookTickerMessage


@dataclass
class PushMessage(BaseMessage):
    channel: Annotated[str, Field(1)] = ""
    body: ClassVar[OneOf] = OneOf()
    which_body = body.which_one_of_getter()

    public_deals: Annotated[Optional[PublicDealsMessage], Field(301, one_of=body)] = (
        None
    )
    public_increase_depths: Annotated[
        Optional[PublicIncreaseDepthsMessage], Field(302, one_of=body)
    ] = None
    public_limit_depths: Annotated[
        Optional[PublicLimitDepthsMessage], Field(303, one_of=body)
    ] = None
    private_orders: Annotated[
        Optional[PrivateOrdersMessage], Field(304, one_of=body)
    ] = None
    public_book_ticker: Annotated[
        Optional[PublicBookTickerMessage], Field(305, one_of=body)
    ] = None
    private_deals: Annotated[Optional[PrivateDealsMessage], Field(306, one_of=body)] = (
        None
    )
    private_account: Annotated[
        Optional[PrivateAccountMessage], Field(307, one_of=body)
    ] = None
    public_spot_kline: Annotated[
        Optional[PublicSpotKlineMessage], Field(308, one_of=body)
    ] = None
    public_mini_ticker: Annotated[
        Optional[PublicMiniTickerMessage], Field(309, one_of=body)
    ] = None
    public_mini_tickers: Annotated[
        Optional[PublicMiniTickersMessage], Field(310, one_of=body)
    ] = None
    public_book_tickers_batch: Annotated[
        Optional[PublicBookTickersBatchMessage], Field(311, one_of=body)
    ] = None
    public_increase_depths_batch: Annotated[
        Optional[PublicIncreaseDepthsBatchMessage], Field(312, one_of=body)
    ] = None
    public_aggre_depths: Annotated[
        Optional[PublicAggreDepthsMessage], Field(313, one_of=body)
    ] = None
    public_aggre_deals: Annotated[
        Optional[PublicAggreDealsMessage], Field(314, one_of=body)
    ] = None
    public_aggre_book_ticker: Annotated[
        Optional[PublicAggreBookTickerMessage], Field(315, one_of=body)
    ] = None

    symbol: Annotated[Optional[str], Field(3)] = None
    symbol_id: Annotated[Optional[str], Field(4)] = None
    create_time: Annotated[Optional[int], Field(5)] = None
    send_time: Annotated[Optional[int], Field(6)] = None

    @classmethod
    def from_bytes(cls, data: bytes) -> "PushMessage":
        return cls.loads(data)

    @property
    def message_type(self) -> str | None:
        return self.which_body()

    @property
    def message(self) -> BaseMessage:
        if self.message_type is None:
            raise ValueError("message_type is None")
        return getattr(self, self.message_type)
