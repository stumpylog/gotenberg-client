# SPDX-FileCopyrightText: 2025-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
from gotenberg_client._base import AsyncBaseApi
from gotenberg_client._base import SyncBaseApi
from gotenberg_client._pdfa_ua.routes import AsyncConvertToArchiveFormatRoute
from gotenberg_client._pdfa_ua.routes import SyncConvertToArchiveFormatRoute


class SyncPdfAApi(SyncBaseApi):
    def to_pdfa(self) -> SyncConvertToArchiveFormatRoute:
        return SyncConvertToArchiveFormatRoute(self._client, SyncConvertToArchiveFormatRoute.ENDPOINT_URL, self._log)


class AsyncPdfAApi(AsyncBaseApi):
    def to_pdfa(self) -> AsyncConvertToArchiveFormatRoute:
        """
        Creates a ConvertPdfToPdfAUa object for converting PDFs to PDF/A format.

        Returns:
            ConvertPdfToPdfAUa: A new ConvertPdfToPdfAUa object.
        """

        return AsyncConvertToArchiveFormatRoute(self._client, AsyncConvertToArchiveFormatRoute.ENDPOINT_URL, self._log)
