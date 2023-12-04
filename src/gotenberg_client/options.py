# SPDX-FileCopyrightText: 2023-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
import dataclasses
import enum
from typing import Dict
from typing import Final
from typing import Optional
from typing import Union

from gotenberg_client._utils import optional_to_form


@enum.unique
class PdfAFormat(enum.Enum):
    A1a = enum.auto()
    A2b = enum.auto()
    A3b = enum.auto()

    def to_form(self) -> Dict[str, str]:
        format_name = None
        if self.value == PdfAFormat.A1a.value:
            format_name = "PDF/A-1a"
        elif self.value == PdfAFormat.A2b.value:
            format_name = "PDF/A-2b"
        elif self.value == PdfAFormat.A3b.value:
            format_name = "PDF/A-3b"
        if format_name is not None:
            return {"pdfa": format_name, "pdfFormat": format_name}
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
    width: Optional[Union[float, int]] = None
    height: Optional[Union[float, int]] = None

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


@dataclasses.dataclass
class Margin:
    top: Optional[Union[float, int]] = None
    bottom: Optional[Union[float, int]] = None
    left: Optional[Union[float, int]] = None
    right: Optional[Union[float, int]] = None

    def to_form(self) -> Dict[str, str]:
        data = optional_to_form(self.top, "marginTop")
        data.update(optional_to_form(self.bottom, "marginBottom"))
        data.update(optional_to_form(self.left, "marginLeft"))
        data.update(optional_to_form(self.right, "marginRight"))
        return data


Gotenberg_Default_Margins: Final = Margin(0.39, 0.39, 0.39, 0.39)
Word_Default_Margins: Final = Margin(top=1.0, bottom=1.0, left=1.0, right=1.0)
Word_Narrow_Margins: Final = Margin(top=0.5, bottom=0.5, left=0.5, right=0.5)


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
