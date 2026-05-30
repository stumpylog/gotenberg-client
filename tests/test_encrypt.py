# SPDX-FileCopyrightText: 2025-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
from pathlib import Path

import pytest
from pytest_httpx import HTTPXMock

from gotenberg_client import GotenbergClient
from gotenberg_client._others.routes import AsyncEncryptRoute
from tests.utils import verify_basic_response_values_pdf
from tests.utils import verify_stream_contains


class TestEncryptRouteMocked:
    def test_encrypt_user_password(
        self,
        mock_sync_client: GotenbergClient,
        sample_directory: Path,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")
        with mock_sync_client.encrypt.encrypt() as route:
            route.add_file(sample_directory / "sample1.pdf").user_password("open").run()
        verify_stream_contains(httpx_mock.get_request(), "userPassword", "open")

    def test_encrypt_owner_password(
        self,
        mock_sync_client: GotenbergClient,
        sample_directory: Path,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")
        with mock_sync_client.encrypt.encrypt() as route:
            route.add_file(sample_directory / "sample1.pdf").owner_password("owner").run()
        verify_stream_contains(httpx_mock.get_request(), "ownerPassword", "owner")

    def test_encrypt_add_files_mocked(
        self,
        mock_sync_client: GotenbergClient,
        sample_directory: Path,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")
        with mock_sync_client.encrypt.encrypt() as route:
            route.add_files([sample_directory / "sample1.pdf"]).user_password("open").run()
        verify_stream_contains(httpx_mock.get_request(), "userPassword", "open")


@pytest.mark.live
@pytest.mark.async_route
class TestEncryptRouteLive:
    async def test_encrypt_user_password(
        self,
        async_encrypt_route: AsyncEncryptRoute,
        pdf_sample_one_file: Path,
    ):
        resp = await async_encrypt_route.add_file(pdf_sample_one_file).user_password("open").run_with_retry()
        verify_basic_response_values_pdf(resp)

    async def test_encrypt_both_passwords(
        self,
        async_encrypt_route: AsyncEncryptRoute,
        pdf_sample_one_file: Path,
    ):
        # ownerPassword requires userPassword to also be set (userPassword is required by the API)
        resp = (
            await async_encrypt_route.add_file(pdf_sample_one_file)
            .user_password("open")
            .owner_password("owner")
            .run_with_retry()
        )
        verify_basic_response_values_pdf(resp)
