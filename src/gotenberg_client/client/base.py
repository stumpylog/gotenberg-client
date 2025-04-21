# SPDX-FileCopyrightText: 2023-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
import logging
from abc import ABC
from abc import abstractmethod
from collections.abc import Coroutine
from contextlib import AbstractAsyncContextManager
from contextlib import AbstractContextManager
from types import TracebackType
from typing import Any
from typing import Generic
from typing import Literal
from typing import Optional
from typing import TypeVar
from typing import Union

from httpx import AsyncClient
from httpx import BasicAuth
from httpx import Client

from gotenberg_client.__about__ import __version__
from gotenberg_client._base import AsyncBaseApi
from gotenberg_client._base import SyncBaseApi
from gotenberg_client._chromium import AsyncChromiumApi
from gotenberg_client._chromium import SyncChromiumApi
from gotenberg_client._common import ClientT
from gotenberg_client._health import AsyncHealthCheckApi
from gotenberg_client._health import SyncHealthCheckApi
from gotenberg_client._libreoffice import AsyncLibreOfficeApi
from gotenberg_client._libreoffice import SyncLibreOfficeApi
from gotenberg_client._merge import AsyncMergePdfsApi
from gotenberg_client._merge import SyncMergePdfsApi
from gotenberg_client._others import AyncFlattenApi
from gotenberg_client._others import AyncSplitApi
from gotenberg_client._others import SyncFlattenApi
from gotenberg_client._others import SyncSplitApi
from gotenberg_client._pdfa_ua import AsyncPdfAApi
from gotenberg_client._pdfa_ua import SyncPdfAApi
from gotenberg_client._pdfmetadata import AsyncPdfMetadataApi
from gotenberg_client._pdfmetadata import SyncPdfMetadataApi

SyncOrAsyncApiT = TypeVar("SyncOrAsyncApiT", bound="SyncBaseApi | AsyncBaseApi")


class BaseGotenbergClient(ABC, Generic[ClientT, SyncOrAsyncApiT]):
    """
    Internal base class for Gotenberg clients.
    Provides core functionalities for handling HTTP clients and API integrations.
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
    def close(self) -> Union[None, Coroutine[Any, Any, None]]:
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
        Add custom headers to the request, such as authentication, etc

        Args:
            header (Dict[str, str]): A dictionary of header names and values to add.
        """
        self._client.headers.update(header)

    def add_webhook_url(self, url: str) -> None:
        """
        Configure the [webhook](https://gotenberg.dev/docs/webhook) URL value.

        Args:
            url (str): The URL to be used as the webhook endpoint.
        """
        self.add_headers({"Gotenberg-Webhook-Url": url})

    def add_error_webhook_url(self, url: str) -> None:
        """
        Configure the [webhook](https://gotenberg.dev/docs/webhook) error URL value.

        Args:
            url (str): The URL to be used as the webhook endpoint.
        """
        self.add_headers({"Gotenberg-Webhook-Error-Url": url})

    def set_webhook_http_method(self, method: Literal["POST", "PATCH", "PUT"]) -> None:
        """
        Set the HTTP method Gotenberg will use to call the [webhook](https://gotenberg.dev/docs/webhook) url.

        Args:
            method: The HTTP method to use.
        """
        self.add_headers({"Gotenberg-Webhook-Method": method})

    def set_error_webhook_http_method(self, method: Literal["POST", "PATCH", "PUT"]) -> None:
        """
        Set the HTTP method Gotenberg will use to call the error [webhook](https://gotenberg.dev/docs/webhook) url.

         Args:
             method: The HTTP method to use.
        """
        self.add_headers({"Gotenberg-Webhook-Error-Method": method})

    def set_webhook_extra_headers(self, extra_headers: dict[str, str]) -> None:
        """
        Add custom headers to the [webhook](https://gotenberg.dev/docs/webhook) request, such as authentication, etc

        Args:
            extra_headers (Dict[str, str]): A dictionary of additional headers to include in webhook calls.
        """
        from json import dumps

        self.add_headers({"Gotenberg-Webhook-Extra-Http-Headers": dumps(extra_headers)})


