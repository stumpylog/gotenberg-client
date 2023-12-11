# SPDX-FileCopyrightText: 2023-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
import logging
from contextlib import ExitStack
from pathlib import Path
from tempfile import TemporaryDirectory
from types import TracebackType
from typing import Dict
from typing import Optional
from typing import Type

from httpx import Client
from httpx import Response
from httpx._types import RequestFiles

from gotenberg_client._typing_compat import Self
from gotenberg_client._utils import guess_mime_type
from gotenberg_client.options import PdfAFormat

logger = logging.getLogger(__name__)


class BaseRoute:
    """
    The base implementation of a Gotenberg API route.  Anything settings or
    actions shared between all routes should be implemented here
    """

    def __init__(self, client: Client, api_route: str) -> None:
        self._client = client
        self._route = api_route
        self._stack = ExitStack()
        # These are the options that will be set to Gotenberg.  Things like PDF/A
        self._form_data: Dict[str, str] = {}
        # These are the names of files, mapping to their Path
        self._file_map: Dict[str, Path] = {}
        # Any header that will also be sent
        self._headers: Dict[str, str] = {}

    def __enter__(self) -> Self:
        self.reset()
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        self.close()

    def reset(self) -> None:
        """
        Calls all context manager __exit__ via the ExitStack and clears
        all set files and form data options
        """
        self._stack.close()
        self._form_data.clear()
        self._file_map.clear()

    def close(self) -> None:
        """
        Alias for reset
        """
        self.reset()

    def run(self) -> Response:
        """
        Executes the configured route against the server and returns the resulting
        Response.
        TODO: It would be nice to return a simpler response to the user
        """
        resp = self._client.post(url=self._route, headers=self._headers, data=self._form_data, files=self._get_files())
        resp.raise_for_status()
        return resp

    def _get_files(self) -> RequestFiles:
        """
        Deals with opening all provided files for multi-part uploads, including
        pushing their new contexts onto the stack to ensure resources like file
        handles are cleaned up
        """
        files = {}
        for filename in self._file_map:
            file_path = self._file_map[filename]

            # Helpful but not necessary to provide the mime type when possible
            mime_type = guess_mime_type(file_path)
            if mime_type is not None:
                files.update(
                    {filename: (filename, self._stack.enter_context(file_path.open("rb")), mime_type)},
                )
            else:  # pragma: no cover
                files.update({filename: (filename, self._stack.enter_context(file_path.open("rb")))})  # type: ignore [dict-item]
        return files

    def _add_file_map(self, filepath: Path, name: Optional[str] = None) -> None:
        """
        Small helper to handle bookkeeping of files for later opening.  The name is
        optional to support those things which are required to have a certain name
        generally for ordering or just to be found at all
        """
        if name is None:
            name = filepath.name

        if name in self._file_map:  # pragma: no cover
            logger.warning(f"{name} has already been provided, overwriting anyway")

        try:
            name.encode("utf8").decode("ascii")
        except UnicodeDecodeError:
            logger.warning(f"filename {name} includes non-ascii characters, compensating for Gotenberg")
            tmp_dir = self._stack.enter_context(TemporaryDirectory())
            # Filename can be fixed, the directory is random
            new_path = Path(tmp_dir) / Path(name).with_name(f"clean-filename-copy{filepath.suffix}")
            logger.warning(f"New path {new_path}")
            new_path.write_bytes(filepath.read_bytes())
            filepath = new_path
            name = new_path.name
            logger.warning(f"New name {name}")

        self._file_map[name] = filepath

    def pdf_format(self, pdf_format: PdfAFormat) -> Self:
        """
        All routes provide the option to configure the output PDF as a
        PDF/A format
        """
        self._form_data.update(pdf_format.to_form())
        return self

    def universal_access_pdf(self, *, pdf_ua: bool) -> Self:
        self._form_data.update({"pdfua": str(pdf_ua).lower()})
        return self

    def trace(self, trace_id: str) -> Self:
        self._headers["Gotenberg-Trace"] = trace_id
        return self

    def output_name(self, filename: str) -> Self:
        self._headers["Gotenberg-Output-Filename"] = filename
        return self


class BaseApi:
    """
    Simple base class for an API, which wraps one or more routes, providing
    each with the client to use
    """

    def __init__(self, client: Client) -> None:
        self._client = client
