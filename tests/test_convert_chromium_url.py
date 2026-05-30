# SPDX-FileCopyrightText: 2023-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
import json
from http import HTTPStatus
from typing import Literal

import pytest
from pytest_httpx import HTTPXMock

from gotenberg_client import GotenbergClient
from gotenberg_client import NegativeWaitDurationError
from gotenberg_client._chromium.routes import AsyncUrlToPdfRoute
from gotenberg_client._chromium.routes import SyncUrlToPdfRoute
from gotenberg_client.options import CookieJar
from tests.utils import verify_basic_response_values_pdf
from tests.utils import verify_stream_contains


@pytest.mark.live
@pytest.mark.chromium
@pytest.mark.usefixtures("webserver_docker_internal_url")
class TestConvertChromiumUrl:
    def test_basic_convert_sync(self, sync_url_to_pdf_route: SyncUrlToPdfRoute, webserver_docker_internal_url: str):
        verify_basic_response_values_pdf(sync_url_to_pdf_route.url(webserver_docker_internal_url).run_with_retry())

    async def test_basic_convert_async(
        self,
        async_url_to_pdf_route: AsyncUrlToPdfRoute,
        webserver_docker_internal_url: str,
    ):
        verify_basic_response_values_pdf(
            await async_url_to_pdf_route.url(webserver_docker_internal_url).run_with_retry(),
        )

    async def test_basic_convert_cookies(
        self,
        async_url_to_pdf_route: AsyncUrlToPdfRoute,
        webserver_docker_internal_url: str,
    ):
        verify_basic_response_values_pdf(
            await async_url_to_pdf_route.url(webserver_docker_internal_url)
            .cookies([CookieJar("someCookie", "someValue", "mydomain.com", "/path", True, True, "Lax")])
            .run_with_retry(),
        )


