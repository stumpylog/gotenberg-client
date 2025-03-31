# SPDX-FileCopyrightText: 2023-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
from http import HTTPStatus
from pathlib import Path
from unittest.mock import patch

import pikepdf
import pytest

from gotenberg_client import GotenbergClient
from gotenberg_client import SingleFileResponse
from gotenberg_client import ZipFileResponse
from gotenberg_client._libreoffice.routes import AsyncOfficeDocumentToPdfRoute
from gotenberg_client._utils import guess_mime_type_stdlib
from gotenberg_client.options import PageOrientation
from gotenberg_client.options import PdfAFormat


class TestLibreOfficeConvert:
    def test_libre_office_convert_docx_format(self, sync_client: GotenbergClient, docx_sample_file: Path):
        with sync_client.libre_office.to_pdf() as route:
            resp = route.convert(docx_sample_file).run_with_retry()

        assert resp.status_code == HTTPStatus.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "application/pdf"

    def test_libre_office_convert_docx_format_for_coverage(
        self,
        sync_client: GotenbergClient,
        docx_sample_file: Path,
    ):
        with sync_client.libre_office.to_pdf() as route:
            try:
                resp = route.convert(docx_sample_file).run()
            except:  # noqa: E722, pragma: no cover
                return

        assert resp.status_code == HTTPStatus.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "application/pdf"

    def test_libre_office_convert_odt_format(self, sync_client: GotenbergClient, odt_sample_file: Path):
        with sync_client.libre_office.to_pdf() as route:
            resp = route.convert(odt_sample_file).run_with_retry()

        assert resp.status_code == HTTPStatus.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "application/pdf"

    def test_libre_office_convert_xlsx_format(self, sync_client: GotenbergClient, xlsx_sample_file: Path):
        with sync_client.libre_office.to_pdf() as route:
            resp = route.convert(xlsx_sample_file).run_with_retry()

        assert resp.status_code == HTTPStatus.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "application/pdf"

    def test_libre_office_convert_ods_format(self, sync_client: GotenbergClient, ods_sample_file: Path):
        with sync_client.libre_office.to_pdf() as route:
            resp = route.convert(ods_sample_file).run_with_retry()

        assert resp.status_code == HTTPStatus.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "application/pdf"

    def test_libre_office_convert_multiples_format_no_merge(
        self,
        sync_client: GotenbergClient,
        docx_sample_file: Path,
        odt_sample_file: Path,
        tmp_path: Path,
    ):
        with sync_client.libre_office.to_pdf() as route:
            resp = route.convert_files([docx_sample_file, odt_sample_file]).no_merge().run_with_retry()

        assert resp.status_code == HTTPStatus.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "application/zip"
        assert isinstance(resp, ZipFileResponse)
        assert resp.is_zip

        resp.extract_to(tmp_path)

        assert len(list(tmp_path.iterdir())) == 2

    async def test_libre_office_convert_multiples_format_no_merge_async(
        self,
        async_office_to_pdf_route: AsyncOfficeDocumentToPdfRoute,
        docx_sample_file: Path,
        odt_sample_file: Path,
        tmp_path: Path,
    ):
        resp = (
            await async_office_to_pdf_route.convert_files([docx_sample_file, odt_sample_file])
            .no_merge()
            .run_with_retry()
        )

        assert resp.status_code == HTTPStatus.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "application/zip"
        assert isinstance(resp, ZipFileResponse)
        assert resp.is_zip

        resp.extract_to(tmp_path)

        assert len(list(tmp_path.iterdir())) == 2

    def test_libre_office_convert_multiples_format_merged(
        self,
        sync_client: GotenbergClient,
        docx_sample_file: Path,
        odt_sample_file: Path,
    ):
        with sync_client.libre_office.to_pdf() as route:
            resp = route.convert_files([docx_sample_file, odt_sample_file]).do_merge().run_with_retry()

        assert resp.status_code == HTTPStatus.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "application/pdf"
        assert isinstance(resp, SingleFileResponse)

    def test_libre_office_convert_std_lib_mime(
        self,
        sync_client: GotenbergClient,
        docx_sample_file: Path,
        odt_sample_file: Path,
    ):
        with patch("gotenberg_client._utils.guess_mime_type") as mocked_guess_mime_type:
            mocked_guess_mime_type.side_effect = guess_mime_type_stdlib
            with sync_client.libre_office.to_pdf() as route:
                resp = route.convert_files([docx_sample_file, odt_sample_file]).no_merge().run_with_retry()

            assert resp.status_code == HTTPStatus.OK
            assert "Content-Type" in resp.headers
            assert resp.headers["Content-Type"] == "application/zip"

    @pytest.mark.parametrize(
        ("gt_format", "pike_format"),
        [(PdfAFormat.A2b, "2B"), (PdfAFormat.A3b, "3B")],
    )
    def test_libre_office_convert_xlsx_format_pdfa(
        self,
        sync_client: GotenbergClient,
        xlsx_sample_file: Path,
        tmp_path: Path,
        gt_format: PdfAFormat,
        pike_format: str,
    ):
        with sync_client.libre_office.to_pdf() as route:
            resp = route.convert(xlsx_sample_file).pdf_format(gt_format).run_with_retry()

        assert resp.status_code == HTTPStatus.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "application/pdf"

        output = tmp_path / "test_libre_office_convert_xlsx_format_pdfa.pdf"
        resp.to_file(output)
        with pikepdf.open(output) as pdf:
            meta = pdf.open_metadata()
            assert meta.pdfa_status == pike_format


