# SPDX-FileCopyrightText: 2025-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0


from gotenberg_client._base import BaseApi
from gotenberg_client._chromium.routes import UrlToPdfRoute


class ChromiumApi(BaseApi):
    """
    Represents the Gotenberg API for Chromium-based conversions and screenshots.

    Provides methods to create specific route objects for different conversion and screenshot types.

    https://gotenberg.dev/docs/routes#convert-with-chromium
    """

    _URL_CONVERT_ENDPOINT = "/forms/chromium/convert/url"
    _HTML_CONVERT_ENDPOINT = "/forms/chromium/convert/html"
    _MARKDOWN_CONVERT_ENDPOINT = "/forms/chromium/convert/markdown"
    _SCREENSHOT_URL = "/forms/chromium/screenshot/url"
    _SCREENSHOT_HTML = "/forms/chromium/screenshot/html"
    _SCREENSHOT_MARK_DOWN = "/forms/chromium/screenshot/markdown"

    def html_to_pdf(self) -> UrlToPdfRoute:
        """
        Creates an HtmlRoute object for converting HTML to PDF.

        Returns:
            HtmlRoute: A new HtmlRoute object.
        """

        return UrlToPdfRoute(self._client, UrlToPdfRoute.ENDPOINT_URL)

    def url_to_pdf(self) -> UrlRoute:
        """
        Creates a UrlRoute object for converting URLs to PDF.

        Returns:
            UrlRoute: A new UrlRoute object.
        """

        return UrlRoute(self._client, self._URL_CONVERT_ENDPOINT)

    def markdown_to_pdf(self) -> MarkdownRoute:
        """
        Creates a MarkdownRoute object for converting Markdown to PDF.

        Returns:
            MarkdownRoute: A new MarkdownRoute object.
        """

        return MarkdownRoute(self._client, self._MARKDOWN_CONVERT_ENDPOINT)

    def screenshot_url(self) -> ScreenshotRouteUrl:
        """
        Creates a ScreenshotRouteUrl object for capturing screenshots from URLs.

        Returns:
            ScreenshotRouteUrl: A new ScreenshotRouteUrl object.
        """

        return ScreenshotRouteUrl(self._client, self._SCREENSHOT_URL)

    def screenshot_html(self) -> ScreenshotRouteHtml:
        """
        Creates a ScreenshotRouteHtml object for capturing screenshots from HTML files.

        Returns:
            ScreenshotRouteHtml: A new ScreenshotRouteHtml object.
        """

        return ScreenshotRouteHtml(self._client, self._SCREENSHOT_HTML)

    def screenshot_markdown(self) -> ScreenshotRouteMarkdown:
        """
        Creates a ScreenshotRouteMarkdown object for capturing screenshots from Markdown files.

        Returns:
            ScreenshotRouteMarkdown: A new ScreenshotRouteMarkdown object.
        """

        return ScreenshotRouteMarkdown(self._client, self._SCREENSHOT_MARK_DOWN)
