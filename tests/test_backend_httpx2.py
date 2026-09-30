# SPDX-FileCopyrightText: 2025-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
"""
Integration tests for the httpx2 backend against a real Gotenberg server (Docker).
These run a representative subset of routes — just enough to prove end-to-end connectivity.
"""

import logging
from collections.abc import AsyncGenerator
from collections.abc import Generator
from http import HTTPStatus
from pathlib import Path

import pytest

from gotenberg_client import AsyncGotenbergClient
from gotenberg_client import HealthStatus
from gotenberg_client import SyncGotenbergClient


@pytest.fixture
def sync_httpx2_client(gotenberg_host: str) -> Generator[SyncGotenbergClient, None, None]:
    with SyncGotenbergClient(host=gotenberg_host, backend="httpx2", log_level=logging.INFO) as c:
        yield c


@pytest.fixture
async def async_httpx2_client(gotenberg_host: str) -> AsyncGenerator[AsyncGotenbergClient, None]:
    async with AsyncGotenbergClient(host=gotenberg_host, backend="httpx2", log_level=logging.INFO) as c:
        yield c


@pytest.mark.live
@pytest.mark.httpx2
class TestHttpx2BackendSync:
    @pytest.mark.flaky(reruns=5, rerun_delay=5)
    def test_health_check(self, sync_httpx2_client: SyncGotenbergClient):
        with sync_httpx2_client.health as api:
            status = api.health()
        assert isinstance(status, HealthStatus)

    def test_chromium_html_to_pdf(self, sync_httpx2_client: SyncGotenbergClient, basic_html_file: Path):
        with sync_httpx2_client.chromium.html_to_pdf() as route:
            resp = route.index(basic_html_file).run()
        assert resp.status_code == HTTPStatus.OK
        assert resp.headers["Content-Type"] == "application/pdf"

    def test_libre_office_to_pdf(self, sync_httpx2_client: SyncGotenbergClient, odt_sample_file: Path):
        with sync_httpx2_client.libre_office.to_pdf() as route:
            resp = route.convert(odt_sample_file).run()
        assert resp.status_code == HTTPStatus.OK
        assert resp.headers["Content-Type"] == "application/pdf"

    def test_merge_pdfs(self, sync_httpx2_client: SyncGotenbergClient, sample_directory: Path):
        with sync_httpx2_client.merge.merge() as route:
            resp = route.merge(
                [sample_directory / "z_first_merge.pdf", sample_directory / "a_merge_second.pdf"],
            ).run()
        assert resp.status_code == HTTPStatus.OK
        assert resp.headers["Content-Type"] == "application/pdf"


@pytest.mark.live
@pytest.mark.httpx2
@pytest.mark.async_route
class TestHttpx2BackendAsync:
    @pytest.mark.flaky(reruns=5, rerun_delay=5)
    async def test_health_check(self, async_httpx2_client: AsyncGotenbergClient):
        async with async_httpx2_client.health as api:
            status = await api.health()
        assert isinstance(status, HealthStatus)

    async def test_chromium_html_to_pdf(self, async_httpx2_client: AsyncGotenbergClient, basic_html_file: Path):
        async with async_httpx2_client.chromium.html_to_pdf() as route:
            resp = await route.index(basic_html_file).run()
        assert resp.status_code == HTTPStatus.OK
        assert resp.headers["Content-Type"] == "application/pdf"
