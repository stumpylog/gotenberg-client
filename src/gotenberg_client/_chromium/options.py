# SPDX-FileCopyrightText: 2025-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0

import dataclasses
import enum
import json
import logging
from datetime import datetime
from datetime import timedelta
from http import HTTPStatus
from pathlib import Path
from typing import Final
from typing import Literal
from typing import Optional
from typing import Union

from gotenberg_client._common.protocols import PageScaleType
from gotenberg_client._common.units import Measurement
from gotenberg_client._errors import InvalidKeywordError
from gotenberg_client._errors import InvalidPdfRevisionError
from gotenberg_client._errors import NegativeWaitDurationError
from gotenberg_client._types import Self
from gotenberg_client._utils import bool_to_form
from gotenberg_client.options import PdfAFormat
from gotenberg_client.options import TrappedStatus

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class PageSize:
    """
    Represents the dimensions of a page in Gotenberg.

    Attributes:
        width (Optional[Measurement]): The width of the page.
        height (Optional[Measurement]): The height of the page.
    """

    width: Optional[Measurement] = None
    height: Optional[Measurement] = None

    def to_form(self) -> dict[str, str]:
        """
        Converts this PageSize object to a dictionary suitable for form data.

        Returns:
            A dictionary containing the "paperWidth" and "paperHeight" keys with their corresponding values,
            if they are not None.
        """
        data: dict[str, str] = {}
        for field, name in [(self.width, "paperWidth"), (self.height, "paperHeight")]:
            if field:
                data.update(field.to_form(name))
        return data


@dataclasses.dataclass
class PageMarginsType:
    """
    Represents the margins for a page in Gotenberg.

    Attributes:
        top (Optional[Measurement]): The top margin of the page.
        bottom (Optional[Measurement]): The bottom margin of the page.
        left (Optional[Measurement]): The left margin of the page.
        right (Optional[Measurement]): The right margin of the page.
    """

    top: Optional[Measurement] = None
    bottom: Optional[Measurement] = None
    left: Optional[Measurement] = None
    right: Optional[Measurement] = None

    def to_form(self) -> dict[str, str]:
        """
        Converts this PageMarginsType object to a dictionary suitable for form data.

        Returns:
            A dictionary containing key-value pairs for each margin property with their corresponding Gotenberg names
            (e.g., "marginTop", "marginBottom", etc.) and the formatted margin values as strings.
        """

        form_data = {}
        margin_names = ["marginTop", "marginBottom", "marginLeft", "marginRight"]

        for margin, name in zip([self.top, self.bottom, self.left, self.right], margin_names):
            if margin:
                form_data.update(margin.to_form(name))

        return form_data


@enum.unique
class PageOrientation(enum.Enum):
    """
    Represents the possible orientations for a page in Gotenberg.
    """

    Landscape = enum.auto()
    Portrait = enum.auto()

    def to_form(self) -> dict[str, str]:
        """
        Converts this PageOrientation enum value to a dictionary suitable for form data.

        Returns:
            A dictionary containing a single key-value pair with the key "orientation"
            and the corresponding Gotenberg value ("landscape" or "portrait") as the value.
        """

        orientation_mapping: Final[dict[PageOrientation, dict[str, str]]] = {
            PageOrientation.Landscape: bool_to_form("landscape", True),
            PageOrientation.Portrait: bool_to_form("landscape", False),
        }

        return orientation_mapping[self]


@dataclasses.dataclass
class ChromiumCookieJar:
    name: str
    value: str
    domain: str
    path: Optional[str] = None
    secure: Optional[bool] = None
    http_only: Optional[bool] = None
    same_site: Optional[Literal["Strict", "Lax", "None"]] = None

    def asdict(self) -> dict[str, str]:
        data = {
            "name": self.name,
            "value": self.value,
            "domain": self.domain,
        }
        if self.path:
            data["path"] = self.path
        if self.secure:
            data.update(bool_to_form("secure", self.secure))
        if self.http_only:
            data.update(bool_to_form("httpOnly", self.http_only))
        if self.same_site:
            data["sameSite"] = self.same_site
        return data


