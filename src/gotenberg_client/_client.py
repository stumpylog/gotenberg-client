# SPDX-FileCopyrightText: 2023-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
import logging
from types import TracebackType
from typing import Optional

from httpx import BasicAuth
from httpx import Client

from gotenberg_client.__about__ import __version__
from gotenberg_client._convert.chromium import ChromiumApi
from gotenberg_client._convert.libre_office import LibreOfficeApi
from gotenberg_client._convert.pdfa import PdfAApi
from gotenberg_client._health import HealthCheckApi
from gotenberg_client._merge import MergeApi
from gotenberg_client._types import HttpMethodsType
from gotenberg_client._types import Self


class GotenbergClient:
    """
    The user's primary interface to the Gotenberg instance.

    This class provides methods to configure and interact with a Gotenberg service,
    including setting up API endpoints for various Gotenberg features and managing
    webhook configurations.

    Attributes:
        chromium (ChromiumApi): Interface for Chromium-related operations.
        libre_office (LibreOfficeApi): Interface for LibreOffice-related operations.
        pdf_a (PdfAApi): Interface for PDF/A-related operations.
        merge (MergeApi): Interface for PDF merging operations.
        health (HealthCheckApi): Interface for health check operations.
    """

    def __init__(
        self,
        host: str,
        user_agent: str = f"gotenberg-client/{__version__}",
        auth: BasicAuth | None = None,
        *,
        timeout: float = 30.0,
        log_level: int = logging.ERROR,
        http2: bool = True,
    ):
        """
        Initialize a new GotenbergClient instance.

        Args:
            host (str): The base URL of the Gotenberg service.
            user_agent (str): The value of the User-Agent header to set.  Defaults to gotenberg-client/{version}
            auth (httpx.BasicAuth, optional): The value of the authentication for the server.  Defaults to None
            timeout (float, optional): The timeout for API requests in seconds. Defaults to 30.0.
            log_level (int, optional): The logging level for httpx and httpcore. Defaults to logging.ERROR.
            http2 (bool, optional): Whether to use HTTP/2. Defaults to True.
        """
        # Configure the client
        self._client = Client(
            base_url=host,
            timeout=timeout,
            http2=http2,
            auth=auth,
            headers={"User-Agent": user_agent},
        )

        # Set the log level
        logging.getLogger("httpx").setLevel(log_level)
        logging.getLogger("httpcore").setLevel(log_level)

        # Add the resources
        self.chromium = ChromiumApi(self._client)
        self.libre_office = LibreOfficeApi(self._client)
        self.pdf_a = PdfAApi(self._client)
        self.merge = MergeApi(self._client)
        self.health = HealthCheckApi(self._client)

    def add_headers(self, header: dict[str, str]) -> None:
        """
        Update the httpx Client headers with the given values.

        Args:
            header (Dict[str, str]): A dictionary of header names and values to add.
        """
        self._client.headers.update(header)

    def add_webhook_url(self, url: str) -> None:
        """
        Add the webhook URL to the headers.

        Args:
            url (str): The URL to be used as the webhook endpoint.
        """
        self.add_headers({"Gotenberg-Webhook-Url": url})

    def add_error_webhook_url(self, url: str) -> None:
        """
        Add the webhook error URL to the headers.

        Args:
            url (str): The URL to be used as the error webhook endpoint.
        """
        self.add_headers({"Gotenberg-Webhook-Error-Url": url})

    def set_webhook_http_method(self, method: HttpMethodsType = "PUT") -> None:
        """
        Set the HTTP method Gotenberg will use to call the webhooks.

        Args:
            method (HttpMethodsType, optional): The HTTP method to use. Defaults to "PUT".
        """
        self.add_headers({"Gotenberg-Webhook-Method": method})

    def set_error_webhook_http_method(self, method: HttpMethodsType = "PUT") -> None:
        """
        Set the HTTP method Gotenberg will use to call the error webhooks.

        Args:
            method (HttpMethodsType, optional): The HTTP method to use. Defaults to "PUT".
        """
        self.add_headers({"Gotenberg-Webhook-Error-Method": method})

    def set_webhook_extra_headers(self, extra_headers: dict[str, str]) -> None:
        """
        Set additional HTTP headers for Gotenberg to use when calling webhooks.

        Args:
            extra_headers (Dict[str, str]): A dictionary of additional headers to include in webhook calls.
        """
        from json import dumps

        self.add_headers({"Gotenberg-Webhook-Extra-Http-Headers": dumps(extra_headers)})

    def __enter__(self) -> Self:
        """
        Enter the runtime context related to this object.

        Returns:
            Self: The instance itself.
        """
        return self

    def close(self) -> None:
        """
        Close the underlying HTTP client connection.
        """
        self._client.close()

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        """
        Exit the runtime context related to this object.

        This method ensures that the client connection is closed when exiting a context manager.

        Args:
            exc_type: The type of the exception that caused the context to be exited, if any.
            exc_val: The instance of the exception that caused the context to be exited, if any.
            exc_tb: A traceback object encoding the stack trace, if an exception occurred.
        """
        self.close()
