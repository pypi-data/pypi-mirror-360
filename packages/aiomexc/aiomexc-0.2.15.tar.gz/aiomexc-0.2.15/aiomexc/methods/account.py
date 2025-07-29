from dataclasses import dataclass
from http import HTTPMethod

from aiomexc.types import AccountInformation
from .base import MexcMethod


@dataclass(kw_only=True)
class GetAccountInformation(MexcMethod):
    __returning__ = AccountInformation
    __api_http_method__ = HTTPMethod.GET
    __api_method__ = "account"
    __requires_auth__ = True