class ChromiumPageProperties:
    """
    https://gotenberg.dev/docs/routes#page-properties-chromium
    """

    def use_single_page(self, *, use_single_page: bool = False) -> Self:
        self._form_data.update(bool_to_form("singlePage", use_single_page))
        return self

    def size(self, size: PageSize) -> Self:
        self._form_data.update(size.to_form())
        return self

    def margins(self, margins: PageMarginsType) -> Self:
        self._form_data.update(margins.to_form())
        return self

    #
    # CSS Page Size
    #
    def css_page_size(self, *, prefer_css_page_size: bool = False) -> Self:
        self._form_data.update(bool_to_form("preferCssPageSize", prefer_css_page_size))
        return self

    def prefer_css_page_size(self) -> Self:
        return self.css_page_size(prefer_css_page_size=True)

    def prefer_set_page_size(self) -> Self:
        return self.css_page_size(prefer_css_page_size=False)

    def generate_document_outline(self, *, generate_document_outline: bool = False) -> Self:
        self._form_data.update(bool_to_form("generateDocumentOutline", generate_document_outline))
        return self

    #
    # Background Graphic Control
    #
    def print_background(self, *, print_background: bool = False) -> Self:
        self._form_data.update(bool_to_form("printBackground", print_background))
        return self

    def background_graphics(self) -> Self:
        return self.print_background(print_background=True)

    def no_background_graphics(self) -> Self:
        return self.print_background(print_background=False)

    def omit_background(self, *, omit_background: bool = False) -> Self:
        self._form_data.update(bool_to_form("omitBackground", omit_background))
        return self

    def hide_background(self) -> Self:
        return self.omit_background(omit_background=True)

    def show_background(self) -> Self:
        return self.omit_background(omit_background=False)

    def orient(self, orient: PageOrientation) -> Self:
        """
        Sets the page orientation, either Landscape or portrait
        """
        self._form_data.update(orient.to_form())
        return self

    def scale(self, scale: PageScaleType) -> Self:
        self._form_data.update({"scale": str(scale)})
        return self

    def page_ranges(self, ranges: str) -> Self:
        """
        Sets the page range string, allowing either some range or just a
        few pages
        """
        self._form_data.update({"nativePageRanges": ranges})
        return self


class ChromiumHeaderFooter:
    """
    https://gotenberg.dev/docs/routes#header-footer-chromium
    """

    def header(self, header: Path) -> Self:
        self._add_file_map(header, name="header.html")
        return self

    def footer(self, footer: Path) -> Self:
        self._add_file_map(footer, name="footer.html")
        return self


class ChromiumRenderWait:
    """
    https://gotenberg.dev/docs/routes#wait-before-rendering-chromium
    """

    def render_wait(self, wait: timedelta) -> Self:
        time_s = wait.total_seconds()
        if time_s < 0:
            raise NegativeWaitDurationError
        self._form_data.update({"waitDelay": f"{time_s}s"})
        return self

    def render_expr(self, expr: str) -> Self:
        self._form_data.update({"waitForExpression": expr})
        return self


class ChromiumEmulatedMediaType:
    """
    https://gotenberg.dev/docs/routes#emulated-media-type-chromium
    """

    def media_type(self, media_type: Literal["print", "screen"]) -> Self:
        self._form_data.update({"emulatedMediaType": media_type})
        return self


class ChromiumCookies:
    """
    https://gotenberg.dev/docs/routes#cookies-chromium
    """

    def cookies(self, cookies: list[ChromiumCookieJar]) -> Self:
        cookie_dicts = [x.asdict() for x in cookies]
        self._form_data.update({"cookies": json.dumps(cookie_dicts)})
        return self


class ChromiumCustomHTTPHeader:
    """
    https://gotenberg.dev/docs/routes#custom-http-headers-chromium
    """

    def user_agent(self, agent: str) -> Self:
        self._form_data.update({"userAgent": agent})
        return self

    def headers(self, headers: dict[str, str]) -> Self:
        json_str = json.dumps(headers)
        self._form_data.update({"extraHttpHeaders": json_str})
        return self


