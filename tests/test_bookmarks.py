# SPDX-FileCopyrightText: 2025-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
from pathlib import Path

from pytest_httpx import HTTPXMock

from gotenberg_client import BookmarkEntry
from gotenberg_client import GotenbergClient
from gotenberg_client._bookmarks.routes import AsyncReadBookmarksRoute
from gotenberg_client._bookmarks.routes import AsyncWriteBookmarksRoute
from tests.utils import verify_basic_response_values_pdf
from tests.utils import verify_stream_contains


class TestReadBookmarksRouteMocked:
    def test_read_bookmarks_mocked(
        self,
        sync_client: GotenbergClient,
        sample_directory: Path,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST", json={"sample1.pdf": []})
        with sync_client.bookmarks.read() as route:
            result = route.read(sample_directory / "sample1.pdf").run()
        assert isinstance(result, dict)


class TestWriteBookmarksRouteMocked:
    def test_write_bookmarks_mocked(
        self,
        sync_client: GotenbergClient,
        sample_directory: Path,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")
        bookmarks: list[BookmarkEntry] = [{"title": "Chapter 1", "page": 1, "children": []}]
        with sync_client.bookmarks.write() as route:
            route.add_file(sample_directory / "sample1.pdf").bookmarks(bookmarks).run()
        verify_stream_contains(httpx_mock.get_request(), "bookmarks", "Chapter 1")


class TestReadBookmarksRouteLive:
    async def test_read_bookmarks(
        self,
        async_read_bookmarks_route: AsyncReadBookmarksRoute,
        pdf_sample_one_file: Path,
    ):
        result = await async_read_bookmarks_route.read(pdf_sample_one_file).run_with_retry()
        assert isinstance(result, dict)
        # sample1.pdf key should be present; bookmarks list may be empty if the PDF has none
        assert "sample1.pdf" in result
        assert isinstance(result["sample1.pdf"], list)


class TestWriteBookmarksRouteLive:
    async def test_write_bookmarks(
        self,
        async_write_bookmarks_route: AsyncWriteBookmarksRoute,
        pdf_sample_one_file: Path,
    ):
        bookmarks: list[BookmarkEntry] = [
            {"title": "Chapter 1", "page": 1, "children": []},
            {"title": "Chapter 2", "page": 1, "children": [{"title": "Section 2.1", "page": 1, "children": []}]},
        ]
        resp = await async_write_bookmarks_route.add_file(pdf_sample_one_file).bookmarks(bookmarks).run_with_retry()
        verify_basic_response_values_pdf(resp)
