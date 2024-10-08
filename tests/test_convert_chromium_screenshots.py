# SPDX-FileCopyrightText: 2023-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
from pathlib import Path
from typing import Literal

import pytest
from httpx import codes

from gotenberg_client import GotenbergClient


class TestChromiumScreenshots:
    def test_basic_screenshot(self, client: GotenbergClient, web_server_host: str):
        with client.chromium.screenshot_url() as route:
            resp = route.url(web_server_host).run_with_retry()

        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "image/png"

    @pytest.mark.parametrize(
        "image_format",
        ["png", "webp", "jpeg"],
    )
    def test_screenshot_formats(
        self,
        client: GotenbergClient,
        web_server_host: str,
        image_format: Literal["png", "webp", "jpeg"],
    ):
        with client.chromium.screenshot_url() as route:
            resp = route.url(web_server_host).output_format(image_format).run_with_retry()

        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == f"image/{image_format}"

    def test_screenshot_quality_valid(self, client: GotenbergClient, web_server_host: str):
        with client.chromium.screenshot_url() as route:
            resp = route.url(web_server_host).quality(80).run_with_retry()

        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "image/png"

    def test_screenshot_quality_too_low(self, client: GotenbergClient, web_server_host: str):
        with client.chromium.screenshot_url() as route:
            resp = route.url(web_server_host).quality(-10).run_with_retry()

        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "image/png"

    def test_screenshot_quality_too_high(self, client: GotenbergClient, web_server_host: str):
        with client.chromium.screenshot_url() as route:
            resp = route.url(web_server_host).quality(101).run_with_retry()

        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "image/png"

    def test_screenshot_optimize_speed(self, client: GotenbergClient, web_server_host: str):
        with client.chromium.screenshot_url() as route:
            resp = route.url(web_server_host).optimize_speed().run_with_retry()

        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "image/png"

    def test_screenshot_optimize_quality(self, client: GotenbergClient, web_server_host: str):
        with client.chromium.screenshot_url() as route:
            resp = route.url(web_server_host).optimize_size().run_with_retry()

        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "image/png"

    def test_network_idle_on(self, client: GotenbergClient, web_server_host: str):
        with client.chromium.screenshot_url() as route:
            resp = route.url(web_server_host).skip_network_idle().run_with_retry()

        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "image/png"

    def test_network_idle_off(self, client: GotenbergClient, web_server_host: str):
        with client.chromium.screenshot_url() as route:
            resp = route.url(web_server_host).use_network_idle().run_with_retry()

        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "image/png"

    def test_status_codes(self, client: GotenbergClient, web_server_host: str):
        with client.chromium.screenshot_url() as route:
            resp = route.url(web_server_host).fail_on_status_codes([499, 599]).run_with_retry()

        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "image/png"

    def test_status_codes_empty(self, client: GotenbergClient, web_server_host: str):
        with client.chromium.screenshot_url() as route:
            resp = route.url(web_server_host).fail_on_status_codes([]).run_with_retry()

        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "image/png"


class TestChromiumScreenshotsFromMarkdown:
    def test_markdown_screenshot(
        self,
        client: GotenbergClient,
        basic_html_file: Path,
        markdown_sample_one_file: Path,
        markdown_sample_two_file: Path,
    ):
        with client.chromium.screenshot_markdown() as route:
            resp = (
                route.index(basic_html_file)
                .resources([markdown_sample_one_file, markdown_sample_two_file])
                .run_with_retry()
            )
        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "image/png"


class TestChromiumScreenshotsFromHtml:
    def test_markdown_screenshot(self, client: GotenbergClient, basic_html_file: Path):
        with client.chromium.screenshot_html() as route:
            resp = route.index(basic_html_file).run_with_retry()
        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "image/png"
