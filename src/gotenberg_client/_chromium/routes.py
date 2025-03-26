# SPDX-FileCopyrightText: 2025-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
import logging
from pathlib import Path
from typing import Final
from typing import Optional

from gotenberg_client._base import BaseSingleFileResponseRoute
from gotenberg_client._chromium.options import ChromiumConsoleExceptions
from gotenberg_client._chromium.options import ChromiumCookies
from gotenberg_client._chromium.options import ChromiumCustomHTTPHeader
from gotenberg_client._chromium.options import ChromiumCustomHttpStatusCodes
from gotenberg_client._chromium.options import ChromiumEmulatedMediaType
from gotenberg_client._chromium.options import ChromiumHeaderFooter
from gotenberg_client._chromium.options import ChromiumMetadata
from gotenberg_client._chromium.options import ChromiumNetworkErrors
from gotenberg_client._chromium.options import ChromiumPageProperties
from gotenberg_client._chromium.options import ChromiumPdfOptions
from gotenberg_client._chromium.options import ChromiumPerformanceMode
from gotenberg_client._chromium.options import ChromiumRenderWait
from gotenberg_client._chromium.options import ChromiumSplit
from gotenberg_client._chromium.options import ScreenshotSettings
from gotenberg_client._types import Self
from gotenberg_client._utils import FORCE_MULTIPART
from gotenberg_client._utils import ForceMultipartDict

logger = logging.getLogger()


class _FileBasedRoute(BaseSingleFileResponseRoute):
    def index(self, index: Path) -> Self:
        """
        Adds the given HTML file as the index file.

        The file name will be ignored and cannot be configured
        """
        self._add_file_map(index, name="index.html")
        return self

    def string_index(self, index: str) -> Self:
        """
        Provides the given string data as the index HTML for conversion.

        Args:
            index (str): The HTML content to be used as the index file.

        Returns:
            Self: This object itself for method chaining.
        """

        self._add_in_memory_file(index, name="index.html", mime_type="text/html")
        return self


class _RouteWithResources(BaseSingleFileResponseRoute):
    def resource(self, resource: Path, *, name: Optional[str] = None) -> Self:
        """
        Adds additional resources for the index HTML file to reference.

        The filename may optionally be overridden if the HTML refers to the file with a different name
        """
        self._add_file_map(resource, name=name)
        return self

    def string_resource(self, resource: str, name: str, mime_type: Optional[str] = None) -> Self:
        """
        Adds a string resource to the conversion process.

        The provided string data will be made available to the index HTML file during conversion,
        using the specified name and MIME type.

        Args:
            resource (str): The string data to be added as a resource.
            name (str): The name to assign to the resource.
            mime_type (Optional[str]): The MIME type of the resource (optional).

        Returns:
            Self: This object itself for method chaining.
        """

        self._add_in_memory_file(resource, name=name, mime_type=mime_type)
        return self

    def resources(self, resources: list[Path]) -> Self:
        """
        Adds multiple resource files for the index HTML file to reference.

        At this time, the name cannot be set
        """
        for x in resources:
            self.resource(x)
        return self

    def string_resources(
        self,
        resources: list[tuple[str, str, Optional[str]]],
    ) -> Self:
        """
        Process string resources.

        This method takes a list of resource tuples and processes them.

        Args:
            resources: A list of resource tuples.
                Each tuple contains:
                - str: Resource Data - The content or data of the resource.
                - str: Resource Filename - The filename of the resource for reference in the index
                - Optional[str]: Resource mimetype - The MIME type of the resource, if available.

        Returns:
            Self: Returns the instance of the class for method chaining.

        Note:
            The third element of each tuple (Resource Mime-Type) is optional.
        """
        for resource, name, mime_type in resources:
            self._add_in_memory_file(resource, name=name, mime_type=mime_type)

        return self


class UrlToPdfRoute(
    ChromiumPageProperties,
    ChromiumHeaderFooter,
    ChromiumRenderWait,
    ChromiumEmulatedMediaType,
    ChromiumCookies,
    ChromiumCustomHTTPHeader,
    ChromiumCustomHttpStatusCodes,
    ChromiumNetworkErrors,
    ChromiumConsoleExceptions,
    ChromiumPerformanceMode,
    ChromiumSplit,
    ChromiumPdfOptions,
    ChromiumMetadata,
    BaseSingleFileResponseRoute,
):
    """
    https://gotenberg.dev/docs/routes#url-into-pdf-route
    """

    ENDPOINT_URL: Final[str] = "/forms/chromium/convert/url"

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

    def _get_all_resources(self) -> ForceMultipartDict:
        """
        Returns an empty ForceMultipartDict.

        This route does not require any file uploads, so an empty dictionary
        is returned as Gotenberg still requires multipart/form-data
        """
        return FORCE_MULTIPART


class HtmlToPdfRoute(
    ChromiumPageProperties,
    ChromiumHeaderFooter,
    ChromiumRenderWait,
    ChromiumMetadata,
    _RouteWithResources,
    _FileBasedRoute,
):
    """
    https://gotenberg.dev/docs/routes#hPageOrientMixintml-file-into-pdf-route
    """

    ENDPOINT_URL: Final[str] = "/forms/chromium/convert/html"


class MarkdownToPdfRoute(
    ChromiumPageProperties,
    ChromiumHeaderFooter,
    ChromiumMetadata,
    _RouteWithResources,
    _FileBasedRoute,
):
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

    ENDPOINT_URL: Final[str] = "/forms/chromium/convert/markdown"

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

    def markdown_files(self, markdown_files: list[Path]) -> Self:
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


class _BaseScreenShotRoute(
    ScreenshotSettings,
    ChromiumRenderWait,
    ChromiumEmulatedMediaType,
    ChromiumCookies,
    ChromiumCustomHTTPHeader,
    ChromiumCustomHttpStatusCodes,
    ChromiumConsoleExceptions,
    ChromiumPerformanceMode,
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


class ScreenshotFromUrlRoute(_BaseScreenShotRoute):
    """
    Represents the Gotenberg route for capturing screenshots from URLs.

    Inherits from ScreenshotRoute and provides a specific URL-based method.

    https://gotenberg.dev/docs/routes#screenshots-route
    """

    ENDPOINT_URL: Final[str] = "/forms/chromium/screenshot/url"

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

    def _get_all_resources(self) -> ForceMultipartDict:
        """
        Returns an empty ForceMultipartDict.

        This route does not require any file uploads, so an empty dictionary
        is returned.
        """
        return FORCE_MULTIPART


class ScreenshotFromHtmlRoute(_BaseScreenShotRoute, _RouteWithResources, _FileBasedRoute):
    """
    Represents the Gotenberg route for capturing screenshots from HTML files.

    Inherits from _FileBasedRoute, _RouteWithResources, and ScreenshotRoute,
    combining functionalities for file-based operations, resource handling,
    and screenshot capture.

    https://gotenberg.dev/docs/routes#screenshots-route
    """

    ENDPOINT_URL: Final[str] = "/forms/chromium/screenshot/html"


class ScreenshotFromMarkdownRoute(_RouteWithResources, _FileBasedRoute, _BaseScreenShotRoute):
    """
    Represents the Gotenberg route for capturing screenshots from Markdown files.

    Inherits from _FileBasedRoute, _RouteWithResources, and ScreenshotRoute,
    combining functionalities for file-based operations, resource handling,
    and screenshot capture.

    https://gotenberg.dev/docs/routes#screenshots-route
    """

    ENDPOINT_URL: Final[str] = "/forms/chromium/screenshot/markdown"
