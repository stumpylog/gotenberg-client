# SPDX-FileCopyrightText: 2025-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0


from gotenberg_client._base import BaseApi
from gotenberg_client._chromium.routes import HtmlToPdfRoute
from gotenberg_client._chromium.routes import MarkdownToPdfRoute
from gotenberg_client._chromium.routes import ScreenshotFromHtmlRoute
from gotenberg_client._chromium.routes import ScreenshotFromMarkdownRoute
from gotenberg_client._chromium.routes import ScreenshotFromUrlRoute
from gotenberg_client._chromium.routes import UrlToPdfRoute


class ChromiumApi(BaseApi):
    """
    Represents the Gotenberg API for Chromium-based conversions and screenshots.

    Provides methods to create specific route objects for different conversion and screenshot types.

    https://gotenberg.dev/docs/routes#convert-with-chromium
    """

    def html_to_pdf(self) -> HtmlToPdfRoute:
        """
        Creates an HtmlToPdfRoute object for converting HTML to PDF.

        Returns:
            HtmlToPdfRoute: A new HtmlToPdfRoute object.
        """

        return HtmlToPdfRoute(self._client, HtmlToPdfRoute.ENDPOINT_URL)

    def url_to_pdf(self) -> UrlToPdfRoute:
        """
        Creates a UrlToPdfRoute object for converting URLs to PDF.

        Returns:
            UrlToPdfRoute: A new UrlToPdfRoute object.
        """

        return UrlToPdfRoute(self._client, UrlToPdfRoute.ENDPOINT_URL)

    def markdown_to_pdf(self) -> MarkdownToPdfRoute:
        """
        Creates a MarkdownToPdfRoute object for converting Markdown to PDF.

        Returns:
            MarkdownToPdfRoute: A new MarkdownToPdfRoute object.
        """

        return MarkdownToPdfRoute(self._client, MarkdownToPdfRoute.ENDPOINT_URL)

    def screenshot_url(self) -> ScreenshotFromUrlRoute:
        """
        Creates a ScreenshotFromUrlRoute object for capturing screenshots from URLs.

        Returns:
            ScreenshotFromUrlRoute: A new ScreenshotFromUrlRoute object.
        """

        return ScreenshotFromUrlRoute(self._client, ScreenshotFromUrlRoute.ENDPOINT_URL)

    def screenshot_html(self) -> ScreenshotFromHtmlRoute:
        """
        Creates a ScreenshotFromHtmlRoute object for capturing screenshots from HTML files.

        Returns:
            ScreenshotFromHtmlRoute: A new ScreenshotFromHtmlRoute object.
        """

        return ScreenshotFromHtmlRoute(self._client, ScreenshotFromHtmlRoute.ENDPOINT_URL)

    def screenshot_markdown(self) -> ScreenshotFromMarkdownRoute:
        """
        Creates a ScreenshotFromMarkdownRoute object for capturing screenshots from Markdown files.

        Returns:
            ScreenshotFromMarkdownRoute: A new ScreenshotFromMarkdownRoute object.
        """

        return ScreenshotFromMarkdownRoute(self._client, ScreenshotFromMarkdownRoute.ENDPOINT_URL)