class TestLibreOfficeConvertAsync:
    async def test_libre_office_convert_docx_format(
        self,
        async_office_to_pdf_route: AsyncOfficeDocumentToPdfRoute,
        docx_sample_file: Path,
    ):
        resp = await async_office_to_pdf_route.convert(docx_sample_file).run_with_retry()

        assert resp.status_code == HTTPStatus.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "application/pdf"


class TestLibreOfficeProperties:
    async def test_libre_office_password(
        self,
        async_office_to_pdf_route: AsyncOfficeDocumentToPdfRoute,
        odt_sample_file_with_password: Path,
    ):
        resp = (
            await async_office_to_pdf_route.convert(odt_sample_file_with_password).password("password").run_with_retry()
        )

        assert resp.status_code == HTTPStatus.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "application/pdf"

    async def test_libre_office_settings(
        self,
        async_office_to_pdf_route: AsyncOfficeDocumentToPdfRoute,
        docx_sample_file: Path,
    ):
        resp = (
            await async_office_to_pdf_route.convert(docx_sample_file)
            .orient(PageOrientation.Landscape)
            .page_ranges("1-4")
            .update_indexes(update_indexes=True)
            .export_form_fields(export_form_fields=True)
            .allow_duplicate_form_fields(allow_duplicate_form_fields=False)
            .export_bookmarks(export_bookmarks=True)
            .export_bookmarks_to_pdf_destination(export_bookmarks_to_pdf_destination=False)
            .export_notes(export_notes=True)
            .export_notes_pages(export_notes_pages=True)
            .export_only_notes_pages(export_only_notes_pages=True)
            .export_notes_in_margin(export_notes_in_margin=False)
            .convert_ooo_target_to_pdf_target()
            .export_links_relative_fsys()
            .skip_empty_pages(skip_empty_pages=True)
            .add_original_document_as_stream(add_original_document_as_stream=True)
            .single_page_sheets()
            .flatten()
            .run_with_retry()
        )

        assert resp.status_code == HTTPStatus.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "application/pdf"

    async def test_libre_office_compress_settings(
        self,
        async_office_to_pdf_route: AsyncOfficeDocumentToPdfRoute,
        docx_sample_file: Path,
    ):
        resp = (
            await async_office_to_pdf_route.convert(docx_sample_file)
            .lossless_image_compression(lossless_image_compression=True)
            .reduce_image_resolution(reduce_image_resolution=True)
            .max_image_resolution(600)
            .quality(90)
            .run_with_retry()
        )

        assert resp.status_code == HTTPStatus.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "application/pdf"

    async def test_libre_office_image_quality_too_low(
        self,
        async_office_to_pdf_route: AsyncOfficeDocumentToPdfRoute,
        odt_sample_file_with_images: Path,
    ):
        resp = await async_office_to_pdf_route.convert(odt_sample_file_with_images).quality(-1).run_with_retry()

        assert resp.status_code == HTTPStatus.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "application/pdf"

    async def test_libre_office_image_quality_too_high(
        self,
        async_office_to_pdf_route: AsyncOfficeDocumentToPdfRoute,
        odt_sample_file_with_images: Path,
    ):
        resp = await async_office_to_pdf_route.convert(odt_sample_file_with_images).quality(101).run_with_retry()

        assert resp.status_code == HTTPStatus.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "application/pdf"
