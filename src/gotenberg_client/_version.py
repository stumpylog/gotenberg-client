# SPDX-FileCopyrightText: 2025-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
from contextlib import AbstractAsyncContextManager
from contextlib import AbstractContextManager
from types import TracebackType
from typing import Final

from gotenberg_client._base import AsyncBaseApi
from gotenberg_client._base import SyncBaseApi
from gotenberg_client._typing_compat import Self

_VERSION_ENDPOINT: Final[str] = "/version"


class SyncVersionApi(SyncBaseApi, AbstractContextManager):
    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        pass

    def get(self) -> str:
        response = self._client.get(url=_VERSION_ENDPOINT, headers={})
        response.raise_for_status()
        return response.content.decode().strip()


class AsyncVersionApi(AsyncBaseApi, AbstractAsyncContextManager):
    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        pass

    async def get(self) -> str:
        response = await self._client.get(url=_VERSION_ENDPOINT, headers={})
        response.raise_for_status()
        return response.content.decode().strip()
