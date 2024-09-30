# SPDX-FileCopyrightText: 2023-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
import logging
from pathlib import Path
from typing import List
from typing import Literal

from gotenberg_client._base import BaseApi
from gotenberg_client._base import BaseSingleFileResponseRoute
from gotenberg_client._convert.common import ConsoleExceptionMixin
from gotenberg_client._convert.common import CustomHTTPHeaderMixin
from gotenberg_client._convert.common import EmulatedMediaMixin
from gotenberg_client._convert.common import HeaderFooterMixin
from gotenberg_client._convert.common import InvalidStatusCodesMixin
from gotenberg_client._convert.common import PageOrientMixin
from gotenberg_client._convert.common import PagePropertiesMixin
from gotenberg_client._convert.common import PerformanceModeMixin
from gotenberg_client._convert.common import RenderControlMixin
from gotenberg_client._types import Self
from gotenberg_client._utils import FORCE_MULTIPART
from gotenberg_client._utils import ForceMultipartDict

logger = logging.getLogger()


class _FileBasedRoute(BaseSingleFileResponseRoute):
    def index(self, index: Path) -> Self:
        self._add_file_map(index, "index.html")
        return self


class _RouteWithResources(BaseSingleFileResponseRoute):
    def resource(self, resource: Path) -> Self:
        self._add_file_map(resource)
        return self

    def resources(self, resources: List[Path]) -> Self:
        for x in resources:
            self.resource(x)
        return self


class HtmlRoute(
    PagePropertiesMixin,
    HeaderFooterMixin,
    RenderControlMixin,
    PageOrientMixin,
    _RouteWithResources,
    _FileBasedRoute,
):
    """
    https://gotenberg.dev/docs/routes#html-file-into-pdf-route
    """


class UrlRoute(
    PagePropertiesMixin,
    HeaderFooterMixin,
    RenderControlMixin,
    ConsoleExceptionMixin,
    EmulatedMediaMixin,
    CustomHTTPHeaderMixin,
    PageOrientMixin,
    BaseSingleFileResponseRoute,
):
    """
    Represents the Gotenberg route for converting a URL to a PDF.

    This class inherits from various mixins that provide functionalities such as
    - Page properties (margins, size)
    - Headers and footers
    - Rendering control options
    - Console exception handling
    - Emulated media type
    - Custom HTTP headers
    - Page orientation

    See the Gotenberg documentation (https://gotenberg.dev/docs/routes#url-into-pdf-route)
    for detailed information on these functionalities.
    """

    def url(self, url: str) -> Self:
        """
        Sets the URL to convert to PDF.

        Args:
            url (str): The URL of the web page to convert.

        Returns:
            UrlRoute: This object itself for method chaining.
        """

        self._form_data["url"] = url
        return self

    def _get_files(self) -> ForceMultipartDict:
        """
        Returns an empty ForceMultipartDict.

        This route does not require any file uploads, so an empty dictionary
        is returned as Gotenberg still requires multipart/form-data
        """

        return FORCE_MULTIPART  # Assuming FORCE_MULTIPART is a pre-defined empty dictionary


class MarkdownRoute(PagePropertiesMixin, HeaderFooterMixin, _RouteWithResources, _FileBasedRoute):
    """
    Represents the Gotenberg route for converting Markdown files to a PDF.

    This class inherits from various mixins that provide functionalities such as
    - Page properties (margins, size)
    - Headers and footers
    - Handling file resources
    - File-based route behavior

    See the Gotenberg documentation (https://gotenberg.dev/docs/routes#markdown-files-into-pdf-route)
    for detailed information on these functionalities.
    """

    def markdown_file(self, markdown_file: Path) -> Self:
        """
        Adds a single Markdown file to be converted.

        Args:
            markdown_file (Path): The path to the Markdown file.

        Returns:
            MarkdownRoute: This object itself for method chaining.
        """

        self._add_file_map(markdown_file)

        return self

    def markdown_files(self, markdown_files: List[Path]) -> Self:
        """
        Adds multiple Markdown files to be converted.

        Args:
            markdown_files (List[Path]): A list of paths to Markdown files.

        Returns:
            MarkdownRoute: This object itself for method chaining.
        """
        for x in markdown_files:
            self.markdown_file(x)
        return self


