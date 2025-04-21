# SPDX-FileCopyrightText: 2023-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
from datetime import timedelta
from pathlib import Path

import pikepdf
import pytest
from pytest_httpx import HTTPXMock

from gotenberg_client import GotenbergClient
from gotenberg_client._chromium.routes import AsyncHtmlToPdfRoute
from gotenberg_client._chromium.routes import SyncHtmlToPdfRoute
from gotenberg_client.constants import A4
from gotenberg_client.options import Measurement
from gotenberg_client.options import MeasurementUnitType
from gotenberg_client.options import PageMarginsType
from gotenberg_client.options import PageOrientation
from gotenberg_client.options import PdfAFormat
from tests.utils import verify_basic_response_values_pdf
from tests.utils import verify_stream_contains


class TestConvertChromiumHtml:
    def test_basic_convert_sync(self, sync_html_to_pdf_route: SyncHtmlToPdfRoute, basic_html_file: Path):
        verify_basic_response_values_pdf(
            sync_html_to_pdf_route.index(basic_html_file)
            .fail_on_resource_loading_failed(fail_on_resource_loading_failed=True)
            .run_with_retry(),
        )

    async def test_basic_convert_async(self, async_html_to_pdf_route: AsyncHtmlToPdfRoute, basic_html_file: Path):
        verify_basic_response_values_pdf(await async_html_to_pdf_route.index(basic_html_file).run_with_retry())

    def test_convert_with_header_footer_sync(
        self,
        sync_html_to_pdf_route: SyncHtmlToPdfRoute,
        basic_html_file: Path,
        header_html_file: Path,
        footer_html_file: Path,
    ):
        verify_basic_response_values_pdf(
            sync_html_to_pdf_route.index(basic_html_file)
            .header(header_html_file)
            .footer(footer_html_file)
            .run_with_retry(),
        )

    async def test_convert_with_header_footer_async(
        self,
        async_html_to_pdf_route: AsyncHtmlToPdfRoute,
        basic_html_file: Path,
        header_html_file: Path,
        footer_html_file: Path,
    ):
        verify_basic_response_values_pdf(
            await async_html_to_pdf_route.index(basic_html_file)
            .header(header_html_file)
            .footer(footer_html_file)
            .run_with_retry(),
        )

    def test_convert_additional_files_sync(
        self,
        sync_html_to_pdf_route: SyncHtmlToPdfRoute,
        complex_html_file: Path,
        img_gif_file: Path,
        font_file: Path,
        css_style_file: Path,
    ):
        verify_basic_response_values_pdf(
            sync_html_to_pdf_route.index(complex_html_file)
            .resource(img_gif_file)
            .resource(font_file)
            .resource(css_style_file)
            .run_with_retry(),
        )

    async def test_convert_additional_files_async(
        self,
        async_html_to_pdf_route: AsyncHtmlToPdfRoute,
        complex_html_file: Path,
        img_gif_file: Path,
        font_file: Path,
        css_style_file: Path,
    ):
        verify_basic_response_values_pdf(
            await async_html_to_pdf_route.index(complex_html_file)
            .resource(img_gif_file)
            .resource(font_file)
            .resource(css_style_file)
            .run_with_retry(),
        )

    async def test_convert_split_mode_async(
        self,
        async_html_to_pdf_route: AsyncHtmlToPdfRoute,
        basic_html_file: Path,
    ):
        await (
            async_html_to_pdf_route.index(basic_html_file)
            .split_mode("pages")
            .split_span("1,2")
            .split_unify(split_unify=False)
            .run_with_retry()
        )

    def test_convert_html_from_string_sync(self, sync_html_to_pdf_route: SyncHtmlToPdfRoute, basic_html_file: Path):
        html_str = basic_html_file.read_text()

        verify_basic_response_values_pdf(sync_html_to_pdf_route.string_index(html_str).run_with_retry())

    async def test_convert_html_from_string_async(
        self,
        async_html_to_pdf_route: AsyncHtmlToPdfRoute,
        basic_html_file: Path,
    ):
        html_str = basic_html_file.read_text()

        verify_basic_response_values_pdf(await async_html_to_pdf_route.string_index(html_str).run_with_retry())

    @pytest.mark.parametrize(
        ("gt_format", "pike_format"),
        [(PdfAFormat.A2b, "2B"), (PdfAFormat.A3b, "3B")],
    )
    def test_convert_pdfa_format_sync(
        self,
        sync_html_to_pdf_route: SyncHtmlToPdfRoute,
        basic_html_file: Path,
        tmp_path: Path,
        gt_format: PdfAFormat,
        pike_format: str,
    ):
        response = sync_html_to_pdf_route.index(basic_html_file).pdf_format(gt_format).run_with_retry()

        verify_basic_response_values_pdf(response)

        output = tmp_path / "test_convert_pdfa_format_sync.pdf"
        response.to_file(output)
        with pikepdf.open(output) as pdf:
            meta = pdf.open_metadata()
            assert meta.pdfa_status == pike_format

    @pytest.mark.parametrize(
        ("gt_format", "pike_format"),
        [(PdfAFormat.A2b, "2B"), (PdfAFormat.A3b, "3B")],
    )
    async def test_convert_pdfa_format_async(
        self,
        async_html_to_pdf_route: AsyncHtmlToPdfRoute,
        basic_html_file: Path,
        tmp_path: Path,
        gt_format: PdfAFormat,
        pike_format: str,
    ):
        response = await async_html_to_pdf_route.index(basic_html_file).pdf_format(gt_format).run_with_retry()

        verify_basic_response_values_pdf(response)

        output = tmp_path / "test_convert_pdfa_format_async.pdf"
        response.to_file(output)
        with pikepdf.open(output) as pdf:
            meta = pdf.open_metadata()
            assert meta.pdfa_status == pike_format

    def test_convert_additional_file_string_with_name_sync(
        self,
        sync_html_to_pdf_route: SyncHtmlToPdfRoute,
        complex_html_file: Path,
        img_gif_file: Path,
        font_file: Path,
        css_style_file: Path,
    ):
        response = (
            sync_html_to_pdf_route.index(complex_html_file)
            .resources([img_gif_file, font_file])
            .string_resource(css_style_file.read_text(), name="style.css", mime_type="text/css")
            .run_with_retry()
        )

        verify_basic_response_values_pdf(response)

    async def test_convert_additional_file_string_with_name_async(
        self,
        async_html_to_pdf_route: AsyncHtmlToPdfRoute,
        complex_html_file: Path,
        img_gif_file: Path,
        font_file: Path,
        css_style_file: Path,
    ):
        response = await (
            async_html_to_pdf_route.index(complex_html_file)
            .resources([img_gif_file, font_file])
            .string_resource(css_style_file.read_text(), name="style.css", mime_type="text/css")
            .run_with_retry()
        )

        verify_basic_response_values_pdf(response)


