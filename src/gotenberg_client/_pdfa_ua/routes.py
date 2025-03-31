# SPDX-FileCopyrightText: 2025-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
from pathlib import Path
from typing import Final

from gotenberg_client._base import AsyncBaseRoute
from gotenberg_client._base import SyncBaseRoute
from gotenberg_client._common import PdfFormatMixin
from gotenberg_client._common import PfdUniversalAccessMixin
from gotenberg_client._typing_compat import Self


class _BaseConvertToArchiveFormatRoute(PdfFormatMixin, PfdUniversalAccessMixin):
    """
    Represents the Gotenberg route for converting PDFs to PDF/A format.

    This class allows converting a single or multiple PDF files to the
    specified PDF/A format (e.g., PDF/A-1b, PDF/A-2b).

    See the Gotenberg documentation for details on supported PDF/A formats.

    https://gotenberg.dev/docs/routes#convert-into-pdfa--pdfua-route
    """

    ENDPOINT_URL: Final[str] = "/forms/pdfengines/convert"

    def convert(self, file_path: Path) -> Self:
        """
        Converts a single PDF file to the provided PDF/A format.

        Args:
            file_path (Path): The path to the PDF file to be converted.

        Returns:
            PdfAConvertRoute: This object itself for method chaining.
        """

        self._add_file_map(file_path)  # type: ignore[attr-defined]
        return self

    def convert_files(self, file_paths: list[Path]) -> Self:
        """
        Converts multiple PDF files to the provided PDF/A format.

        Args:
            file_paths (List[Path]): A list of paths to the PDF files to be converted.

        Returns:
            PdfAConvertRoute: This object itself for method chaining.
        """

        for x in file_paths:
            self.convert(x)
        return self


class SyncConvertToArchiveFormatRoute(_BaseConvertToArchiveFormatRoute, SyncBaseRoute):
    pass


class AsyncConvertToArchiveFormatRoute(_BaseConvertToArchiveFormatRoute, AsyncBaseRoute):
    pass
