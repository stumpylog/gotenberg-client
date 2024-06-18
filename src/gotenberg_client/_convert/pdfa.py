# SPDX-FileCopyrightText: 2023-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
from pathlib import Path
from typing import List

from gotenberg_client._base import BaseApi
from gotenberg_client._base import BaseSingleFileResponseRoute
from gotenberg_client._types import Self


class PdfAConvertRoute(BaseSingleFileResponseRoute):
    """
    https://gotenberg.dev/docs/routes#convert-into-pdfa-route
    """

    def convert(self, file_path: Path) -> Self:
        """
        Convert a single PDF into the provided PDF/A format
        """
        self._add_file_map(file_path)
        return self

    def convert_files(self, file_paths: List[Path]) -> Self:
        for x in file_paths:
            self.convert(x)
        return self


class PdfAApi(BaseApi):
    _CONVERT_ENDPOINT = "/forms/pdfengines/convert"

    def to_pdfa(self) -> PdfAConvertRoute:
        return PdfAConvertRoute(self._client, self._CONVERT_ENDPOINT)
