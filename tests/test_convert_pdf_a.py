# SPDX-FileCopyrightText: 2023-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
from pathlib import Path

import pikepdf
import pytest
from httpx import codes

from gotenberg_client import GotenbergClient
from gotenberg_client.options import PdfAFormat
from tests.conftest import SAVE_OUTPUTS
from tests.conftest import output_file_save_directory


class TestPdfAConvert:
    @pytest.mark.parametrize(
        ("gt_format", "pike_format"),
        [(PdfAFormat.A2b, "2B"), (PdfAFormat.A3b, "3B")],
    )
    def test_pdf_a_single_file(
        self,
        client: GotenbergClient,
        sample_directory: Path,
        tmp_path: Path,
        gt_format: PdfAFormat,
        pike_format: str,
    ):
        test_file = sample_directory / "sample1.pdf"
        with client.pdf_a.to_pdfa() as route:
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
            resp.to_file(output_file_save_directory / f"test_pdf_a_single_file{pike_format}.pdf")

    @pytest.mark.parametrize("gt_format", [PdfAFormat.A2b, PdfAFormat.A3b])
    def test_pdf_a_multiple_file(
        self,
        client: GotenbergClient,
        sample_directory: Path,
        tmp_path: Path,
        gt_format: PdfAFormat,
    ):
        test_file = sample_directory / "sample1.pdf"
        other_test_file = tmp_path / "sample2.pdf"
        other_test_file.write_bytes(test_file.read_bytes())
        with client.pdf_a.to_pdfa() as route:
            resp = route.convert_files([test_file, other_test_file]).pdf_format(gt_format).run_with_retry()

            assert resp.status_code == codes.OK
            assert "Content-Type" in resp.headers
            assert resp.headers["Content-Type"] == "application/zip"

    def test_pdf_universal_access_enable(
        self,
        client: GotenbergClient,
        sample_directory: Path,
    ):
        test_file = sample_directory / "sample1.pdf"
        with client.pdf_a.to_pdfa() as route:
            resp = route.convert(test_file).pdf_format(PdfAFormat.A2b).enable_universal_access().run_with_retry()

        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "application/pdf"

    def test_pdf_universal_access_disable(
        self,
        client: GotenbergClient,
        sample_directory: Path,
    ):
        test_file = sample_directory / "sample1.pdf"
        with client.pdf_a.to_pdfa() as route:
            resp = route.convert(test_file).pdf_format(PdfAFormat.A2b).disable_universal_access().run_with_retry()

        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "application/pdf"
