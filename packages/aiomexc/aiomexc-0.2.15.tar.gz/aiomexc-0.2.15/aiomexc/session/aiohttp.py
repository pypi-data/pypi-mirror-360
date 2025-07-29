import asyncio
import ssl

from typing import Any, Type, cast
import certifi

from aiohttp import ClientSession, TCPConnector, ClientTimeout, ClientError
from aiohttp.hdrs import USER_AGENT
from aiohttp.http import SERVER_SOFTWARE

from aiomexc.methods import MexcMethod
from aiomexc.types import MexcType
from aiomexc.__meta__ import __version__
from aiomexc import loggers
from aiomexc.exceptions import MexcNetworkError

from .base import BaseSession, Credentials


class AiohttpSession(BaseSession):
    def __init__(self, limit: int = 100, **kwargs: Any):
        super().__init__(**kwargs)

        self._session: ClientSession | None = None
        self._connector_type: Type[TCPConnector] = TCPConnector
        self._connector_init: dict[str, Any] = {
            "ssl": ssl.create_default_context(cafile=certifi.where()),
            "limit": limit,
            "ttl_dns_cache": 3600,  # Workaround for https://github.com/aiogram/aiogram/issues/1500
        }
        self._should_reset_connector = True  # flag determines connector state

    async def create_session(self) -> ClientSession:
        if self._should_reset_connector:
            await self.close()

        if self._session is None or self._session.closed:
            self._session = ClientSession(
                connector=self._connector_type(**self._connector_init),
                headers={
                    USER_AGENT: f"{SERVER_SOFTWARE} aiomexc/{__version__}",
                },
            )
            self._should_reset_connector = False

        return self._session

    async def close(self) -> None:
        if self._session is not None and not self._session.closed:
            await self._session.close()

            # Wait 250 ms for the underlying SSL connections to close
            # https://docs.aiohttp.org/en/stable/client_advanced.html#graceful-shutdown
            await asyncio.sleep(0.25)

    async def request(
        self,
        method: MexcMethod[MexcType],
        credentials: Credentials | None = None,
        timeout: float | None = None,
    ) -> MexcType:
        session = await self.create_session()
        url, params, headers = self.prepare_request(method, credentials)

        loggers.client.debug(
            "Requesting %s %s with params %s", method.__api_http_method__, url, params
        )

        try:
            async with session.request(
                method.__api_http_method__,
                url,
                params=params,
                headers=headers,
                timeout=ClientTimeout(
                    total=self.timeout if timeout is None else timeout
                ),
            ) as resp:
                raw_result = await resp.text()
        except asyncio.TimeoutError:
            raise MexcNetworkError(method=method, message="Request timeout error")
        except ClientError as e:
            raise MexcNetworkError(method=method, message=f"{type(e).__name__}: {e}")

        loggers.client.debug("Response: %s", raw_result)
        response = self.check_response(
            method=method, status_code=resp.status, content=raw_result
        )
        return cast(MexcType, response.result)

    async def __aenter__(self) -> "AiohttpSession":
        await self.create_session()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await self.close()
