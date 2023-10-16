import tempfile
from pathlib import Path

import pikepdf
import pytest
from httpx import codes
from pytest_httpx import HTTPXMock

from gotenberg_client._client import GotenbergClient
from gotenberg_client._convert.chromium import Margin
from gotenberg_client.options import A4
from gotenberg_client.options import PageOrientation
from gotenberg_client.options import PdfAFormat
from tests.conftest import SAMPLE_DIR
from tests.conftest import SAVE_DIR
from tests.conftest import SAVE_OUTPUTS
from tests.utils import call_run_with_server_error_handling
from tests.utils import verify_stream_contains


class TestConvertChromiumHtmlRoute:
    def test_basic_convert(self, client: GotenbergClient):
        test_file = SAMPLE_DIR / "basic.html"

        with client.chromium.html_to_pdf() as route:
            resp = call_run_with_server_error_handling(route.index(test_file))

        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "application/pdf"
        if SAVE_OUTPUTS:
            (SAVE_DIR / "test_basic_convert.pdf").write_bytes(resp.content)

    def test_convert_with_header_footer(self, client: GotenbergClient):
        test_file = SAMPLE_DIR / "basic.html"
        header_file = SAMPLE_DIR / "header.html"
        footer_file = SAMPLE_DIR / "footer.html"

        with client.chromium.html_to_pdf() as route:
            resp = call_run_with_server_error_handling(route.index(test_file).header(header_file).footer(footer_file))

        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "application/pdf"

    def test_convert_additional_files(self, client: GotenbergClient):
        test_file = SAMPLE_DIR / "complex.html"
        img = SAMPLE_DIR / "img.gif"
        font = SAMPLE_DIR / "font.woff"
        style = SAMPLE_DIR / "style.css"

        with client.chromium.html_to_pdf() as route:
            resp = call_run_with_server_error_handling(
                route.index(test_file).resource(img).resource(font).resource(style),
            )

        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "application/pdf"

        if SAVE_OUTPUTS:
            (SAVE_DIR / "test_convert_additional_files.pdf").write_bytes(resp.content)

    @pytest.mark.parametrize(
        ("gt_format", "pike_format"),
        [(PdfAFormat.A1a, "1A"), (PdfAFormat.A2b, "2B"), (PdfAFormat.A3b, "3B")],
    )
    def test_convert_pdfa_1a_format(self, client: GotenbergClient, gt_format: PdfAFormat, pike_format: str):
        test_file = SAMPLE_DIR / "basic.html"

        with client.chromium.html_to_pdf() as route:
            resp = call_run_with_server_error_handling(route.index(test_file).pdf_format(gt_format))

        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "application/pdf"

        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "test_convert_pdfa_format.pdf"
            output.write_bytes(resp.content)
            with pikepdf.open(output) as pdf:
                meta = pdf.open_metadata()
                assert meta.pdfa_status == pike_format


class TestConvertChromiumHtmlRouteMocked:
    def test_convert_page_size(self, client: GotenbergClient, httpx_mock: HTTPXMock):
        httpx_mock.add_response(method="POST")
        test_file = SAMPLE_DIR / "basic.html"

        with client.chromium.html_to_pdf() as route:
            _ = route.index(test_file).size(A4).run()

        request = httpx_mock.get_request()
        verify_stream_contains("paperWidth", "8.5", request.stream)
        verify_stream_contains("paperHeight", "11", request.stream)

    def test_convert_margin(self, client: GotenbergClient, httpx_mock: HTTPXMock):
        httpx_mock.add_response(method="POST")
        test_file = SAMPLE_DIR / "basic.html"

        with client.chromium.html_to_pdf() as route:
            _ = route.index(test_file).margins(Margin(1, 2, 3, 4)).run()

        request = httpx_mock.get_request()
        verify_stream_contains("marginTop", "1", request.stream)
        verify_stream_contains("marginBottom", "2", request.stream)
        verify_stream_contains("marginLeft", "3", request.stream)
        verify_stream_contains("marginRight", "4", request.stream)

    def test_convert_render_control(self, client: GotenbergClient, httpx_mock: HTTPXMock):
        httpx_mock.add_response(method="POST")
        test_file = SAMPLE_DIR / "basic.html"

        with client.chromium.html_to_pdf() as route:
            _ = route.index(test_file).render_wait(500.0).run()

        request = httpx_mock.get_request()
        verify_stream_contains("waitDelay", "500.0", request.stream)

    @pytest.mark.parametrize(
        ("orientation"),
        [PageOrientation.Landscape, PageOrientation.Portrait],
    )
    def test_convert_orientation(
        self,
        client: GotenbergClient,
        httpx_mock: HTTPXMock,
        orientation: PageOrientation,
    ):
        httpx_mock.add_response(method="POST")
        test_file = SAMPLE_DIR / "basic.html"

        with client.chromium.html_to_pdf() as route:
            _ = route.index(test_file).orient(orientation).run()

        request = httpx_mock.get_request()
        verify_stream_contains(
            "landscape",
            "true" if orientation == PageOrientation.Landscape else "false",
            request.stream,
        )
