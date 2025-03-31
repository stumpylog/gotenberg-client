# SPDX-FileCopyrightText: 2025-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
from gotenberg_client._base import AsyncBaseApi
from gotenberg_client._base import SyncBaseApi
from gotenberg_client._others.routes import AsyncFlattenRoute
from gotenberg_client._others.routes import AsyncSplitRoute
from gotenberg_client._others.routes import SyncFlattenRoute
from gotenberg_client._others.routes import SyncSplitRoute


class SyncFlattenApi(SyncBaseApi):
    def flatten(self) -> SyncFlattenRoute:
        return SyncFlattenRoute(self._client, SyncFlattenRoute.ENDPOINT_URL, self._log)


class AyncFlattenApi(AsyncBaseApi):
    def flatten(self) -> AsyncFlattenRoute:
        return AsyncFlattenRoute(self._client, AsyncFlattenRoute.ENDPOINT_URL, self._log)


class SyncSplitApi(SyncBaseApi):
    def split(self) -> SyncSplitRoute:
        return SyncSplitRoute(self._client, SyncSplitRoute.ENDPOINT_URL, self._log)


class AyncSplitApi(AsyncBaseApi):
    def split(self) -> AsyncSplitRoute:
        return AsyncSplitRoute(self._client, AsyncSplitRoute.ENDPOINT_URL, self._log)
