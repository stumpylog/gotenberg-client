# SPDX-FileCopyrightText: 2025-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
"""
Integration tests for the requests backend against a real Gotenberg server (Docker).
These run a representative subset of routes — just enough to prove end-to-end connectivity.
"""

import logging
from collections.abc import Generator
from http import HTTPStatus
from pathlib import Path

import pytest

from gotenberg_client import HealthStatus
from gotenberg_client import SyncGotenbergClient


@pytest.fixture
def sync_requests_client(gotenberg_host: str) -> Generator[SyncGotenbergClient, None, None]:
    with SyncGotenbergClient(host=gotenberg_host, backend="requests", log_level=logging.INFO) as c:
        yield c


@pytest.mark.live
@pytest.mark.requests
class TestRequestsBackendSync:
    @pytest.mark.flaky(reruns=5, rerun_delay=5)
    def test_health_check(self, sync_requests_client: SyncGotenbergClient):
        with sync_requests_client.health as api:
            status = api.health()
        assert isinstance(status, HealthStatus)

    def test_chromium_html_to_pdf(self, sync_requests_client: SyncGotenbergClient, basic_html_file: Path):
        with sync_requests_client.chromium.html_to_pdf() as route:
            resp = route.index(basic_html_file).run()
        assert resp.status_code == HTTPStatus.OK
        assert resp.headers["Content-Type"] == "application/pdf"

    def test_libre_office_to_pdf(self, sync_requests_client: SyncGotenbergClient, odt_sample_file: Path):
        with sync_requests_client.libre_office.to_pdf() as route:
            resp = route.convert(odt_sample_file).run()
        assert resp.status_code == HTTPStatus.OK
        assert resp.headers["Content-Type"] == "application/pdf"

    def test_merge_pdfs(self, sync_requests_client: SyncGotenbergClient, sample_directory: Path):
        with sync_requests_client.merge.merge() as route:
            resp = route.merge(
                [sample_directory / "z_first_merge.pdf", sample_directory / "a_merge_second.pdf"],
            ).run()
        assert resp.status_code == HTTPStatus.OK
        assert resp.headers["Content-Type"] == "application/pdf"
