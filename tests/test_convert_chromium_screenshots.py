# SPDX-FileCopyrightText: 2023-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
import pytest
from httpx import codes

from gotenberg_client import GotenbergClient
from tests.conftest import SAMPLE_DIR
from tests.conftest import SAVE_DIR
from tests.conftest import SAVE_OUTPUTS


class TestChromiumScreenshots:
    def test_basic_screenshot(self, client: GotenbergClient):
        with client.chromium.screenshot_url() as route:
            resp = route.url("http://localhost:8888").run_with_retry()

        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "image/png"
        if SAVE_OUTPUTS:
            (SAVE_DIR / "test_basic_screenshot.png").write_bytes(resp.content)

    @pytest.mark.parametrize(
        "image_format",
        ["png", "webp", "jpeg"],
    )
    def test_screenshot_formats(self, client: GotenbergClient, image_format: str):
        with client.chromium.screenshot_url() as route:
            resp = route.url("http://localhost:8888").output_format(image_format).run_with_retry()

        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == f"image/{image_format}"
        if SAVE_OUTPUTS:
            (SAVE_DIR / f"test_screenshot_formats.{image_format}").write_bytes(resp.content)

    def test_screenshot_quality_valid(self, client: GotenbergClient):
        with client.chromium.screenshot_url() as route:
            resp = route.url("http://localhost:8888").quality(80).run_with_retry()

        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "image/png"
        if SAVE_OUTPUTS:
            (SAVE_DIR / "test_screenshot_quality_valid.png").write_bytes(resp.content)

    def test_screenshot_quality_too_low(self, client: GotenbergClient):
        with client.chromium.screenshot_url() as route:
            resp = route.url("http://localhost:8888").quality(-10).run_with_retry()

        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "image/png"
        if SAVE_OUTPUTS:
            (SAVE_DIR / "test_screenshot_quality_too_low.png").write_bytes(resp.content)

    def test_screenshot_quality_too_high(self, client: GotenbergClient):
        with client.chromium.screenshot_url() as route:
            resp = route.url("http://localhost:8888").quality(101).run_with_retry()

        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "image/png"
        if SAVE_OUTPUTS:
            (SAVE_DIR / "test_screenshot_quality_too_high.png").write_bytes(resp.content)

    def test_screenshot_optimize_speed(self, client: GotenbergClient):
        with client.chromium.screenshot_url() as route:
            resp = route.url("http://localhost:8888").optimize_speed().run_with_retry()

        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "image/png"
        if SAVE_OUTPUTS:
            (SAVE_DIR / "test_screenshot_optimize_speed.png").write_bytes(resp.content)

    def test_screenshot_optimize_quality(self, client: GotenbergClient):
        with client.chromium.screenshot_url() as route:
            resp = route.url("http://localhost:8888").optimize_size().run_with_retry()

        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "image/png"
        if SAVE_OUTPUTS:
            (SAVE_DIR / "test_screenshot_optimize_quality.png").write_bytes(resp.content)

    def test_network_idle_on(self, client: GotenbergClient):
        with client.chromium.screenshot_url() as route:
            resp = route.url("http://localhost:8888").skip_network_idle().run_with_retry()

        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "image/png"
        if SAVE_OUTPUTS:
            (SAVE_DIR / "test_screenshot_optimize_quality.png").write_bytes(resp.content)

    def test_network_idle_off(self, client: GotenbergClient):
        with client.chromium.screenshot_url() as route:
            resp = route.url("http://localhost:8888").use_network_idle().run_with_retry()

        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "image/png"
        if SAVE_OUTPUTS:
            (SAVE_DIR / "test_screenshot_optimize_quality.png").write_bytes(resp.content)

    def test_status_codes(self, client: GotenbergClient):
        with client.chromium.screenshot_url() as route:
            resp = route.url("http://localhost:8888").fail_on_status_codes([499, 599]).run_with_retry()

        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "image/png"
        if SAVE_OUTPUTS:
            (SAVE_DIR / "test_screenshot_optimize_quality.png").write_bytes(resp.content)

    def test_status_codes_empty(self, client: GotenbergClient):
        with client.chromium.screenshot_url() as route:
            resp = route.url("http://localhost:8888").fail_on_status_codes([]).run_with_retry()

        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "image/png"
        if SAVE_OUTPUTS:
            (SAVE_DIR / "test_screenshot_optimize_quality.png").write_bytes(resp.content)


class TestChromiumScreenshotsFromMarkdown:
    def test_markdown_screenshot(self, client: GotenbergClient):
        test_file = SAMPLE_DIR / "basic.html"
        md_files = [SAMPLE_DIR / "markdown1.md", SAMPLE_DIR / "markdown2.md"]

        with client.chromium.screenshot_markdown() as route:
            resp = route.index(test_file).resources(md_files).run_with_retry()
        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "image/png"


class TestChromiumScreenshotsFromHtml:
    def test_markdown_screenshot(self, client: GotenbergClient):
        test_file = SAMPLE_DIR / "basic.html"

        with client.chromium.screenshot_html() as route:
            resp = route.index(test_file).run_with_retry()
        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "image/png"
