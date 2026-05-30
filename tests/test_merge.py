# SPDX-FileCopyrightText: 2023-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
from http import HTTPStatus
from pathlib import Path

import pikepdf
import pytest
from pytest_httpx import HTTPXMock

from gotenberg_client import GotenbergClient
from gotenberg_client._merge.routes import AsyncMergePdfsRoute
from gotenberg_client.options import PdfAFormat
from gotenberg_client.options import WatermarkStampSource
from tests.utils import extract_text
from tests.utils import verify_stream_contains


@pytest.mark.live
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
        assert resp.status_code == HTTPStatus.OK
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
        with sync_client.merge.merge() as route:
            # By default, these would not merge correctly, as it happens alphabetically
            resp = route.merge(
                [sample_directory / "z_first_merge.pdf", sample_directory / "a_merge_second.pdf"],
            ).run_with_retry()

            assert resp.status_code == HTTPStatus.OK
            assert "Content-Type" in resp.headers
            assert resp.headers["Content-Type"] == "application/pdf"

            out_file = tmp_path / "test.pdf"
            resp.to_file(out_file)

            lines = extract_text(out_file)

            assert len(lines) == 2
            assert "first PDF to be merged." in lines[0]
            assert "second PDF to be merged." in lines[1]


@pytest.mark.live
@pytest.mark.async_route
class TestMergePdfsAsync:
    async def test_merge_multiple_file(
        self,
        async_merge_pdfs_route: AsyncMergePdfsRoute,
        sample_directory: Path,
        tmp_path: Path,
    ):
        # By default, these would not merge correctly, as it happens alphabetically
        resp = await async_merge_pdfs_route.merge(
            [sample_directory / "z_first_merge.pdf", sample_directory / "a_merge_second.pdf"],
        ).run_with_retry()

        assert resp.status_code == HTTPStatus.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "application/pdf"

        out_file = tmp_path / "test.pdf"
        resp.to_file(out_file)

        lines = extract_text(out_file)

        assert len(lines) == 2
        assert "first PDF to be merged." in lines[0]
        assert "second PDF to be merged." in lines[1]


class TestMergePdfsMocked:
    def test_merge_watermark_source(
        self,
        mock_sync_client: GotenbergClient,
        sample_directory: Path,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")
        with mock_sync_client.merge.merge() as route:
            route.merge([sample_directory / "sample1.pdf"]).watermark_source(WatermarkStampSource.Text).run()
        verify_stream_contains(httpx_mock.get_request(), "watermarkSource", "text")

    def test_merge_encrypt(
        self,
        mock_sync_client: GotenbergClient,
        sample_directory: Path,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")
        with mock_sync_client.merge.merge() as route:
            route.merge([sample_directory / "sample1.pdf"]).user_password("pw").run()
        verify_stream_contains(httpx_mock.get_request(), "userPassword", "pw")

    def test_merge_auto_index_bookmarks(
        self,
        mock_sync_client: GotenbergClient,
        sample_directory: Path,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")
        with mock_sync_client.merge.merge() as route:
            route.merge([sample_directory / "sample1.pdf"]).auto_index_bookmarks(enable=True).run()
        verify_stream_contains(httpx_mock.get_request(), "autoIndexBookmarks", "true")

    def test_merge_bookmarks(
        self,
        mock_sync_client: GotenbergClient,
        sample_directory: Path,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")
        bookmarks = [{"title": "Section 1", "page": 1}]
        with mock_sync_client.merge.merge() as route:
            route.merge([sample_directory / "sample1.pdf"]).merge_bookmarks(bookmarks).run()
        verify_stream_contains(httpx_mock.get_request(), "bookmarks", "Section 1")
