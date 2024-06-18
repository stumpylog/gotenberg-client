# SPDX-FileCopyrightText: 2023-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0

import sys
from typing import Literal
from typing import Union

if sys.version_info >= (3, 11):  # pragma: no cover
    from typing import Self
else:  # pragma: no cover
    from typing_extensions import Self  # noqa: F401

WaitTimeType = Union[float, int]
FormFieldType = Union[bool, int, float, str]
PageSizeType = Union[float, int]
MarginSizeType = Union[float, int]
PageScaleType = Union[float, int]
HttpMethodsType = Literal["POST", "PATCH", "PUT"]
