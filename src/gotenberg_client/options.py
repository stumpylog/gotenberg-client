# SPDX-FileCopyrightText: 2023-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
import dataclasses
import enum
import json
from typing import Final
from typing import Literal
from typing import TypedDict

from gotenberg_client._typing_compat import StrEnum
from gotenberg_client._utils import bool_to_form
from gotenberg_client._utils import optional_to_form


class _CookieJarDictRequired(TypedDict):
    name: str
    value: str
    domain: str


class CookieJarDict(_CookieJarDictRequired, total=False):
    """TypedDict for the return value of :meth:`CookieJar.asdict`."""

    path: str
    secure: bool
    httpOnly: bool
    sameSite: str


@dataclasses.dataclass(slots=True)
class CookieJar:
    """
    A cookie to send with Chromium requests.

    See https://gotenberg.dev/docs/routes#cookies-chromium

    Attributes:
        name (str): The cookie name.
        value (str): The cookie value.
        domain (str): The domain the cookie applies to.
        path (str | None): The URL path the cookie applies to.
        secure (bool | None): Whether the cookie is only sent over HTTPS.
        http_only (bool | None): Whether the cookie is inaccessible to JavaScript.
        same_site (str | None): SameSite policy — ``"Strict"``, ``"Lax"``, or ``"None"``.
    """

    name: str
    value: str
    domain: str
    path: str | None = None
    secure: bool | None = None
    http_only: bool | None = None
    same_site: Literal["Strict", "Lax", "None"] | None = None

    def asdict(self) -> CookieJarDict:
        data: CookieJarDict = {
            "name": self.name,
            "value": self.value,
            "domain": self.domain,
        }
        if self.path:
            data["path"] = self.path
        if self.secure:
            data["secure"] = self.secure
        if self.http_only:
            data["httpOnly"] = self.http_only
        if self.same_site:
            data["sameSite"] = self.same_site
        return data


@enum.unique
class MeasurementUnitType(StrEnum):
    """
    Represents the different units of measurement for sizes.

    Attributes:
        Undefined: Indicates that no unit is specified. (Gotenberg will use inches )
        Points: Represents points (1/72 of an inch).
        Pixels: Represents pixels.
        Inches: Represents inches.
        Millimeters: Represents millimeters.
        Centimeters: Represents centimeters.
        Percent: Represents a percentage relative to the page size.
    """

    Undefined = "none"
    Points = "pt"
    Pixels = "px"
    Inches = "in"
    Millimeters = "mm"
    Centimeters = "cm"
    Percent = "pc"


@dataclasses.dataclass(slots=True)
class Measurement:
    """
    Represents a value with a specified unit of measurement.

    Attributes:
        value (float or int): The numerical value of the measurement.
        unit (MeasurementUnitType): The unit of measurement for the measurement.
    """

    value: float | int
    unit: MeasurementUnitType = MeasurementUnitType.Undefined

    def to_form(self, name: str) -> dict[str, str]:
        """
        Converts this Measurement object to a dictionary suitable for form data.

        Returns:
            A dictionary containing the name with the formatted measurement value, according to the
            defined units of the measurement
        """

        if self.unit == MeasurementUnitType.Undefined:
            return optional_to_form(self.value, name)
        else:
            # Fail to see how mypy thinks this is "Any"
            return optional_to_form(f"{self.value}{self.unit.value}", name)  # type: ignore[misc]


