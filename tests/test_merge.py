# SPDX-FileCopyrightText: 2023-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
import shutil
import tempfile
from pathlib import Path

import pikepdf
import pytest
from httpx import codes

from gotenberg_client import GotenbergClient
from gotenberg_client.options import PdfAFormat
from tests.conftest import SAMPLE_DIR
from tests.conftest import SAVE_DIR
from tests.conftest import SAVE_OUTPUTS
from tests.utils import extract_text


class TestMergePdfs:
    @pytest.mark.parametrize(
        ("gt_format", "pike_format"),
        [(PdfAFormat.A2b, "2B"), (PdfAFormat.A3b, "3B")],
    )
    def test_merge_files_pdf_a(
        self,
        client: GotenbergClient,
        gt_format: PdfAFormat,
        pike_format: str,
    ):
        with client.merge.merge() as route:
            resp = (
                route.merge([SAMPLE_DIR / "z_first_merge.pdf", SAMPLE_DIR / "a_merge_second.pdf"])
                .pdf_format(
                    gt_format,
                )
                .run_with_retry()
            )
        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "application/pdf"

        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "test_merge_files_pdf_a.pdf"
            resp.to_file(output)
            with pikepdf.open(output) as pdf:
                meta = pdf.open_metadata()
                assert meta.pdfa_status == pike_format

        if SAVE_OUTPUTS:
            resp.to_file(SAVE_DIR / f"test_libre_office_convert_xlsx_format_{pike_format}.pdf")

    def test_merge_multiple_file(
        self,
        client: GotenbergClient,
    ):
        if shutil.which("pdftotext") is None:  # pragma: no cover
            pytest.skip("No pdftotext executable found")
        else:
            with client.merge.merge() as route:
                # By default, these would not merge correctly, as it happens alphabetically
                resp = route.merge(
                    [SAMPLE_DIR / "z_first_merge.pdf", SAMPLE_DIR / "a_merge_second.pdf"],
                ).run_with_retry()

                assert resp.status_code == codes.OK
                assert "Content-Type" in resp.headers
                assert resp.headers["Content-Type"] == "application/pdf"

                with tempfile.TemporaryDirectory() as tmpdir:
                    out_file = Path(tmpdir) / "test.pdf"
                    resp.to_file(out_file)

                    text = extract_text(out_file)
                    lines = text.split("\n")
                    # Extra is empty line
                    assert len(lines) == 3
                    assert "first PDF to be merged." in lines[0]
                    assert "second PDF to be merged." in lines[1]

                if SAVE_OUTPUTS:
                    resp.to_file(SAVE_DIR / "test_pdf_a_multiple_file.pdf")
