# SPDX-FileCopyrightText: 2025-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
from pathlib import Path
from typing import Final
from typing import Optional

from gotenberg_client._base import AsyncBaseRoute
from gotenberg_client._base import SyncBaseRoute
from gotenberg_client._chromium.mixins import ConsoleExceptionMixin
from gotenberg_client._chromium.mixins import CookiesMixin
from gotenberg_client._chromium.mixins import CssPageSizeMixin
from gotenberg_client._chromium.mixins import CustomHTTPHeaderMixin
from gotenberg_client._chromium.mixins import DocumentOutlineMixin
from gotenberg_client._chromium.mixins import EmulatedMediaMixin
from gotenberg_client._chromium.mixins import HeaderFooterMixin
from gotenberg_client._chromium.mixins import InvalidStatusCodesMixin
from gotenberg_client._chromium.mixins import MarginMixin
from gotenberg_client._chromium.mixins import NativePageRangeMixin
from gotenberg_client._chromium.mixins import NetworkErrorsMixin
from gotenberg_client._chromium.mixins import OmitBackgroundMixin
from gotenberg_client._chromium.mixins import PageOrientMixin
from gotenberg_client._chromium.mixins import PageSizeMixin
from gotenberg_client._chromium.mixins import PerformanceModeMixin
from gotenberg_client._chromium.mixins import PrintBackgroundMixin
from gotenberg_client._chromium.mixins import RenderControlMixin
from gotenberg_client._chromium.mixins import ScaleMixin
from gotenberg_client._chromium.mixins import ScreenShotSettingsMixin
from gotenberg_client._chromium.mixins import SinglePageMixin
from gotenberg_client._common import MetadataMixin
from gotenberg_client._common import PdfFormatMixin
from gotenberg_client._common import PfdUniversalAccessMixin
from gotenberg_client._common import SplitModeMixin
from gotenberg_client._typing_compat import Self
from gotenberg_client._utils import FORCE_MULTIPART
from gotenberg_client._utils import ForceMultipartDict


class _BaseChromiumConvertMixin(
    SinglePageMixin,
    PageSizeMixin,
    MarginMixin,
    CssPageSizeMixin,
    DocumentOutlineMixin,
    PrintBackgroundMixin,
    OmitBackgroundMixin,
    PageOrientMixin,
    ScaleMixin,
    NativePageRangeMixin,
    HeaderFooterMixin,
    RenderControlMixin,
    EmulatedMediaMixin,
    CookiesMixin,
    CustomHTTPHeaderMixin,
    InvalidStatusCodesMixin,
    NetworkErrorsMixin,
    ConsoleExceptionMixin,
    PerformanceModeMixin,
    SplitModeMixin,
    PdfFormatMixin,
    PfdUniversalAccessMixin,
    MetadataMixin,
):
    """
    Common form fields for Chromium-based PDF conversion routes.

      - https://gotenberg.dev/docs/routes#url-into-pdf-route
      - https://gotenberg.dev/docs/routes#html-file-into-pdf-route
      - https://gotenberg.dev/docs/routes#markdown-files-into-pdf-route

    Provides shared functionality for URL, HTML and Markdown PDF conversion routes:
      - Page layout control (size, margins, orientation)
      - Content rendering options (backgrounds, scaling)
      - Document properties (outlines, metadata)
      - Browser emulation settings (headers, cookies)
      - Error handling (network errors, status codes)

    """


class _BaseIndexFilesMixin:
    """
    Mixin for routes requiring an index.html file and supporting resources.

    Provides methods to add HTML content and related resources for conversion.
    """

    def index(self, index: Path) -> Self:
        """
        Sets the main HTML file for conversion.

        Args:
            index (Path): Path to the HTML file to use as the main entry point.

        Returns:
            Self: This object for method chaining.

        Note:
            The file name will be normalized to "index.html" regardless of original name.
        """
        self._add_file_map(index, name="index.html")  # type: ignore[attr-defined]
        return self

    def string_index(self, index: str) -> Self:
        """
        Sets the main HTML content as a string.

        Args:
            index (str): HTML content to use as the main entry point.

        Returns:
            Self: This object for method chaining.

        Note:
            The file name will be normalized to "index.html" regardless of original name.
        """

        self._add_in_memory_file(index, name="index.html", mime_type="text/html")  # type: ignore[attr-defined]
        return self

    def resource(self, resource: Path, *, name: Optional[str] = None) -> Self:
        """
        Adds a resource file for the HTML to reference.

        Args:
            resource (Path): Path to the resource file (CSS, JS, images, etc.).
            name (Optional[str]): Override the filename if HTML references it differently.

        Returns:
            Self: This object for method chaining.
        """
        self._add_file_map(resource, name=name)  # type: ignore[attr-defined]
        return self

    def string_resource(self, resource: str, name: str, mime_type: Optional[str] = None) -> Self:
        """
        Adds an in-memory string resource.

        Args:
            resource (str): String content of the resource.
            name (str): Name to reference this resource in the HTML.
            mime_type (Optional[str]): MIME type of the resource.

        Returns:
            Self: This object for method chaining.
        """

        self._add_in_memory_file(resource, name=name, mime_type=mime_type)  # type: ignore[attr-defined]
        return self

    def resources(self, resources: list[Path]) -> Self:
        """
        Adds multiple resource files at once.

        Args:
            resources (list[Path]): List of paths to resource files.

        Returns:
            Self: This object for method chaining.

        Note:
            Uses original filenames; cannot override names in batch mode.
        """
        for x in resources:
            self.resource(x)
        return self

    def string_resources(
        self,
        resources: list[tuple[str, str, Optional[str]]],
    ) -> Self:
        """
        Adds multiple in-memory string resources.

        Args:
            resources: List of tuples, each containing:
                - str: Resource content
                - str: Resource filename
                - Optional[str]: Resource MIME type

        Returns:
            Self: This object for method chaining.

        Note:
            The third element of each tuple (Resource Mime-Type) is optional.
        """
        for resource, name, mime_type in resources:
            self._add_in_memory_file(resource, name=name, mime_type=mime_type)  # type: ignore[attr-defined]

        return self


