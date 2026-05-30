# SPDX-FileCopyrightText: 2025-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
from pathlib import Path

import pytest
from pytest_httpx import HTTPXMock

from gotenberg_client import GotenbergClient
from gotenberg_client._others.routes import AsyncRotateRoute
from gotenberg_client.options import RotateAngle
from tests.utils import verify_basic_response_values_pdf
from tests.utils import verify_stream_contains


class TestRotateRouteMocked:
    def test_rotate_90_mocked(
        self,
        mock_sync_client: GotenbergClient,
        sample_directory: Path,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")
        with mock_sync_client.rotate.rotate() as route:
            route.add_file(sample_directory / "sample1.pdf").rotate(RotateAngle.Clockwise90).run()
        verify_stream_contains(httpx_mock.get_request(), "rotateAngle", "90")

    def test_rotate_add_files_mocked(
        self,
        mock_sync_client: GotenbergClient,
        sample_directory: Path,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")
        with mock_sync_client.rotate.rotate() as route:
            route.add_files([sample_directory / "sample1.pdf"]).rotate(RotateAngle.Clockwise90).run()
        verify_stream_contains(httpx_mock.get_request(), "rotateAngle", "90")


@pytest.mark.live
@pytest.mark.async_route
class TestRotateRouteLive:
    async def test_rotate_pdf(
        self,
        async_rotate_route: AsyncRotateRoute,
        pdf_sample_one_file: Path,
    ):
        resp = await async_rotate_route.add_file(pdf_sample_one_file).rotate(RotateAngle.Clockwise90).run_with_retry()
        verify_basic_response_values_pdf(resp)
