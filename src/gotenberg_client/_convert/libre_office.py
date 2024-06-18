# SPDX-FileCopyrightText: 2023-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
from pathlib import Path
from typing import List
from typing import Union

from httpx import Client

from gotenberg_client._base import BaseApi
from gotenberg_client._base import BaseSingleFileResponseRoute
from gotenberg_client._convert.common import PageOrientMixin
from gotenberg_client._convert.common import PageRangeMixin
from gotenberg_client._types import Self
from gotenberg_client._types import WaitTimeType
from gotenberg_client.responses import SingleFileResponse
from gotenberg_client.responses import ZipFileResponse


class LibreOfficeConvertRoute(PageOrientMixin, PageRangeMixin, BaseSingleFileResponseRoute):
    """
    https://gotenberg.dev/docs/routes#convert-with-libreoffice
    """

    def __init__(self, client: Client, api_route: str) -> None:
        super().__init__(client, api_route)
        self._merged_result = False

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
        self._merged_result = False
        return self

    def no_merge(self) -> Self:
        """
        Don't merge the resulting PDFs
        """
        self._form_data.update({"merge": "false"})
        self._merged_result = False
        return self

    def run(self) -> Union[SingleFileResponse, ZipFileResponse]:
        resp = super().run()

        if self._merged_result:
            return ZipFileResponse(resp.status_code, resp.headers, resp.content)
        return resp

    def run_with_retry(
        self,
        *,
        max_retry_count: int = 5,
        initial_retry_wait: WaitTimeType = 5,
        retry_scale: WaitTimeType = 2,
    ) -> Union[SingleFileResponse, ZipFileResponse]:
        resp = super().run_with_retry(
            max_retry_count=max_retry_count,
            initial_retry_wait=initial_retry_wait,
            retry_scale=retry_scale,
        )

        if self._merged_result:
            return ZipFileResponse(resp.status_code, resp.headers, resp.content)
        return resp


class LibreOfficeApi(BaseApi):
    _CONVERT_ENDPOINT = "/forms/libreoffice/convert"

    def to_pdf(self) -> LibreOfficeConvertRoute:
        """
        Returns the LibreOffice conversion route
        """
        return LibreOfficeConvertRoute(self._client, self._CONVERT_ENDPOINT)
