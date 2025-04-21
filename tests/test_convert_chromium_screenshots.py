# SPDX-FileCopyrightText: 2023-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
from http import HTTPStatus
from pathlib import Path
from typing import Literal

import pytest

from gotenberg_client import GotenbergClient
from gotenberg_client._chromium.routes import AsyncScreenshotFromHtmlRoute
from gotenberg_client._chromium.routes import AsyncScreenshotFromMarkdownRoute
from gotenberg_client._chromium.routes import AsyncScreenshotFromUrlRoute


@pytest.mark.usefixtures("web_server_host")
class TestConvertChromiumScreenshotFromUrl:
    def test_basic_screenshot(self, sync_client: GotenbergClient, webserver_docker_internal_url: str):
        with sync_client.chromium.screenshot_url() as route:
            resp = route.url(webserver_docker_internal_url).run_with_retry()

        assert resp.status_code == HTTPStatus.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "image/png"

    async def test_basic_screenshot_sync(
        self,
        async_screenshot_url_route: AsyncScreenshotFromUrlRoute,
        webserver_docker_internal_url: str,
    ):
        resp = await async_screenshot_url_route.url(webserver_docker_internal_url).run_with_retry()

        assert resp.status_code == HTTPStatus.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "image/png"

    @pytest.mark.parametrize(
        "image_format",
        ["png", "webp", "jpeg"],
    )
    def test_screenshot_formats(
        self,
        sync_client: GotenbergClient,
        webserver_docker_internal_url: str,
        image_format: Literal["png", "webp", "jpeg"],
    ):
        with sync_client.chromium.screenshot_url() as route:
            resp = route.url(webserver_docker_internal_url).output_format(image_format).run_with_retry()

        assert resp.status_code == HTTPStatus.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == f"image/{image_format}"

    def test_screenshot_quality_valid(self, sync_client: GotenbergClient, webserver_docker_internal_url: str):
        with sync_client.chromium.screenshot_url() as route:
            resp = route.url(webserver_docker_internal_url).quality(80).run_with_retry()

        assert resp.status_code == HTTPStatus.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "image/png"

    def test_screenshot_quality_too_low(self, sync_client: GotenbergClient, webserver_docker_internal_url: str):
        with sync_client.chromium.screenshot_url() as route:
            resp = route.url(webserver_docker_internal_url).quality(-10).run_with_retry()

        assert resp.status_code == HTTPStatus.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "image/png"

    def test_screenshot_quality_too_high(self, sync_client: GotenbergClient, webserver_docker_internal_url: str):
        with sync_client.chromium.screenshot_url() as route:
            resp = route.url(webserver_docker_internal_url).quality(101).run_with_retry()

        assert resp.status_code == HTTPStatus.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "image/png"

    def test_screenshot_optimize_speed(self, sync_client: GotenbergClient, webserver_docker_internal_url: str):
        with sync_client.chromium.screenshot_url() as route:
            resp = route.url(webserver_docker_internal_url).image_optimize_for_speed().run_with_retry()

        assert resp.status_code == HTTPStatus.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "image/png"

    def test_screenshot_optimize_quality(self, sync_client: GotenbergClient, webserver_docker_internal_url: str):
        with sync_client.chromium.screenshot_url() as route:
            resp = route.url(webserver_docker_internal_url).image_optimize_for_quality().run_with_retry()

        assert resp.status_code == HTTPStatus.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "image/png"

    def test_network_idle_on(self, sync_client: GotenbergClient, webserver_docker_internal_url: str):
        with sync_client.chromium.screenshot_url() as route:
            resp = route.url(webserver_docker_internal_url).skip_network_idle().run_with_retry()

        assert resp.status_code == HTTPStatus.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "image/png"

    def test_network_idle_off(self, sync_client: GotenbergClient, webserver_docker_internal_url: str):
        with sync_client.chromium.screenshot_url() as route:
            resp = route.url(webserver_docker_internal_url).use_network_idle().run_with_retry()

        assert resp.status_code == HTTPStatus.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "image/png"

    def test_screen_size(self, sync_client: GotenbergClient, webserver_docker_internal_url: str):
        with sync_client.chromium.screenshot_url() as route:
            resp = route.url(webserver_docker_internal_url).width(800).height(1200).run_with_retry()

        assert resp.status_code == HTTPStatus.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "image/png"

    def test_clipping(self, sync_client: GotenbergClient, webserver_docker_internal_url: str):
        with sync_client.chromium.screenshot_url() as route:
            resp = (
                route.url(webserver_docker_internal_url).no_clip_to_dimensions().clip_to_dimensions().run_with_retry()
            )

        assert resp.status_code == HTTPStatus.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "image/png"

    def test_status_codes(self, sync_client: GotenbergClient, webserver_docker_internal_url: str):
        with sync_client.chromium.screenshot_url() as route:
            resp = (
                route.url(webserver_docker_internal_url)
                .fail_on_status_codes([HTTPStatus.INTERNAL_SERVER_ERROR, HTTPStatus.NETWORK_AUTHENTICATION_REQUIRED])
                .run_with_retry()
            )

        assert resp.status_code == HTTPStatus.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "image/png"

    def test_status_codes_empty(self, sync_client: GotenbergClient, webserver_docker_internal_url: str):
        with sync_client.chromium.screenshot_url() as route:
            resp = route.url(webserver_docker_internal_url).fail_on_status_codes([]).run_with_retry()

        assert resp.status_code == HTTPStatus.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "image/png"


class TestConvertChromiumScreenshotFromMarkdown:
    def test_markdown_screenshot(
        self,
        sync_client: GotenbergClient,
        basic_html_file: Path,
        markdown_sample_one_file: Path,
        markdown_sample_two_file: Path,
    ):
        with sync_client.chromium.screenshot_markdown() as route:
            resp = (
                route.index(basic_html_file)
                .resources([markdown_sample_one_file, markdown_sample_two_file])
                .run_with_retry()
            )
        assert resp.status_code == HTTPStatus.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "image/png"

    async def test_markdown_screenshot_async(
        self,
        async_screenshot_markdown_route: AsyncScreenshotFromMarkdownRoute,
        basic_html_file: Path,
        markdown_sample_one_file: Path,
        markdown_sample_two_file: Path,
    ):
        resp = await (
            async_screenshot_markdown_route.index(basic_html_file)
            .resources([markdown_sample_one_file, markdown_sample_two_file])
            .run_with_retry()
        )
        assert resp.status_code == HTTPStatus.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "image/png"


class TestConvertChromiumScreenshotFromHtml:
    def test_html_screenshot(self, sync_client: GotenbergClient, basic_html_file: Path):
        with sync_client.chromium.screenshot_html() as route:
            resp = route.index(basic_html_file).run_with_retry()
        assert resp.status_code == HTTPStatus.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "image/png"

    async def test_html_screenshot_async(
        self,
        async_screenshot_html_route: AsyncScreenshotFromHtmlRoute,
        basic_html_file: Path,
    ):
        resp = await async_screenshot_html_route.index(basic_html_file).run_with_retry()
        assert resp.status_code == HTTPStatus.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "image/png"
