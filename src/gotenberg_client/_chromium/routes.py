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
    The common form fields for the following:

      - https://gotenberg.dev/docs/routes#url-into-pdf-route
      - https://gotenberg.dev/docs/routes#html-file-into-pdf-route
      - https://gotenberg.dev/docs/routes#markdown-files-into-pdf-route
    """


class _BaseIndexFilesMixin:
    """
    Mixin for routes which require an index.html and supporting resources
    """

    def index(self, index: Path) -> Self:
        """
        Adds the given HTML file as the index file.

        The file name will be ignored and cannot be configured
        """
        self._add_file_map(index, name="index.html")  # type: ignore[attr-defined]
        return self

    def string_index(self, index: str) -> Self:
        """
        Provides the given string data as the index HTML for conversion.

        Args:
            index (str): The HTML content to be used as the index file.

        Returns:
            Self: This object itself for method chaining.
        """

        self._add_in_memory_file(index, name="index.html", mime_type="text/html")  # type: ignore[attr-defined]
        return self

    def resource(self, resource: Path, *, name: Optional[str] = None) -> Self:
        """
        Adds additional resources for the index HTML file to reference.

        The filename may optionally be overridden if the HTML refers to the file with a different name
        """
        self._add_file_map(resource, name=name)  # type: ignore[attr-defined]
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

        self._add_in_memory_file(resource, name=name, mime_type=mime_type)  # type: ignore[attr-defined]
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
            self._add_in_memory_file(resource, name=name, mime_type=mime_type)  # type: ignore[attr-defined]

        return self


class _BaseUrlFormMixin:
    """
    Mixin for routes which have no files but provide the url form field
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
    https://gotenberg.dev/docs/routes#url-into-pdf-route
    """

    ENDPOINT_URL: Final[str] = "/forms/chromium/convert/url"


class SyncUrlToPdfRoute(_BaseUrlToPdfChromiumConvertRoute, SyncBaseRoute):
    pass


class AsyncUrlToPdfRoute(_BaseUrlToPdfChromiumConvertRoute, AsyncBaseRoute):
    pass


class _BaseHtmlToPdfRoute(_BaseIndexFilesMixin, _BaseChromiumConvertMixin):
    """
    https://gotenberg.dev/docs/routes#html-file-into-pdf-route
    """

    ENDPOINT_URL: Final[str] = "/forms/chromium/convert/html"


class SyncHtmlToPdfRoute(_BaseHtmlToPdfRoute, _BaseChromiumConvertMixin, SyncBaseRoute):
    pass


class AsyncHtmlToPdfRoute(_BaseHtmlToPdfRoute, _BaseChromiumConvertMixin, AsyncBaseRoute):
    pass


class _BaseMarkdownToPdfRoute(_BaseIndexFilesMixin, _BaseChromiumConvertMixin):
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

        self._add_file_map(markdown_file)  # type: ignore[attr-defined]

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


class SyncMarkdownToPdfRoute(_BaseMarkdownToPdfRoute, SyncBaseRoute):
    pass


class AsyncMarkdownToPdfRoute(_BaseMarkdownToPdfRoute, AsyncBaseRoute):
    pass


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
    The common form field settings for the following route:
      - https://gotenberg.dev/docs/routes#screenshots-route
    """


class _BaseScreenshotFromUrlRoute(_BaseScreenShotSettingsMixin, _BaseUrlFormMixin):
    """
    Represents the Gotenberg route for capturing screenshots from URLs.

    Inherits from ScreenshotRoute and provides a specific URL-based method.

    https://gotenberg.dev/docs/routes#screenshots-route
    """

    ENDPOINT_URL: Final[str] = "/forms/chromium/screenshot/url"


class SyncScreenshotFromUrlRoute(_BaseScreenshotFromUrlRoute, SyncBaseRoute):
    pass


class AsyncScreenshotFromUrlRoute(_BaseScreenshotFromUrlRoute, AsyncBaseRoute):
    pass


class _BaseScreenshotFromHtmlRoute(_BaseIndexFilesMixin, _BaseScreenShotSettingsMixin):
    """
    Represents the Gotenberg route for capturing screenshots from HTML files.

    Inherits from _FileBasedRoute, _RouteWithResources, and ScreenshotRoute,
    combining functionalities for file-based operations, resource handling,
    and screenshot capture.

    https://gotenberg.dev/docs/routes#screenshots-route
    """

    ENDPOINT_URL: Final[str] = "/forms/chromium/screenshot/html"


class SyncScreenshotFromHtmlRoute(_BaseScreenshotFromHtmlRoute, SyncBaseRoute):
    pass


class AsyncScreenshotFromHtmlRoute(_BaseScreenshotFromHtmlRoute, AsyncBaseRoute):
    pass


class _BaseScreenshotFromMarkdownRoute(_BaseIndexFilesMixin, _BaseScreenShotSettingsMixin):
    """
    Represents the Gotenberg route for capturing screenshots from Markdown files.

    Inherits from _FileBasedRoute, _RouteWithResources, and ScreenshotRoute,
    combining functionalities for file-based operations, resource handling,
    and screenshot capture.

    https://gotenberg.dev/docs/routes#screenshots-route
    """

    ENDPOINT_URL: Final[str] = "/forms/chromium/screenshot/markdown"


class SyncScreenshotFromMarkdownRoute(_BaseScreenshotFromMarkdownRoute, SyncBaseRoute):
    pass


class AsyncScreenshotFromMarkdownRoute(_BaseScreenshotFromMarkdownRoute, AsyncBaseRoute):
    pass
