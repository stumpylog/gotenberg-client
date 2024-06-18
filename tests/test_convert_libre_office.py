# SPDX-FileCopyrightText: 2023-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
import tempfile
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
from tests.conftest import SAMPLE_DIR
from tests.conftest import SAVE_DIR
from tests.conftest import SAVE_OUTPUTS


class TestLibreOfficeConvert:
    def test_libre_office_convert_docx_format(self, client: GotenbergClient):
        test_file = SAMPLE_DIR / "sample.docx"
        with client.libre_office.to_pdf() as route:
            resp = route.convert(test_file).run_with_retry()

        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "application/pdf"

        if SAVE_OUTPUTS:
            resp.to_file(SAVE_DIR / "test_libre_office_convert_docx_format.pdf")

    def test_libre_office_convert_odt_format(self, client: GotenbergClient):
        test_file = SAMPLE_DIR / "sample.odt"
        with client.libre_office.to_pdf() as route:
            resp = route.convert(test_file).run_with_retry()

        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "application/pdf"

        if SAVE_OUTPUTS:
            resp.to_file(SAVE_DIR / "test_libre_office_convert_odt_format.pdf")

    def test_libre_office_convert_xlsx_format(self, client: GotenbergClient):
        test_file = SAMPLE_DIR / "sample.xlsx"
        with client.libre_office.to_pdf() as route:
            resp = route.convert(test_file).run_with_retry()

        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "application/pdf"

        if SAVE_OUTPUTS:
            resp.to_file(SAVE_DIR / "test_libre_office_convert_xlsx_format.pdf")

    def test_libre_office_convert_ods_format(self, client: GotenbergClient):
        test_file = SAMPLE_DIR / "sample.ods"
        with client.libre_office.to_pdf() as route:
            resp = route.convert(test_file).run_with_retry()

        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "application/pdf"

        if SAVE_OUTPUTS:
            resp.to_file(SAVE_DIR / "test_libre_office_convert_ods_format.pdf")

    def test_libre_office_convert_multiples_format_no_merge(self, client: GotenbergClient, temporary_dir: Path):
        with client.libre_office.to_pdf() as route:
            resp = (
                route.convert_files([SAMPLE_DIR / "sample.docx", SAMPLE_DIR / "sample.odt"]).no_merge().run_with_retry()
            )

        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "application/zip"
        assert isinstance(resp, ZipFileResponse)

        resp.extract_to(temporary_dir)

        assert len(list(temporary_dir.iterdir())) == 2

        if SAVE_OUTPUTS:
            resp.to_file(SAVE_DIR / "test_libre_office_convert_multiples_format_no_merge.zip")

    def test_libre_office_convert_multiples_format_merged(self, client: GotenbergClient):
        with client.libre_office.to_pdf() as route:
            resp = route.convert_files([SAMPLE_DIR / "sample.docx", SAMPLE_DIR / "sample.odt"]).merge().run_with_retry()

        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "application/pdf"
        assert isinstance(resp, SingleFileResponse)

        if SAVE_OUTPUTS:
            resp.to_file(SAVE_DIR / "test_libre_office_convert_multiples_format_merged.pdf")

    def test_libre_office_convert_std_lib_mime(self, client: GotenbergClient):
        with patch("gotenberg_client._utils.guess_mime_type") as mocked_guess_mime_type:
            mocked_guess_mime_type.side_effect = guess_mime_type_stdlib
            with client.libre_office.to_pdf() as route:
                resp = (
                    route.convert_files([SAMPLE_DIR / "sample.docx", SAMPLE_DIR / "sample.odt"])
                    .no_merge()
                    .run_with_retry()
                )

            assert resp.status_code == codes.OK
            assert "Content-Type" in resp.headers
            assert resp.headers["Content-Type"] == "application/zip"

            if SAVE_OUTPUTS:
                resp.to_file(SAVE_DIR / "test_libre_office_convert_std_lib_mime.pdf")

    @pytest.mark.parametrize(
        ("gt_format", "pike_format"),
        [(PdfAFormat.A2b, "2B"), (PdfAFormat.A3b, "3B")],
    )
    def test_libre_office_convert_xlsx_format_pdfa(
        self,
        client: GotenbergClient,
        gt_format: PdfAFormat,
        pike_format: str,
    ):
        test_file = SAMPLE_DIR / "sample.xlsx"
        with client.libre_office.to_pdf() as route:
            resp = route.convert(test_file).pdf_format(gt_format).run_with_retry()

        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "application/pdf"

        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "test_libre_office_convert_xlsx_format_pdfa.pdf"
            resp.to_file(output)
            with pikepdf.open(output) as pdf:
                meta = pdf.open_metadata()
                assert meta.pdfa_status == pike_format

        if SAVE_OUTPUTS:
            resp.to_file(SAVE_DIR / f"test_libre_office_convert_xlsx_format_pdfa-{pike_format}.pdf")
