# SPDX-FileCopyrightText: 2025-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
from pathlib import Path

import pytest
from pytest_httpx import HTTPXMock

from gotenberg_client import GotenbergClient
from gotenberg_client._others.routes import AsyncStampRoute
from gotenberg_client.options import WatermarkStampSource
from tests.utils import verify_basic_response_values_pdf
from tests.utils import verify_stream_contains


class TestStampRouteMocked:
    def test_stamp_text_mocked(
        self,
        mock_sync_client: GotenbergClient,
        sample_directory: Path,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")
        with mock_sync_client.stamp.stamp() as route:
            route.add_file(sample_directory / "sample1.pdf").stamp_source(WatermarkStampSource.Text).stamp_expression(
                "CONFIDENTIAL",
            ).run()
        verify_stream_contains(httpx_mock.get_request(), "stampSource", "text")
        verify_stream_contains(httpx_mock.get_request(), "stampExpression", "CONFIDENTIAL")

    def test_stamp_add_files_mocked(
        self,
        mock_sync_client: GotenbergClient,
        sample_directory: Path,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")
        with mock_sync_client.stamp.stamp() as route:
            route.add_files([sample_directory / "sample1.pdf"]).stamp_source(
                WatermarkStampSource.Text,
            ).stamp_expression("CONFIDENTIAL").run()
        verify_stream_contains(httpx_mock.get_request(), "stampExpression", "CONFIDENTIAL")


@pytest.mark.live
@pytest.mark.async_route
class TestStampRouteLive:
    async def test_stamp_pdf(
        self,
        async_stamp_route: AsyncStampRoute,
        pdf_sample_one_file: Path,
    ):
        resp = (
            await async_stamp_route.add_file(pdf_sample_one_file)
            .stamp_source(WatermarkStampSource.Text)
            .stamp_expression("CONFIDENTIAL")
            .run_with_retry()
        )
        verify_basic_response_values_pdf(resp)
