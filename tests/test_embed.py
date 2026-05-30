# SPDX-FileCopyrightText: 2025-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
from pathlib import Path

import pytest
from pytest_httpx import HTTPXMock

from gotenberg_client import GotenbergClient
from gotenberg_client._others.routes import AsyncEmbedRoute
from tests.utils import verify_basic_response_values_pdf


class TestEmbedRouteMocked:
    def test_embed_file(
        self,
        mock_sync_client: GotenbergClient,
        sample_directory: Path,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")
        with mock_sync_client.embed.embed() as route:
            route.add_pdf(sample_directory / "sample1.pdf").embed(sample_directory / "basic.html").run()
        request = httpx_mock.get_request()
        boundary = request.headers["Content-Type"].split("boundary=")[1]
        parts = request.content.split(f"--{boundary}".encode())
        assert any(b'name="files"' in part for part in parts), "No files field found"
        assert any(b'name="embeds"' in part for part in parts), "No embeds field found"

    def test_embed_add_pdfs_mocked(
        self,
        mock_sync_client: GotenbergClient,
        sample_directory: Path,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")
        with mock_sync_client.embed.embed() as route:
            route.add_pdfs([sample_directory / "sample1.pdf"]).embed(sample_directory / "basic.html").run()
        request = httpx_mock.get_request()
        boundary = request.headers["Content-Type"].split("boundary=")[1]
        parts = request.content.split(f"--{boundary}".encode())
        assert any(b'name="files"' in part for part in parts), "No files field found"
        assert any(b'name="embeds"' in part for part in parts), "No embeds field found"


@pytest.mark.live
@pytest.mark.async_route
class TestEmbedRouteLive:
    async def test_embed_attachment(
        self,
        async_embed_route: AsyncEmbedRoute,
        pdf_sample_one_file: Path,
        sample_directory: Path,
    ):
        resp = (
            await async_embed_route.add_pdf(pdf_sample_one_file).embed(sample_directory / "basic.html").run_with_retry()
        )
        verify_basic_response_values_pdf(resp)
