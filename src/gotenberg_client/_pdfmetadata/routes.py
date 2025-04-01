# SPDX-FileCopyrightText: 2025-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
from pathlib import Path
from typing import Final
from typing import Union

from gotenberg_client._base import AsyncBaseRoute
from gotenberg_client._base import SyncBaseRoute
from gotenberg_client._common import MetadataMixin
from gotenberg_client._typing_compat import Self


class _BaseReadPdfMetadataRoute:
    """
    https://gotenberg.dev/docs/routes#read-pdf-metadata-route
    """

    ENDPOINT_URL: Final[str] = "/forms/pdfengines/metadata/read"

    def read(self, input_file_path: Path) -> Self:
        self._add_file_map(input_file_path)  # type: ignore[attr-defined]
        return self

    def read_files(self, file_paths: list[Path]) -> Self:
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
            self.read(x)
        return self


class SyncReadPdfMetadataRoute(_BaseReadPdfMetadataRoute, SyncBaseRoute):
    def run(self) -> dict[str, dict[str, str]]:  # type: ignore[override]
        response = self._post_data()
        return response.json()  # type: ignore[misc]

    def run_with_retry(  # type: ignore[override]
        self,
        *,
        max_retry_count: int = 5,
        initial_retry_wait: Union[float, int] = 5.0,
        retry_scale: Union[float, int] = 2.0,
    ) -> dict[str, dict[str, str]]:
        response = self._post_data_with_retry(
            max_retry_count=max_retry_count,
            initial_retry_wait=initial_retry_wait,
            retry_scale=retry_scale,
        )
        return response.json()  # type: ignore[misc]


class AsyncReadPdfMetadataRoute(_BaseReadPdfMetadataRoute, AsyncBaseRoute):
    async def run(self) -> dict[str, dict[str, str]]:  # type: ignore[override]
        response = await self._post_data()
        return response.json()  # type: ignore[misc]

    async def run_with_retry(  # type: ignore[override]
        self,
        *,
        max_retry_count: int = 5,
        initial_retry_wait: Union[float, int] = 5.0,
        retry_scale: Union[float, int] = 2.0,
    ) -> dict[str, dict[str, str]]:
        response = await self._post_data_with_retry(
            max_retry_count=max_retry_count,
            initial_retry_wait=initial_retry_wait,
            retry_scale=retry_scale,
        )
        return response.json()  # type: ignore[misc]


class _BaseWritePdfMetadataRoute(MetadataMixin):
    """
    https://gotenberg.dev/docs/routes#write-pdf-metadata-route
    """

    ENDPOINT_URL: Final[str] = "/forms/pdfengines/metadata/write"

    def write(self, input_file_path: Path) -> Self:
        self._add_file_map(input_file_path)  # type: ignore[attr-defined]
        return self

    def write_files(self, file_paths: list[Path]) -> Self:
        for x in file_paths:
            self.write(x)
        return self


class SyncWritePdfMetadataRoute(_BaseWritePdfMetadataRoute, SyncBaseRoute):
    pass


class AsyncWritePdfMetadataRoute(_BaseWritePdfMetadataRoute, AsyncBaseRoute):
    pass
