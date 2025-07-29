from typing import TypeVar, Generic
from dataclasses import dataclass

MexcType = TypeVar("MexcType")


@dataclass
class MexcResult(Generic[MexcType]):
    ok: bool = True
    msg: str | None = None
    code: int | None = None
    result: MexcType | None = None
