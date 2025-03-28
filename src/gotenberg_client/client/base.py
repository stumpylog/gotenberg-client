# SPDX-FileCopyrightText: 2023-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
import logging
from abc import ABC
from abc import abstractmethod
from collections.abc import Coroutine
from contextlib import AbstractAsyncContextManager
from contextlib import AbstractContextManager
from http import HTTPMethod
from types import TracebackType
from typing import Any
from typing import Generic
from typing import Optional
from typing import TypeVar

from httpx import AsyncClient
from httpx import BasicAuth
from httpx import Client

from gotenberg_client.__about__ import __version__
from gotenberg_client._base import AsyncBaseApi
from gotenberg_client._base import SyncBaseApi
from gotenberg_client._chromium import AsyncChromiumApi
from gotenberg_client._chromium import SyncChromiumApi
from gotenberg_client._common.units import ClientT
from gotenberg_client._common.units import HttpMethodsType
from gotenberg_client._health import AsyncHealthCheckApi
from gotenberg_client._health import SyncHealthCheckApi
from gotenberg_client._libreoffice import AsyncLibreOfficeApi
from gotenberg_client._libreoffice import SyncLibreOfficeApi
from gotenberg_client._merge import AsyncMergePdfsApi
from gotenberg_client._merge import SyncMergePdfsApi
from gotenberg_client._pdfa_ua import AsyncPdfAApi
from gotenberg_client._pdfa_ua import SyncPdfAApi

SyncOrAsyncApiT = TypeVar("SyncOrAsyncApiT", bound="SyncBaseApi | AsyncBaseApi")


class BaseGotenbergClient(ABC, Generic[ClientT, SyncOrAsyncApiT]):
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
        auth: Optional[BasicAuth] = None,
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
        self._client = self._get_client(host, timeout, user_agent, auth, http2=http2)

        # Set the log level
        logging.getLogger("httpx").setLevel(log_level)
        logging.getLogger("httpcore").setLevel(log_level)
        self._log = logging.getLogger("gotenberg-client")
        self._log.setLevel(log_level)

    @staticmethod
    @abstractmethod
    def _get_client(
        base_url: str,
        timeout: float,
        user_agent: str,
        auth: Optional[BasicAuth] = None,
        *,
        http2: bool,
    ) -> ClientT:  # pragma: no cover
        pass

    @abstractmethod
    def close(self) -> None | Coroutine[Any, Any, None]:
        """
        Close the underlying HTTP client connection.
        """

    @property
    @abstractmethod
    def chromium(self) -> SyncOrAsyncApiT:  # pragma: no cover
        pass

    @property
    @abstractmethod
    def libre_office(self) -> SyncOrAsyncApiT:  # pragma: no cover
        pass

    @property
    @abstractmethod
    def pdf_convert(self) -> SyncOrAsyncApiT:  # pragma: no cover
        pass

    @property
    @abstractmethod
    def metadata(self) -> SyncOrAsyncApiT:  # pragma: no cover
        pass

    @property
    @abstractmethod
    def merge(self) -> SyncOrAsyncApiT:  # pragma: no cover
        pass

    @property
    @abstractmethod
    def split(self) -> SyncOrAsyncApiT:  # pragma: no cover
        pass

    @property
    @abstractmethod
    def flatten(self) -> SyncOrAsyncApiT:  # pragma: no cover
        pass

    @property
    @abstractmethod
    def health(self) -> SyncOrAsyncApiT:  # pragma: no cover
        pass

    @property
    @abstractmethod
    def version(self) -> SyncOrAsyncApiT:  # pragma: no cover
        pass

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

    def set_webhook_http_method(self, method: HttpMethodsType = HTTPMethod.PUT) -> None:
        """
        Set the HTTP method Gotenberg will use to call the webhooks.

        Args:
            method (HttpMethodsType, optional): The HTTP method to use. Defaults to "PUT".
        """
        self.add_headers({"Gotenberg-Webhook-Method": method})

    def set_error_webhook_http_method(self, method: HttpMethodsType = HTTPMethod.PUT) -> None:
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


class SyncGotenbergClient(AbstractContextManager, BaseGotenbergClient[Client, SyncBaseApi]):
    @staticmethod
    def _get_client(
        base_url: str,
        timeout: float,
        user_agent: str,
        auth: Optional[BasicAuth] = None,
        *,
        http2: bool,
    ) -> Client:
        return Client(
            base_url=base_url,
            timeout=timeout,
            http2=http2,
            auth=auth,
            headers={"User-Agent": user_agent},
        )

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        self.close()

    def close(self) -> None:
        """
        Close the underlying HTTP client connection.
        """
        self._client.close()

    @property
    def chromium(self) -> SyncChromiumApi:
        return SyncChromiumApi(self._client, self._log)

    @property
    def libre_office(self) -> SyncLibreOfficeApi:
        return SyncLibreOfficeApi(self._client, self._log)

    @property
    def pdf_convert(self) -> SyncPdfAApi:
        return SyncPdfAApi(self._client, self._log)

    @property
    def metadata(self) -> SyncOrAsyncApiT:
        raise NotImplementedError

    @property
    def merge(self) -> SyncMergePdfsApi:
        return SyncMergePdfsApi(self._client, self._log)

    @property
    def split(self) -> SyncOrAsyncApiT:
        raise NotImplementedError

    @property
    def flatten(self) -> SyncOrAsyncApiT:
        raise NotImplementedError

    @property
    def health(self) -> SyncHealthCheckApi:
        return SyncHealthCheckApi(self._client, self._log)

    @property
    def version(self) -> SyncOrAsyncApiT:
        raise NotImplementedError


class AsyncGotenbergClient(AbstractAsyncContextManager, BaseGotenbergClient[AsyncClient, AsyncBaseApi]):
    @staticmethod
    def _get_client(
        base_url: str,
        timeout: float,
        user_agent: str,
        auth: Optional[BasicAuth] = None,
        *,
        http2: bool,
    ) -> AsyncClient:
        return AsyncClient(
            base_url=base_url,
            timeout=timeout,
            http2=http2,
            auth=auth,
            headers={"User-Agent": user_agent},
        )

    async def __aexit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        await self.close()

    async def close(self) -> None:
        """
        Close the underlying HTTP client connection.
        """
        await self._client.aclose()

    @property
    def chromium(self) -> AsyncChromiumApi:
        return AsyncChromiumApi(self._client, self._log)

    @property
    def libre_office(self) -> AsyncLibreOfficeApi:
        return AsyncLibreOfficeApi(self._client, self._log)

    @property
    def pdf_convert(self) -> AsyncPdfAApi:
        return AsyncPdfAApi(self._client, self._log)

    @property
    def metadata(self) -> SyncOrAsyncApiT:
        raise NotImplementedError

    @property
    def merge(self) -> AsyncMergePdfsApi:
        return AsyncMergePdfsApi(self._client, self._log)

    @property
    def split(self) -> SyncOrAsyncApiT:
        raise NotImplementedError

    @property
    def flatten(self) -> SyncOrAsyncApiT:
        raise NotImplementedError

    @property
    def health(self) -> AsyncHealthCheckApi:
        return AsyncHealthCheckApi(self._client, self._log)

    @property
    def version(self) -> SyncOrAsyncApiT:
        raise NotImplementedError


GotenbergClient = SyncGotenbergClient
