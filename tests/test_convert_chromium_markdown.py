# SPDX-FileCopyrightText: 2023-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
from pathlib import Path

from gotenberg_client._chromium.routes import AsyncMarkdownToPdfRoute
from gotenberg_client._chromium.routes import SyncMarkdownToPdfRoute
from tests.utils import verify_basic_response_values_pdf


class TestConvertChromiumMarkdown:
    def test_basic_convert_markdown_to_pdf_sync(
        self,
        sync_markdown_to_pdf_route: SyncMarkdownToPdfRoute,
        markdown_index_file: Path,
        markdown_sample_one_file: Path,
        markdown_sample_two_file: Path,
        img_gif_file: Path,
        font_file: Path,
        css_style_file: Path,
    ):
        response = (
            sync_markdown_to_pdf_route.index(markdown_index_file)
            .markdown_files([markdown_sample_one_file, markdown_sample_two_file])
            .resources([img_gif_file, font_file])
            .resource(css_style_file)
            .run_with_retry()
        )
        verify_basic_response_values_pdf(response)

    async def test_basic_convert_markdown_to_pdf_async(
        self,
        async_markdown_to_pdf_route: AsyncMarkdownToPdfRoute,
        markdown_index_file: Path,
        markdown_sample_one_file: Path,
        markdown_sample_two_file: Path,
        img_gif_file: Path,
        font_file: Path,
        css_style_file: Path,
    ):
        response = await (
            async_markdown_to_pdf_route.index(markdown_index_file)
            .markdown_files([markdown_sample_one_file, markdown_sample_two_file])
            .resources([img_gif_file, font_file])
            .resource(css_style_file)
            .run_with_retry()
        )
        verify_basic_response_values_pdf(response)

    def test_basic_convert_string_references_sync(
        self,
        sync_markdown_to_pdf_route: SyncMarkdownToPdfRoute,
        markdown_index_file: Path,
        markdown_sample_one_file: Path,
        markdown_sample_two_file: Path,
        img_gif_file: Path,
        font_file: Path,
        css_style_file: Path,
    ):
        response = (
            sync_markdown_to_pdf_route.index(markdown_index_file)
            .string_resources(
                [
                    (markdown_sample_one_file.read_text(), "markdown1.md", "text/markdown"),
                    (markdown_sample_two_file.read_text(), "markdown2.md", "text/markdown"),
                ],
            )
            .resources([img_gif_file, font_file])
            .resource(css_style_file)
            .run_with_retry()
        )

        verify_basic_response_values_pdf(response)

    async def test_basic_convert_string_references_async(
        self,
        async_markdown_to_pdf_route: AsyncMarkdownToPdfRoute,
        markdown_index_file: Path,
        markdown_sample_one_file: Path,
        markdown_sample_two_file: Path,
        img_gif_file: Path,
        font_file: Path,
        css_style_file: Path,
    ):
        response = await (
            async_markdown_to_pdf_route.index(markdown_index_file)
            .string_resources(
                [
                    (markdown_sample_one_file.read_text(), "markdown1.md", "text/markdown"),
                    (markdown_sample_two_file.read_text(), "markdown2.md", "text/markdown"),
                ],
            )
            .resources([img_gif_file, font_file])
            .resource(css_style_file)
            .run_with_retry()
        )

        verify_basic_response_values_pdf(response)
