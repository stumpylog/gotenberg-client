# SPDX-FileCopyrightText: 2023-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
from pathlib import Path

from httpx import codes

from gotenberg_client import GotenbergClient


class TestConvertChromiumUrlRoute:
    def test_basic_convert(
        self,
        client: GotenbergClient,
        markdown_index_file: Path,
        markdown_sample_one_file: Path,
        markdown_sample_two_file: Path,
        img_gif_file: Path,
        font_file: Path,
        css_style_file: Path,
    ):
        with client.chromium.markdown_to_pdf() as route:
            resp = (
                route.index(markdown_index_file)
                .markdown_files([markdown_sample_one_file, markdown_sample_two_file])
                .resources([img_gif_file, font_file])
                .resource(css_style_file)
                .run_with_retry()
            )

        assert resp.status_code == codes.OK
        assert "Content-Type" in resp.headers
        assert resp.headers["Content-Type"] == "application/pdf"
