# SPDX-FileCopyrightText: 2025-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
import pytest
from pytest_httpx import HTTPXMock

from gotenberg_client import GotenbergClient
from gotenberg_client._version import AsyncVersionApi
from gotenberg_client._version import SyncVersionApi


class TestVersionApiMocked:
    def test_version_mocked(
        self,
        mock_sync_client: GotenbergClient,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="GET", text="8.29.1")
        with mock_sync_client.version as api:
            version = api.get()
        assert version == "8.29.1"


@pytest.mark.live
@pytest.mark.flaky(reruns=3)
class TestVersionApiLive:
    def test_version_sync(self, sync_version_api: SyncVersionApi):
        version = sync_version_api.get()
        assert isinstance(version, str)
        assert len(version) > 0
        # semver (e.g. "8.29.1") or a build tag (e.g. "edge")
        if "." in version:
            parts = version.split(".")
            assert len(parts) == 3
            assert all(p.isdigit() for p in parts)

    async def test_version_async(self, async_version_api: AsyncVersionApi):
        version = await async_version_api.get()
        assert isinstance(version, str)
        assert len(version) > 0
        # semver (e.g. "8.29.1") or a build tag (e.g. "edge")
        if "." in version:
            parts = version.split(".")
            assert len(parts) == 3
            assert all(p.isdigit() for p in parts)