@enum.unique
class PdfAFormat(enum.Enum):
    """
    Represents different PDF/A archival formats supported by Gotenberg.

    Documentation:
      - https://gotenberg.dev/docs/routes#pdfa-chromium
      - https://gotenberg.dev/docs/routes#pdfa-libreoffice
      - https://gotenberg.dev/docs/routes#convert-into-pdfa--pdfua-route
      - https://gotenberg.dev/docs/routes#merge-pdfs-route

    Attributes:
        A1a: PDF/A-1a (deprecated).
        A1b: PDF/A-1b.
        A2b: PDF/A-2b.
        A3b: PDF/A-3b.
    """

    A1a = enum.auto()
    A1b = enum.auto()
    A2b = enum.auto()
    A3b = enum.auto()

    def to_form(self) -> dict[str, str]:
        """
        Converts this PdfAFormat enum value to a dictionary suitable for form data.

        Returns:
            A dictionary containing a single key-value pair with the key "pdfa" and the corresponding format name
            as the value.
            If the format is not supported (e.g., A1a), raises an Exception.
        """

        format_mapping: Final[dict[PdfAFormat, str]] = {
            PdfAFormat.A1a: "PDF/A-1a",  # Include deprecated format with warning
            PdfAFormat.A1b: "PDF/A-1b",
            PdfAFormat.A2b: "PDF/A-2b",
            PdfAFormat.A3b: "PDF/A-3b",
        }

        format_name = format_mapping[self]
        # Warn about deprecated format usage (ideally move outside this method)
        if self is PdfAFormat.A1a:
            import warnings  # noqa: PLC0415

            warnings.warn(
                "PDF Format PDF/A-1a is deprecated",
                DeprecationWarning,
                stacklevel=2,
            )
            return {}
        return {"pdfa": format_name}


