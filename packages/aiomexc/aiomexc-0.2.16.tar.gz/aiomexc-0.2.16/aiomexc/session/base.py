import json
import time
import hmac
import hashlib

from urllib.parse import urlencode, urljoin
from abc import ABC, abstractmethod
from typing import Callable, Any, Final, cast
from dataclasses import dataclass

from http import HTTPStatus
from adaptix.load_error import LoadError
from aiomexc.methods import MexcMethod
from aiomexc.types import MexcResult, MexcType
from aiomexc.exceptions import (
    MexcBadRequest,
    MexcNotFound,
    MexcApiKeyInvalid,
    MexcApiKeyMissing,
    MexcAPIError,
    MexcApiInvalidListenKey,
    MexcApiIpNotAllowed,
    MexcApiSignatureInvalid,
    MexcApiOpenOrdersTooMany,
    MexcApiInsufficientRights,
    MexcApiRateLimitExceeded,
    MexcApiRequireKyc,
    MexcApiOversold,
    MexcApiInsufficientBalance,
    ClientDecodeError,
    MexcApiCredentialsMissing,
    MexcApiRiskControlError,
)
from aiomexc.retort import _retort

_JsonLoads = Callable[..., Any]
_JsonDumps = Callable[..., str]
DEFAULT_TIMEOUT: Final[float] = 60.0
BASE_URL = "https://api.mexc.com/api/v3/"


@dataclass
class Credentials:
    access_key: str
    secret_key: str


class BaseSession(ABC):
    def __init__(
        self,
        json_loads: _JsonLoads = json.loads,
        json_dumps: _JsonDumps = json.dumps,
        timeout: float = DEFAULT_TIMEOUT,
        recv_window: int = 30000,
        base_url: str = BASE_URL,
    ):
        self.json_loads = json_loads
        self.json_dumps = json_dumps
        self.timeout = timeout
        self.recv_window = recv_window
        self._base_url = base_url

        self._map_error_code_to_exception = {
            700004: MexcBadRequest,  # Param 'origClientOrderId' or 'orderId' must be sent, but both were empty/null
            400: MexcBadRequest,  # api key required
            -1121: MexcBadRequest,  # Invalid symbol
            -2013: MexcNotFound,  # Order does not exist
            10072: MexcApiKeyInvalid,  # Invalid API-Key format
            402: MexcApiKeyMissing,  # API-Key missing, not sure
            730708: MexcApiInvalidListenKey,  # Invalid listen key
            700006: MexcApiIpNotAllowed,  # IP [x] not in the ip white list
            700002: MexcApiSignatureInvalid,  # Signature for this request is not valid.
            30069: MexcApiOpenOrdersTooMany,  # Open orders too many
            700007: MexcApiInsufficientRights,  # Insufficient rights with this API key
            429: MexcApiRateLimitExceeded,  # Rate limit exceeded
            200010: MexcApiRequireKyc,  # User requires KYC
            200006: MexcApiRequireKyc,  # User requires KYC
            30005: MexcApiOversold,  # Order is oversold
            30004: MexcApiInsufficientBalance,  # Insufficient balance
            30019: MexcApiRiskControlError,  # Probably, risk control is triggered
        }
        self._headers = {
            "Content-Type": "application/json",
        }

    def encrypt_params(self, secret_key: str, params: dict | None = None) -> dict:
        """
        Encrypt params for auth required requests

        :param secret_key: Secret key
        :param params: Params to encrypt
        :return: Encrypted params
        """
        if params is not None:
            params = {k: v for k, v in params.items() if v is not None}
        else:
            params = {}

        params["recvWindow"] = self.recv_window
        params["timestamp"] = int(time.time() * 1000)  # timestamp in milliseconds

        encoded_params = urlencode(params)
        params["signature"] = hmac.new(
            secret_key.encode(), encoded_params.encode(), hashlib.sha256
        ).hexdigest()
        return params

    def check_response(
        self, method: MexcMethod[MexcType], status_code: int, content: str
    ) -> MexcResult[MexcType]:
        try:
            json_data = self.json_loads(content)
        except Exception as e:
            raise ClientDecodeError(
                message="Failed to decode object",
                original=e,
                data=content,
            )

        api_code = 200
        msg = None

        if isinstance(
            json_data, dict
        ):  # we can trust the api that the error will not be returned in the list
            api_code = int(json_data.get("code", 200))
            msg = json_data.get("msg")

        wrapped_result = {
            "ok": status_code < 400,
            "msg": msg,
            "code": api_code,
            "result": json_data if api_code == 200 else None,
        }  # this is needed, because mexc api don't have stable response structure

        try:
            response_type = MexcResult[method.__returning__]
            response = _retort.load(wrapped_result, response_type)
        except LoadError as e:
            raise ClientDecodeError(
                message="Failed to deserialize object",
                original=e,
                data=wrapped_result,
            )

        if HTTPStatus.OK <= status_code <= HTTPStatus.IM_USED and response.ok:
            return response

        message = cast(str, response.msg)

        if exception_cls := self._map_error_code_to_exception.get(api_code):
            raise exception_cls(
                method=method,
                message=message,
                error_code=api_code,
            )

        raise MexcAPIError(
            method=method,
            message=message,
            error_code=api_code,
        )

    def prepare_request(
        self,
        method: MexcMethod[MexcType],
        credentials: Credentials | None = None,
    ) -> tuple[str, dict, dict]:
        params = _retort.dump(method)
        headers = self._headers.copy()

        if method.__requires_auth__:
            if credentials is None:
                raise MexcApiCredentialsMissing(method)

            params = self.encrypt_params(credentials.secret_key, params)
            headers["X-MEXC-APIKEY"] = credentials.access_key

        return urljoin(self._base_url, method.__api_method__), params, headers

    @abstractmethod
    async def request(
        self,
        method: MexcMethod[MexcType],
        credentials: Credentials | None = None,
        timeout: float | None = None,
    ) -> MexcType:  # pragma: no cover
        """
        Make request to Mexc API

        :param method: Method instance
        :param credentials: Optional credentials to use for this specific request
        :param timeout: Request timeout
        :return:
        :raise MexcAPIError:
        """
        pass

    @abstractmethod
    async def close(self) -> None:  # pragma: no cover
        """
        Close client session
        """
        pass
