# SPDX-FileCopyrightText: 2023-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
import dataclasses
import enum
from typing import Final
from typing import Literal
from typing import Optional
from typing import Union

from gotenberg_client._utils import bool_to_form
from gotenberg_client._utils import optional_to_form


@dataclasses.dataclass
class CookieJar:
    """
    https://gotenberg.dev/docs/routes#cookies-chromium
    """

    name: str
    value: str
    domain: str
    path: Optional[str] = None
    secure: Optional[bool] = None
    http_only: Optional[bool] = None
    same_site: Optional[Literal["Strict", "Lax", "None"]] = None

    def asdict(self) -> dict[str, Union[str, bool]]:
        data: dict[str, Union[str, bool]] = {
            "name": self.name,
            "value": self.value,
            "domain": self.domain,
        }
        if self.path:
            data["path"] = self.path
        if self.secure:
            data.update({"secure": self.secure})
        if self.http_only:
            data.update({"httpOnly": self.http_only})
        if self.same_site:
            data["sameSite"] = self.same_site
        return data


@enum.unique
class MeasurementUnitType(str, enum.Enum):
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


@dataclasses.dataclass
class Measurement:
    """
    Represents a value with a specified unit of measurement.

    Attributes:
        value (float or int): The numerical value of the measurement.
        unit (UnitType): The unit of measurement for the measurement.
    """

    value: Union[float, int]
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
    """

    A1a = enum.auto()
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
            PdfAFormat.A2b: "PDF/A-2b",
            PdfAFormat.A3b: "PDF/A-3b",
        }

        format_name = format_mapping[self]
        # Warn about deprecated format usage (ideally move outside this method)
        if self is PdfAFormat.A1a:
            import warnings

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
class TrappedStatus(str, enum.Enum):
    """Enum for valid trapped status values."""

    TRUE = "True"
    FALSE = "False"
    UNKNOWN = "Unknown"
