# SPDX-FileCopyrightText: 2025-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
from pathlib import Path
from typing import Final

from gotenberg_client._base import AsyncBaseRoute
from gotenberg_client._base import SyncBaseRoute
from gotenberg_client._common import FlattenOptionMixin
from gotenberg_client._common import MetadataMixin
from gotenberg_client._common import PdfFormatMixin
from gotenberg_client._common import PfdUniversalAccessMixin
from gotenberg_client._common import SplitModeMixin
from gotenberg_client._libreoffice.mixins import LibreOfficeCompressOptionsMixin
from gotenberg_client._libreoffice.mixins import LibreOfficeMergeOptionMixin
from gotenberg_client._libreoffice.mixins import LibreOfficePagePropertiesMixin
from gotenberg_client._typing_compat import Self


class _BaseOfficeDocumentToPdfRoute(
    LibreOfficePagePropertiesMixin,
    LibreOfficeCompressOptionsMixin,
    LibreOfficeMergeOptionMixin,
    SplitModeMixin,
    PdfFormatMixin,
    PfdUniversalAccessMixin,
    MetadataMixin,
    FlattenOptionMixin,
):
    """

    Represents the Gotenberg route for converting documents to PDF using LibreOffice.

    This class allows adding single or multiple files for conversion, optionally
    merging them into a single PDF.

    See the Gotenberg documentation for detailed information about the supported features.

    https://gotenberg.dev/docs/routes#office-documents-into-pdfs-route
    """

    ENDPOINT_URL: Final[str] = "/forms/libreoffice/convert"

    def convert(self, input_file_path: Path) -> Self:
        """
        Adds a single file to be converted to PDF.

        Calling this method multiple times will result in a ZIP containing
        individual PDFs for each converted file.

        Args:
            input_file_path (Path): The path to the file to be converted.

        Returns:
            LibreOfficeConvertRoute: This object itself for method chaining.
        """

        self._add_file_map(input_file_path)  # type: ignore[attr-defined]
        return self

    def convert_files(self, file_paths: list[Path]) -> Self:
        """
        Adds all provided files for conversion to individual PDFs.

        This method adds all files in the provided list for conversion. By default,
        the resulting PDFs will be zipped together in the response.

        Args:
            file_paths (List[Path]): A list of paths to the files to be converted.

        Returns:
            LibreOfficeConvertRoute: This object itself for method chaining.
        """
        for x in file_paths:
            self.convert(x)
        return self


class SyncOfficeDocumentToPdfRoute(_BaseOfficeDocumentToPdfRoute, SyncBaseRoute):
    pass


class AsyncOfficeDocumentToPdfRoute(_BaseOfficeDocumentToPdfRoute, AsyncBaseRoute):
    pass
