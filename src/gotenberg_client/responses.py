# SPDX-FileCopyrightText: 2023-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
import dataclasses
import zipfile
from collections.abc import Mapping
from io import BytesIO
from pathlib import Path
from typing import TypedDict

from gotenberg_client._errors import CannotExtractHereError


class PdfMetadata(TypedDict, total=False):
    """
    Typed representation of PDF metadata returned by Gotenberg's read-metadata route.

    All fields are optional (``total=False``) because:

    - Not every PDF contains every metadata field.
    - The set of returned fields varies by Gotenberg version.  System fields
      such as ``FileName``, ``FileSize``, and ``Directory`` are present through
      at least Gotenberg 8.29.1 but are scheduled for removal in a future
      release (see upstream commit 20522fd).  Note that ``FileName`` reflects
      Gotenberg's internal UUID-based temp name, not the original posted
      filename — its value has never been reliable for that purpose.
    - ExifTool-derived fields (``PageCount``, ``PDFVersion``, etc.) are present
      in current Gotenberg releases but the maintainer has indicated they may be
      removed in a future version.

    Use ``.get()`` rather than direct key access to handle version differences
    gracefully.
    """

    # Standard PDF document information fields
    Author: str
    Copyright: str
    CreateDate: str
    Creator: str
    Keywords: str | list[str]  # array when written as JSON array; string otherwise
    Marked: bool
    ModDate: str  # XMP pdf namespace (pdf:ModDate) — written via Gotenberg's metadata route
    ModifyDate: str  # base XMP namespace (xmp:ModifyDate) — present in Chromium/Skia-generated PDFs
    Producer: str
    Subject: str
    Title: str
    Trapped: str
    # ExifTool-derived/computed fields — present in current Gotenberg versions,
    # but flagged by the maintainer as candidates for future removal.
    FileType: str
    FileTypeExtension: str
    Linearized: str
    MIMEType: str
    PageCount: int
    PDFVersion: float
    # ExifTool intrinsic fields — always present in ExifTool JSON output.
    SourceFile: str
    XMPToolkit: str
    # System/filesystem fields present through at least Gotenberg 8.29.1,
    # scheduled for removal in a future release (upstream commit 20522fd).
    # FileName reflects Gotenberg's internal UUID temp name, not the posted filename.
    Directory: str
    ExifToolVersion: float
    FileAccessDate: str
    FileInodeChangeDate: str
    FileModifyDate: str
    FilePermissions: str
    FileName: str
    FileSize: str


@dataclasses.dataclass(slots=True)
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
    headers: Mapping[str, str]
    content: bytes | bytearray

    def to_file(self, file_path: Path) -> None:
        """
        Write the response content to a file.

        This method allows storing the raw response content (typically a PDF)
        directly to the filesystem.

        Args:
            file_path: Path where the content should be saved.
        """
        file_path.write_bytes(self.content)

    @property
    def is_zip(self) -> bool:
        """
        Determine if the response contains a ZIP archive.

        Returns:
            True if the Content-Type header indicates a ZIP file, False otherwise.
        """
        return "Content-Type" in self.headers and self.headers["Content-Type"] == "application/zip"


@dataclasses.dataclass(slots=True)
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


@dataclasses.dataclass(slots=True)
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
