# SPDX-FileCopyrightText: 2023-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
import dataclasses
import datetime
import enum
import re
from contextlib import AbstractAsyncContextManager
from contextlib import AbstractContextManager
from types import TracebackType
from typing import Final
from typing import Optional
from typing import TypedDict
from typing import no_type_check

from gotenberg_client._base import AsyncBaseApi
from gotenberg_client._base import SyncBaseApi

_TIME_RE = re.compile(
    r"(?P<year>\d{4})-"
    r"(?P<month>\d{2})-"
    r"(?P<day>\d{2})"
    r"[ tT]"
    r"(?P<hour>\d{2}):"
    r"(?P<minute>\d{2}):"
    r"(?P<second>\d{2})"
    r"(?P<fractional_seconds>\.\d+)?"
    r"(?P<timezone>[zZ]|[+-]\d{2}:\d{2})?",
)


class _ModuleStatusType(TypedDict):
    status: str
    timestamp: str


class _AllModulesType(TypedDict):
    chromium: _ModuleStatusType
    uno: _ModuleStatusType


class _HealthCheckApiResponseType(TypedDict):
    status: str
    details: _AllModulesType


@enum.unique
class StatusOptions(str, enum.Enum):
    Up = "up"
    Down = "down"


@enum.unique
class ModuleOptions(str, enum.Enum):
    Chromium = "chromium"
    Uno = "uno"


@dataclasses.dataclass
class ModuleStatus:
    status: StatusOptions
    timestamp: datetime.datetime


class HealthStatus:
    """
    Decodes the JSON health response into Python types
    """

    def __init__(self, data: _HealthCheckApiResponseType) -> None:
        self.data = data
        self.overall = StatusOptions(data["status"])

        self.chromium: Optional[ModuleStatus] = None
        if ModuleOptions.Chromium.value in self.data["details"]:
            self.chromium = self._extract_status(ModuleOptions.Chromium)

        self.uno: Optional[ModuleStatus] = None
        if ModuleOptions.Uno.value in self.data["details"]:  # pragma: no cover
            self.uno = self._extract_status(ModuleOptions.Uno)

    def _extract_status(self, module: ModuleOptions) -> ModuleStatus:
        status = StatusOptions(self.data["details"][module.value]["status"])

        # mypy is quite wrong here, it's clearly marked as a datetime.datetime, not Any
        # but ...
        timestamp: datetime.datetime = self._extract_datetime(self.data["details"][module.value]["timestamp"])
        return ModuleStatus(status, timestamp)

    @staticmethod
    @no_type_check
    def _extract_datetime(timestamp: str) -> datetime.datetime:
        m = _TIME_RE.match(timestamp)
        if not m:  # pragma: no cover
            msg = f"Unable to parse {timestamp}"
            raise ValueError(msg)

        (year, month, day, hour, minute, second, frac_sec, timezone_str) = m.groups()

        microseconds = int(float(frac_sec) * 1000000.0) if frac_sec is not None else 0
        tzinfo = None
        if timezone_str is not None:
            if timezone_str.lower() == "z":
                tzinfo = datetime.timezone.utc
            else:  # pragma: no cover
                multi = -1 if timezone_str[0:1] == "-" else 1
                hours = int(timezone_str[1:3])
                minutes = int(timezone_str[4:])
                delta = datetime.timedelta(hours=hours, minutes=minutes) * multi
                tzinfo = datetime.timezone(delta)

        return datetime.datetime(
            year=int(year),
            month=int(month),
            day=int(day),
            hour=int(hour),
            minute=int(minute),
            second=int(second),
            microsecond=microseconds,
            tzinfo=tzinfo,
        )


class _BaseHealthCheckApi:
    """
    Provides the route for health checks in the Gotenberg API.

    This class encapsulates the functionality to perform health checks on the Gotenberg service.
    It inherits from BaseApi, presumably providing common API functionality.

    For more information on Gotenberg's health check endpoint, see:
    https://gotenberg.dev/docs/routes#health

    """

    HEALTH_ENDPOINT: Final[str] = "/health"


class SyncHealthCheckApi(_BaseHealthCheckApi, AbstractContextManager, SyncBaseApi):
    """
    Provides the route for health checks in the Gotenberg API.

    This class encapsulates the functionality to perform health checks on the Gotenberg service.
    It inherits from BaseApi, presumably providing common API functionality.

    For more information on Gotenberg's health check endpoint, see:
    https://gotenberg.dev/docs/routes#health

    """

    def health(self) -> HealthStatus:
        """
        Perform a health check on the Gotenberg service.

        This method sends a GET request to the Gotenberg health check endpoint
        and returns the parsed health status.

        For more details on the health check API, see:
        https://gotenberg.dev/docs/routes#health

        Returns:
            HealthStatus: An object representing the current health status of the Gotenberg service.

        Raises:
            httpx.HTTPStatusError: If the request to the health check endpoint fails.
        """
        resp = self._client.get(self.HEALTH_ENDPOINT, headers={"Accept": "application/json"})
        resp.raise_for_status()
        json_data: _HealthCheckApiResponseType = resp.json()
        return HealthStatus(json_data)

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        return None


class AsyncHealthCheckApi(_BaseHealthCheckApi, AbstractAsyncContextManager, AsyncBaseApi):
    async def health(self) -> HealthStatus:
        """
        Perform a health check on the Gotenberg service.

        This method sends a GET request to the Gotenberg health check endpoint
        and returns the parsed health status.

        For more details on the health check API, see:
        https://gotenberg.dev/docs/routes#health

        Returns:
            HealthStatus: An object representing the current health status of the Gotenberg service.

        Raises:
            httpx.HTTPStatusError: If the request to the health check endpoint fails.
        """
        resp = await self._client.get(self.HEALTH_ENDPOINT, headers={"Accept": "application/json"})
        resp.raise_for_status()
        json_data: _HealthCheckApiResponseType = resp.json()
        return HealthStatus(json_data)

    async def __aexit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        return None
