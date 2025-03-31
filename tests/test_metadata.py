from datetime import datetime
from datetime import timedelta
from datetime import timezone
from pathlib import Path

import pikepdf
import pytest
from httpx import codes

from gotenberg_client import GotenbergClient
from gotenberg_client import InvalidKeywordError
from gotenberg_client import InvalidPdfRevisionError
from gotenberg_client._common import MetadataMixin
from gotenberg_client._pdfmetadata.routes import AsyncReadPdfMetadataRoute
from gotenberg_client._pdfmetadata.routes import SyncReadPdfMetadataRoute
from gotenberg_client._pdfmetadata.routes import SyncWritePdfMetadataRoute
from gotenberg_client.options import TrappedStatus


class TestPdfMetadataOnConvert:
    def test_metadata_basic(
        self,
        sync_client: GotenbergClient,
        tmp_path: Path,
        webserver_docker_internal_url: str,
    ):
        """Test basic metadata setting."""

        author = "Gotenberg Test"
        copyright_info = "Copyright Me at Me, Inc"
        creation_date = datetime(2006, 9, 18, 16, 27, 50, tzinfo=timezone(timedelta(hours=-4)))
        creator = "Gotenberg Some Version"
        keywords = ["Test", "Something"]
        marked = True
        mod_date = datetime(2006, 9, 18, 16, 27, 50, tzinfo=timezone(timedelta(hours=-5)))
        pdf_version = 1.5
        producer = "Gotenberg Client"
        subject = "A Test File"
        title = "An override title"
        trapped = TrappedStatus.TRUE

        with sync_client.chromium.url_to_pdf() as route:
            resp = (
                route.url(webserver_docker_internal_url)
                .metadata(
                    author=author,
                    pdf_copyright=copyright_info,
                    creation_date=creation_date,
                    creator=creator,
                    keywords=keywords,
                    marked=marked,
                    modification_date=mod_date,
                    pdf_version=pdf_version,
                    producer=producer,
                    subject=subject,
                    title=title,
                    trapped=trapped,
                )
                .run_with_retry()
            )

        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "application/pdf"

        output = tmp_path / "test_metadata_basic.pdf"
        resp.to_file(output)

        with pikepdf.Pdf.open(output) as pdf:
            assert "/Author" in pdf.docinfo
            assert pdf.docinfo["/Author"] == author

            assert "/Creator" in pdf.docinfo
            assert pdf.docinfo["/Creator"] == creator

            assert "/Keywords" in pdf.docinfo
            assert pdf.docinfo["/Keywords"] == ", ".join(keywords)

            assert "/Producer" in pdf.docinfo
            assert pdf.docinfo["/Producer"] == producer

            assert "/Subject" in pdf.docinfo
            assert pdf.docinfo["/Subject"] == subject

            assert "/Title" in pdf.docinfo
            assert pdf.docinfo["/Title"] == title

            assert "/Trapped" in pdf.docinfo
            assert pdf.docinfo["/Trapped"] == "/True"

            # TODO(stumpylog): Investigate why certain fields seems to not be possible to set

    def test_metadata_trapped_bool(
        self,
        sync_client: GotenbergClient,
        tmp_path: Path,
        webserver_docker_internal_url: str,
    ):
        with sync_client.chromium.url_to_pdf() as route:
            resp = (
                route.url(webserver_docker_internal_url)
                .metadata(
                    trapped=True,
                )
                .run_with_retry()
            )

        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "application/pdf"

        output = tmp_path / "test_metadata_trapped_bool.pdf"
        resp.to_file(output)

        with pikepdf.Pdf.open(output) as pdf:
            assert "/Trapped" in pdf.docinfo
            assert pdf.docinfo["/Trapped"] == "/True"

    def test_metadata_merging(
        self,
        sync_client: GotenbergClient,
        tmp_path: Path,
        webserver_docker_internal_url: str,
    ):
        inital_title = "Initial Title"
        new_title = "An New Title"
        trapped = TrappedStatus.UNKNOWN

        with sync_client.chromium.url_to_pdf() as route:
            resp = (
                route.url(webserver_docker_internal_url)
                .metadata(
                    title=inital_title,
                    trapped=trapped,
                )
                .metadata(title=new_title)
                .run_with_retry()
            )

        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "application/pdf"

        output = tmp_path / "test_metadata_merging.pdf"
        resp.to_file(output)

        with pikepdf.Pdf.open(output) as pdf:
            assert "/Title" in pdf.docinfo
            assert pdf.docinfo["/Title"] == new_title

            assert "/Trapped" in pdf.docinfo
            assert pdf.docinfo["/Trapped"] == "/Unknown"

    @pytest.mark.parametrize(
        ("base_value", "delta"),
        [(MetadataMixin.MIN_PDF_VERSION, -0.5), (MetadataMixin.MAX_PDF_VERSION, 0.5)],
    )
    def test_metadata_invalid_pdf_revision(
        self,
        sync_client: GotenbergClient,
        webserver_docker_internal_url: str,
        base_value: float,
        delta: float,
    ):
        with sync_client.chromium.url_to_pdf() as route, pytest.raises(InvalidPdfRevisionError):
            _ = (
                route.url(webserver_docker_internal_url)
                .metadata(
                    pdf_version=base_value + delta,
                )
                .run_with_retry()
            )

    @pytest.mark.parametrize(
        ("keywords"),
        [["Test, Something"], ["Test", 1]],
    )
    def test_metadata_invalid_pdf_keyword(
        self,
        sync_client: GotenbergClient,
        webserver_docker_internal_url: str,
        keywords: list[str],
    ):
        with sync_client.chromium.url_to_pdf() as route, pytest.raises(InvalidKeywordError):
            _ = (
                route.url(webserver_docker_internal_url)
                .metadata(
                    keywords=keywords,
                )
                .run_with_retry()
            )


