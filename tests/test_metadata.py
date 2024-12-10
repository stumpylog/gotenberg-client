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
from gotenberg_client._convert.common import MetadataMixin
from gotenberg_client.options import TrappedStatus


class TestPdfMetadata:
    def test_metadata_basic(
        self,
        client: GotenbergClient,
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

        with client.chromium.url_to_pdf() as route:
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

    def test_metadata_trapped_bool(self, client: GotenbergClient, tmp_path: Path, webserver_docker_internal_url: str):
        with client.chromium.url_to_pdf() as route:
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
        client: GotenbergClient,
        tmp_path: Path,
        webserver_docker_internal_url: str,
    ):
        inital_title = "Initial Title"
        new_title = "An New Title"
        trapped = TrappedStatus.UNKNOWN

        with client.chromium.url_to_pdf() as route:
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
        client: GotenbergClient,
        webserver_docker_internal_url: str,
        base_value: float,
        delta: float,
    ):
        with client.chromium.url_to_pdf() as route, pytest.raises(InvalidPdfRevisionError):
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
        client: GotenbergClient,
        webserver_docker_internal_url: str,
        keywords: list[str],
    ):
        with client.chromium.url_to_pdf() as route, pytest.raises(InvalidKeywordError):
            _ = (
                route.url(webserver_docker_internal_url)
                .metadata(
                    keywords=keywords,
                )
                .run_with_retry()
            )
