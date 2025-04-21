# SPDX-FileCopyrightText: 2025-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0


from gotenberg_client._base import AsyncBaseApi
from gotenberg_client._base import SyncBaseApi
from gotenberg_client._pdfmetadata.routes import AsyncReadPdfMetadataRoute
from gotenberg_client._pdfmetadata.routes import AsyncWritePdfMetadataRoute
from gotenberg_client._pdfmetadata.routes import SyncReadPdfMetadataRoute
from gotenberg_client._pdfmetadata.routes import SyncWritePdfMetadataRoute


class SyncPdfMetadataApi(SyncBaseApi):
    def read(self) -> SyncReadPdfMetadataRoute:
        return SyncReadPdfMetadataRoute(self._client, SyncReadPdfMetadataRoute.ENDPOINT_URL, self._log)

    def write(self) -> SyncWritePdfMetadataRoute:
        return SyncWritePdfMetadataRoute(self._client, SyncWritePdfMetadataRoute.ENDPOINT_URL, self._log)


class AsyncPdfMetadataApi(AsyncBaseApi):
    def read(self) -> AsyncReadPdfMetadataRoute:
        return AsyncReadPdfMetadataRoute(self._client, AsyncReadPdfMetadataRoute.ENDPOINT_URL, self._log)

    def write(self) -> AsyncWritePdfMetadataRoute:
        return AsyncWritePdfMetadataRoute(self._client, AsyncWritePdfMetadataRoute.ENDPOINT_URL, self._log)