class ChromiumCustomHttpStatusCodes:
    """
    https://gotenberg.dev/docs/routes#invalid-http-status-codes-chromium
    """

    def fail_on_codes(self, codes: list[HTTPStatus]) -> Self:
        self._form_data.update({"failOnHttpStatusCodes": ",".join(str(x) for x in codes)})
        return self

    def fail_on_resource_codes(self, codes: list[HTTPStatus]) -> Self:
        self._form_data.update({"failOnResourceHttpStatusCodes": ",".join(str(x) for x in codes)})
        return self


class ChromiumNetworkErrors:
    """
    https://gotenberg.dev/docs/routes#network-errors-chromium
    """

    def fail_on_resource_loading_failed(self, *, fail_on_resource_loading_failed: bool = False) -> Self:
        self._form_data.update(bool_to_form("failOnResourceLoadingFailed", fail_on_resource_loading_failed))
        return self


class ChromiumConsoleExceptions:
    """
    https://gotenberg.dev/docs/routes#console-exceptions-chromium
    """

    def fail_on_console_exception(self, *, fail_on_console_exception: bool = False) -> Self:
        self._form_data.update(bool_to_form("failOnConsoleExceptions", fail_on_console_exception))
        return self

    def fail_on_exceptions(self) -> Self:
        return self.fail_on_console_exception(fail_on_console_exception=True)

    def dont_fail_on_exceptions(self) -> Self:
        return self.fail_on_console_exception(fail_on_console_exception=False)


class ChromiumPerformanceMode:
    """
    https://gotenberg.dev/docs/routes#performance-mode-chromium
    """

    def performance_mode(self, *, use_performance_mode: bool) -> Self:
        self._form_data.update(bool_to_form("skipNetworkIdleEvent", use_performance_mode))
        return self

    def skip_network_idle(self) -> Self:
        return self.performance_mode(use_performance_mode=True)

    def use_network_idle(self) -> Self:
        return self.performance_mode(use_performance_mode=False)


class ChromiumSplit:
    """
    https://gotenberg.dev/docs/routes#split-chromium
    """

    def split_mode(self, mode: Literal["intervals", "pages"]) -> Self:
        self._form_data.update({"splitMode": mode})
        return self

    def split_span(self, span: str) -> Self:
        self._form_data.update({"splitSpan": span})
        return self

    def split_unify(self, *, split_unify: bool) -> Self:
        self._form_data.update(bool_to_form("splitUnify", split_unify))
        return self


class ChromiumPdfOptions:
    """
    https://gotenberg.dev/docs/routes#pdfa-chromium
    """

    def pdf_format(self, pdf_format: PdfAFormat) -> Self:
        """
        All routes provide the option to configure the output PDF as a
        PDF/A format
        """
        self._form_data.update(pdf_format.to_form())
        return self

    def universal_access(self, *, universal_access: bool) -> Self:
        self._form_data.update(bool_to_form("pdfua", universal_access))
        return self

    def enable_universal_access(self) -> Self:
        return self.universal_access(universal_access=True)

    def disable_universal_access(self) -> Self:
        return self.universal_access(universal_access=False)


