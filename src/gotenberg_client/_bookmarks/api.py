# SPDX-FileCopyrightText: 2025-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
from gotenberg_client._base import AsyncBaseApi
from gotenberg_client._base import SyncBaseApi
from gotenberg_client._bookmarks.routes import AsyncReadBookmarksRoute
from gotenberg_client._bookmarks.routes import AsyncWriteBookmarksRoute
from gotenberg_client._bookmarks.routes import SyncReadBookmarksRoute
from gotenberg_client._bookmarks.routes import SyncWriteBookmarksRoute


class SyncBookmarksApi(SyncBaseApi):
    def read(self) -> SyncReadBookmarksRoute:
        return SyncReadBookmarksRoute(self._client, SyncReadBookmarksRoute.ENDPOINT_URL, self._log)

    def write(self) -> SyncWriteBookmarksRoute:
        return SyncWriteBookmarksRoute(self._client, SyncWriteBookmarksRoute.ENDPOINT_URL, self._log)


class AsyncBookmarksApi(AsyncBaseApi):
    def read(self) -> AsyncReadBookmarksRoute:
        return AsyncReadBookmarksRoute(self._client, AsyncReadBookmarksRoute.ENDPOINT_URL, self._log)

    def write(self) -> AsyncWriteBookmarksRoute:
        return AsyncWriteBookmarksRoute(self._client, AsyncWriteBookmarksRoute.ENDPOINT_URL, self._log)