class TestConvertChromiumHtmlMocked:
    def test_convert_page_size(self, sync_client: GotenbergClient, sample_directory: Path, httpx_mock: HTTPXMock):
        httpx_mock.add_response(method="POST")
        test_file = sample_directory / "basic.html"

        with sync_client.chromium.html_to_pdf() as route:
            _ = route.index(test_file).size(A4).run()

        request = httpx_mock.get_request()
        verify_stream_contains(request, "paperWidth", "8.27")
        verify_stream_contains(request, "paperHeight", "11.7")

    def test_convert_margin(self, sync_client: GotenbergClient, sample_directory: Path, httpx_mock: HTTPXMock):
        httpx_mock.add_response(method="POST")
        test_file = sample_directory / "basic.html"

        with sync_client.chromium.html_to_pdf() as route:
            _ = (
                route.index(test_file)
                .margins(
                    PageMarginsType(
                        Measurement(1, MeasurementUnitType.Centimeters),
                        Measurement(2, MeasurementUnitType.Percent),
                        Measurement(3, MeasurementUnitType.Millimeters),
                        Measurement(4),
                    ),
                )
                .run()
            )

        request = httpx_mock.get_request()
        verify_stream_contains(request, "marginTop", "1cm")
        verify_stream_contains(request, "marginBottom", "2pc")
        verify_stream_contains(request, "marginLeft", "3mm")
        verify_stream_contains(request, "marginRight", "4")

    def test_convert_render_control(self, sync_client: GotenbergClient, sample_directory: Path, httpx_mock: HTTPXMock):
        httpx_mock.add_response(method="POST")
        test_file = sample_directory / "basic.html"

        with sync_client.chromium.html_to_pdf() as route:
            _ = route.index(test_file).render_wait(timedelta(seconds=500.0)).run()

        verify_stream_contains(httpx_mock.get_request(), "waitDelay", "500.0")

    @pytest.mark.parametrize(
        ("orientation"),
        [PageOrientation.Landscape, PageOrientation.Portrait],
    )
    def test_convert_orientation(
        self,
        sync_client: GotenbergClient,
        sample_directory: Path,
        httpx_mock: HTTPXMock,
        orientation: PageOrientation,
    ):
        httpx_mock.add_response(method="POST")
        test_file = sample_directory / "basic.html"

        with sync_client.chromium.html_to_pdf() as route:
            _ = route.index(test_file).orient(orientation).run()

        verify_stream_contains(
            httpx_mock.get_request(),
            "landscape",
            "true" if orientation == PageOrientation.Landscape else "false",
        )