class _BaseUrlFormMixin:
    """
    Mixin for routes that accept a URL parameter.

    Provides URL handling functionality for routes that convert web pages.
    """

    def url(self, url: str) -> Self:
        """
        Sets the URL to convert to PDF.

        Args:
            url (str): The URL of the web page to convert.

        Returns:
            UrlRoute: This object itself for method chaining.
        """

        self._form_data["url"] = url  # type: ignore[attr-defined,misc]
        return self

    def _get_all_resources(self) -> ForceMultipartDict:
        """
        Returns an empty ForceMultipartDict.

        This route does not require any file uploads, so an empty dictionary
        is returned as Gotenberg still requires multipart/form-data
        """
        return FORCE_MULTIPART


class _BaseUrlToPdfChromiumConvertRoute(_BaseUrlFormMixin, _BaseChromiumConvertMixin):
    """
    Base route for converting URLs to PDFs using Chromium.

    Provides the functionality to convert a web page at a specified URL to PDF.

    See https://gotenberg.dev/docs/routes#url-into-pdf-route
    """

    ENDPOINT_URL: Final[str] = "/forms/chromium/convert/url"


class SyncUrlToPdfRoute(_BaseUrlToPdfChromiumConvertRoute, SyncBaseRoute):
    """
    Synchronous route for converting URLs to PDFs using Chromium.

    Implements the synchronous API for converting web pages at specified URLs to PDF documents.

    See https://gotenberg.dev/docs/routes#url-into-pdf-route
    """


class AsyncUrlToPdfRoute(_BaseUrlToPdfChromiumConvertRoute, AsyncBaseRoute):
    """
    Asynchronous route for converting URLs to PDFs using Chromium.

    Implements the asynchronous API for converting web pages at specified URLs to PDF documents.

    See https://gotenberg.dev/docs/routes#url-into-pdf-route
    """


class _BaseHtmlToPdfRoute(_BaseIndexFilesMixin, _BaseChromiumConvertMixin):
    """
    Base route for converting HTML files to PDFs using Chromium.

    Provides the functionality to convert HTML files with associated resources to PDF.

    See https://gotenberg.dev/docs/routes#html-file-into-pdf-route
    """

    ENDPOINT_URL: Final[str] = "/forms/chromium/convert/html"


class SyncHtmlToPdfRoute(_BaseHtmlToPdfRoute, _BaseChromiumConvertMixin, SyncBaseRoute):
    """
    Synchronous route for converting HTML files to PDFs using Chromium.

    Implements the synchronous API for converting HTML files with associated resources to PDF documents.

    See https://gotenberg.dev/docs/routes#html-file-into-pdf-route
    """


class AsyncHtmlToPdfRoute(_BaseHtmlToPdfRoute, _BaseChromiumConvertMixin, AsyncBaseRoute):
    """
    Asynchronous route for converting HTML files to PDFs using Chromium.

    Implements the asynchronous API for converting HTML files with associated resources to PDF documents.

    See https://gotenberg.dev/docs/routes#html-file-into-pdf-route
    """


class _BaseMarkdownToPdfRoute(_BaseIndexFilesMixin, _BaseChromiumConvertMixin):
    """
    Base route for converting Markdown files to PDFs using Chromium.

    Provides methods to add Markdown files and supporting resources for PDF conversion.

    See https://gotenberg.dev/docs/routes#markdown-files-into-pdf-route
    """

    ENDPOINT_URL: Final[str] = "/forms/chromium/convert/markdown"

    def markdown_file(self, markdown_file: Path) -> Self:
        """
        Adds a Markdown file to be converted.

        Args:
            markdown_file (Path): Path to the Markdown file.

        Returns:
            Self: This object for method chaining.
        """

        self._add_file_map(markdown_file)  # type: ignore[attr-defined]

        return self

    def markdown_files(self, markdown_files: list[Path]) -> Self:
        """
        Adds multiple Markdown files to be converted.

        Args:
            markdown_files (list[Path]): List of paths to Markdown files.

        Returns:
            Self: This object for method chaining.

        Note:
            Files will be processed in the order they're provided.
        """
        for x in markdown_files:
            self.markdown_file(x)
        return self


