from dataclasses import dataclass
from decimal import Decimal


@dataclass
class TickerPrice:
    symbol: str
    price: Decimal
