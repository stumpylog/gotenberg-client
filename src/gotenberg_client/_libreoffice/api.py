# SPDX-FileCopyrightText: 2025-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
from gotenberg_client._base import AsyncBaseApi
from gotenberg_client._base import SyncBaseApi
from gotenberg_client._libreoffice.routes import AsyncOfficeDocumentToPdfRoute
from gotenberg_client._libreoffice.routes import SyncOfficeDocumentToPdfRoute


class SyncLibreOfficeApi(SyncBaseApi):
    """
    Represents the sync Gotenberg API for LibreOffice-based conversions.
    """

    def to_pdf(self) -> SyncOfficeDocumentToPdfRoute:
        """
        Creates a SyncOfficeDocumentToPdfRoute object for converting documents to PDF.

        Returns:
            SyncOfficeDocumentToPdfRoute: A new SyncOfficeDocumentToPdfRoute object.
        """

        return SyncOfficeDocumentToPdfRoute(self._client, SyncOfficeDocumentToPdfRoute.ENDPOINT_URL, self._log)


class AsyncLibreOfficeApi(AsyncBaseApi):
    """
    Represents the sync Gotenberg API for LibreOffice-based conversions.
    """

    def to_pdf(self) -> AsyncOfficeDocumentToPdfRoute:
        """
        Creates a AsyncOfficeDocumentToPdfRoute object for converting documents to PDF.

        Returns:
            AsyncOfficeDocumentToPdfRoute: A new AsyncOfficeDocumentToPdfRoute object.
        """

        return AsyncOfficeDocumentToPdfRoute(self._client, AsyncOfficeDocumentToPdfRoute.ENDPOINT_URL, self._log)
