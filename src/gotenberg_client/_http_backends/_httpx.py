# SPDX-FileCopyrightText: 2025-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Mapping
from collections.abc import MutableMapping
from typing import Any

import httpx

from gotenberg_client._errors import HttpStatusError
from gotenberg_client._http_backends._protocols import AuthType
from gotenberg_client._http_backends._protocols import RequestFiles


class HttpxResponseAdapter:
    """Wraps an httpx.Response to satisfy ResponseProtocol."""

    def __init__(self, response: httpx.Response) -> None:
        self._response = response

    @property
    def status_code(self) -> int:
        return self._response.status_code

    @property
    def headers(self) -> Mapping[str, str]:
        return self._response.headers

    @property
    def content(self) -> bytes:
        return self._response.content

    @property
    def is_server_error(self) -> bool:
        return self._response.is_server_error

    def raise_for_status(self) -> None:
        try:
            self._response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise HttpStatusError(response=self) from e

    def json(self) -> Any:
        return self._response.json()  # type: ignore[misc]


class HttpxSyncAdapter:
    """Wraps httpx.Client to satisfy SyncClientProtocol."""

    def __init__(self, client: httpx.Client) -> None:
        self._client = client

    @property
    def headers(self) -> MutableMapping[str, str]:
        return self._client.headers

    def post(
        self,
        url: str,
        *,
        headers: dict[str, str],
        data: dict[str, str],
        files: RequestFiles,
    ) -> HttpxResponseAdapter:
        resp = self._client.post(url=url, headers=headers, data=data, files=files)
        return HttpxResponseAdapter(resp)

    def get(
        self,
        url: str,
        *,
        headers: dict[str, str],
    ) -> HttpxResponseAdapter:
        resp = self._client.get(url, headers=headers)
        return HttpxResponseAdapter(resp)

    def close(self) -> None:
        self._client.close()


class HttpxAsyncAdapter:
    """Wraps httpx.AsyncClient to satisfy AsyncClientProtocol."""

    def __init__(self, client: httpx.AsyncClient) -> None:
        self._client = client

    @property
    def headers(self) -> MutableMapping[str, str]:
        return self._client.headers

    async def post(
        self,
        url: str,
        *,
        headers: dict[str, str],
        data: dict[str, str],
        files: RequestFiles,
    ) -> HttpxResponseAdapter:
        resp = await self._client.post(url=url, headers=headers, data=data, files=files)
        return HttpxResponseAdapter(resp)

    async def get(
        self,
        url: str,
        *,
        headers: dict[str, str],
    ) -> HttpxResponseAdapter:
        resp = await self._client.get(url, headers=headers)
        return HttpxResponseAdapter(resp)

    async def aclose(self) -> None:
        await self._client.aclose()


def make_httpx_sync_client(
    base_url: str,
    timeout: float,
    user_agent: str,
    auth: AuthType,
    *,
    http2: bool,
) -> HttpxSyncAdapter:
    httpx_auth: httpx.BasicAuth | None = (
        httpx.BasicAuth(username=auth[0], password=auth[1]) if auth is not None else None
    )
    client = httpx.Client(
        base_url=base_url,
        timeout=timeout,
        http2=http2,
        auth=httpx_auth,
        headers={"User-Agent": user_agent},
    )
    return HttpxSyncAdapter(client)


def make_httpx_async_client(
    base_url: str,
    timeout: float,
    user_agent: str,
    auth: AuthType,
    *,
    http2: bool,
) -> HttpxAsyncAdapter:
    httpx_auth: httpx.BasicAuth | None = (
        httpx.BasicAuth(username=auth[0], password=auth[1]) if auth is not None else None
    )
    client = httpx.AsyncClient(
        base_url=base_url,
        timeout=timeout,
        http2=http2,
        auth=httpx_auth,
        headers={"User-Agent": user_agent},
    )
    return HttpxAsyncAdapter(client)
