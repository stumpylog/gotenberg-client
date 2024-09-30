# SPDX-FileCopyrightText: 2023-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
from pathlib import Path

from httpx import codes

from gotenberg_client import GotenbergClient


class TestConvertChromiumUrlRoute:
    def test_basic_convert(self, client: GotenbergClient, sample_directory: Path):
        index = sample_directory / "markdown_index.html"
        md_files = [sample_directory / "markdown1.md", sample_directory / "markdown2.md"]
        img = sample_directory / "img.gif"
        font = sample_directory / "font.woff"
        style = sample_directory / "style.css"
        with client.chromium.markdown_to_pdf() as route:
            resp = route.index(index).markdown_files(md_files).resources([img, font]).resource(style).run_with_retry()

        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "application/pdf"
