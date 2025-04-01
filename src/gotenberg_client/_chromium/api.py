# SPDX-FileCopyrightText: 2025-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0


from gotenberg_client._base import AsyncBaseApi
from gotenberg_client._base import SyncBaseApi
from gotenberg_client._chromium.routes import AsyncHtmlToPdfRoute
from gotenberg_client._chromium.routes import AsyncMarkdownToPdfRoute
from gotenberg_client._chromium.routes import AsyncScreenshotFromHtmlRoute
from gotenberg_client._chromium.routes import AsyncScreenshotFromMarkdownRoute
from gotenberg_client._chromium.routes import AsyncScreenshotFromUrlRoute
from gotenberg_client._chromium.routes import AsyncUrlToPdfRoute
from gotenberg_client._chromium.routes import SyncHtmlToPdfRoute
from gotenberg_client._chromium.routes import SyncMarkdownToPdfRoute
from gotenberg_client._chromium.routes import SyncScreenshotFromHtmlRoute
from gotenberg_client._chromium.routes import SyncScreenshotFromMarkdownRoute
from gotenberg_client._chromium.routes import SyncScreenshotFromUrlRoute
from gotenberg_client._chromium.routes import SyncUrlToPdfRoute


class SyncChromiumApi(SyncBaseApi):
    """
    Represents the Gotenberg API for Chromium-based conversions and screenshots.

    Provides methods to create specific route objects for different conversion and screenshot types.

    https://gotenberg.dev/docs/routes#convert-with-chromium
    """

    def html_to_pdf(self) -> SyncHtmlToPdfRoute:
        """
        Creates an SyncHtmlToPdfRoute object for converting HTML to PDF.

        Returns:
            SyncHtmlToPdfRoute: A new SyncHtmlToPdfRoute object.
        """

        return SyncHtmlToPdfRoute(self._client, SyncHtmlToPdfRoute.ENDPOINT_URL, self._log)

    def url_to_pdf(self) -> SyncUrlToPdfRoute:
        """
        Creates a SyncUrlToPdfRoute object for converting URLs to PDF.

        Returns:
            SyncUrlToPdfRoute: A new SyncUrlToPdfRoute object.
        """

        return SyncUrlToPdfRoute(self._client, SyncUrlToPdfRoute.ENDPOINT_URL, self._log)

    def markdown_to_pdf(self) -> SyncMarkdownToPdfRoute:
        """
        Creates a SyncMarkdownToPdfRoute object for converting Markdown to PDF.

        Returns:
            SyncMarkdownToPdfRoute: A new SyncMarkdownToPdfRoute object.
        """

        return SyncMarkdownToPdfRoute(self._client, SyncMarkdownToPdfRoute.ENDPOINT_URL, self._log)

    def screenshot_url(self) -> SyncScreenshotFromUrlRoute:
        """
        Creates a SyncScreenshotFromUrlRoute object for capturing screenshots from URLs.

        Returns:
            SyncScreenshotFromUrlRoute: A new SyncScreenshotFromUrlRoute object.
        """

        return SyncScreenshotFromUrlRoute(self._client, SyncScreenshotFromUrlRoute.ENDPOINT_URL, self._log)

    def screenshot_html(self) -> SyncScreenshotFromHtmlRoute:
        """
        Creates a SyncScreenshotFromHtmlRoute object for capturing screenshots from HTML files.

        Returns:
            SyncScreenshotFromHtmlRoute: A new SyncScreenshotFromHtmlRoute object.
        """

        return SyncScreenshotFromHtmlRoute(self._client, SyncScreenshotFromHtmlRoute.ENDPOINT_URL, self._log)

    def screenshot_markdown(self) -> SyncScreenshotFromMarkdownRoute:
        """
        Creates a SyncScreenshotFromMarkdownRoute object for capturing screenshots from Markdown files.

        Returns:
            SyncScreenshotFromMarkdownRoute: A new SyncScreenshotFromMarkdownRoute object.
        """

        return SyncScreenshotFromMarkdownRoute(self._client, SyncScreenshotFromMarkdownRoute.ENDPOINT_URL, self._log)


class AsyncChromiumApi(AsyncBaseApi):
    """
    Represents the asynchronous Gotenberg API for Chromium-based conversions and screenshots.

    Provides methods to create specific route objects for different conversion and screenshot types.

    https://gotenberg.dev/docs/routes#convert-with-chromium
    """

    def html_to_pdf(self) -> AsyncHtmlToPdfRoute:
        """
        Creates an AsyncHtmlToPdfRoute object for converting HTML to PDF.

        Returns:
            AsyncHtmlToPdfRoute: A new AsyncHtmlToPdfRoute object.
        """

        return AsyncHtmlToPdfRoute(self._client, SyncHtmlToPdfRoute.ENDPOINT_URL, self._log)

    def url_to_pdf(self) -> AsyncUrlToPdfRoute:
        """
        Creates a AsyncUrlToPdfRoute object for converting URLs to PDF.

        Returns:
            AsyncUrlToPdfRoute: A new AsyncUrlToPdfRoute object.
        """

        return AsyncUrlToPdfRoute(self._client, AsyncUrlToPdfRoute.ENDPOINT_URL, self._log)

    def markdown_to_pdf(self) -> AsyncMarkdownToPdfRoute:
        """
        Creates a AsyncMarkdownToPdfRoute object for converting Markdown to PDF.

        Returns:
            AsyncMarkdownToPdfRoute: A new AsyncMarkdownToPdfRoute object.
        """

        return AsyncMarkdownToPdfRoute(self._client, AsyncMarkdownToPdfRoute.ENDPOINT_URL, self._log)

    def screenshot_url(self) -> AsyncScreenshotFromUrlRoute:
        """
        Creates a AsyncScreenshotFromUrlRoute object for capturing screenshots from URLs.

        Returns:
            AsyncScreenshotFromUrlRoute: A new AsyncScreenshotFromUrlRoute object.
        """

        return AsyncScreenshotFromUrlRoute(self._client, AsyncScreenshotFromUrlRoute.ENDPOINT_URL, self._log)

    def screenshot_html(self) -> AsyncScreenshotFromHtmlRoute:
        """
        Creates a AsyncScreenshotFromHtmlRoute object for capturing screenshots from HTML files.

        Returns:
            AsyncScreenshotFromHtmlRoute: A new AsyncScreenshotFromHtmlRoute object.
        """

        return AsyncScreenshotFromHtmlRoute(self._client, AsyncScreenshotFromHtmlRoute.ENDPOINT_URL, self._log)

    def screenshot_markdown(self) -> AsyncScreenshotFromMarkdownRoute:
        """
        Creates a AsyncScreenshotFromMarkdownRoute object for capturing screenshots from Markdown files.

        Returns:
            AsyncScreenshotFromMarkdownRoute: A new SyncScreenshotFromMarkdownRoute object.
        """

        return AsyncScreenshotFromMarkdownRoute(self._client, AsyncScreenshotFromMarkdownRoute.ENDPOINT_URL, self._log)