@enum.unique
class PageOrientation(enum.Enum):
    """
    Represents the possible orientations for a page in Gotenberg.

    Attributes:
        Landscape: Horizontal page orientation.
        Portrait: Vertical page orientation.
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


@dataclasses.dataclass(slots=True)
class PageSize:
    """
    Represents the dimensions of a page in Gotenberg.

    Attributes:
        width (Optional[Measurement]): The width of the page.
        height (Optional[Measurement]): The height of the page.
    """

    width: Measurement | None = None
    height: Measurement | None = None

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


@dataclasses.dataclass(slots=True)
class PageMarginsType:
    """
    Represents the margins for a page in Gotenberg.

    Attributes:
        top (Optional[Measurement]): The top margin of the page.
        bottom (Optional[Measurement]): The bottom margin of the page.
        left (Optional[Measurement]): The left margin of the page.
        right (Optional[Measurement]): The right margin of the page.
    """

    top: Measurement | None = None
    bottom: Measurement | None = None
    left: Measurement | None = None
    right: Measurement | None = None

    def to_form(self) -> dict[str, str]:
        """
        Converts this PageMarginsType object to a dictionary suitable for form data.

        Returns:
            A dictionary containing key-value pairs for each margin property with their corresponding Gotenberg names
            (e.g., "marginTop", "marginBottom", etc.) and the formatted margin values as strings.
        """

        form_data = {}
        margin_names = ["marginTop", "marginBottom", "marginLeft", "marginRight"]

        for margin, name in zip([self.top, self.bottom, self.left, self.right], margin_names, strict=True):
            if margin:
                form_data.update(margin.to_form(name))

        return form_data


@enum.unique
class TrappedStatus(StrEnum):
    """
    Valid values for the PDF ``Trapped`` metadata key.

    Attributes:
        TRUE: Trapping has been applied to the document.
        FALSE: Trapping has not been applied.
        UNKNOWN: Trapping status is unknown.
    """

    TRUE = "True"
    FALSE = "False"
    UNKNOWN = "Unknown"


@enum.unique
class WatermarkStampSource(str, enum.Enum):
    """
    Source type for watermark or stamp content.

    Attributes:
        Text: Watermark/stamp content is plain text.
        Image: Watermark/stamp content is an image file.
        Pdf: Watermark/stamp content is a PDF file.
    """

    Text = "text"
    Image = "image"
    Pdf = "pdf"


@enum.unique
class RotateAngle(str, enum.Enum):
    """
    Valid rotation angles in degrees.

    Attributes:
        Clockwise90: Rotate 90 degrees clockwise.
        Clockwise180: Rotate 180 degrees.
        Clockwise270: Rotate 270 degrees clockwise (90 degrees counter-clockwise).
    """

    Clockwise90 = "90"
    Clockwise180 = "180"
    Clockwise270 = "270"


@dataclasses.dataclass(slots=True)
class WatermarkStampOptions:
    """
    Advanced options for watermark/stamp rendering.
    Field names and semantics depend on the configured PDF engine (pdfcpu by default).
    See https://gotenberg.dev/docs/manipulate-pdfs/watermark-pdfs for details.

    Attributes:
        font (str | None): Font name for text watermarks/stamps.
        points (int | None): Font size in points.
        color (str | None): Font color as a hex string (e.g. ``"#FF0000"``).
        rotation (int | None): Rotation angle in degrees.
        opacity (float | None): Opacity between 0.0 (transparent) and 1.0 (opaque).
        scale (float | None): Scale factor relative to the page size.
    """

    font: str | None = None
    points: int | None = None
    color: str | None = None
    rotation: int | None = None
    opacity: float | None = None
    scale: float | None = None

    def to_json(self) -> str:
        data: dict[str, str | int | float] = {}
        if self.font is not None:
            data["font"] = self.font
        if self.points is not None:
            data["points"] = self.points
        if self.color is not None:
            data["color"] = self.color
        if self.rotation is not None:
            data["rotation"] = self.rotation
        if self.opacity is not None:
            data["opacity"] = self.opacity
        if self.scale is not None:
            data["scale"] = self.scale
        return json.dumps(data)


@enum.unique
class InitialView(enum.IntEnum):
    """
    Controls which panel is open in the PDF viewer on initial display.

    Used with the LibreOffice route's `initial_view()` method.

    Attributes:
        NONE: No panel open (default).
        OUTLINE: Show document outline/bookmarks panel.
        THUMBNAILS: Show page thumbnails panel.
    """

    NONE = 0
    OUTLINE = 1
    THUMBNAILS = 2


@enum.unique
class MagnificationOption(enum.IntEnum):
    """
    Controls the initial magnification/zoom level used by the PDF viewer.

    Used with the LibreOffice route's `magnification()` method.

    Attributes:
        DEFAULT: Use the viewer default.
        FIT_PAGE: Fit the entire page in the window.
        FIT_WIDTH: Fit the page width in the window.
        FIT_HEIGHT: Fit the page height in the window.
        FIT_BOX: Fit the bounding box of the page in the window.
    """

    DEFAULT = 0
    FIT_PAGE = 1
    FIT_WIDTH = 2
    FIT_HEIGHT = 3
    FIT_BOX = 4


@enum.unique
class PageLayout(enum.IntEnum):
    """
    Controls the page layout mode used by the PDF viewer on initial display.

    Used with the LibreOffice route's `page_layout()` method.

    Attributes:
        DEFAULT: Use the viewer default.
        SINGLE_PAGE: Display one page at a time.
        CONTINUOUS: Display pages in a continuous vertical column.
        TWO_COLUMNS: Display two pages side by side.
    """

    DEFAULT = 0
    SINGLE_PAGE = 1
    CONTINUOUS = 2
    TWO_COLUMNS = 3


class _DownloadFromUrlDictRequired(TypedDict):
    url: str
    embedded: bool


class DownloadFromUrlDict(_DownloadFromUrlDictRequired, total=False):
    """TypedDict for the return value of :meth:`DownloadFromUrl.asdict`."""

    extraHttpHeaders: dict[str, str]
    field: str


@dataclasses.dataclass(slots=True)
class DownloadFromUrl:
    """
    Instructs Gotenberg to fetch a file from a URL instead of a direct upload.
    See https://gotenberg.dev/docs/webhook-download for details.

    Attributes:
        url (str): URL of the file. The remote server must return a ``Content-Disposition``
            header with a ``filename`` parameter.
        extra_http_headers (dict[str, str] | None): Extra HTTP headers to send when fetching
            this URL.
        embedded (bool): Whether to embed the file (legacy; prefer ``field``).
        field (str | None): Routes the downloaded file to a specific form field: ``"embedded"``,
            ``"watermark"``, or ``"stamp"``. Takes precedence over ``embedded`` when set.
    """

    url: str
    extra_http_headers: dict[str, str] | None = None
    embedded: bool = False
    field: str | None = None

    def asdict(self) -> DownloadFromUrlDict:
        data: DownloadFromUrlDict = {"url": self.url, "embedded": self.embedded}
        if self.extra_http_headers:
            data["extraHttpHeaders"] = self.extra_http_headers
        if self.field is not None:
            data["field"] = self.field
        return data
