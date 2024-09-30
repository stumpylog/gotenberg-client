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
from tests.utils import verify_stream_contains


class TestConvertChromiumHtmlRoute:
    def test_basic_convert(self, client: GotenbergClient, basic_html_file: Path):
        with client.chromium.html_to_pdf() as route:
            resp = route.index(basic_html_file).run_with_retry()

        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "application/pdf"

    def test_convert_with_header_footer(
        self,
        client: GotenbergClient,
        basic_html_file: Path,
        header_html_file: Path,
        footer_html_file: Path,
    ):
        with client.chromium.html_to_pdf() as route:
            resp = route.index(basic_html_file).header(header_html_file).footer(footer_html_file).run_with_retry()

        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "application/pdf"

    def test_convert_additional_files(
        self,
        client: GotenbergClient,
        complex_html_file: Path,
        img_gif_file: Path,
        font_file: Path,
        css_style_file: Path,
    ):
        with client.chromium.html_to_pdf() as route:
            resp = (
                route.index(complex_html_file)
                .resource(img_gif_file)
                .resource(font_file)
                .resource(css_style_file)
                .run_with_retry()
            )

        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "application/pdf"

    @pytest.mark.parametrize(
        ("gt_format", "pike_format"),
        [(PdfAFormat.A2b, "2B"), (PdfAFormat.A3b, "3B")],
    )
    def test_convert_pdfa_format(
        self,
        client: GotenbergClient,
        basic_html_file: Path,
        tmp_path: Path,
        gt_format: PdfAFormat,
        pike_format: str,
    ):
        with client.chromium.html_to_pdf() as route:
            resp = route.index(basic_html_file).pdf_format(gt_format).run_with_retry()

        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "application/pdf"

        output = tmp_path / "test_convert_pdfa_format.pdf"
        resp.to_file(output)
        with pikepdf.open(output) as pdf:
            meta = pdf.open_metadata()
            assert meta.pdfa_status == pike_format


class TestConvertChromiumHtmlRouteMocked:
    def test_convert_page_size(self, client: GotenbergClient, sample_directory: Path, httpx_mock: HTTPXMock):
        httpx_mock.add_response(method="POST")
        test_file = sample_directory / "basic.html"

        with client.chromium.html_to_pdf() as route:
            _ = route.index(test_file).size(A4).run()

        request = httpx_mock.get_request()
        verify_stream_contains("paperWidth", "8.27", request.stream)
        verify_stream_contains("paperHeight", "11.7", request.stream)

    def test_convert_margin(self, client: GotenbergClient, sample_directory: Path, httpx_mock: HTTPXMock):
        httpx_mock.add_response(method="POST")
        test_file = sample_directory / "basic.html"

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

    def test_convert_render_control(self, client: GotenbergClient, sample_directory: Path, httpx_mock: HTTPXMock):
        httpx_mock.add_response(method="POST")
        test_file = sample_directory / "basic.html"

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
        sample_directory: Path,
        httpx_mock: HTTPXMock,
        orientation: PageOrientation,
    ):
        httpx_mock.add_response(method="POST")
        test_file = sample_directory / "basic.html"

        with client.chromium.html_to_pdf() as route:
            _ = route.index(test_file).orient(orientation).run()

        request = httpx_mock.get_request()
        verify_stream_contains(
            "landscape",
            "true" if orientation == PageOrientation.Landscape else "false",
            request.stream,
        )
