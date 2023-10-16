# SPDX-FileCopyrightText: 2023-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
from pathlib import Path
from typing import List

from httpx import Client

from gotenberg_client._base import BaseApi
from gotenberg_client._base import BaseRoute


class MergeRoute(BaseRoute):
    """
    Handles the merging of a given set of files
    """

    def __init__(self, client: Client, api_route: str) -> None:
        super().__init__(client, api_route)
        self._next = 1

    def merge(self, files: List[Path]) -> "MergeRoute":
        """
        Adds the given files into the file mapping.  This method will maintain the
        ordering of the list.  Calling this method multiple times may not merge
        in the expected ordering
        """
        for filepath in files:
            # Include index to enforce ordering
            self._add_file_map(filepath, f"{self._next}_{filepath.name}")
            self._next += 1
        return self


class MergeApi(BaseApi):
    """
    Wraps the merge route
    """

    _MERGE_ENDPOINT = "/forms/pdfengines/merge"

    def merge(self) -> MergeRoute:
        return MergeRoute(self._client, self._MERGE_ENDPOINT)