class ChromiumMetadata:
    """
    https://gotenberg.dev/docs/routes#metadata-chromium
    """

    MIN_PDF_VERSION: Final[float] = 1.0
    MAX_PDF_VERSION: Final[float] = 2.0

    def metadata(
        self,
        author: Optional[str] = None,
        pdf_copyright: Optional[str] = None,
        creation_date: Optional[datetime] = None,
        creator: Optional[str] = None,
        keywords: Optional[list[str]] = None,
        marked: Optional[bool] = None,
        modification_date: Optional[datetime] = None,
        pdf_version: Optional[float] = None,
        producer: Optional[str] = None,
        subject: Optional[str] = None,
        title: Optional[str] = None,
        trapped: Optional[Union[bool, TrappedStatus]] = None,
    ) -> Self:
        """
        Sets PDF metadata for the document.

        Args:
            author: Document author name
            copyright: Copyright information
            creation_date: Document creation date (Note: Gotenberg will override this)
            creator: Name of the creating application
            keywords: List of keywords/tags for the document
            marked: Whether the PDF is marked for structure
            modification_date: Last modification date (Note: Gotenberg will override this)
            pdf_version: PDF version number (Note: Gotenberg will override this)
            producer: Name of the PDF producer
            subject: Document subject/description
            title: Document title
            trapped: Trapping status (bool or one of: 'True', 'False', 'Unknown')

        Returns:
            Self for method chaining

        Raises:
            InvalidPdfRevisionError: If the provided PDF revision is outside the valid range
            InvalidKeywordError: If any metadata keyword values are not allowed
            TypeError: If any metadata values have incorrect types
        """

        # Validate metadata values
        if pdf_version is not None and not (self.MIN_PDF_VERSION <= pdf_version <= self.MAX_PDF_VERSION):
            msg = "PDF version must be between 1.0 and 2.0"
            raise InvalidPdfRevisionError(msg)

        if trapped is not None and isinstance(trapped, bool):
            trapped = TrappedStatus.TRUE if trapped else TrappedStatus.FALSE

        if keywords is not None:
            if not all(isinstance(k, str) for k in keywords):
                raise InvalidKeywordError("All keywords must be strings")  # noqa: EM101, TRY003
            if any("," in k for k in keywords):
                raise InvalidKeywordError("Keywords cannot contain commas")  # noqa: EM101, TRY003

        # Get existing metadata if any
        existing_metadata: dict[str, Union[str, bool, float]] = {}
        if "metadata" in self._form_data:
            existing_metadata = json.loads(self._form_data["metadata"])

        # Convert validated metadata to dictionary
        metadata: dict[str, Union[str, bool, float]] = {}

        if author:
            metadata["Author"] = author
        if pdf_copyright:
            metadata["Copyright"] = pdf_copyright
        if creation_date:
            metadata["CreationDate"] = creation_date.isoformat()
        if creator:
            metadata["Creator"] = creator
        if keywords:
            metadata["Keywords"] = ", ".join(keywords)
        if marked is not None:
            metadata["Marked"] = marked
        if modification_date:
            metadata["ModDate"] = modification_date.isoformat()
        if pdf_version:
            metadata["PDFVersion"] = pdf_version
        if producer:
            metadata["Producer"] = producer
        if subject:
            metadata["Subject"] = subject
        if title:
            metadata["Title"] = title
        if trapped is not None:
            metadata["Trapped"] = trapped.value

        # Merge existing and new metadata
        if metadata:
            new_metadata: dict[str, Union[str, bool, float]] = {**existing_metadata, **metadata}
            self._form_data.update({"metadata": json.dumps(new_metadata)})

        return self


class ScreenshotSettings:
    """
    https://gotenberg.dev/docs/routes#screenshots-route
    """

    _QUALITY_MAX: Final[int] = 100
    _QUALITY_MIN: Final[int] = 0

    def width(self, width: int) -> Self:
        self._form_data.update({"width": str(width)})
        return self

    def height(self, height: int) -> Self:
        self._form_data.update({"height": str(height)})
        return self

    def clip(self, *, clip: bool) -> Self:
        self._form_data.update(bool_to_form("clip", clip))
        return self

    def clip_to_dimensions(self) -> Self:
        return self.clip(clip=True)

    def no_clip_to_dimensions(self) -> Self:
        return self.clip(clip=False)

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

    def omit_background(self, *, omit_background: bool = False) -> Self:
        self._form_data.update(bool_to_form("omitBackground", omit_background))
        return self

    def hide_background(self) -> Self:
        return self.omit_background(omit_background=True)

    def show_background(self) -> Self:
        return self.omit_background(omit_background=False)

    def image_optimize(self, *, optimize_for_speed: bool = False) -> Self:
        self._form_data.update(bool_to_form("optimizeForSpeed", optimize_for_speed))
        return self

    def image_optimize_for_speed(self) -> Self:
        """
        Sets the optimization mode to prioritize speed.

        Returns:
            ScreenshotRoute: This object itself for method chaining.
        """
        return self.image_optimize(optimize_for_speed=True)

    def image_optimize_for_quality(self) -> Self:
        """
        Sets the optimization mode to prioritize size reduction.

        Returns:
            ScreenshotRoute: This object itself for method chaining.
        """
        return self.image_optimize(optimize_for_speed=False)
