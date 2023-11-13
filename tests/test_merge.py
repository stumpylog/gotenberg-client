import shutil
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
from tests.utils import extract_text


class TestMergePdfs:
    @pytest.mark.parametrize(
        ("gt_format", "pike_format"),
        [(PdfAFormat.A1a, "1A"), (PdfAFormat.A2b, "2B"), (PdfAFormat.A3b, "3B")],
    )
    def test_merge_files_pdf_a(
        self,
        client: GotenbergClient,
        gt_format: PdfAFormat,
        pike_format: str,
    ):
        with client.merge.merge() as route:
            resp = call_run_with_server_error_handling(
                route.merge([SAMPLE_DIR / "z_first_merge.pdf", SAMPLE_DIR / "a_merge_second.pdf"]).pdf_format(
                    gt_format,
                ),
            )

        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "application/pdf"

        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "test_merge_files_pdf_a.pdf"
            output.write_bytes(resp.content)
            with pikepdf.open(output) as pdf:
                meta = pdf.open_metadata()
                assert meta.pdfa_status == pike_format

        if SAVE_OUTPUTS:
            (SAVE_DIR / f"test_libre_office_convert_xlsx_format_{pike_format}.pdf").write_bytes(resp.content)

    def test_merge_multiple_file(
        self,
        client: GotenbergClient,
    ):
        if shutil.which("pdftotext") is None:  # pragma: no cover
            pytest.skip("No pdftotext executable found")
        else:
            with client.merge.merge() as route:
                # By default, these would not merge correctly, as it happens alphabetically
                route.merge([SAMPLE_DIR / "z_first_merge.pdf", SAMPLE_DIR / "a_merge_second.pdf"])
                resp = call_run_with_server_error_handling(route)

                assert resp.status_code == codes.OK
                assert "Content-Type" in resp.headers
                assert resp.headers["Content-Type"] == "application/pdf"

                with tempfile.NamedTemporaryFile(mode="wb") as tmp:
                    tmp.write(resp.content)

                    text = extract_text(Path(tmp.name))
                    lines = text.split("\n")
                    # Extra is empty line
                    assert len(lines) == 3
                    assert "first PDF to be merged." in lines[0]
                    assert "second PDF to be merged." in lines[1]

                if SAVE_OUTPUTS:
                    (SAVE_DIR / "test_pdf_a_multiple_file.pdf").write_bytes(resp.content)
