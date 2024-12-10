# SPDX-FileCopyrightText: 2023-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
import json

import pytest
from httpx import codes
from pytest_httpx import HTTPXMock

from gotenberg_client import GotenbergClient
from gotenberg_client.options import EmulatedMediaType
from tests.utils import verify_stream_contains


@pytest.mark.usefixtures("webserver_docker_internal_url")
class TestConvertChromiumUrlRoute:
    def test_basic_convert(self, client: GotenbergClient, webserver_docker_internal_url: str):
        with client.chromium.url_to_pdf() as route:
            resp = route.url(webserver_docker_internal_url).run_with_retry()

        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "application/pdf"


@pytest.mark.usefixtures("webserver_docker_internal_url")
class TestConvertChromiumUrlMocked:
    @pytest.mark.parametrize(
        ("emulation"),
        [EmulatedMediaType.Screen, EmulatedMediaType.Print],
    )
    def test_convert_orientation(
        self,
        client: GotenbergClient,
        webserver_docker_internal_url: str,
        httpx_mock: HTTPXMock,
        emulation: EmulatedMediaType,
    ):
        httpx_mock.add_response(method="POST")

        with client.chromium.url_to_pdf() as route:
            _ = route.url(webserver_docker_internal_url).media_type(emulation).run()

        verify_stream_contains(
            httpx_mock.get_request(),
            "emulatedMediaType",
            "screen" if emulation == EmulatedMediaType.Screen else "print",
        )

    @pytest.mark.parametrize(
        ("method"),
        ["prefer_css_page_size", "prefer_set_page_size"],
    )
    def test_convert_css_or_not_size(
        self,
        client: GotenbergClient,
        webserver_docker_internal_url: str,
        httpx_mock: HTTPXMock,
        method: str,
    ):
        httpx_mock.add_response(method="POST")

        with client.chromium.url_to_pdf() as route:
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
        client: GotenbergClient,
        webserver_docker_internal_url: str,
        httpx_mock: HTTPXMock,
        method: str,
    ):
        httpx_mock.add_response(method="POST")

        with client.chromium.url_to_pdf() as route:
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
        client: GotenbergClient,
        webserver_docker_internal_url: str,
        httpx_mock: HTTPXMock,
        method: str,
    ):
        httpx_mock.add_response(method="POST")

        with client.chromium.url_to_pdf() as route:
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
        client: GotenbergClient,
        webserver_docker_internal_url: str,
        httpx_mock: HTTPXMock,
        method: str,
    ):
        httpx_mock.add_response(method="POST")

        with client.chromium.url_to_pdf() as route:
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
        client: GotenbergClient,
        webserver_docker_internal_url: str,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")

        with client.chromium.url_to_pdf() as route:
            _ = route.url(webserver_docker_internal_url).scale(1.5).run()

        verify_stream_contains(
            httpx_mock.get_request(),
            "scale",
            "1.5",
        )

    def test_convert_page_ranges(
        self,
        client: GotenbergClient,
        webserver_docker_internal_url: str,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")

        with client.chromium.url_to_pdf() as route:
            _ = route.url(webserver_docker_internal_url).page_ranges("1-5").run()

        verify_stream_contains(
            httpx_mock.get_request(),
            "nativePageRanges",
            "1-5",
        )

    def test_convert_url_render_wait(
        self,
        client: GotenbergClient,
        webserver_docker_internal_url: str,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")

        with client.chromium.url_to_pdf() as route:
            _ = route.url(webserver_docker_internal_url).render_wait(500).run()

        verify_stream_contains(
            httpx_mock.get_request(),
            "waitDelay",
            "500",
        )

    def test_convert_url_render_expression(
        self,
        client: GotenbergClient,
        webserver_docker_internal_url: str,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")

        with client.chromium.url_to_pdf() as route:
            _ = route.url(webserver_docker_internal_url).render_expr("wait while false;").run()

        verify_stream_contains(
            httpx_mock.get_request(),
            "waitForExpression",
            "wait while false;",
        )

    @pytest.mark.filterwarnings("ignore::DeprecationWarning")
    def test_convert_url_user_agent(
        self,
        client: GotenbergClient,
        webserver_docker_internal_url: str,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")

        with client.chromium.url_to_pdf() as route:
            _ = route.url(webserver_docker_internal_url).user_agent("Firefox").run()

        verify_stream_contains(
            httpx_mock.get_request(),
            "userAgent",
            "Firefox",
        )

    def test_convert_url_headers(
        self,
        client: GotenbergClient,
        webserver_docker_internal_url: str,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")

        headers = {"X-Auth-Token": "Secure"}

        with client.chromium.url_to_pdf() as route:
            _ = route.url(webserver_docker_internal_url).headers(headers).run()
        verify_stream_contains(
            httpx_mock.get_request(),
            "extraHttpHeaders",
            json.dumps(headers),
        )
