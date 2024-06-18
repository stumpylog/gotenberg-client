# SPDX-FileCopyrightText: 2023-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
import dataclasses
import zipfile
from io import BytesIO
from pathlib import Path
from typing import Union

from httpx import Headers

from gotenberg_client._errors import CannotExtractHereError


@dataclasses.dataclass
class _BaseApiResponse:
    """
    The basic response from the API, containing the status code and the
    response content.  This is compatible with the Response used before from
    httpx
    """

    status_code: int
    headers: Headers
    content: Union[bytes, bytearray]

    def to_file(self, file_path: Path) -> None:
        """
        Writes the response content to a given file.
        """
        file_path.write_bytes(self.content)


@dataclasses.dataclass
class SingleFileResponse(_BaseApiResponse):
    pass


@dataclasses.dataclass
class ZipFileResponse(_BaseApiResponse):
    def extract_to(self, directory: Path) -> None:
        """
        Extracts the multiple files of a zip file response into the given directory
        """
        if not directory.exists() or not directory.is_dir():
            raise CannotExtractHereError

        with zipfile.ZipFile(BytesIO(self.content), mode="r") as zipref:
            zipref.extractall(directory)
