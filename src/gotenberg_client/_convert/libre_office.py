# SPDX-FileCopyrightText: 2023-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
from pathlib import Path
from typing import List

from gotenberg_client._base import BaseApi
from gotenberg_client._convert.common import ConvertBaseRoute
from gotenberg_client._typing_compat import Self


class LibreOfficeConvertRoute(ConvertBaseRoute):
    """
    https://gotenberg.dev/docs/routes#convert-with-libreoffice
    """

    def convert(self, file_path: Path) -> Self:
        """
        Adds a single file to be converted to PDF.  Can be called multiple times,
        resulting in a ZIP of the PDFs, unless merged
        """
        self._add_file_map(file_path)
        return self

    def convert_files(self, file_paths: List[Path]) -> Self:
        """
        Adds all provided files for conversion
        """
        for x in file_paths:
            self.convert(x)
        return self

    def merge(self) -> Self:
        """
        Merge the resulting PDFs into one
        """
        self._form_data.update({"merge": "true"})
        return self

    def no_merge(self) -> Self:
        """
        Don't merge the resulting PDFs
        """
        self._form_data.update({"merge": "false"})
        return self


class LibreOfficeApi(BaseApi):
    _CONVERT_ENDPOINT = "/forms/libreoffice/convert"

    def to_pdf(self) -> LibreOfficeConvertRoute:
        """
        Returns the LibreOffice conversion route
        """
        return LibreOfficeConvertRoute(self._client, self._CONVERT_ENDPOINT)