class SyncMarkdownToPdfRoute(_BaseMarkdownToPdfRoute, SyncBaseRoute):
    """
    Asynchronous route for converting Markdown files to PDFs using Chromium.

    Implements the asynchronous API for converting Markdown files with associated resources to PDF documents.

    See https://gotenberg.dev/docs/routes#markdown-files-into-pdf-route
    """


class AsyncMarkdownToPdfRoute(_BaseMarkdownToPdfRoute, AsyncBaseRoute):
    """
    Synchronous route for capturing screenshots from URLs.

    Implements the synchronous API for capturing screenshots of web pages at specified URLs.

    See https://gotenberg.dev/docs/routes#screenshots-route
    """


class _BaseScreenShotSettingsMixin(
    RenderControlMixin,
    EmulatedMediaMixin,
    CookiesMixin,
    CustomHTTPHeaderMixin,
    InvalidStatusCodesMixin,
    ConsoleExceptionMixin,
    PerformanceModeMixin,
    OmitBackgroundMixin,
    ScreenShotSettingsMixin,
):
    """
    Common settings for screenshot capture routes.

    Provides shared functionality for screenshot routes:
    - Rendering control (timing, waiting)
    - Media emulation settings
    - Browser configuration (cookies, headers)
    - Error handling
    - Screenshot options (format, quality, scale)

    See https://gotenberg.dev/docs/routes#screenshots-route
    """


class _BaseScreenshotFromUrlRoute(_BaseScreenShotSettingsMixin, _BaseUrlFormMixin):
    """
    Base route for capturing screenshots from URLs.

    Provides the functionality to capture screenshots of web pages at specified URLs.

    See https://gotenberg.dev/docs/routes#screenshots-route
    """

    ENDPOINT_URL: Final[str] = "/forms/chromium/screenshot/url"


class SyncScreenshotFromUrlRoute(_BaseScreenshotFromUrlRoute, SyncBaseRoute):
    """
    Synchronous route for capturing screenshots from URLs.

    Implements the synchronous API for capturing screenshots of web pages at specified URLs.

    See https://gotenberg.dev/docs/routes#screenshots-route
    """


class AsyncScreenshotFromUrlRoute(_BaseScreenshotFromUrlRoute, AsyncBaseRoute):
    """
    Asynchronous route for capturing screenshots from URLs.

    Implements the asynchronous API for capturing screenshots of web pages at specified URLs.

    See https://gotenberg.dev/docs/routes#screenshots-route
    """


class _BaseScreenshotFromHtmlRoute(_BaseIndexFilesMixin, _BaseScreenShotSettingsMixin):
    """
    Base route for capturing screenshots from HTML files.

    Provides the functionality to capture screenshots of HTML files with associated resources.

    See https://gotenberg.dev/docs/routes#screenshots-route
    """

    ENDPOINT_URL: Final[str] = "/forms/chromium/screenshot/html"


class SyncScreenshotFromHtmlRoute(_BaseScreenshotFromHtmlRoute, SyncBaseRoute):
    """
    Synchronous route for capturing screenshots from HTML files.

    Implements the synchronous API for capturing screenshots of HTML files with associated resources.

    See https://gotenberg.dev/docs/routes#screenshots-route
    """


class AsyncScreenshotFromHtmlRoute(_BaseScreenshotFromHtmlRoute, AsyncBaseRoute):
    """
    Asynchronous route for capturing screenshots from HTML files.

    Implements the asynchronous API for capturing screenshots of HTML files with associated resources.

    See https://gotenberg.dev/docs/routes#screenshots-route
    """


class _BaseScreenshotFromMarkdownRoute(_BaseIndexFilesMixin, _BaseScreenShotSettingsMixin):
    """
    Base route for capturing screenshots from Markdown files.

    Provides the functionality to capture screenshots of rendered Markdown content.

    See https://gotenberg.dev/docs/routes#screenshots-route
    """

    ENDPOINT_URL: Final[str] = "/forms/chromium/screenshot/markdown"


class SyncScreenshotFromMarkdownRoute(_BaseScreenshotFromMarkdownRoute, SyncBaseRoute):
    """
    Synchronous route for capturing screenshots from Markdown files.

    Implements the synchronous API for capturing screenshots of rendered Markdown content.

    See https://gotenberg.dev/docs/routes#screenshots-route
    """


class AsyncScreenshotFromMarkdownRoute(_BaseScreenshotFromMarkdownRoute, AsyncBaseRoute):
    """
    Asynchronous route for capturing screenshots from Markdown files.

    Implements the asynchronous API for capturing screenshots of rendered Markdown content.

    See https://gotenberg.dev/docs/routes#screenshots-route
    """
