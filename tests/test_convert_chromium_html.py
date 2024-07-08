# SPDX-FileCopyrightText: 2023-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
from pathlib import Path

import pikepdf
import pytest
from httpx import codes
from pytest_httpx import HTTPXMock

from gotenberg_client import GotenbergClient
from gotenberg_client.options import A4
from gotenberg_client.options import MarginType
from gotenberg_client.options import MarginUnitType
from gotenberg_client.options import PageMarginsType
from gotenberg_client.options import PageOrientation
from gotenberg_client.options import PdfAFormat
from tests.conftest import SAMPLE_DIR
from tests.conftest import SAVE_DIR
from tests.conftest import SAVE_OUTPUTS
from tests.utils import verify_stream_contains


class TestConvertChromiumHtmlRoute:
    def test_basic_convert(self, client: GotenbergClient):
        test_file = SAMPLE_DIR / "basic.html"

        with client.chromium.html_to_pdf() as route:
            resp = route.index(test_file).run_with_retry()

        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "application/pdf"
        if SAVE_OUTPUTS:
            resp.to_file(SAVE_DIR / "test_basic_convert.pdf")

    def test_convert_with_header_footer(self, client: GotenbergClient):
        test_file = SAMPLE_DIR / "basic.html"
        header_file = SAMPLE_DIR / "header.html"
        footer_file = SAMPLE_DIR / "footer.html"

        with client.chromium.html_to_pdf() as route:
            resp = route.index(test_file).header(header_file).footer(footer_file).run_with_retry()

        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "application/pdf"

    def test_convert_additional_files(self, client: GotenbergClient):
        test_file = SAMPLE_DIR / "complex.html"
        img = SAMPLE_DIR / "img.gif"
        font = SAMPLE_DIR / "font.woff"
        style = SAMPLE_DIR / "style.css"

        with client.chromium.html_to_pdf() as route:
            resp = route.index(test_file).resource(img).resource(font).resource(style).run_with_retry()

        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "application/pdf"

        if SAVE_OUTPUTS:
            resp.to_file(SAVE_DIR / "test_convert_additional_files.pdf")

    @pytest.mark.parametrize(
        ("gt_format", "pike_format"),
        [(PdfAFormat.A2b, "2B"), (PdfAFormat.A3b, "3B")],
    )
    def test_convert_pdfa_format(
        self,
        client: GotenbergClient,
        temporary_dir: Path,
        gt_format: PdfAFormat,
        pike_format: str,
    ):
        test_file = SAMPLE_DIR / "basic.html"

        with client.chromium.html_to_pdf() as route:
            resp = route.index(test_file).pdf_format(gt_format).run_with_retry()

        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "application/pdf"

        output = temporary_dir / "test_convert_pdfa_format.pdf"
        resp.to_file(output)
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
        verify_stream_contains("paperWidth", "8.27", request.stream)
        verify_stream_contains("paperHeight", "11.7", request.stream)

    def test_convert_margin(self, client: GotenbergClient, httpx_mock: HTTPXMock):
        httpx_mock.add_response(method="POST")
        test_file = SAMPLE_DIR / "basic.html"

        with client.chromium.html_to_pdf() as route:
            _ = (
                route.index(test_file)
                .margins(
                    PageMarginsType(
                        MarginType(1, MarginUnitType.Centimeters),
                        MarginType(2, MarginUnitType.Percent),
                        MarginType(3, MarginUnitType.Millimeters),
                        MarginType(4),
                    ),
                )
                .run()
            )

        request = httpx_mock.get_request()
        verify_stream_contains("marginTop", "1cm", request.stream)
        verify_stream_contains("marginBottom", "2pc", request.stream)
        verify_stream_contains("marginLeft", "3mm", request.stream)
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