class SyncGotenbergClient(AbstractContextManager, BaseGotenbergClient[Client, SyncBaseApi]):
    """
    A synchronous client for interacting with a Gotenberg instance.

    This client provides methods to interact with various Gotenberg APIs, including:

      - [Chromium](https://gotenberg.dev/docs/routes#convert-with-chromium)
      - [Libreoffice](https://gotenberg.dev/docs/routes#convert-with-libreoffice)
      - [PDF/A & PDF/UA](https://gotenberg.dev/docs/routes#convert-into-pdfa--pdfua-route)
      - [Read PDF Metadata](https://gotenberg.dev/docs/routes#read-pdf-metadata-route)
      - [Write PDF Metadata](https://gotenberg.dev/docs/routes#write-pdf-metadata-route)
      - [Merge PDFs](https://gotenberg.dev/docs/routes#merge-pdfs-route)
      - [Split PDFs](https://gotenberg.dev/docs/routes#split-pdfs-route)
      - [Flatten PDFs](https://gotenberg.dev/docs/routes#flatten-pdfs-route)
      - [Health](https://gotenberg.dev/docs/routes#health-check-route)
      - [Version](https://gotenberg.dev/docs/routes#version-route)
    """

    @staticmethod
    def _get_client(
        base_url: str,
        timeout: float,
        user_agent: str,
        auth: Optional[BasicAuth] = None,
        *,
        http2: bool,
    ) -> Client:
        """
        Create and configure an HTTP client for synchronous requests.
        """
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
        """
        Returns a new instance for interacting with
        [Chromium](https://gotenberg.dev/docs/routes#convert-with-chromium) routes
        for the conversion of URLs, HTML, Markdown into PDFs and the generation of screenshots from those types
        """
        return SyncChromiumApi(self._client, self._log)

    @property
    def libre_office(self) -> SyncLibreOfficeApi:
        """
        Returns a new instance for interacting with
        [Libreoffice](https://gotenberg.dev/docs/routes#convert-with-libreoffice) routes
        for the conversion of a variety of office documents into PDFs
        """
        return SyncLibreOfficeApi(self._client, self._log)

    @property
    def pdf_convert(self) -> SyncPdfAApi:
        """
        Returns a new instance for interacting with
        [PDF/A & PDF/UA](https://gotenberg.dev/docs/routes#convert-into-pdfa--pdfua-route) routes
        for the conversion of PDFs to [PDF/A](https://en.wikipedia.org/wiki/PDF/A) and/or
        [PDF/UA](https://en.wikipedia.org/wiki/PDF/UA)
        """
        return SyncPdfAApi(self._client, self._log)

    @property
    def metadata(self) -> SyncPdfMetadataApi:
        """
        Returns a new instance for interacting with
        [Read PDF Metadata](https://gotenberg.dev/docs/routes#read-pdf-metadata-route) and
         [Write PDF Metadata](https://gotenberg.dev/docs/routes#write-pdf-metadata-route) routes
        for the manipulation or reading of metadata
        """
        return SyncPdfMetadataApi(self._client, self._log)

    @property
    def merge(self) -> SyncMergePdfsApi:
        """
        Returns a new instance for interacting with
        [Merge PDFs](https://gotenberg.dev/docs/routes#merge-pdfs-route) route
        for merging multiple PDFs into one
        """
        return SyncMergePdfsApi(self._client, self._log)

    @property
    def split(self) -> SyncSplitApi:
        """
        Returns a new instance for interacting with
        [Split PDFs](https://gotenberg.dev/docs/routes#split-pdfs-route) route
        for splitting PDFs
        """
        return SyncSplitApi(self._client, self._log)

    @property
    def flatten(self) -> SyncFlattenApi:
        """
        Returns a new instance for interacting with
        [Flatten PDFs](https://gotenberg.dev/docs/routes#flatten-pdfs-route) route
        for flattening PDFs
        """
        return SyncFlattenApi(self._client, self._log)

    @property
    def health(self) -> SyncHealthCheckApi:
        """
        Returns a new instance for reading the [Health](https://gotenberg.dev/docs/routes#health-check-route) route
        """
        return SyncHealthCheckApi(self._client, self._log)

    # TODO: Implement this
    @property
    def version(self) -> SyncOrAsyncApiT:  # type: ignore[override,type-var]
        """
        Returns a new instance for reading the
        [Version](https://gotenberg.dev/docs/routes#version-route) route

        Raises:
            NotImplementedError: This API is not yet implemented
        """
        raise NotImplementedError


