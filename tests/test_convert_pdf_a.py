import tempfile
from pathlib import Path

import pikepdf
import pytest
from httpx import codes

from gotenberg_client._client import GotenbergClient
from gotenberg_client.options import PdfAFormat
from tests.conftest import SAMPLE_DIR
from tests.conftest import SAVE_DIR
from tests.conftest import SAVE_OUTPUTS
from tests.utils import call_run_with_server_error_handling


class TestPdfAConvert:
    @pytest.mark.parametrize(
        ("gt_format", "pike_format"),
        [(PdfAFormat.A1a, "1A"), (PdfAFormat.A2b, "2B"), (PdfAFormat.A3b, "3B")],
    )
    def test_pdf_a_single_file(
        self,
        client: GotenbergClient,
        gt_format: PdfAFormat,
        pike_format: str,
    ):
        test_file = SAMPLE_DIR / "sample1.pdf"
        with client.pdf_a.to_pdfa() as route:
            resp = call_run_with_server_error_handling(route.convert(test_file).pdf_format(gt_format))

        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "application/pdf"

        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "test_libre_office_convert_xlsx_format_pdfa.pdf"
            output.write_bytes(resp.content)
            with pikepdf.open(output) as pdf:
                meta = pdf.open_metadata()
                assert meta.pdfa_status == pike_format

        if SAVE_OUTPUTS:
            (SAVE_DIR / f"test_libre_office_convert_xlsx_format_{pike_format}.pdf").write_bytes(resp.content)

    @pytest.mark.parametrize("gt_format", [PdfAFormat.A1a, PdfAFormat.A2b, PdfAFormat.A3b])
    def test_pdf_a_multiple_file(
        self,
        client: GotenbergClient,
        gt_format: PdfAFormat,
    ):
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = SAMPLE_DIR / "sample1.pdf"
            other_test_file = Path(temp_dir) / "sample2.pdf"
            other_test_file.write_bytes(test_file.read_bytes())
            with client.pdf_a.to_pdfa() as route:
                resp = call_run_with_server_error_handling(
                    route.convert_files([test_file, other_test_file]).pdf_format(gt_format),
                )

                assert resp.status_code == codes.OK
                assert "Content-Type" in resp.headers
                assert resp.headers["Content-Type"] == "application/zip"
