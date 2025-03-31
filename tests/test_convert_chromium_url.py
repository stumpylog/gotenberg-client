# SPDX-FileCopyrightText: 2023-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
import json
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


@pytest.mark.usefixtures("webserver_docker_internal_url")
class TestConvertChromiumUrlMocked:
    @pytest.mark.parametrize(
        ("emulation"),
        ["screen", "print"],
    )
    def test_convert_orientation(
        self,
        sync_client: GotenbergClient,
        webserver_docker_internal_url: str,
        httpx_mock: HTTPXMock,
        emulation: Literal["screen", "print"],
    ):
        httpx_mock.add_response(method="POST")

        with sync_client.chromium.url_to_pdf() as route:
            _ = route.url(webserver_docker_internal_url).media_type(emulation).run()

        verify_stream_contains(httpx_mock.get_request(), "emulatedMediaType", emulation)

    @pytest.mark.parametrize(
        ("method"),
        ["prefer_css_page_size", "prefer_set_page_size"],
    )
    def test_convert_css_or_not_size(
        self,
        sync_client: GotenbergClient,
        webserver_docker_internal_url: str,
        httpx_mock: HTTPXMock,
        method: str,
    ):
        httpx_mock.add_response(method="POST")

        with sync_client.chromium.url_to_pdf() as route:
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
        sync_client: GotenbergClient,
        webserver_docker_internal_url: str,
        httpx_mock: HTTPXMock,
        method: str,
    ):
        httpx_mock.add_response(method="POST")

        with sync_client.chromium.url_to_pdf() as route:
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
        sync_client: GotenbergClient,
        webserver_docker_internal_url: str,
        httpx_mock: HTTPXMock,
        method: str,
    ):
        httpx_mock.add_response(method="POST")

        with sync_client.chromium.url_to_pdf() as route:
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
        sync_client: GotenbergClient,
        webserver_docker_internal_url: str,
        httpx_mock: HTTPXMock,
        method: str,
    ):
        httpx_mock.add_response(method="POST")

        with sync_client.chromium.url_to_pdf() as route:
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
        sync_client: GotenbergClient,
        webserver_docker_internal_url: str,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")

        with sync_client.chromium.url_to_pdf() as route:
            _ = route.url(webserver_docker_internal_url).scale(1.5).run()

        verify_stream_contains(
            httpx_mock.get_request(),
            "scale",
            "1.5",
        )

    def test_convert_page_ranges(
        self,
        sync_client: GotenbergClient,
        webserver_docker_internal_url: str,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")

        with sync_client.chromium.url_to_pdf() as route:
            _ = route.url(webserver_docker_internal_url).page_ranges("1-5").run()

        verify_stream_contains(
            httpx_mock.get_request(),
            "nativePageRanges",
            "1-5",
        )

    def test_convert_url_render_wait(
        self,
        sync_client: GotenbergClient,
        webserver_docker_internal_url: str,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")

        with sync_client.chromium.url_to_pdf() as route:
            _ = route.url(webserver_docker_internal_url).render_wait(500).run()

        verify_stream_contains(
            httpx_mock.get_request(),
            "waitDelay",
            "500",
        )

    def test_convert_url_render_wait_error(
        self,
        sync_url_to_pdf_route: SyncUrlToPdfRoute,
        webserver_docker_internal_url: str,
    ):
        with pytest.raises(NegativeWaitDurationError):
            sync_url_to_pdf_route.url(webserver_docker_internal_url).render_wait(-1).run()

    def test_convert_url_render_expression(
        self,
        sync_client: GotenbergClient,
        webserver_docker_internal_url: str,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")

        with sync_client.chromium.url_to_pdf() as route:
            _ = route.url(webserver_docker_internal_url).render_expression("wait while false;").run()

        verify_stream_contains(
            httpx_mock.get_request(),
            "waitForExpression",
            "wait while false;",
        )

    def test_convert_url_user_agent(
        self,
        sync_client: GotenbergClient,
        webserver_docker_internal_url: str,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")

        with sync_client.chromium.url_to_pdf() as route:
            _ = route.url(webserver_docker_internal_url).user_agent("Firefox").run()

        verify_stream_contains(
            httpx_mock.get_request(),
            "userAgent",
            "Firefox",
        )

    def test_convert_url_headers(
        self,
        sync_client: GotenbergClient,
        webserver_docker_internal_url: str,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")

        headers = {"X-Auth-Token": "Secure"}

        with sync_client.chromium.url_to_pdf() as route:
            _ = route.url(webserver_docker_internal_url).headers(headers).run()
        verify_stream_contains(
            httpx_mock.get_request(),
            "extraHttpHeaders",
            json.dumps(headers),
        )
