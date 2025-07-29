import asyncio
from typing import cast

from aiohttp import ClientSession, ClientTimeout, ClientError
from aiohttp.hdrs import USER_AGENT
from aiohttp.http import SERVER_SOFTWARE
from aiohttp_socks import ProxyConnector

from aiomexc.methods import MexcMethod
from aiomexc.types import MexcType
from aiomexc.__meta__ import __version__
from aiomexc import loggers
from aiomexc.exceptions import MexcNetworkError
from aiomexc.session.aiohttp import AiohttpSession

from .credentials import CliCredentials


class CliAiohttpSession(AiohttpSession):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.proxy_sessions: dict[str, ClientSession] = {}

    async def create_session(
        self, credentials: CliCredentials | None = None
    ) -> ClientSession:
        if self._should_reset_connector:
            await self.close()

        socks5_proxy = credentials.socks5_proxy if credentials else None

        if socks5_proxy:
            if (
                socks5_proxy not in self.proxy_sessions
                or self.proxy_sessions[socks5_proxy].closed
            ):
                connector = ProxyConnector.from_url(socks5_proxy)
                self.proxy_sessions[socks5_proxy] = ClientSession(
                    connector=connector,
                    headers={
                        USER_AGENT: f"{SERVER_SOFTWARE} aiomexc/{__version__}",
                    },
                )
            return self.proxy_sessions[socks5_proxy]

        if self._session is None or self._session.closed:
            self._session = ClientSession(
                connector=self._connector_type(**self._connector_init),
                headers={
                    USER_AGENT: f"{SERVER_SOFTWARE} aiomexc/{__version__}",
                },
            )
            self._should_reset_connector = False

        return self._session

    async def request(
        self,
        method: MexcMethod[MexcType],
        credentials: CliCredentials | None = None,
        timeout: float | None = None,
    ) -> MexcType:
        session = await self.create_session(credentials)
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

    async def close(self) -> None:
        await super().close()
        for session in self.proxy_sessions.values():
            if not session.closed:
                await session.close()
        self.proxy_sessions.clear()