class AsyncGotenbergClient(AbstractAsyncContextManager, BaseGotenbergClient[AsyncClient, AsyncBaseApi]):
    """
    An asynchronous client for interacting with a Gotenberg instance.

    This client provides methods to interact with various Gotenberg APIs, including:

      - [Chromium](https://gotenberg.dev/docs/routes#convert-with-chromium)
      - [Libreoffice](https://gotenberg.dev/docs/routes#convert-with-libreoffice)
      - [PDF/A & PDF/UA](https://gotenberg.dev/docs/routes#convert-into-pdfa--pdfua-route)
      - [Read PDF Metadata](https://gotenberg.dev/docs/routes#read-pdf-metadata-route)
      - [Write PDF Metadata](https://gotenberg.dev/docs/routes#write-pdf-metadata-route)
      - [Merge PDFs](https://gotenberg.dev/docs/routes#merge-pdfs-route)
      - [Split PDFs](https://gotenberg.dev/docs/routes#split-pdfs-route)
      - [Flatten PDFs](https://gotenberg.dev/docs/routes#flatten-pdfs-route)
      - [Health](https://gotenberg.dev/docs/routes#health-check-route)
      - [Version](https://gotenberg.dev/docs/routes#version-route)
    """

    @staticmethod
    def _get_client(
        base_url: str,
        timeout: float,
        user_agent: str,
        auth: Optional[BasicAuth] = None,
        *,
        http2: bool,
    ) -> AsyncClient:
        """
        Create and configure an HTTP client for asynchronous requests.
        """
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
        Close the underlying asynchronous HTTP client connection.
        """
        await self._client.aclose()

    @property
    def chromium(self) -> AsyncChromiumApi:
        """
        Returns a new instance for interacting with
        [Chromium](https://gotenberg.dev/docs/routes#convert-with-chromium) routes
        for the conversion of URLs, HTML, Markdown into PDFs and the generation of screenshots from those types
        """
        return AsyncChromiumApi(self._client, self._log)

    @property
    def libre_office(self) -> AsyncLibreOfficeApi:
        """
        Returns a new instance for interacting with
        [Libreoffice](https://gotenberg.dev/docs/routes#convert-with-libreoffice) routes
        for the conversion of a variety of office documents into PDFs
        """
        return AsyncLibreOfficeApi(self._client, self._log)

    @property
    def pdf_convert(self) -> AsyncPdfAApi:
        """
        Returns a new instance for interacting with
        [PDF/A & PDF/UA](https://gotenberg.dev/docs/routes#convert-into-pdfa--pdfua-route) routes
        for the conversion of PDFs to [PDF/A](https://en.wikipedia.org/wiki/PDF/A) and/or
        [PDF/UA](https://en.wikipedia.org/wiki/PDF/UA)
        """
        return AsyncPdfAApi(self._client, self._log)

    @property
    def metadata(self) -> AsyncPdfMetadataApi:
        """
        Returns a new instance for interacting with
        [Read PDF Metadata](https://gotenberg.dev/docs/routes#read-pdf-metadata-route) and
         [Write PDF Metadata](https://gotenberg.dev/docs/routes#write-pdf-metadata-route) routes
        for the manipulation or reading of metadata
        """
        return AsyncPdfMetadataApi(self._client, self._log)

    @property
    def merge(self) -> AsyncMergePdfsApi:
        """
        Returns a new instance for interacting with
        [Merge PDFs](https://gotenberg.dev/docs/routes#merge-pdfs-route) route
        for merging multiple PDFs into one
        """
        return AsyncMergePdfsApi(self._client, self._log)

    @property
    def split(self) -> AyncSplitApi:
        """
        Returns a new instance for interacting with
        [Split PDFs](https://gotenberg.dev/docs/routes#split-pdfs-route) route
        for splitting PDFs
        """
        return AyncSplitApi(self._client, self._log)

    @property
    def flatten(self) -> AyncFlattenApi:
        """
        Returns a new instance for interacting with
        [Flatten PDFs](https://gotenberg.dev/docs/routes#flatten-pdfs-route) route
        for flattening PDFs
        """
        return AyncFlattenApi(self._client, self._log)

    @property
    def health(self) -> AsyncHealthCheckApi:
        """
        Returns a new instance for reading the [Health](https://gotenberg.dev/docs/routes#health-check-route) route
        """
        return AsyncHealthCheckApi(self._client, self._log)

    # TODO: Implement this
    @property
    def version(self) -> SyncOrAsyncApiT:  # type: ignore[override,type-var]
        """
        Returns a new instance for reading the
        [Version](https://gotenberg.dev/docs/routes#version-route) route

        Raises:
            NotImplementedError: This API is not yet implemented
        """
        raise NotImplementedError


GotenbergClient = SyncGotenbergClient
