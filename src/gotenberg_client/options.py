# SPDX-FileCopyrightText: 2023-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
import dataclasses
import enum
from typing import Dict
from typing import Final
from typing import Optional
from warnings import warn

from gotenberg_client._types import MarginSizeType
from gotenberg_client._types import PageSizeType
from gotenberg_client._utils import optional_to_form


@enum.unique
class PdfAFormat(enum.Enum):
    A1a = enum.auto()
    A2b = enum.auto()
    A3b = enum.auto()

    def to_form(self) -> Dict[str, str]:
        format_name = None
        if self.value == PdfAFormat.A1a.value:  # pragma: no cover
            format_name = "PDF/A-1a"
            warn("PDF Format PDF/A-1a is deprecated", DeprecationWarning, stacklevel=2)
            return {}
        elif self.value == PdfAFormat.A2b.value:
            format_name = "PDF/A-2b"
        elif self.value == PdfAFormat.A3b.value:
            format_name = "PDF/A-3b"
        if format_name is not None:
            return {"pdfa": format_name}
        else:  # pragma: no cover
            raise NotImplementedError(self.value)


@enum.unique
class PageOrientation(enum.Enum):
    Landscape = enum.auto()
    Portrait = enum.auto()

    def to_form(self) -> Dict[str, str]:
        if self.value == PageOrientation.Landscape.value:
            return {"landscape": "true"}
        elif self.value == PageOrientation.Portrait.value:
            return {"landscape": "false"}
        else:  # pragma: no cover
            raise NotImplementedError(self.value)


@dataclasses.dataclass
class PageSize:
    width: Optional[PageSizeType] = None
    height: Optional[PageSizeType] = None

    def to_form(self) -> Dict[str, str]:
        data = optional_to_form(self.width, "paperWidth")
        data.update(optional_to_form(self.height, "paperHeight"))
        return data


# Define common paper sizes as shortcuts
A0: Final = PageSize(width=33.1, height=46.8)
A1: Final = PageSize(width=23.4, height=33.1)
A2: Final = PageSize(width=16.54, height=23.4)
A3: Final = PageSize(width=11.7, height=16.54)
A4: Final = PageSize(width=8.5, height=11)
A5: Final = PageSize(width=5.83, height=8.27)
A6: Final = PageSize(width=4.13, height=5.83)
Letter = A4
Legal: Final = PageSize(width=8.5, height=14)
Tabloid: Final = PageSize(width=11, height=17)
Ledge: Final = PageSize(width=17, height=11)


class MarginUnitType(str, enum.Enum):
    Undefined = "none"
    Points = "pt"
    Pixels = "px"
    Inches = "in"
    Millimeters = "mm"
    Centimeters = "cm"
    Percent = "pc"


@dataclasses.dataclass
class MarginType:
    value: MarginSizeType
    unit: MarginUnitType = MarginUnitType.Undefined


@dataclasses.dataclass
class PageMarginsType:
    top: Optional[MarginType] = None
    bottom: Optional[MarginType] = None
    left: Optional[MarginType] = None
    right: Optional[MarginType] = None

    def to_form(self) -> Dict[str, str]:
        form_data = {}
        values: list[tuple[MarginType | None, str]] = [
            (self.top, "marginTop"),
            (self.bottom, "marginBottom"),
            (self.left, "marginLeft"),
            (self.right, "marginRight"),
        ]
        for attr, name in values:
            if attr is not None:
                if attr.unit == MarginUnitType.Undefined:
                    form_data.update(optional_to_form(attr.value, name))
                else:
                    # mypy claims the string is of type "Any"
                    form_data.update(optional_to_form(f"{attr.value}{attr.unit.value}", name))  # type: ignore[misc]

        return form_data


@enum.unique
class EmulatedMediaType(str, enum.Enum):
    Print = enum.auto()
    Screen = enum.auto()

    def to_form(self) -> Dict[str, str]:
        if self.value == EmulatedMediaType.Print.value:
            return {"emulatedMediaType": "print"}
        elif self.value == EmulatedMediaType.Screen.value:
            return {"emulatedMediaType": "screen"}
        else:  # pragma: no cover
            raise NotImplementedError(self.value)
