# SPDX-FileCopyrightText: 2025-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0

from typing import Final

from gotenberg_client.options import Measurement
from gotenberg_client.options import MeasurementUnitType
from gotenberg_client.options import PageSize

# Define common paper sizes as shortcuts
A0: Final = PageSize(
    width=Measurement(33.1, MeasurementUnitType.Inches),
    height=Measurement(46.8, MeasurementUnitType.Inches),
)
A1: Final = PageSize(
    width=Measurement(23.4, MeasurementUnitType.Inches),
    height=Measurement(33.1, MeasurementUnitType.Inches),
)
A2: Final = PageSize(
    width=Measurement(16.54, MeasurementUnitType.Inches),
    height=Measurement(23.4, MeasurementUnitType.Inches),
)
A3: Final = PageSize(
    width=Measurement(11.7, MeasurementUnitType.Inches),
    height=Measurement(16.54, MeasurementUnitType.Inches),
)
A4: Final = PageSize(
    width=Measurement(8.27, MeasurementUnitType.Inches),
    height=Measurement(11.7, MeasurementUnitType.Inches),
)
A5: Final = PageSize(
    width=Measurement(5.83, MeasurementUnitType.Inches),
    height=Measurement(8.27, MeasurementUnitType.Inches),
)
A6: Final = PageSize(
    width=Measurement(4.13, MeasurementUnitType.Inches),
    height=Measurement(5.83, MeasurementUnitType.Inches),
)
Letter: Final = PageSize(
    width=Measurement(8.5, MeasurementUnitType.Inches),
    height=Measurement(11, MeasurementUnitType.Inches),
)
Legal: Final = PageSize(
    width=Measurement(8.5, MeasurementUnitType.Inches),
    height=Measurement(14, MeasurementUnitType.Inches),
)
Tabloid: Final = PageSize(
    width=Measurement(11, MeasurementUnitType.Inches),
    height=Measurement(17, MeasurementUnitType.Inches),
)
Ledge: Final = PageSize(
    width=Measurement(17, MeasurementUnitType.Inches),
    height=Measurement(11, MeasurementUnitType.Inches),
)
