# SPDX-FileCopyrightText: 2023-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0

import sys

if sys.version_info >= (3, 11):  # pragma: no cover
    from enum import StrEnum
    from typing import Self
else:  # pragma: no cover
    import enum

    from typing_extensions import Self  # noqa: F401

    class StrEnum(str, enum.Enum):
        """
        Python 3.10 or older compatibility for string based enums
        """
