# SPDX-FileCopyrightText: 2025-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
from gotenberg_client._base import AsyncBaseApi
from gotenberg_client._base import SyncBaseApi
from gotenberg_client._others.routes import AsyncEmbedRoute
from gotenberg_client._others.routes import AsyncEncryptRoute
from gotenberg_client._others.routes import AsyncFlattenRoute
from gotenberg_client._others.routes import AsyncRotateRoute
from gotenberg_client._others.routes import AsyncSplitRoute
from gotenberg_client._others.routes import AsyncStampRoute
from gotenberg_client._others.routes import AsyncWatermarkRoute
from gotenberg_client._others.routes import SyncEmbedRoute
from gotenberg_client._others.routes import SyncEncryptRoute
from gotenberg_client._others.routes import SyncFlattenRoute
from gotenberg_client._others.routes import SyncRotateRoute
from gotenberg_client._others.routes import SyncSplitRoute
from gotenberg_client._others.routes import SyncStampRoute
from gotenberg_client._others.routes import SyncWatermarkRoute


class SyncFlattenApi(SyncBaseApi):
    def flatten(self) -> SyncFlattenRoute:
        return SyncFlattenRoute(self._client, SyncFlattenRoute.ENDPOINT_URL, self._log)


class AsyncFlattenApi(AsyncBaseApi):
    def flatten(self) -> AsyncFlattenRoute:
        return AsyncFlattenRoute(self._client, AsyncFlattenRoute.ENDPOINT_URL, self._log)


class SyncSplitApi(SyncBaseApi):
    def split(self) -> SyncSplitRoute:
        return SyncSplitRoute(self._client, SyncSplitRoute.ENDPOINT_URL, self._log)


class AsyncSplitApi(AsyncBaseApi):
    def split(self) -> AsyncSplitRoute:
        return AsyncSplitRoute(self._client, AsyncSplitRoute.ENDPOINT_URL, self._log)


class SyncWatermarkApi(SyncBaseApi):
    def watermark(self) -> SyncWatermarkRoute:
        return SyncWatermarkRoute(self._client, SyncWatermarkRoute.ENDPOINT_URL, self._log)


class AsyncWatermarkApi(AsyncBaseApi):
    def watermark(self) -> AsyncWatermarkRoute:
        return AsyncWatermarkRoute(self._client, AsyncWatermarkRoute.ENDPOINT_URL, self._log)


class SyncStampApi(SyncBaseApi):
    def stamp(self) -> SyncStampRoute:
        return SyncStampRoute(self._client, SyncStampRoute.ENDPOINT_URL, self._log)


class AsyncStampApi(AsyncBaseApi):
    def stamp(self) -> AsyncStampRoute:
        return AsyncStampRoute(self._client, AsyncStampRoute.ENDPOINT_URL, self._log)


class SyncRotateApi(SyncBaseApi):
    def rotate(self) -> SyncRotateRoute:
        return SyncRotateRoute(self._client, SyncRotateRoute.ENDPOINT_URL, self._log)


class AsyncRotateApi(AsyncBaseApi):
    def rotate(self) -> AsyncRotateRoute:
        return AsyncRotateRoute(self._client, AsyncRotateRoute.ENDPOINT_URL, self._log)


class SyncEncryptApi(SyncBaseApi):
    def encrypt(self) -> SyncEncryptRoute:
        return SyncEncryptRoute(self._client, SyncEncryptRoute.ENDPOINT_URL, self._log)


class AsyncEncryptApi(AsyncBaseApi):
    def encrypt(self) -> AsyncEncryptRoute:
        return AsyncEncryptRoute(self._client, AsyncEncryptRoute.ENDPOINT_URL, self._log)


class SyncEmbedApi(SyncBaseApi):
    def embed(self) -> SyncEmbedRoute:
        return SyncEmbedRoute(self._client, SyncEmbedRoute.ENDPOINT_URL, self._log)


class AsyncEmbedApi(AsyncBaseApi):
    def embed(self) -> AsyncEmbedRoute:
        return AsyncEmbedRoute(self._client, AsyncEmbedRoute.ENDPOINT_URL, self._log)
