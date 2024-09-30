# SPDX-FileCopyrightText: 2023-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
from pathlib import Path
from unittest.mock import patch

import pikepdf
import pytest
from httpx import codes

from gotenberg_client import GotenbergClient
from gotenberg_client import SingleFileResponse
from gotenberg_client import ZipFileResponse
from gotenberg_client._utils import guess_mime_type_stdlib
from gotenberg_client.options import PdfAFormat
from tests.conftest import SAVE_OUTPUTS
from tests.conftest import output_file_save_directory


class TestLibreOfficeConvert:
    def test_libre_office_convert_docx_format(self, client: GotenbergClient, sample_directory: Path):
        test_file = sample_directory / "sample.docx"
        with client.libre_office.to_pdf() as route:
            resp = route.convert(test_file).run_with_retry()

        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "application/pdf"

        if SAVE_OUTPUTS:
            resp.to_file(output_file_save_directory / "test_libre_office_convert_docx_format.pdf")

    def test_libre_office_convert_docx_format_for_coverage(
        self,
        client: GotenbergClient,
        sample_directory: Path,
    ):  # pragma: no cover
        test_file = sample_directory / "sample.docx"
        with client.libre_office.to_pdf() as route:
            try:
                resp = route.convert(test_file).run()
            except:  # noqa: E722 - this is only for coverage
                return

        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "application/pdf"

        if SAVE_OUTPUTS:
            resp.to_file(output_file_save_directory / "test_libre_office_convert_docx_format_for_coverage.pdf")

    def test_libre_office_convert_odt_format(self, client: GotenbergClient, sample_directory: Path):
        test_file = sample_directory / "sample.odt"
        with client.libre_office.to_pdf() as route:
            resp = route.convert(test_file).run_with_retry()

        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "application/pdf"

        if SAVE_OUTPUTS:
            resp.to_file(output_file_save_directory / "test_libre_office_convert_odt_format.pdf")

    def test_libre_office_convert_xlsx_format(self, client: GotenbergClient, sample_directory: Path):
        test_file = sample_directory / "sample.xlsx"
        with client.libre_office.to_pdf() as route:
            resp = route.convert(test_file).run_with_retry()

        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "application/pdf"

        if SAVE_OUTPUTS:
            resp.to_file(output_file_save_directory / "test_libre_office_convert_xlsx_format.pdf")

    def test_libre_office_convert_ods_format(self, client: GotenbergClient, sample_directory: Path):
        test_file = sample_directory / "sample.ods"
        with client.libre_office.to_pdf() as route:
            resp = route.convert(test_file).run_with_retry()

        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "application/pdf"

        if SAVE_OUTPUTS:
            resp.to_file(output_file_save_directory / "test_libre_office_convert_ods_format.pdf")

    def test_libre_office_convert_multiples_format_no_merge(
        self,
        client: GotenbergClient,
        sample_directory: Path,
        tmp_path: Path,
    ):
        with client.libre_office.to_pdf() as route:
            resp = (
                route.convert_files([sample_directory / "sample.docx", sample_directory / "sample.odt"])
                .no_merge()
                .run_with_retry()
            )

        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "application/zip"
        assert isinstance(resp, ZipFileResponse)
        assert resp.is_zip

        resp.extract_to(tmp_path)

        assert len(list(tmp_path.iterdir())) == 2

        if SAVE_OUTPUTS:
            resp.to_file(output_file_save_directory / "test_libre_office_convert_multiples_format_no_merge.zip")

    def test_libre_office_convert_multiples_format_merged(self, client: GotenbergClient, sample_directory: Path):
        with client.libre_office.to_pdf() as route:
            resp = (
                route.convert_files([sample_directory / "sample.docx", sample_directory / "sample.odt"])
                .merge()
                .run_with_retry()
            )

        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "application/pdf"
        assert isinstance(resp, SingleFileResponse)

        if SAVE_OUTPUTS:
            resp.to_file(output_file_save_directory / "test_libre_office_convert_multiples_format_merged.pdf")

    def test_libre_office_convert_std_lib_mime(self, client: GotenbergClient, sample_directory: Path):
        with patch("gotenberg_client._utils.guess_mime_type") as mocked_guess_mime_type:
            mocked_guess_mime_type.side_effect = guess_mime_type_stdlib
            with client.libre_office.to_pdf() as route:
                resp = (
                    route.convert_files([sample_directory / "sample.docx", sample_directory / "sample.odt"])
                    .no_merge()
                    .run_with_retry()
                )

            assert resp.status_code == codes.OK
            assert "Content-Type" in resp.headers
            assert resp.headers["Content-Type"] == "application/zip"

            if SAVE_OUTPUTS:
                resp.to_file(output_file_save_directory / "test_libre_office_convert_std_lib_mime.pdf")

    @pytest.mark.parametrize(
        ("gt_format", "pike_format"),
        [(PdfAFormat.A2b, "2B"), (PdfAFormat.A3b, "3B")],
    )
    def test_libre_office_convert_xlsx_format_pdfa(
        self,
        client: GotenbergClient,
        sample_directory: Path,
        tmp_path: Path,
        gt_format: PdfAFormat,
        pike_format: str,
    ):
        test_file = sample_directory / "sample.xlsx"
        with client.libre_office.to_pdf() as route:
            resp = route.convert(test_file).pdf_format(gt_format).run_with_retry()

        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "application/pdf"

        output = tmp_path / "test_libre_office_convert_xlsx_format_pdfa.pdf"
        resp.to_file(output)
        with pikepdf.open(output) as pdf:
            meta = pdf.open_metadata()
            assert meta.pdfa_status == pike_format

        if SAVE_OUTPUTS:
            resp.to_file(output_file_save_directory / f"test_libre_office_convert_xlsx_format_pdfa-{pike_format}.pdf")
