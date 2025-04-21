# SPDX-FileCopyrightText: 2025-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
from gotenberg_client._base import AsyncBaseApi
from gotenberg_client._base import SyncBaseApi
from gotenberg_client._merge.routes import AsyncMergePdfsRoute
from gotenberg_client._merge.routes import SyncMergePdfsRoute


class SyncMergePdfsApi(SyncBaseApi):
    def merge(self) -> SyncMergePdfsRoute:
        return SyncMergePdfsRoute(self._client, SyncMergePdfsRoute.ENDPOINT_URL, self._log)


class AsyncMergePdfsApi(AsyncBaseApi):
    def merge(self) -> AsyncMergePdfsRoute:
        return AsyncMergePdfsRoute(self._client, AsyncMergePdfsRoute.ENDPOINT_URL, self._log)
