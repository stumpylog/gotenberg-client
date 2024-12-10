# SPDX-FileCopyrightText: 2023-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
from pathlib import Path

from gotenberg_client._base import BaseApi
from gotenberg_client._base import BaseSingleFileResponseRoute
from gotenberg_client._convert.common import MetadataMixin
from gotenberg_client._types import Self


class PdfAConvertRoute(MetadataMixin, BaseSingleFileResponseRoute):
    """
    Represents the Gotenberg route for converting PDFs to PDF/A format.

    This class allows converting a single or multiple PDF files to the
    specified PDF/A format (e.g., PDF/A-1b, PDF/A-2b).

    See the Gotenberg documentation (https://gotenberg.dev/docs/routes#convert-into-pdfa-route)
    for details on supported PDF/A formats.
    """

    def convert(self, file_path: Path) -> Self:
        """
        Converts a single PDF file to the provided PDF/A format.

        Args:
            file_path (Path): The path to the PDF file to be converted.

        Returns:
            PdfAConvertRoute: This object itself for method chaining.
        """

        self._add_file_map(file_path)
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


class PdfAApi(BaseApi):
    """
    Represents the Gotenberg API for PDF/A conversion.

    Provides a method to create a PdfAConvertRoute object for converting PDFs to PDF/A format.
    """

    _CONVERT_ENDPOINT = "/forms/pdfengines/convert"

    def to_pdfa(self) -> PdfAConvertRoute:
        """
        Creates a PdfAConvertRoute object for converting PDFs to PDF/A format.

        Returns:
            PdfAConvertRoute: A new PdfAConvertRoute object.
        """

        return PdfAConvertRoute(self._client, self._CONVERT_ENDPOINT)
