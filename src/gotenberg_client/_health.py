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
    """
    Typed dictionary representing the status of a module, as the JSON strings

    Attributes:
        status: String indicating the current status of the module.
        timestamp: String containing the timestamp of the status check.
    """

    status: str
    timestamp: str


class _AllModulesType(TypedDict):
    chromium: _ModuleStatusType
    libreoffice: _ModuleStatusType


class _HealthCheckApiResponseType(TypedDict):
    status: str
    details: _AllModulesType


@enum.unique
class StatusOptions(str, enum.Enum):
    Up = "up"
    Down = "down"


@enum.unique
class ModuleOptions(str, enum.Enum):
    """
    Enumeration of available modules that can be health-checked.

    Attributes:
        Chromium: The Chromium browser module used for HTML processing.
        Libreoffice: The LibreOffice module used for document conversion.
    """

    Chromium = "chromium"
    Libreoffice = "libreoffice"


@dataclasses.dataclass
class ModuleStatus:
    """
    Data class representing the status of an individual module.

    Attributes:
        status: The current operational status of the module.
        timestamp: The datetime when the status was last checked.
    """

    status: StatusOptions
    timestamp: datetime.datetime


class HealthStatus:
    """
    The overall health of the Gotenberg service and its modules which
    report health

    This class parses the raw health check API response and provides
    structured access to overall system status and individual module statuses.

    Attributes:
        data: The raw health check API response data.
        overall: The overall status of the system.
        chromium: The status of the Chromium module, if available.
        uno: The status of the Uno module, if available.
    """

    def __init__(self, data: _HealthCheckApiResponseType) -> None:
        self.data = data
        self.overall: StatusOptions = StatusOptions(data["status"])

        self.chromium: Optional[ModuleStatus] = None
        if ModuleOptions.Chromium.value in self.data["details"]:
            self.chromium = self._extract_status(ModuleOptions.Chromium)

        self.uno: Optional[ModuleStatus] = None
        if ModuleOptions.Libreoffice.value in self.data["details"]:
            self.uno = self._extract_status(ModuleOptions.Libreoffice)

    def _extract_status(self, module: ModuleOptions) -> ModuleStatus:
        status = StatusOptions(self.data["details"][module.value]["status"])
        timestamp: datetime.datetime = self._extract_datetime(self.data["details"][module.value]["timestamp"])
        return ModuleStatus(status, timestamp)

    @staticmethod
    def _extract_datetime(timestamp: str) -> datetime.datetime:
        """P
        arse an ISO-format timestamp string into a datetime object.

        Args:
            timestamp: ISO format timestamp string.

        Returns:
            Parsed datetime object with timezone information if present.

        Raises:
            ValueError: If the timestamp cannot be parsed.
        """
        m = _TIME_RE.match(timestamp)
        if not m:  # pragma: no cover
            msg = f"Unable to parse {timestamp}"
            raise ValueError(msg)

        (year, month, day, hour, minute, second, frac_sec, timezone_str) = m.groups()

        microseconds = int(float(frac_sec) * 1_000_000.0) if frac_sec is not None else 0

        tzinfo = None
        if timezone_str is not None:
            if timezone_str.lower() == "z":  # type: ignore[misc]
                tzinfo = datetime.timezone.utc
            else:  # pragma: no cover
                multi = -1 if timezone_str[0:1] == "-" else 1  # type: ignore[misc]
                hours = int(timezone_str[1:3])  # type: ignore[misc]
                minutes = int(timezone_str[4:])  # type: ignore[misc]
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
    It defines the endpoint used for health checks and serves as a base class for both
    synchronous and asynchronous implementations.

    For more information on Gotenberg's health check endpoint, see:
    https://gotenberg.dev/docs/routes#health
    """

    HEALTH_ENDPOINT: Final[str] = "/health"


class SyncHealthCheckApi(_BaseHealthCheckApi, AbstractContextManager, SyncBaseApi):
    """
    Synchronous implementation of the Gotenberg health check API.

    This class provides a synchronous interface for performing health checks
    on the Gotenberg service.

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
        """
        Exit the context manager.  This is provided for completeness and does nothing

        Args:
            exc_type: The exception type if an exception was raised in the context.
            exc_val: The exception value if an exception was raised in the context.
            exc_tb: The traceback if an exception was raised in the context.

        Returns:
            None
        """
        return None


class AsyncHealthCheckApi(_BaseHealthCheckApi, AbstractAsyncContextManager, AsyncBaseApi):
    """
    Asynchronous implementation of the Gotenberg health check API.

    This class provides an asynchronous interface for performing health checks
    on the Gotenberg service.

    For more information on Gotenberg's health check endpoint, see:
    https://gotenberg.dev/docs/routes#health
    """

    async def health(self) -> HealthStatus:
        """
        Perform an asynchronous health check on the Gotenberg service.

        This method sends an asynchronous GET request to the Gotenberg health check endpoint
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
        """
        Exit the asynchronous context manager.  This is provided for completeness and does nothing

        Args:
            exc_type: The exception type if an exception was raised in the context.
            exc_val: The exception value if an exception was raised in the context.
            exc_tb: The traceback if an exception was raised in the context.

        Returns:
            None
        """
        return None
