# SPDX-FileCopyrightText: 2023-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
import dataclasses
import zipfile
from functools import cached_property
from io import BytesIO
from pathlib import Path
from typing import Union

from httpx import Headers

from gotenberg_client._errors import CannotExtractHereError


@dataclasses.dataclass
class _BaseApiResponse:
    """
    Base response from the Gotenberg API containing standard HTTP response data.

    This class serves as the foundation for specific response types from the Gotenberg API.
    It provides common attributes and functionality needed to process any API response,
    including status code, headers, and raw content handling.

    Attributes:
        status_code: HTTP status code returned by the Gotenberg API.
        headers: HTTP headers included in the response.
        content: Raw binary content of the response.
    """

    status_code: int
    headers: Headers
    content: Union[bytes, bytearray]

    def to_file(self, file_path: Path) -> None:
        """
        Write the response content to a file.

        This method allows storing the raw response content (typically a PDF)
        directly to the filesystem.

        Args:
            file_path: Path where the content should be saved.
        """
        file_path.write_bytes(self.content)

    @cached_property
    def is_zip(self) -> bool:
        """
        Determine if the response contains a ZIP archive.

        Returns:
            True if the Content-Type header indicates a ZIP file, False otherwise.
        """
        return "Content-Type" in self.headers and self.headers["Content-Type"] == "application/zip"


@dataclasses.dataclass
class SingleFileResponse(_BaseApiResponse):
    """
    Response containing a single PDF file.

    This response type is returned by Gotenberg API operations that produce
    a single output file, such as:
    - Converting a single document to PDF
    - Merging multiple PDFs into one
    - Converting HTML to PDF

    The content will be a binary PDF file that can be saved using the to_file() method.
    """


@dataclasses.dataclass
class ZipFileResponse(_BaseApiResponse):
    """
    Response containing multiple files packaged as a ZIP archive.

    This response type is returned by Gotenberg API operations that produce
    multiple output files, such as:
    - Converting multiple documents in a single request
    - PDF splitting operations
    - Operations with the multiple=true parameter

    The content will be a binary ZIP file containing multiple PDFs.
    """

    def extract_to(self, directory: Path) -> None:
        """
        Extract all files from the ZIP archive to a specified directory.

        Args:
            directory: The target directory where files should be extracted.

        Raises:
            CannotExtractHereError: If the directory doesn't exist or isn't a directory.
        """
        if not directory.exists() or not directory.is_dir():
            raise CannotExtractHereError

        with zipfile.ZipFile(BytesIO(self.content), mode="r") as zipref:
            zipref.extractall(directory)
