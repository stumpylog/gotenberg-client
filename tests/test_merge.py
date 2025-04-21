# SPDX-FileCopyrightText: 2023-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
import shutil
from pathlib import Path

import pikepdf
import pytest
from httpx import codes

from gotenberg_client import GotenbergClient
from gotenberg_client._merge.routes import AsyncMergePdfsRoute
from gotenberg_client.options import PdfAFormat
from tests.utils import extract_text


class TestMergePdfs:
    @pytest.mark.parametrize(
        ("gt_format", "pike_format"),
        [(PdfAFormat.A2b, "2B"), (PdfAFormat.A3b, "3B")],
    )
    def test_merge_files_pdf_a(
        self,
        sync_client: GotenbergClient,
        sample_directory: Path,
        tmp_path: Path,
        gt_format: PdfAFormat,
        pike_format: str,
    ):
        with sync_client.merge.merge() as route:
            resp = (
                route.merge([sample_directory / "z_first_merge.pdf", sample_directory / "a_merge_second.pdf"])
                .pdf_format(
                    gt_format,
                )
                .run_with_retry()
            )
        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "application/pdf"

        output = tmp_path / "test_merge_files_pdf_a.pdf"
        resp.to_file(output)
        with pikepdf.open(output) as pdf:
            meta = pdf.open_metadata()
            assert meta.pdfa_status == pike_format

    def test_merge_multiple_file(
        self,
        sync_client: GotenbergClient,
        sample_directory: Path,
        tmp_path: Path,
    ):
        if shutil.which("pdftotext") is None:  # pragma: no cover
            pytest.skip("No pdftotext executable found")
        else:
            with sync_client.merge.merge() as route:
                # By default, these would not merge correctly, as it happens alphabetically
                resp = route.merge(
                    [sample_directory / "z_first_merge.pdf", sample_directory / "a_merge_second.pdf"],
                ).run_with_retry()

                assert resp.status_code == codes.OK
                assert "Content-Type" in resp.headers
                assert resp.headers["Content-Type"] == "application/pdf"

                out_file = tmp_path / "test.pdf"
                resp.to_file(out_file)

                text = extract_text(out_file)
                lines = text.split("\n")
                # Extra is empty line
                assert len(lines) == 3
                assert "first PDF to be merged." in lines[0]
                assert "second PDF to be merged." in lines[1]


class TestMergePdfsAsync:
    async def test_merge_multiple_file(
        self,
        async_merge_pdfs_route: AsyncMergePdfsRoute,
        sample_directory: Path,
        tmp_path: Path,
    ):
        if shutil.which("pdftotext") is None:  # pragma: no cover
            pytest.skip("No pdftotext executable found")
        else:
            # By default, these would not merge correctly, as it happens alphabetically
            resp = await async_merge_pdfs_route.merge(
                [sample_directory / "z_first_merge.pdf", sample_directory / "a_merge_second.pdf"],
            ).run_with_retry()

            assert resp.status_code == codes.OK
            assert "Content-Type" in resp.headers
            assert resp.headers["Content-Type"] == "application/pdf"

            out_file = tmp_path / "test.pdf"
            resp.to_file(out_file)

            text = extract_text(out_file)
            lines = text.split("\n")
            # Extra is empty line
            assert len(lines) == 3
            assert "first PDF to be merged." in lines[0]
            assert "second PDF to be merged." in lines[1]