class ScreenshotRoute(
    RenderControlMixin,
    EmulatedMediaMixin,
    CustomHTTPHeaderMixin,
    InvalidStatusCodesMixin,
    ConsoleExceptionMixin,
    PerformanceModeMixin,
    PageOrientMixin,
    BaseSingleFileResponseRoute,
):
    """
    Represents the Gotenberg route for capturing screenshots.

    This class inherits from various mixins that provide functionalities such as
    - Rendering control options
    - Emulated media type
    - Custom HTTP headers
    - Handling invalid status codes from the captured page
    - Console exception handling
    - Performance mode selection (optimize for speed or size)
    - Page orientation

    See the Gotenberg documentation (https://gotenberg.dev/docs/routes#screenshots-route)
    for detailed information on these functionalities.
    """

    _QUALITY_MAX = 100
    _QUALITY_MIN = 0

    def output_format(self, output_format: Literal["png", "jpeg", "webp"] = "png") -> Self:
        """
        Sets the output format for the screenshot.

        Args:
            output_format (Literal["png", "jpeg", "webp"], optional): The desired output format. Defaults to "png".

        Returns:
            ScreenshotRoute: This object itself for method chaining.
        """

        self._form_data.update({"format": output_format})
        return self

    def quality(self, quality: int) -> Self:
        """
        Sets the quality of the screenshot (0-100).

        Args:
            quality (int): The desired quality level (0-100).

        Returns:
            ScreenshotRoute: This object itself for method chaining.
        """

        if quality > self._QUALITY_MAX:
            logging.warning(f"quality {quality} is above {self._QUALITY_MAX}, resetting to {self._QUALITY_MAX}")
            quality = self._QUALITY_MAX
        elif quality < self._QUALITY_MIN:
            logging.warning(f"quality {quality} is below {self._QUALITY_MIN}, resetting to {self._QUALITY_MIN}")
            quality = self._QUALITY_MIN

        self._form_data.update({"quality": str(quality)})
        return self

    def optimize_speed(self) -> Self:
        """
        Sets the optimization mode to prioritize speed.

        Returns:
            ScreenshotRoute: This object itself for method chaining.
        """

        self._form_data.update({"optimizeForSpeed": "true"})
        return self

    def optimize_size(self) -> Self:
        """
        Sets the optimization mode to prioritize size reduction.

        Returns:
            ScreenshotRoute: This object itself for method chaining.
        """

        self._form_data.update({"optimizeForSpeed": "false"})
        return self


class ScreenshotRouteUrl(ScreenshotRoute):
    """
    Represents the Gotenberg route for capturing screenshots from URLs.

    Inherits from ScreenshotRoute and provides a specific URL-based method.
    """

    def url(self, url: str) -> Self:
        """
        Sets the URL to capture a screenshot from.

        Args:
            url (str): The URL of the web page to capture a screenshot of.

        Returns:
            ScreenshotRouteUrl: This object itself for method chaining.
        """

        self._form_data.update({"url": url})
        return self

    def _get_files(self) -> ForceMultipartDict:
        """
        Returns an empty ForceMultipartDict.

        This route does not require any file uploads, so an empty dictionary
        is returned.
        """

        return FORCE_MULTIPART


class ScreenshotRouteHtml(_FileBasedRoute, _RouteWithResources, ScreenshotRoute):
    """
    Represents the Gotenberg route for capturing screenshots from HTML files.

    Inherits from _FileBasedRoute, _RouteWithResources, and ScreenshotRoute,
    combining functionalities for file-based operations, resource handling,
    and screenshot capture.
    """


class ScreenshotRouteMarkdown(_FileBasedRoute, _RouteWithResources, ScreenshotRoute):
    """
    Represents the Gotenberg route for capturing screenshots from Markdown files.

    Inherits from _FileBasedRoute, _RouteWithResources, and ScreenshotRoute,
    combining functionalities for file-based operations, resource handling,
    and screenshot capture.
    """


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

    def html_to_pdf(self) -> HtmlRoute:
        """
        Creates an HtmlRoute object for converting HTML to PDF.

        Returns:
            HtmlRoute: A new HtmlRoute object.
        """

        return HtmlRoute(self._client, self._HTML_CONVERT_ENDPOINT)

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
