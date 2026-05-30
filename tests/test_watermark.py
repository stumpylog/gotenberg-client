# SPDX-FileCopyrightText: 2025-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
from pathlib import Path

import pytest
from pytest_httpx import HTTPXMock

from gotenberg_client import GotenbergClient
from gotenberg_client._others.routes import AsyncWatermarkRoute
from gotenberg_client.options import WatermarkStampSource
from tests.utils import verify_basic_response_values_pdf
from tests.utils import verify_stream_contains


class TestWatermarkRouteMocked:
    def test_watermark_text_mocked(
        self,
        mock_sync_client: GotenbergClient,
        sample_directory: Path,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")
        with mock_sync_client.watermark.watermark() as route:
            route.add_file(sample_directory / "sample1.pdf").watermark_source(
                WatermarkStampSource.Text,
            ).watermark_expression("DRAFT").run()
        verify_stream_contains(httpx_mock.get_request(), "watermarkSource", "text")
        verify_stream_contains(httpx_mock.get_request(), "watermarkExpression", "DRAFT")

    def test_watermark_add_files_mocked(
        self,
        mock_sync_client: GotenbergClient,
        sample_directory: Path,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")
        with mock_sync_client.watermark.watermark() as route:
            route.add_files([sample_directory / "sample1.pdf"]).watermark_source(
                WatermarkStampSource.Text,
            ).watermark_expression("DRAFT").run()
        verify_stream_contains(httpx_mock.get_request(), "watermarkExpression", "DRAFT")


@pytest.mark.live
@pytest.mark.async_route
class TestWatermarkRouteLive:
    async def test_watermark_pdf(
        self,
        async_watermark_route: AsyncWatermarkRoute,
        pdf_sample_one_file: Path,
    ):
        resp = (
            await async_watermark_route.add_file(pdf_sample_one_file)
            .watermark_source(WatermarkStampSource.Text)
            .watermark_expression("DRAFT")
            .run_with_retry()
        )
        verify_basic_response_values_pdf(resp)
