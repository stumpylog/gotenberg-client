# SPDX-FileCopyrightText: 2023-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
from pathlib import Path
from typing import List
from typing import Union

from httpx import Client

from gotenberg_client._base import BaseApi
from gotenberg_client._base import BaseSingleFileResponseRoute
from gotenberg_client._convert.common import MetadataMixin
from gotenberg_client._convert.common import PageOrientMixin
from gotenberg_client._convert.common import PageRangeMixin
from gotenberg_client._types import Self
from gotenberg_client._types import WaitTimeType
from gotenberg_client.responses import SingleFileResponse
from gotenberg_client.responses import ZipFileResponse


class LibreOfficeConvertRoute(PageOrientMixin, PageRangeMixin, MetadataMixin, BaseSingleFileResponseRoute):
    """
    Represents the Gotenberg route for converting documents to PDF using LibreOffice.

    This class allows adding single or multiple files for conversion, optionally
    merging them into a single PDF.

    See the Gotenberg documentation (https://gotenberg.dev/docs/routes#convert-with-libreoffice)
    for detailed information about the supported features.
    """

    def __init__(self, client: Client, api_route: str) -> None:
        super().__init__(client, api_route)
        self._result_is_zip = False
        self._convert_calls = 0

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

        self._add_file_map(input_file_path)
        self._convert_calls += 1
        if self._convert_calls > 1:
            self._result_is_zip = True
        return self

    def convert_files(self, file_paths: List[Path]) -> Self:
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

    def merge(self) -> Self:
        """
        Merges the resulting PDFs into a single PDF document.

        This method enables merging previously added files into a single PDF during conversion.

        Returns:
            LibreOfficeConvertRoute: This object itself for method chaining.
        """

        self._form_data.update({"merge": "true"})
        self._result_is_zip = False
        return self

    def no_merge(self) -> Self:
        """
        Disables merging of resulting PDFs.

        This method ensures that even when converting multiple files, the results
        will be individual PDFs in a ZIP archive.

        Returns:
            LibreOfficeConvertRoute: This object itself for method chaining.
        """

        self._form_data.update({"merge": "false"})
        self._result_is_zip = True
        return self

    def run(self) -> Union[SingleFileResponse, ZipFileResponse]:  # type: ignore[override]
        resp = super().run()

        if self._result_is_zip:  # pragma: no cover
            return ZipFileResponse(resp.status_code, resp.headers, resp.content)
        return resp

    def run_with_retry(  # type: ignore[override]
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

        if self._result_is_zip:
            return ZipFileResponse(resp.status_code, resp.headers, resp.content)
        return resp


class LibreOfficeApi(BaseApi):
    """
    Represents the Gotenberg API for LibreOffice-based conversions.

    Provides a method to create a LibreOfficeConvertRoute object for converting
    documents to PDF using LibreOffice.
    """

    _CONVERT_ENDPOINT = "/forms/libreoffice/convert"

    def to_pdf(self) -> LibreOfficeConvertRoute:
        """
        Creates a LibreOfficeConvertRoute object for converting documents to PDF.

        Returns:
            LibreOfficeConvertRoute: A new LibreOfficeConvertRoute object.
        """

        return LibreOfficeConvertRoute(self._client, self._CONVERT_ENDPOINT)
