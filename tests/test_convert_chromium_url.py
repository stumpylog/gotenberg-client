import json

import pytest
from httpx import codes
from pytest_httpx import HTTPXMock

from gotenberg_client._client import GotenbergClient
from gotenberg_client._convert.chromium import EmulatedMediaType
from tests.utils import call_run_with_server_error_handling
from tests.utils import verify_stream_contains


class TestConvertChromiumUrlRoute:
    def test_basic_convert(self, client: GotenbergClient):
        with client.chromium.url_to_pdf() as route:
            resp = call_run_with_server_error_handling(
                route.url("https://en.wikipedia.org/wiki/William_Edward_Sanders"),
            )

        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "application/pdf"


class TestConvertChromiumUrlMocked:
    @pytest.mark.parametrize(
        ("emulation"),
        [EmulatedMediaType.Screen, EmulatedMediaType.Print],
    )
    def test_convert_orientation(
        self,
        client: GotenbergClient,
        httpx_mock: HTTPXMock,
        emulation: EmulatedMediaType,
    ):
        httpx_mock.add_response(method="POST")

        with client.chromium.url_to_pdf() as route:
            _ = route.url("https://en.wikipedia.org/wiki/William_Edward_Sanders").media_type(emulation).run()

        request = httpx_mock.get_request()
        verify_stream_contains(
            "emulatedMediaType",
            "screen" if emulation == EmulatedMediaType.Screen else "print",
            request.stream,
        )

    @pytest.mark.parametrize(
        ("method"),
        ["prefer_css_page_size", "prefer_set_page_size"],
    )
    def test_convert_css_or_not_size(
        self,
        client: GotenbergClient,
        httpx_mock: HTTPXMock,
        method: str,
    ):
        httpx_mock.add_response(method="POST")

        with client.chromium.url_to_pdf() as route:
            route.url("https://en.wikipedia.org/wiki/William_Edward_Sanders")
            getattr(route, method)()
            _ = route.run()

        request = httpx_mock.get_request()
        verify_stream_contains(
            "preferCssPageSize",
            "true" if method == "prefer_css_page_size" else "false",
            request.stream,
        )

    @pytest.mark.parametrize(
        ("method"),
        ["background_graphics", "no_background_graphics"],
    )
    def test_convert_background_graphics_or_not(
        self,
        client: GotenbergClient,
        httpx_mock: HTTPXMock,
        method: str,
    ):
        httpx_mock.add_response(method="POST")

        with client.chromium.url_to_pdf() as route:
            route.url("https://en.wikipedia.org/wiki/William_Edward_Sanders")
            getattr(route, method)()
            _ = route.run()

        request = httpx_mock.get_request()
        verify_stream_contains(
            "printBackground",
            "true" if method == "background_graphics" else "false",
            request.stream,
        )

    @pytest.mark.parametrize(
        ("method"),
        ["hide_background", "show_background"],
    )
    def test_convert_hide_background_or_not(
        self,
        client: GotenbergClient,
        httpx_mock: HTTPXMock,
        method: str,
    ):
        httpx_mock.add_response(method="POST")

        with client.chromium.url_to_pdf() as route:
            route.url("https://en.wikipedia.org/wiki/William_Edward_Sanders")
            getattr(route, method)()
            _ = route.run()

        request = httpx_mock.get_request()
        verify_stream_contains(
            "omitBackground",
            "true" if method == "hide_background" else "false",
            request.stream,
        )

    @pytest.mark.parametrize(
        ("method"),
        ["fail_on_exceptions", "dont_fail_on_exceptions"],
    )
    def test_convert_fail_exceptions(
        self,
        client: GotenbergClient,
        httpx_mock: HTTPXMock,
        method: str,
    ):
        httpx_mock.add_response(method="POST")

        with client.chromium.url_to_pdf() as route:
            route.url("https://en.wikipedia.org/wiki/William_Edward_Sanders")
            getattr(route, method)()
            _ = route.run()

        request = httpx_mock.get_request()
        verify_stream_contains(
            "failOnConsoleExceptions",
            "true" if method == "fail_on_exceptions" else "false",
            request.stream,
        )

    def test_convert_scale(
        self,
        client: GotenbergClient,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")

        with client.chromium.url_to_pdf() as route:
            _ = route.url("https://en.wikipedia.org/wiki/William_Edward_Sanders").scale(1.5).run()

        request = httpx_mock.get_request()
        verify_stream_contains(
            "scale",
            "1.5",
            request.stream,
        )

    def test_convert_page_ranges(
        self,
        client: GotenbergClient,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")

        with client.chromium.url_to_pdf() as route:
            _ = route.url("https://en.wikipedia.org/wiki/William_Edward_Sanders").page_ranges("1-5").run()

        request = httpx_mock.get_request()
        verify_stream_contains(
            "nativePageRanges",
            "1-5",
            request.stream,
        )

    def test_convert_url_render_wait(
        self,
        client: GotenbergClient,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")

        with client.chromium.url_to_pdf() as route:
            _ = route.url("https://en.wikipedia.org/wiki/William_Edward_Sanders").render_wait(500).run()

        request = httpx_mock.get_request()
        verify_stream_contains(
            "waitDelay",
            "500",
            request.stream,
        )

    def test_convert_url_render_expression(
        self,
        client: GotenbergClient,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")

        with client.chromium.url_to_pdf() as route:
            _ = route.url("https://en.wikipedia.org/wiki/William_Edward_Sanders").render_expr("wait while false;").run()

        request = httpx_mock.get_request()
        verify_stream_contains(
            "waitForExpression",
            "wait while false;",
            request.stream,
        )

    def test_convert_url_user_agent(
        self,
        client: GotenbergClient,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")

        with client.chromium.url_to_pdf() as route:
            _ = route.url("https://en.wikipedia.org/wiki/William_Edward_Sanders").user_agent("Firefox").run()

        request = httpx_mock.get_request()
        verify_stream_contains(
            "userAgent",
            "Firefox",
            request.stream,
        )

    def test_convert_url_headers(
        self,
        client: GotenbergClient,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")

        headers = {"X-Auth-Token": "Secure"}

        with client.chromium.url_to_pdf() as route:
            _ = route.url("https://en.wikipedia.org/wiki/William_Edward_Sanders").headers(headers).run()

        request = httpx_mock.get_request()
        verify_stream_contains(
            "extraHttpHeaders",
            json.dumps(headers),
            request.stream,
        )
