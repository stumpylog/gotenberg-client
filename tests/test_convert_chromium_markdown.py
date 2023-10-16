from httpx import codes

from gotenberg_client._client import GotenbergClient
from tests.conftest import SAMPLE_DIR
from tests.utils import call_run_with_server_error_handling


class TestConvertChromiumUrlRoute:
    def test_basic_convert(self, client: GotenbergClient):
        index = SAMPLE_DIR / "markdown_index.html"
        md_files = [SAMPLE_DIR / "markdown1.md", SAMPLE_DIR / "markdown2.md"]
        img = SAMPLE_DIR / "img.gif"
        font = SAMPLE_DIR / "font.woff"
        style = SAMPLE_DIR / "style.css"
        with client.chromium.markdown_to_pdf() as route:
            resp = call_run_with_server_error_handling(
                route.index(index).markdown_files(md_files).resources([img, font]).resource(style),
            )

        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "application/pdf"
