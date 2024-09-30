# SPDX-FileCopyrightText: 2023-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
import shutil
import uuid
from json import dumps
from json import loads
from pathlib import Path

import pytest
from httpx import HTTPStatusError
from httpx import Request
from httpx import codes
from pytest_httpx import HTTPXMock

from gotenberg_client import CannotExtractHereError
from gotenberg_client import GotenbergClient
from gotenberg_client import MaxRetriesExceededError
from gotenberg_client import ZipFileResponse


class TestMiscFunctionality:
    def test_trace_id_header(
        self,
        client: GotenbergClient,
        sample_directory: Path,
    ):
        trace_id = str(uuid.uuid4())
        with client.merge.merge() as route:
            resp = (
                route.merge([sample_directory / "z_first_merge.pdf", sample_directory / "a_merge_second.pdf"])
                .trace(
                    trace_id,
                )
                .run_with_retry()
            )

        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "application/pdf"
        assert "Gotenberg-Trace" in resp.headers
        assert resp.headers["Gotenberg-Trace"] == trace_id

    def test_output_filename(
        self,
        client: GotenbergClient,
        sample_directory: Path,
    ):
        filename = "my-cool-file"
        with client.merge.merge() as route:
            resp = (
                route.merge([sample_directory / "z_first_merge.pdf", sample_directory / "a_merge_second.pdf"])
                .output_name(
                    filename,
                )
                .run_with_retry()
            )

        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "application/pdf"
        assert "Content-Disposition" in resp.headers
        assert f"{filename}.pdf" in resp.headers["Content-Disposition"]

    def test_libre_office_convert_cyrillic(self, client: GotenbergClient, odt_sample_file: Path, tmp_path: Path):
        """
        Gotenberg versions before 8.0.0 could not internally handle filenames with
        non-ASCII characters.  This replicates such a thing against 1 endpoint to
        verify the workaround inside this library
        """
        copy = shutil.copy(
            odt_sample_file,
            tmp_path / "Карточка партнера Тауберг Альфа.odt",  # noqa: RUF001
        )

        with client.libre_office.to_pdf() as route:
            resp = route.convert(copy).run_with_retry()

        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "application/pdf"

    def test_extract_to_not_existing(self) -> None:
        resp = ZipFileResponse(200, {}, b"")

        output = Path("does-not-exist")

        assert not output.exists()

        with pytest.raises(CannotExtractHereError):
            resp.extract_to(output)


class TestServerErrorRetry:
    def test_server_error_retry(self, client: GotenbergClient, basic_html_file: Path, httpx_mock: HTTPXMock):
        # Response 1
        httpx_mock.add_response(method="POST", status_code=codes.INTERNAL_SERVER_ERROR)
        # Response 2
        httpx_mock.add_response(method="POST", status_code=codes.SERVICE_UNAVAILABLE)
        # Response 3
        httpx_mock.add_response(method="POST", status_code=codes.GATEWAY_TIMEOUT)
        # Response 4
        httpx_mock.add_response(method="POST", status_code=codes.BAD_GATEWAY)
        # Response 5
        httpx_mock.add_response(method="POST", status_code=codes.SERVICE_UNAVAILABLE)

        with client.chromium.html_to_pdf() as route:
            with pytest.raises(MaxRetriesExceededError) as exc_info:
                _ = route.index(basic_html_file).run_with_retry(initial_retry_wait=0.1, retry_scale=0.1)
            assert exc_info.value.response.status_code == codes.SERVICE_UNAVAILABLE

    def test_not_a_server_error(self, client: GotenbergClient, basic_html_file: Path, httpx_mock: HTTPXMock):
        # Response 1
        httpx_mock.add_response(method="POST", status_code=codes.NOT_FOUND)

        with client.chromium.html_to_pdf() as route:
            with pytest.raises(HTTPStatusError) as exc_info:
                _ = route.index(basic_html_file).run_with_retry(initial_retry_wait=0.1, retry_scale=0.1)
            assert exc_info.value.response.status_code == codes.NOT_FOUND


class TestWebhookHeaders:
    def test_webhook_basic_headers(self, client: GotenbergClient, basic_html_file: Path, httpx_mock: HTTPXMock):
        httpx_mock.add_response(method="POST", status_code=codes.OK)

        client.add_webhook_url("http://myapi:3000/on-success")
        client.add_error_webhook_url("http://myapi:3000/on-error")

        with client.chromium.html_to_pdf() as route:
            _ = route.index(basic_html_file).run_with_retry()

        requests = httpx_mock.get_requests()

        assert len(requests) == 1

        request: Request = requests[0]

        assert "Gotenberg-Webhook-Url" in request.headers
        assert request.headers["Gotenberg-Webhook-Url"] == "http://myapi:3000/on-success"
        assert "Gotenberg-Webhook-Error-Url" in request.headers
        assert request.headers["Gotenberg-Webhook-Error-Url"] == "http://myapi:3000/on-error"

    def test_webhook_http_methods(self, client: GotenbergClient, basic_html_file: Path, httpx_mock: HTTPXMock):
        httpx_mock.add_response(method="POST", status_code=codes.OK)

        client.add_webhook_url("http://myapi:3000/on-success")
        client.set_webhook_http_method("POST")
        client.add_error_webhook_url("http://myapi:3000/on-error")
        client.set_error_webhook_http_method("PATCH")

        with client.chromium.html_to_pdf() as route:
            _ = route.index(basic_html_file).run_with_retry()

        requests = httpx_mock.get_requests()

        assert len(requests) == 1

        request: Request = requests[0]

        assert "Gotenberg-Webhook-Method" in request.headers
        assert request.headers["Gotenberg-Webhook-Method"] == "POST"
        assert "Gotenberg-Webhook-Error-Method" in request.headers
        assert request.headers["Gotenberg-Webhook-Error-Method"] == "PATCH"

    def test_webhook_extra_headers(self, client: GotenbergClient, basic_html_file: Path, httpx_mock: HTTPXMock):
        httpx_mock.add_response(method="POST", status_code=codes.OK)

        headers = {"Token": "mytokenvalue"}
        headers_str = dumps(headers)

        client.set_webhook_extra_headers(headers)

        with client.chromium.html_to_pdf() as route:
            _ = route.index(basic_html_file).run_with_retry()

        requests = httpx_mock.get_requests()

        assert len(requests) == 1

        request: Request = requests[0]

        assert "Gotenberg-Webhook-Extra-Http-Headers" in request.headers
        assert request.headers["Gotenberg-Webhook-Extra-Http-Headers"] == headers_str
        assert loads(request.headers["Gotenberg-Webhook-Extra-Http-Headers"]) == headers
