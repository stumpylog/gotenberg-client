# SPDX-FileCopyrightText: 2025-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
import dataclasses
import enum

from gotenberg_client._common.protocols import MeasurementValueType
from gotenberg_client._utils import optional_to_form


class UnitType(str, enum.Enum):
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
        value (MeasurementValueType): The numerical value of the measurement.
        unit (UnitType): The unit of measurement for the measurement.
    """

    value: MeasurementValueType
    unit: UnitType = UnitType.Undefined

    def to_form(self, name: str) -> dict[str, str]:
        """
        Converts this Measurement object to a dictionary suitable for form data.

        Returns:
            A dictionary containing the name with the formatted measurement value, according to the
            defined units of the measurement
        """

        if self.unit == UnitType.Undefined:
            return optional_to_form(self.value, name)
        else:
            # Fail to see how mypy thinks this is "Any"
            return optional_to_form(f"{self.value}{self.unit.value}", name)  # type: ignore[misc]
