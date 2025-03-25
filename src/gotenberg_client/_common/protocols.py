# SPDX-FileCopyrightText: 2025-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
from pathlib import Path
from typing import Optional
from typing import Protocol
from typing import Union

MeasurementValueType = Union[float, int]
PageScaleType = Union[float, int]
WaitTimeType = Union[float, int]


class HasFormDataFieldProtocol(Protocol):
    """
    Mixin classes may inherit this Protocol to assure mypy they do what
    """

    _form_data: dict[str, str]


class HasFileMapMethodProtocol(Protocol):
    def _add_file_map(self, filepath: Path, *, name: Optional[str] = None) -> None: ...
