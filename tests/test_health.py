# SPDX-FileCopyrightText: 2023-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
from gotenberg_client._health import AsyncHealthCheckApi
from gotenberg_client._health import StatusOptions
from gotenberg_client._health import SyncHealthCheckApi


class TestHealthStatus:
    def test_health_endpoint(
        self,
        sync_health_api: SyncHealthCheckApi,
    ):
        status = sync_health_api.health()
        assert status.overall == StatusOptions.Up
        assert status.chromium is not None
        assert status.chromium.status == StatusOptions.Up
        if "uno" in status.data:  # pragma: no cover
            assert status.uno is not None
            assert status.uno.status == StatusOptions.Up

    async def test_health_endpoint_async(
        self,
        async_health_api: AsyncHealthCheckApi,
    ):
        status = await async_health_api.health()
        assert status.overall == StatusOptions.Up
        assert status.chromium is not None
        assert status.chromium.status == StatusOptions.Up
        if "uno" in status.data:  # pragma: no cover
            assert status.uno is not None
            assert status.uno.status == StatusOptions.Up
