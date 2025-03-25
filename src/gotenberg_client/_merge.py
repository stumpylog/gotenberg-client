# SPDX-FileCopyrightText: 2023-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
from pathlib import Path
from typing import Final

from httpx import Client

from gotenberg_client._base import BaseApi
from gotenberg_client._base import BaseZipFileResponseRoute
from gotenberg_client._types import Self


class MergeRoute(BaseZipFileResponseRoute):
    """
    Handles the merging of a given set of PDF files using the Gotenberg API.

    This class provides functionality to merge multiple PDF files into a single PDF.

    For more information on Gotenberg's merge functionality, see:
    https://gotenberg.dev/docs/routes#merge-pdfs-route

    Attributes:
        _next (int): A counter used to maintain the order of added files.
    """

    def __init__(self, client: Client, api_route: str) -> None:
        """
        Initialize a new MergeRoute instance.

        Args:
            client (Client): The HTTP client used to make requests to the Gotenberg API.
            api_route (str): The API route for merge operations.
        """
        super().__init__(client, api_route)
        self._next = 1

    def merge(self, files: list[Path]) -> Self:
        """
        Add the given files to the merge operation.

        This method maintains the ordering of the provided list of files. Note that calling
        this method multiple times may not result in the expected merge order.

        For more details on merging PDFs with Gotenberg, see:
        https://gotenberg.dev/docs/routes#merge-pdfs-route

        Args:
            files (List[Path]): A list of Path objects representing the PDF files to be merged.

        Returns:
            Self: The instance itself, allowing for method chaining.

        Note:
            - The files must be valid PDF documents.
            - The order of the files in the list determines the order in the merged PDF.
        """
        for filepath in files:
            # Include index to enforce ordering
            self._add_file_map(filepath, name=f"{self._next}_{filepath.name}")
            self._next += 1
        return self


class MergeApi(BaseApi):
    """
    Wraps the merge route
    """

    _MERGE_ENDPOINT: Final[str] = "/forms/pdfengines/merge"

    def merge(self) -> MergeRoute:
        return MergeRoute(self._client, self._MERGE_ENDPOINT)
