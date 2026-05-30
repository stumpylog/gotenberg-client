# SPDX-FileCopyrightText: 2025-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0

from pathlib import Path

from pytest_httpx import HTTPXMock

from gotenberg_client import AsyncGotenbergClient
from gotenberg_client import GotenbergClient
from gotenberg_client.options import DownloadFromUrl
from gotenberg_client.options import RotateAngle
from gotenberg_client.options import WatermarkStampOptions
from gotenberg_client.options import WatermarkStampSource
from tests.utils import verify_stream_contains


class TestWatermarkMixin:
    def test_watermark_text_source(
        self,
        mock_sync_client: GotenbergClient,
        webserver_docker_internal_url: str,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")
        with mock_sync_client.chromium.url_to_pdf() as route:
            route.url(webserver_docker_internal_url).watermark_source(WatermarkStampSource.Text).run()
        verify_stream_contains(httpx_mock.get_request(), "watermarkSource", "text")

    def test_watermark_expression(
        self,
        mock_sync_client: GotenbergClient,
        webserver_docker_internal_url: str,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")
        with mock_sync_client.chromium.url_to_pdf() as route:
            route.url(webserver_docker_internal_url).watermark_expression("DRAFT").run()
        verify_stream_contains(httpx_mock.get_request(), "watermarkExpression", "DRAFT")

    def test_watermark_pages(
        self,
        mock_sync_client: GotenbergClient,
        webserver_docker_internal_url: str,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")
        with mock_sync_client.chromium.url_to_pdf() as route:
            route.url(webserver_docker_internal_url).watermark_pages("1-3").run()
        verify_stream_contains(httpx_mock.get_request(), "watermarkPages", "1-3")

    def test_watermark_options(
        self,
        mock_sync_client: GotenbergClient,
        webserver_docker_internal_url: str,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")
        with mock_sync_client.chromium.url_to_pdf() as route:
            route.url(webserver_docker_internal_url).watermark_options(WatermarkStampOptions(font="Arial")).run()
        verify_stream_contains(httpx_mock.get_request(), "watermarkOptions", "Arial")

    def test_watermark_options_points(
        self,
        mock_sync_client: GotenbergClient,
        webserver_docker_internal_url: str,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")
        with mock_sync_client.chromium.url_to_pdf() as route:
            route.url(webserver_docker_internal_url).watermark_options(WatermarkStampOptions(points=14)).run()
        verify_stream_contains(httpx_mock.get_request(), "watermarkOptions", "14")

    def test_watermark_options_rotation(
        self,
        mock_sync_client: GotenbergClient,
        webserver_docker_internal_url: str,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")
        with mock_sync_client.chromium.url_to_pdf() as route:
            route.url(webserver_docker_internal_url).watermark_options(WatermarkStampOptions(rotation=45)).run()
        verify_stream_contains(httpx_mock.get_request(), "watermarkOptions", "45")

    def test_watermark_file(
        self,
        mock_sync_client: GotenbergClient,
        webserver_docker_internal_url: str,
        httpx_mock: HTTPXMock,
        sample_directory: Path,
    ):
        httpx_mock.add_response(method="POST")
        with mock_sync_client.chromium.url_to_pdf() as route:
            route.url(webserver_docker_internal_url).watermark_file(sample_directory / "sample1.pdf").run()
        request = httpx_mock.get_request()
        boundary = request.headers["Content-Type"].split("boundary=")[1]
        parts = request.content.split(f"--{boundary}".encode())
        assert any(b'name="watermark"' in part for part in parts)


class TestStampMixin:
    def test_stamp_text_source(
        self,
        mock_sync_client: GotenbergClient,
        webserver_docker_internal_url: str,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")
        with mock_sync_client.chromium.url_to_pdf() as route:
            route.url(webserver_docker_internal_url).stamp_source(WatermarkStampSource.Text).run()
        verify_stream_contains(httpx_mock.get_request(), "stampSource", "text")

    def test_stamp_expression(
        self,
        mock_sync_client: GotenbergClient,
        webserver_docker_internal_url: str,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")
        with mock_sync_client.chromium.url_to_pdf() as route:
            route.url(webserver_docker_internal_url).stamp_expression("CONFIDENTIAL").run()
        verify_stream_contains(httpx_mock.get_request(), "stampExpression", "CONFIDENTIAL")

    def test_stamp_pages(
        self,
        mock_sync_client: GotenbergClient,
        webserver_docker_internal_url: str,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")
        with mock_sync_client.chromium.url_to_pdf() as route:
            route.url(webserver_docker_internal_url).stamp_pages("2-4").run()
        verify_stream_contains(httpx_mock.get_request(), "stampPages", "2-4")

    def test_stamp_options(
        self,
        mock_sync_client: GotenbergClient,
        webserver_docker_internal_url: str,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")
        with mock_sync_client.chromium.url_to_pdf() as route:
            route.url(webserver_docker_internal_url).stamp_options(WatermarkStampOptions(color="#FF0000")).run()
        verify_stream_contains(httpx_mock.get_request(), "stampOptions", "#FF0000")

    def test_stamp_options_opacity(
        self,
        mock_sync_client: GotenbergClient,
        webserver_docker_internal_url: str,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")
        with mock_sync_client.chromium.url_to_pdf() as route:
            route.url(webserver_docker_internal_url).stamp_options(WatermarkStampOptions(opacity=0.5)).run()
        verify_stream_contains(httpx_mock.get_request(), "stampOptions", "0.5")

    def test_stamp_options_scale(
        self,
        mock_sync_client: GotenbergClient,
        webserver_docker_internal_url: str,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")
        with mock_sync_client.chromium.url_to_pdf() as route:
            route.url(webserver_docker_internal_url).stamp_options(WatermarkStampOptions(scale=0.8)).run()
        verify_stream_contains(httpx_mock.get_request(), "stampOptions", "0.8")

    def test_stamp_file(
        self,
        mock_sync_client: GotenbergClient,
        webserver_docker_internal_url: str,
        httpx_mock: HTTPXMock,
        sample_directory: Path,
    ):
        httpx_mock.add_response(method="POST")
        with mock_sync_client.chromium.url_to_pdf() as route:
            route.url(webserver_docker_internal_url).stamp_file(sample_directory / "sample1.pdf").run()
        request = httpx_mock.get_request()
        boundary = request.headers["Content-Type"].split("boundary=")[1]
        parts = request.content.split(f"--{boundary}".encode())
        assert any(b'name="stamp"' in part for part in parts)


class TestRotateMixin:
    def test_rotate_angle(
        self,
        mock_sync_client: GotenbergClient,
        webserver_docker_internal_url: str,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")
        with mock_sync_client.chromium.url_to_pdf() as route:
            route.url(webserver_docker_internal_url).rotate(RotateAngle.Clockwise90).run()
        verify_stream_contains(httpx_mock.get_request(), "rotateAngle", "90")

    def test_rotate_pages(
        self,
        mock_sync_client: GotenbergClient,
        webserver_docker_internal_url: str,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")
        with mock_sync_client.chromium.url_to_pdf() as route:
            route.url(webserver_docker_internal_url).rotate(RotateAngle.Clockwise180, pages="2-4").run()
        verify_stream_contains(httpx_mock.get_request(), "rotateAngle", "180")
        verify_stream_contains(httpx_mock.get_request(), "rotatePages", "2-4")


class TestEncryptMixin:
    def test_user_password(
        self,
        mock_sync_client: GotenbergClient,
        webserver_docker_internal_url: str,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")
        with mock_sync_client.chromium.url_to_pdf() as route:
            route.url(webserver_docker_internal_url).user_password("secret").run()
        verify_stream_contains(httpx_mock.get_request(), "userPassword", "secret")

    def test_owner_password(
        self,
        mock_sync_client: GotenbergClient,
        webserver_docker_internal_url: str,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")
        with mock_sync_client.chromium.url_to_pdf() as route:
            route.url(webserver_docker_internal_url).owner_password("admin").run()
        verify_stream_contains(httpx_mock.get_request(), "ownerPassword", "admin")


class TestEmbedsMixin:
    def test_single_embed(
        self,
        mock_sync_client: GotenbergClient,
        webserver_docker_internal_url: str,
        httpx_mock: HTTPXMock,
        sample_directory: Path,
    ):
        httpx_mock.add_response(method="POST")
        with mock_sync_client.chromium.url_to_pdf() as route:
            route.url(webserver_docker_internal_url).embed(sample_directory / "sample1.pdf").run()
        # Verify a part with name="embeds" exists in the multipart request
        request = httpx_mock.get_request()
        boundary = request.headers["Content-Type"].split("boundary=")[1]
        parts = request.content.split(f"--{boundary}".encode())
        assert any(b'name="embeds"' in part for part in parts), "No embeds field found in request"

    def test_multiple_embeds(
        self,
        mock_sync_client: GotenbergClient,
        webserver_docker_internal_url: str,
        httpx_mock: HTTPXMock,
        sample_directory: Path,
    ):
        httpx_mock.add_response(method="POST")
        with mock_sync_client.chromium.url_to_pdf() as route:
            route.url(webserver_docker_internal_url).embed_files(
                [
                    sample_directory / "sample1.pdf",
                    sample_directory / "sample1.pdf",
                ],
            ).run()
        request = httpx_mock.get_request()
        boundary = request.headers["Content-Type"].split("boundary=")[1]
        parts = request.content.split(f"--{boundary}".encode())
        embeds_parts = [p for p in parts if b'name="embeds"' in p]
        assert len(embeds_parts) == 2, f"Expected 2 embeds parts, got {len(embeds_parts)}"


class TestDownloadFromMixin:
    def test_download_from(
        self,
        mock_sync_client: GotenbergClient,
        webserver_docker_internal_url: str,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")

        with mock_sync_client.chromium.url_to_pdf() as route:
            route.url(webserver_docker_internal_url).download_from(
                [
                    DownloadFromUrl(url="http://example.com/file.pdf"),
                ],
            ).run()
        verify_stream_contains(httpx_mock.get_request(), "downloadFrom", "http://example.com/file.pdf")

    def test_download_from_extra_http_headers(
        self,
        mock_sync_client: GotenbergClient,
        webserver_docker_internal_url: str,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")
        with mock_sync_client.chromium.url_to_pdf() as route:
            route.url(webserver_docker_internal_url).download_from(
                [
                    DownloadFromUrl(
                        url="http://example.com/file.pdf",
                        extra_http_headers={"Authorization": "Bearer token"},
                    ),
                ],
            ).run()
        verify_stream_contains(httpx_mock.get_request(), "downloadFrom", "extraHttpHeaders")

    def test_download_from_field(
        self,
        mock_sync_client: GotenbergClient,
        webserver_docker_internal_url: str,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")
        with mock_sync_client.chromium.url_to_pdf() as route:
            route.url(webserver_docker_internal_url).download_from(
                [
                    DownloadFromUrl(url="http://example.com/file.pdf", field="watermark"),
                ],
            ).run()
        verify_stream_contains(httpx_mock.get_request(), "downloadFrom", "watermark")


class TestResetFormFieldsMixin:
    def test_reset_form_fields_on_pdf_start_true_sync(
        self,
        mock_sync_client: GotenbergClient,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")
        with mock_sync_client.chromium.url_to_pdf() as route:
            route.url("http://example.com").reset_form_fields_on_pdf_start(reset=True).run()
        verify_stream_contains(httpx_mock.get_request(), "resetFormFieldsOnPdfStart", "true")

    def test_reset_form_fields_on_pdf_start_false_sync(
        self,
        mock_sync_client: GotenbergClient,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")
        with mock_sync_client.chromium.url_to_pdf() as route:
            route.url("http://example.com").reset_form_fields_on_pdf_start(reset=False).run()
        verify_stream_contains(httpx_mock.get_request(), "resetFormFieldsOnPdfStart", "false")

    def test_reset_form_fields_on_pdf_end_true_sync(
        self,
        mock_sync_client: GotenbergClient,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")
        with mock_sync_client.chromium.url_to_pdf() as route:
            route.url("http://example.com").reset_form_fields_on_pdf_end(reset=True).run()
        verify_stream_contains(httpx_mock.get_request(), "resetFormFieldsOnPdfEnd", "true")

    def test_reset_form_fields_on_pdf_end_false_sync(
        self,
        mock_sync_client: GotenbergClient,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")
        with mock_sync_client.chromium.url_to_pdf() as route:
            route.url("http://example.com").reset_form_fields_on_pdf_end(reset=False).run()
        verify_stream_contains(httpx_mock.get_request(), "resetFormFieldsOnPdfEnd", "false")

    async def test_reset_form_fields_on_pdf_start_true_async(
        self,
        mock_async_client: AsyncGotenbergClient,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")
        async with mock_async_client.chromium.url_to_pdf() as route:
            await route.url("http://example.com").reset_form_fields_on_pdf_start(reset=True).run()
        verify_stream_contains(httpx_mock.get_request(), "resetFormFieldsOnPdfStart", "true")

    async def test_reset_form_fields_on_pdf_start_false_async(
        self,
        mock_async_client: AsyncGotenbergClient,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")
        async with mock_async_client.chromium.url_to_pdf() as route:
            await route.url("http://example.com").reset_form_fields_on_pdf_start(reset=False).run()
        verify_stream_contains(httpx_mock.get_request(), "resetFormFieldsOnPdfStart", "false")

    async def test_reset_form_fields_on_pdf_end_true_async(
        self,
        mock_async_client: AsyncGotenbergClient,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")
        async with mock_async_client.chromium.url_to_pdf() as route:
            await route.url("http://example.com").reset_form_fields_on_pdf_end(reset=True).run()
        verify_stream_contains(httpx_mock.get_request(), "resetFormFieldsOnPdfEnd", "true")

    async def test_reset_form_fields_on_pdf_end_false_async(
        self,
        mock_async_client: AsyncGotenbergClient,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")
        async with mock_async_client.chromium.url_to_pdf() as route:
            await route.url("http://example.com").reset_form_fields_on_pdf_end(reset=False).run()
        verify_stream_contains(httpx_mock.get_request(), "resetFormFieldsOnPdfEnd", "false")
