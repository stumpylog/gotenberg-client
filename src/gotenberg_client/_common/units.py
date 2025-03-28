# SPDX-FileCopyrightText: 2025-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
from datetime import timedelta
from http import HTTPMethod
from typing import TYPE_CHECKING
from typing import Literal
from typing import TypeVar
from typing import Union

if TYPE_CHECKING:
    from httpx import AsyncClient
    from httpx import Client

    from gotenberg_client._base import AsyncBaseRoute
    from gotenberg_client._base import SyncBaseRoute

MeasurementValueType = Union[float, int]
PageScaleType = Union[float, int]
WaitTimeType = Union[float, int, timedelta]
FormFieldType = Union[bool, int, float, str]
PageSizeType = Union[float, int]
MarginSizeType = Union[float, int]
HttpMethodsType = Literal[HTTPMethod.POST, HTTPMethod.PATCH, HTTPMethod.PUT]

ClientT = TypeVar("ClientT", bound="Client | AsyncClient")


SyncOrAsyncRouteT = TypeVar("SyncOrAsyncRouteT", bound="SyncBaseRoute | AsyncBaseRoute")
