import tempfile
from pathlib import Path
from unittest.mock import patch

import pikepdf
import pytest
from httpx import codes

from gotenberg_client._client import GotenbergClient
from gotenberg_client._utils import guess_mime_type_stdlib
from gotenberg_client.options import PdfAFormat
from tests.conftest import SAMPLE_DIR
from tests.conftest import SAVE_DIR
from tests.conftest import SAVE_OUTPUTS
from tests.utils import call_run_with_server_error_handling


class TestLibreOfficeConvert:
    def test_libre_office_convert_docx_format(self, client: GotenbergClient):
        test_file = SAMPLE_DIR / "sample.docx"
        with client.libre_office.to_pdf() as route:
            resp = call_run_with_server_error_handling(route.convert(test_file))

        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "application/pdf"

        if SAVE_OUTPUTS:
            (SAVE_DIR / "test_libre_office_convert_docx_format.pdf").write_bytes(resp.content)

    def test_libre_office_convert_odt_format(self, client: GotenbergClient):
        test_file = SAMPLE_DIR / "sample.odt"
        with client.libre_office.to_pdf() as route:
            resp = call_run_with_server_error_handling(route.convert(test_file))

        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "application/pdf"

        if SAVE_OUTPUTS:
            (SAVE_DIR / "test_libre_office_convert_odt_format.pdf").write_bytes(resp.content)

    def test_libre_office_convert_xlsx_format(self, client: GotenbergClient):
        test_file = SAMPLE_DIR / "sample.xlsx"
        with client.libre_office.to_pdf() as route:
            resp = call_run_with_server_error_handling(route.convert(test_file))

        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "application/pdf"

        if SAVE_OUTPUTS:
            (SAVE_DIR / "test_libre_office_convert_xlsx_format.pdf").write_bytes(resp.content)

    def test_libre_office_convert_ods_format(self, client: GotenbergClient):
        test_file = SAMPLE_DIR / "sample.ods"
        with client.libre_office.to_pdf() as route:
            resp = call_run_with_server_error_handling(route.convert(test_file))

        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "application/pdf"

        if SAVE_OUTPUTS:
            (SAVE_DIR / "test_libre_office_convert_ods_format.pdf").write_bytes(resp.content)

    def test_libre_office_convert_multiples_format(self, client: GotenbergClient):
        with client.libre_office.to_pdf() as route:
            resp = call_run_with_server_error_handling(
                route.convert_files([SAMPLE_DIR / "sample.docx", SAMPLE_DIR / "sample.odt"]).no_merge(),
            )

        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "application/zip"

        if SAVE_OUTPUTS:
            (SAVE_DIR / "test_libre_office_convert_multiples_format.zip").write_bytes(resp.content)

    def test_libre_office_convert_multiples_format_merged(self, client: GotenbergClient):
        with client.libre_office.to_pdf() as route:
            resp = call_run_with_server_error_handling(
                route.convert_files([SAMPLE_DIR / "sample.docx", SAMPLE_DIR / "sample.odt"]).merge(),
            )

        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "application/pdf"

        if SAVE_OUTPUTS:
            (SAVE_DIR / "test_libre_office_convert_multiples_format.zip").write_bytes(resp.content)

    def test_libre_office_convert_std_lib_mime(self, client: GotenbergClient):
        with patch("gotenberg_client._utils.guess_mime_type") as mocked_guess_mime_type:
            mocked_guess_mime_type.side_effect = guess_mime_type_stdlib
            with client.libre_office.to_pdf() as route:
                resp = call_run_with_server_error_handling(
                    route.convert_files([SAMPLE_DIR / "sample.docx", SAMPLE_DIR / "sample.odt"]).no_merge(),
                )

            assert resp.status_code == codes.OK
            assert "Content-Type" in resp.headers
            assert resp.headers["Content-Type"] == "application/zip"

            if SAVE_OUTPUTS:
                (SAVE_DIR / "test_libre_office_convert_multiples_format.zip").write_bytes(resp.content)

    @pytest.mark.parametrize(
        ("gt_format", "pike_format"),
        [(PdfAFormat.A1a, "1A"), (PdfAFormat.A2b, "2B"), (PdfAFormat.A3b, "3B")],
    )
    def test_libre_office_convert_xlsx_format_pdfa(
        self,
        client: GotenbergClient,
        gt_format: PdfAFormat,
        pike_format: str,
    ):
        test_file = SAMPLE_DIR / "sample.xlsx"
        with client.libre_office.to_pdf() as route:
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