@pytest.mark.chromium
@pytest.mark.usefixtures("webserver_docker_internal_url")
class TestConvertChromiumUrlMocked:
    @pytest.mark.parametrize(
        ("emulation"),
        ["screen", "print"],
    )
    def test_convert_orientation(
        self,
        mock_sync_client: GotenbergClient,
        webserver_docker_internal_url: str,
        httpx_mock: HTTPXMock,
        emulation: Literal["screen", "print"],
    ):
        httpx_mock.add_response(method="POST")

        with mock_sync_client.chromium.url_to_pdf() as route:
            _ = route.url(webserver_docker_internal_url).media_type(emulation).run()

        verify_stream_contains(httpx_mock.get_request(), "emulatedMediaType", emulation)

    @pytest.mark.parametrize(
        ("method"),
        ["prefer_css_page_size", "prefer_set_page_size"],
    )
    def test_convert_css_or_not_size(
        self,
        mock_sync_client: GotenbergClient,
        webserver_docker_internal_url: str,
        httpx_mock: HTTPXMock,
        method: str,
    ):
        httpx_mock.add_response(method="POST")

        with mock_sync_client.chromium.url_to_pdf() as route:
            route.url(webserver_docker_internal_url)
            getattr(route, method)()
            _ = route.run()

        verify_stream_contains(
            httpx_mock.get_request(),
            "preferCssPageSize",
            "true" if method == "prefer_css_page_size" else "false",
        )

    @pytest.mark.parametrize(
        ("method"),
        ["background_graphics", "no_background_graphics"],
    )
    def test_convert_background_graphics_or_not(
        self,
        mock_sync_client: GotenbergClient,
        webserver_docker_internal_url: str,
        httpx_mock: HTTPXMock,
        method: str,
    ):
        httpx_mock.add_response(method="POST")

        with mock_sync_client.chromium.url_to_pdf() as route:
            route.url(webserver_docker_internal_url)
            getattr(route, method)()
            _ = route.run()

        verify_stream_contains(
            httpx_mock.get_request(),
            "printBackground",
            "true" if method == "background_graphics" else "false",
        )

    @pytest.mark.parametrize(
        ("method"),
        ["hide_background", "show_background"],
    )
    def test_convert_hide_background_or_not(
        self,
        mock_sync_client: GotenbergClient,
        webserver_docker_internal_url: str,
        httpx_mock: HTTPXMock,
        method: str,
    ):
        httpx_mock.add_response(method="POST")

        with mock_sync_client.chromium.url_to_pdf() as route:
            route.url(webserver_docker_internal_url)
            getattr(route, method)()
            _ = route.run()

        verify_stream_contains(
            httpx_mock.get_request(),
            "omitBackground",
            "true" if method == "hide_background" else "false",
        )

    @pytest.mark.parametrize(
        ("method"),
        ["fail_on_exceptions", "dont_fail_on_exceptions"],
    )
    def test_convert_fail_exceptions(
        self,
        mock_sync_client: GotenbergClient,
        webserver_docker_internal_url: str,
        httpx_mock: HTTPXMock,
        method: str,
    ):
        httpx_mock.add_response(method="POST")

        with mock_sync_client.chromium.url_to_pdf() as route:
            route.url(webserver_docker_internal_url)
            getattr(route, method)()
            _ = route.run()

        verify_stream_contains(
            httpx_mock.get_request(),
            "failOnConsoleExceptions",
            "true" if method == "fail_on_exceptions" else "false",
        )

    def test_convert_scale(
        self,
        mock_sync_client: GotenbergClient,
        webserver_docker_internal_url: str,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")

        with mock_sync_client.chromium.url_to_pdf() as route:
            _ = route.url(webserver_docker_internal_url).scale(1.5).run()

        verify_stream_contains(
            httpx_mock.get_request(),
            "scale",
            "1.5",
        )

    def test_convert_page_ranges(
        self,
        mock_sync_client: GotenbergClient,
        webserver_docker_internal_url: str,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")

        with mock_sync_client.chromium.url_to_pdf() as route:
            _ = route.url(webserver_docker_internal_url).page_ranges("1-5").run()

        verify_stream_contains(
            httpx_mock.get_request(),
            "nativePageRanges",
            "1-5",
        )

    def test_convert_url_render_wait(
        self,
        mock_sync_client: GotenbergClient,
        webserver_docker_internal_url: str,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")

        with mock_sync_client.chromium.url_to_pdf() as route:
            _ = route.url(webserver_docker_internal_url).render_wait(500).run()

        verify_stream_contains(
            httpx_mock.get_request(),
            "waitDelay",
            "500",
        )

    def test_convert_url_render_wait_error(
        self,
        mock_sync_client: GotenbergClient,
        webserver_docker_internal_url: str,
    ):
        # The negative duration is rejected client-side before any request is sent,
        # so no server (and no httpx_mock) is required.
        with pytest.raises(NegativeWaitDurationError), mock_sync_client.chromium.url_to_pdf() as route:
            route.url(webserver_docker_internal_url).render_wait(-1).run()

    def test_convert_url_render_expression(
        self,
        mock_sync_client: GotenbergClient,
        webserver_docker_internal_url: str,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")

        with mock_sync_client.chromium.url_to_pdf() as route:
            _ = route.url(webserver_docker_internal_url).render_expression("wait while false;").run()

        verify_stream_contains(
            httpx_mock.get_request(),
            "waitForExpression",
            "wait while false;",
        )

    def test_convert_url_user_agent(
        self,
        mock_sync_client: GotenbergClient,
        webserver_docker_internal_url: str,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")

        with mock_sync_client.chromium.url_to_pdf() as route:
            _ = route.url(webserver_docker_internal_url).user_agent("Firefox").run()

        verify_stream_contains(
            httpx_mock.get_request(),
            "userAgent",
            "Firefox",
        )

    def test_convert_url_headers(
        self,
        mock_sync_client: GotenbergClient,
        webserver_docker_internal_url: str,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")

        headers = {"X-Auth-Token": "Secure"}

        with mock_sync_client.chromium.url_to_pdf() as route:
            _ = route.url(webserver_docker_internal_url).headers(headers).run()
        verify_stream_contains(
            httpx_mock.get_request(),
            "extraHttpHeaders",
            json.dumps(headers),
        )

    def test_convert_url_flatten(
        self,
        mock_sync_client: GotenbergClient,
        webserver_docker_internal_url: str,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")
        with mock_sync_client.chromium.url_to_pdf() as route:
            route.url(webserver_docker_internal_url).flatten(flatten=True).run()
        verify_stream_contains(httpx_mock.get_request(), "flatten", "true")

    def test_wait_for_selector(
        self,
        mock_sync_client: GotenbergClient,
        webserver_docker_internal_url: str,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")
        with mock_sync_client.chromium.url_to_pdf() as route:
            route.url(webserver_docker_internal_url).wait_for_selector("#main-content").run()
        verify_stream_contains(httpx_mock.get_request(), "waitForSelector", "#main-content")

    def test_emulated_media_features(
        self,
        mock_sync_client: GotenbergClient,
        webserver_docker_internal_url: str,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")
        features = [{"name": "prefers-color-scheme", "value": "dark"}]
        with mock_sync_client.chromium.url_to_pdf() as route:
            route.url(webserver_docker_internal_url).emulated_media_features(features).run()
        verify_stream_contains(httpx_mock.get_request(), "emulatedMediaFeatures", "prefers-color-scheme")

    def test_fail_on_resource_http_status_codes(
        self,
        mock_sync_client: GotenbergClient,
        webserver_docker_internal_url: str,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")
        with mock_sync_client.chromium.url_to_pdf() as route:
            route.url(webserver_docker_internal_url).fail_on_resource_status_codes([HTTPStatus.NOT_FOUND]).run()
        verify_stream_contains(httpx_mock.get_request(), "failOnResourceHttpStatusCodes", "404")

    def test_ignore_resource_http_status_domains(
        self,
        mock_sync_client: GotenbergClient,
        webserver_docker_internal_url: str,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")
        with mock_sync_client.chromium.url_to_pdf() as route:
            route.url(webserver_docker_internal_url).ignore_resource_status_domains(["cdn.example.com"]).run()
        verify_stream_contains(httpx_mock.get_request(), "ignoreResourceHttpStatusDomains", "cdn.example.com")

    def test_skip_network_almost_idle_event(
        self,
        mock_sync_client: GotenbergClient,
        webserver_docker_internal_url: str,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")
        with mock_sync_client.chromium.url_to_pdf() as route:
            route.url(webserver_docker_internal_url).skip_network_almost_idle(skip=True).run()
        verify_stream_contains(httpx_mock.get_request(), "skipNetworkAlmostIdleEvent", "true")

    def test_generate_tagged_pdf(
        self,
        mock_sync_client: GotenbergClient,
        webserver_docker_internal_url: str,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")
        with mock_sync_client.chromium.url_to_pdf() as route:
            route.url(webserver_docker_internal_url).generate_tagged_pdf(generate=True).run()
        verify_stream_contains(httpx_mock.get_request(), "generateTaggedPdf", "true")

    def test_string_header(
        self,
        mock_sync_client: GotenbergClient,
        webserver_docker_internal_url: str,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")
        with mock_sync_client.chromium.url_to_pdf() as route:
            route.url(webserver_docker_internal_url).string_header("<html><body>Header</body></html>").run()
        request = httpx_mock.get_request()
        boundary = request.headers["Content-Type"].split("boundary=")[1]
        parts = request.content.split(f"--{boundary}".encode())
        assert any(b'filename="header.html"' in part for part in parts)

    def test_string_footer(
        self,
        mock_sync_client: GotenbergClient,
        webserver_docker_internal_url: str,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")
        with mock_sync_client.chromium.url_to_pdf() as route:
            route.url(webserver_docker_internal_url).string_footer("<html><body>Footer</body></html>").run()
        request = httpx_mock.get_request()
        boundary = request.headers["Content-Type"].split("boundary=")[1]
        parts = request.content.split(f"--{boundary}".encode())
        assert any(b'filename="footer.html"' in part for part in parts)
