# SPDX-FileCopyrightText: 2023-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
import dataclasses
import enum
from typing import Final
from typing import Optional

from gotenberg_client._types import MarginSizeType
from gotenberg_client._types import PageSizeType
from gotenberg_client._utils import optional_to_form


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

    A1a = enum.auto()  # Deprecated format (warning included)
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
        if self is PdfAFormat.A1a:  # pragma: no cover
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
            PageOrientation.Landscape: {"landscape": "true"},
            PageOrientation.Portrait: {"landscape": "false"},
        }

        return orientation_mapping[self]


@dataclasses.dataclass
class PageSize:
    """
    Represents the dimensions of a page in Gotenberg.

    Attributes:
        width (Optional[PageSizeType]): The width of the page.
        height (Optional[PageSizeType]): The height of the page.
    """

    width: Optional[PageSizeType] = None
    height: Optional[PageSizeType] = None

    def to_form(self) -> dict[str, str]:
        """
        Converts this PageSize object to a dictionary suitable for form data.

        Returns:
            A dictionary containing the "paperWidth" and "paperHeight" keys with their corresponding values,
            if they are not None.
        """
        data = optional_to_form(self.width, "paperWidth")
        data.update(optional_to_form(self.height, "paperHeight"))
        return data


# Define common paper sizes as shortcuts
A0: Final = PageSize(width=33.1, height=46.8)
A1: Final = PageSize(width=23.4, height=33.1)
A2: Final = PageSize(width=16.54, height=23.4)
A3: Final = PageSize(width=11.7, height=16.54)
A4: Final = PageSize(width=8.27, height=11.7)
A5: Final = PageSize(width=5.83, height=8.27)
A6: Final = PageSize(width=4.13, height=5.83)
Letter: Final = PageSize(width=8.5, height=11)
Legal: Final = PageSize(width=8.5, height=14)
Tabloid: Final = PageSize(width=11, height=17)
Ledge: Final = PageSize(width=17, height=11)


class MarginUnitType(str, enum.Enum):
    """
    Represents the different units of measurement for page margins.

    Attributes:
        Undefined: Indicates that no unit is specified.
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
class MarginType:
    """
    Represents a margin value with a specified unit of measurement.

    Attributes:
        value (MarginSizeType): The numerical value of the margin.
        unit (MarginUnitType): The unit of measurement for the margin.
    """

    value: MarginSizeType
    unit: MarginUnitType = MarginUnitType.Undefined

    def to_form(self, name: str) -> dict[str, str]:
        """
        Converts this MarginType object to a dictionary suitable for form data.

        Returns:
            A dictionary containing the "margin" key with the formatted margin value as the value.
            The margin value is formatted as a string with the unit appended.
        """

        if self.unit == MarginUnitType.Undefined:
            return optional_to_form(self.value, name)
        else:
            # Fail to see how mypy thinks this is "Any"
            return optional_to_form(f"{self.value}{self.unit.value}", name)  # type: ignore[misc]


@dataclasses.dataclass
class PageMarginsType:
    """
    Represents the margins for a page in Gotenberg.

    Attributes:
        top (Optional[MarginType]): The top margin of the page.
        bottom (Optional[MarginType]): The bottom margin of the page.
        left (Optional[MarginType]): The left margin of the page.
        right (Optional[MarginType]): The right margin of the page.
    """

    top: Optional[MarginType] = None
    bottom: Optional[MarginType] = None
    left: Optional[MarginType] = None
    right: Optional[MarginType] = None

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
class EmulatedMediaType(str, enum.Enum):
    """
    Represents the different media types Gotenberg can emulate for rendering.

    Attributes:
        Print: Emulates print media for print-optimized output.
        Screen: Emulates screen media for displaying on screens.
    """

    Print = enum.auto()
    Screen = enum.auto()

    def to_form(self) -> dict[str, str]:
        """
        Converts this EmulatedMediaType enum value to a dictionary suitable for form data.

        Returns:
            A dictionary containing a single key-value pair with the key "emulatedMediaType"
            and the corresponding Gotenberg value ("print" or "screen") as the value.
        """

        return {"emulatedMediaType": self.name.lower()}


@enum.unique
class TrappedStatus(str, enum.Enum):
    """Enum for valid trapped status values."""

    TRUE = "True"
    FALSE = "False"
    UNKNOWN = "Unknown"
