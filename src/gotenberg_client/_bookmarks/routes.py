# SPDX-FileCopyrightText: 2025-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
from __future__ import annotations

import json
from typing import TYPE_CHECKING
from typing import Final
from typing import TypedDict

from gotenberg_client._base import AsyncBaseRoute
from gotenberg_client._base import SyncBaseRoute

if TYPE_CHECKING:
    from pathlib import Path

    from gotenberg_client._typing_compat import Self


class BookmarkEntry(TypedDict):
    """
    Represents a single bookmark (outline entry) in a PDF document.

    Attributes:
        title: The display name of the bookmark.
        page: The 1-based page number the bookmark points to.
        children: Nested child bookmarks (may be an empty list).
    """

    title: str
    page: int
    children: list[BookmarkEntry]


class _BaseReadBookmarksRoute:
    """
    https://gotenberg.dev/docs/manipulate-pdfs/read-bookmarks
    Extracts bookmarks (document outline) from PDF files.
    Returns JSON: {filename: [BookmarkEntry, ...]}
    """

    ENDPOINT_URL: Final[str] = "/forms/pdfengines/bookmarks/read"

    def read(self, file_path: Path) -> Self:
        self._add_file_map(file_path)  # type: ignore[attr-defined]
        return self

    def read_files(self, file_paths: list[Path]) -> Self:
        for fp in file_paths:
            self.read(fp)
        return self


class SyncReadBookmarksRoute(_BaseReadBookmarksRoute, SyncBaseRoute):
    def run(self) -> dict[str, list[BookmarkEntry]]:  # type: ignore[override]
        response = self._post_data()
        return response.json()  # type: ignore[misc]

    def run_with_retry(  # type: ignore[override]
        self,
        *,
        max_retry_count: int = 5,
        initial_retry_wait: float | int = 5.0,
        retry_scale: float | int = 2.0,
    ) -> dict[str, list[BookmarkEntry]]:
        response = self._post_data_with_retry(
            max_retry_count=max_retry_count,
            initial_retry_wait=initial_retry_wait,
            retry_scale=retry_scale,
        )
        return response.json()  # type: ignore[misc]


class AsyncReadBookmarksRoute(_BaseReadBookmarksRoute, AsyncBaseRoute):
    async def run(self) -> dict[str, list[BookmarkEntry]]:  # type: ignore[override]
        response = await self._post_data()
        return response.json()  # type: ignore[misc]

    async def run_with_retry(  # type: ignore[override]
        self,
        *,
        max_retry_count: int = 5,
        initial_retry_wait: float | int = 5.0,
        retry_scale: float | int = 2.0,
    ) -> dict[str, list[BookmarkEntry]]:
        response = await self._post_data_with_retry(
            max_retry_count=max_retry_count,
            initial_retry_wait=initial_retry_wait,
            retry_scale=retry_scale,
        )
        return response.json()  # type: ignore[misc]


class _BaseWriteBookmarksRoute:
    """
    https://gotenberg.dev/docs/manipulate-pdfs/write-bookmarks
    Writes a bookmark outline into PDF files.
    """

    ENDPOINT_URL: Final[str] = "/forms/pdfengines/bookmarks/write"

    def add_file(self, file_path: Path) -> Self:
        self._add_file_map(file_path)  # type: ignore[attr-defined]
        return self

    def add_files(self, file_paths: list[Path]) -> Self:
        for fp in file_paths:
            self.add_file(fp)
        return self

    def bookmarks(self, bookmark_list: list[BookmarkEntry]) -> Self:
        """
        Set bookmarks to write into the PDF.
        Each entry: BookmarkEntry(title=str, page=int, children=[...])
        """
        self._form_data.update({"bookmarks": json.dumps(bookmark_list)})  # type: ignore[attr-defined,misc]
        return self


class SyncWriteBookmarksRoute(_BaseWriteBookmarksRoute, SyncBaseRoute):
    pass


class AsyncWriteBookmarksRoute(_BaseWriteBookmarksRoute, AsyncBaseRoute):
    pass
