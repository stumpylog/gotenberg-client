# SPDX-FileCopyrightText: 2023-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
import logging
from types import TracebackType
from typing import Dict
from typing import Optional
from typing import Type

from httpx import Client

from gotenberg_client._convert.chromium import ChromiumApi
from gotenberg_client._convert.libre_office import LibreOfficeApi
from gotenberg_client._convert.pdfa import PdfAApi
from gotenberg_client._health import HealthCheckApi
from gotenberg_client._merge import MergeApi
from gotenberg_client._typing_compat import Self


class GotenbergClient:
    """
    The user's primary interface to the Gotenberg instance
    """

    def __init__(
        self,
        host: str,
        *,
        timeout: float = 30.0,
        log_level: int = logging.ERROR,
        http2: bool = True,
    ):
        # Configure the client
        self._client = Client(base_url=host, timeout=timeout, http2=http2)

        # Set the log level
        logging.getLogger("httpx").setLevel(log_level)
        logging.getLogger("httpcore").setLevel(log_level)

        # Add the resources
        self.chromium = ChromiumApi(self._client)
        self.libre_office = LibreOfficeApi(self._client)
        self.pdf_a = PdfAApi(self._client)
        self.merge = MergeApi(self._client)
        self.health = HealthCheckApi(self._client)

    def add_headers(self, header: Dict[str, str]) -> None:  # pragma: no cover
        """
        Updates the httpx Client headers with the given values
        """
        self._client.headers.update(header)

    def __enter__(self) -> Self:
        return self

    def close(self) -> None:
        self._client.close()

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        self.close()
