from datetime import datetime
from datetime import timedelta
from datetime import timezone
from pathlib import Path

import pikepdf
from httpx import codes

from gotenberg_client import GotenbergClient
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
