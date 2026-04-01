# SPDX-FileCopyrightText: 2025-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
from pytest_httpx import HTTPXMock

from gotenberg_client import AsyncGotenbergClient
from gotenberg_client import GotenbergClient


class TestVersionApiMocked:
    def test_version_mocked(
        self,
        sync_client: GotenbergClient,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="GET", text="8.29.1")
        version = sync_client.version.get()
        assert version == "8.29.1"


class TestVersionApiLive:
    def test_version_sync(self, sync_client: GotenbergClient):
        version = sync_client.version.get()
        assert isinstance(version, str)
        assert len(version) > 0
        parts = version.split(".")
        assert len(parts) == 3
        assert all(p.isdigit() for p in parts)

    async def test_version_async(self, async_client: AsyncGotenbergClient):
        version = await async_client.version.get()
        assert isinstance(version, str)
        assert len(version) > 0
        parts = version.split(".")
        assert len(parts) == 3
        assert all(p.isdigit() for p in parts)
