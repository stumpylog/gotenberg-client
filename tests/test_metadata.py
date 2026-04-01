from datetime import datetime
from datetime import timedelta
from datetime import timezone
from http import HTTPStatus
from pathlib import Path

import pikepdf
import pytest

from gotenberg_client import GotenbergClient
from gotenberg_client import InvalidKeywordError
from gotenberg_client import InvalidPdfRevisionError
from gotenberg_client import PdfMetadata
from gotenberg_client._common import MetadataMixin
from gotenberg_client._pdfmetadata.routes import AsyncReadPdfMetadataRoute
from gotenberg_client._pdfmetadata.routes import SyncReadPdfMetadataRoute
from gotenberg_client._pdfmetadata.routes import SyncWritePdfMetadataRoute
from gotenberg_client.options import TrappedStatus


@pytest.mark.live
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

        assert resp.status_code == HTTPStatus.OK
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

        assert resp.status_code == HTTPStatus.OK
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

        assert resp.status_code == HTTPStatus.OK
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


@pytest.mark.live
class TestPdfMetadataReadExisting:
    @staticmethod
    def sample_one_metadata_verify(data: dict[str, PdfMetadata], filename: str):
        meta = data[filename]
        # PDF document information fields
        assert "CreateDate" in meta
        assert meta["CreateDate"] == "2018:12:06 17:50:06+00:00"
        assert "Creator" in meta
        assert meta["Creator"] == "Chromium"
        assert "ModifyDate" in meta
        assert meta["ModifyDate"] == "2018:12:06 17:50:06+00:00"
        assert "Producer" in meta
        assert meta["Producer"] == "Skia/PDF m70"
        # ExifTool-derived fields (present in current Gotenberg, may be removed later)
        assert "FileType" in meta
        assert meta["FileType"] == "PDF"
        assert "FileTypeExtension" in meta
        assert meta["FileTypeExtension"] == "pdf"
        assert "Linearized" in meta
        assert meta["Linearized"] == "No"
        assert "MIMEType" in meta
        assert meta["MIMEType"] == "application/pdf"
        assert "PDFVersion" in meta
        assert meta["PDFVersion"] == 1.4
        assert "PageCount" in meta
        assert meta["PageCount"] == 3
        # FileName is not asserted: it reflects Gotenberg's internal UUID temp name,
        # not the posted filename — that value change is what originally surfaced this issue.

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


@pytest.mark.live
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

        assert response.status_code == HTTPStatus.OK
        assert "Content-Type" in response.headers
        assert response.headers["Content-Type"] == "application/pdf"

        output = tmp_path / "test_write_metadata_to_pdf.pdf"
        response.to_file(output)

        with pikepdf.Pdf.open(output) as pdf:
            assert "/Author" in pdf.docinfo
            assert pdf.docinfo["/Author"] == author


@pytest.mark.live
class TestPdfMetadataRoundTrip:
    def test_write_then_read(
        self,
        sync_client: GotenbergClient,
        pdf_sample_one_file: Path,
        tmp_path: Path,
    ):
        """
        Round-trip: write known metadata, then read it back via Gotenberg.

        This test exercises the write->read contract and confirms that ExifTool
        preserves the XMP pdf namespace key "ModDate" as-is on read - it does
        NOT normalise it to "ModifyDate".  "ModifyDate" only appears for PDFs
        whose modification date is stored in the base XMP namespace (e.g.
        Chromium/Skia-generated PDFs).
        """
        author = "Round Trip Author"
        title = "Round Trip Title"
        creator = "Round Trip Creator"
        modification_date = datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)

        # Step 1: write metadata fields to a copy of the sample PDF.
        with sync_client.metadata.write() as route:
            write_response = (
                route.write(pdf_sample_one_file)
                .metadata(
                    author=author,
                    title=title,
                    creator=creator,
                    modification_date=modification_date,
                )
                .run_with_retry()
            )

        assert write_response.status_code == HTTPStatus.OK
        assert write_response.headers["Content-Type"] == "application/pdf"
        written_pdf = tmp_path / "round_trip.pdf"
        write_response.to_file(written_pdf)

        # Step 2: read the metadata back from the written PDF.
        with sync_client.metadata.read() as route:
            read_response = route.read(written_pdf).run_with_retry()

        assert written_pdf.name in read_response
        result = read_response[written_pdf.name]

        # These document-information fields should survive the round-trip.
        assert result.get("Author") == author
        assert result.get("Title") == title
        assert result.get("Creator") == creator

        # Dates are NOT overridden by Gotenberg; the value is stored and returned exactly.
        # ExifTool converts ISO 8601 (hyphens, T separator) to its own format
        # (colons as date separators, space instead of T).
        expected_mod_date = modification_date.isoformat().replace("-", ":", 2).replace("T", " ", 1)
        assert "ModDate" in result
        assert result["ModDate"] == expected_mod_date
        # The source PDF's original base-XMP ModifyDate survives alongside the new ModDate.
        assert "ModifyDate" in result
