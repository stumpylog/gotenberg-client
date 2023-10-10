import shutil
import tempfile
from pathlib import Path
from typing import List

import pikepdf
import pytest
from httpx import codes

from gotenberg_client._client import GotenbergClient
from gotenberg_client.options import PdfAFormat
from tests.conftest import SAMPLE_DIR
from tests.conftest import SAVE_DIR
from tests.conftest import SAVE_OUTPUTS


@pytest.fixture()
def create_files():
    """
    Creates 2 files in a temporary directory and cleans them up
    after their use
    """
    temp_dir = Path(tempfile.mkdtemp())
    test_file = SAMPLE_DIR / "sample1.pdf"
    other_test_file = temp_dir / "sample2.pdf"
    other_test_file.write_bytes(test_file.read_bytes())
    yield [test_file, other_test_file]
    shutil.rmtree(temp_dir, ignore_errors=True)


class TestMergePdfs:
    @pytest.mark.parametrize(
        ("gt_format", "pike_format"),
        [(PdfAFormat.A1a, "1A"), (PdfAFormat.A2b, "2B"), (PdfAFormat.A3b, "3B")],
    )
    def test_merge_files_pdf_a(
        self,
        client: GotenbergClient,
        create_files: List[Path],
        gt_format: PdfAFormat,
        pike_format: str,
    ):
        with client.merge.merge() as route:
            resp = route.merge(create_files).pdf_format(gt_format).run()

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

    def test_pdf_a_multiple_file(
        self,
        client: GotenbergClient,
        create_files: List[Path],
    ):
        with client.merge.merge() as route:
            resp = route.merge(create_files).run()

            assert resp.status_code == codes.OK
            assert "Content-Type" in resp.headers
            assert resp.headers["Content-Type"] == "application/pdf"