class TestPdfMetadataReadExisting:
    @staticmethod
    def sample_one_metadata_verify(data: dict[str, dict[str, str]], filename: str):
        # These are the stable fields
        assert data[filename]["CreateDate"] == "2018:12:06 17:50:06+00:00"
        assert data[filename]["Creator"] == "Chromium"
        assert data[filename]["FileName"] == filename
        assert data[filename]["FileSize"] == "208 kB"
        assert data[filename]["FileType"] == "PDF"
        assert data[filename]["FileTypeExtension"] == "pdf"
        assert data[filename]["Linearized"] == "No"
        assert data[filename]["MIMEType"] == "application/pdf"
        assert data[filename]["ModifyDate"] == "2018:12:06 17:50:06+00:00"
        assert data[filename]["PDFVersion"] == 1.4
        assert data[filename]["PageCount"] == 3
        assert data[filename]["Producer"] == "Skia/PDF m70"

    async def test_read_metadata_from_pdf(
        self,
        async_read_pdf_metadata_route: AsyncReadPdfMetadataRoute,
        pdf_sample_one_file: Path,
    ):
        response = await async_read_pdf_metadata_route.read(pdf_sample_one_file).run_with_retry()
        assert pdf_sample_one_file.name in response

        self.sample_one_metadata_verify(response, pdf_sample_one_file.name)

        try:
            response = await async_read_pdf_metadata_route.read(pdf_sample_one_file).run()
            assert pdf_sample_one_file.name in response

            self.sample_one_metadata_verify(response, pdf_sample_one_file.name)
        except:  # noqa: E722, S110, pragma: no cover
            pass

    def test_read_metadata_from_pdf_sync(
        self,
        sync_read_pdf_metadata_route: SyncReadPdfMetadataRoute,
        pdf_sample_one_file: Path,
    ):
        response = sync_read_pdf_metadata_route.read(pdf_sample_one_file).run_with_retry()
        assert pdf_sample_one_file.name in response

        self.sample_one_metadata_verify(response, pdf_sample_one_file.name)

        try:
            response = sync_read_pdf_metadata_route.read(pdf_sample_one_file).run()
            assert pdf_sample_one_file.name in response

            self.sample_one_metadata_verify(response, pdf_sample_one_file.name)
        except:  # noqa: E722, S110, pragma: no cover
            pass


class TestPdfMetadataWriteExisting:
    def test_write_metadata_to_pdf(
        self,
        sync_write_pdf_metadata_route: SyncWritePdfMetadataRoute,
        pdf_sample_one_file: Path,
        tmp_path: Path,
    ):
        author = "Gotenberg Testing"
        response = (
            sync_write_pdf_metadata_route.write_files([pdf_sample_one_file]).metadata(author=author).run_with_retry()
        )

        assert response.status_code == codes.OK
        assert "Content-Type" in response.headers
        assert response.headers["Content-Type"] == "application/pdf"

        output = tmp_path / "test_write_metadata_to_pdf.pdf"
        response.to_file(output)

        with pikepdf.Pdf.open(output) as pdf:
            assert "/Author" in pdf.docinfo
            assert pdf.docinfo["/Author"] == author
