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
from typing import TypeVar
from typing import Union

from gotenberg_client.__about__ import __version__
from gotenberg_client._base import AsyncBaseApi
from gotenberg_client._base import SyncBaseApi
from gotenberg_client._bookmarks import AsyncBookmarksApi
from gotenberg_client._bookmarks import SyncBookmarksApi
from gotenberg_client._chromium import AsyncChromiumApi
from gotenberg_client._chromium import SyncChromiumApi
from gotenberg_client._common import ClientT
from gotenberg_client._health import AsyncHealthCheckApi
from gotenberg_client._health import SyncHealthCheckApi
from gotenberg_client._http_backends import AsyncClientProtocol
from gotenberg_client._http_backends import AuthType
from gotenberg_client._http_backends import BackendType
from gotenberg_client._http_backends import SyncClientProtocol
from gotenberg_client._http_backends import make_async_client
from gotenberg_client._http_backends import make_sync_client
from gotenberg_client._libreoffice import AsyncLibreOfficeApi
from gotenberg_client._libreoffice import SyncLibreOfficeApi
from gotenberg_client._merge import AsyncMergePdfsApi
from gotenberg_client._merge import SyncMergePdfsApi
from gotenberg_client._others import AsyncEmbedApi
from gotenberg_client._others import AsyncEncryptApi
from gotenberg_client._others import AsyncFlattenApi
from gotenberg_client._others import AsyncRotateApi
from gotenberg_client._others import AsyncSplitApi
from gotenberg_client._others import AsyncStampApi
from gotenberg_client._others import AsyncWatermarkApi
from gotenberg_client._others import SyncEmbedApi
from gotenberg_client._others import SyncEncryptApi
from gotenberg_client._others import SyncFlattenApi
from gotenberg_client._others import SyncRotateApi
from gotenberg_client._others import SyncSplitApi
from gotenberg_client._others import SyncStampApi
from gotenberg_client._others import SyncWatermarkApi
from gotenberg_client._pdfa_ua import AsyncPdfAApi
from gotenberg_client._pdfa_ua import SyncPdfAApi
from gotenberg_client._pdfmetadata import AsyncPdfMetadataApi
from gotenberg_client._pdfmetadata import SyncPdfMetadataApi
from gotenberg_client._version import AsyncVersionApi
from gotenberg_client._version import SyncVersionApi

SyncOrAsyncApiT = TypeVar("SyncOrAsyncApiT", bound=Union["SyncBaseApi", "AsyncBaseApi"])


class BaseGotenbergClient(ABC, Generic[ClientT, SyncOrAsyncApiT]):
    """
    Internal base class for Gotenberg clients.
    Provides core functionalities for handling HTTP clients and API integrations.
    """

    def __init__(
        self,
        host: str,
        user_agent: str = f"gotenberg-client/{__version__}",
        auth: AuthType = None,
        *,
        timeout: float = 30.0,
        log_level: int = logging.ERROR,
        http2: bool = True,
        backend: BackendType = "auto",
    ):
        # Configure the client
        self._client = self._get_client(host, timeout, user_agent, auth, http2=http2, backend=backend)

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
        auth: AuthType = None,
        *,
        http2: bool,
        backend: BackendType,
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

    @property
    @abstractmethod
    def watermark(self) -> SyncOrAsyncApiT:  # pragma: no cover
        pass

    @property
    @abstractmethod
    def stamp(self) -> SyncOrAsyncApiT:  # pragma: no cover
        pass

    @property
    @abstractmethod
    def rotate(self) -> SyncOrAsyncApiT:  # pragma: no cover
        pass

    @property
    @abstractmethod
    def encrypt(self) -> SyncOrAsyncApiT:  # pragma: no cover
        pass

    @property
    @abstractmethod
    def embed(self) -> SyncOrAsyncApiT:  # pragma: no cover
        pass

    @property
    @abstractmethod
    def bookmarks(self) -> SyncOrAsyncApiT:  # pragma: no cover
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
        from json import dumps  # noqa: PLC0415

        self.add_headers({"Gotenberg-Webhook-Extra-Http-Headers": dumps(extra_headers)})


class SyncGotenbergClient(AbstractContextManager, BaseGotenbergClient[SyncClientProtocol, SyncBaseApi]):
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
      - [Watermark PDFs](https://gotenberg.dev/docs/manipulate-pdfs/watermark-pdfs)
      - [Stamp PDFs](https://gotenberg.dev/docs/manipulate-pdfs/stamp-pdfs)
      - [Rotate PDFs](https://gotenberg.dev/docs/manipulate-pdfs/rotate-pdfs)
      - [Encrypt PDFs](https://gotenberg.dev/docs/manipulate-pdfs/encrypt-pdfs)
      - [Embed Attachments](https://gotenberg.dev/docs/manipulate-pdfs/attachments)
      - [Read Bookmarks](https://gotenberg.dev/docs/manipulate-pdfs/read-bookmarks)
      - [Write Bookmarks](https://gotenberg.dev/docs/manipulate-pdfs/write-bookmarks)
      - [Health](https://gotenberg.dev/docs/routes#health-check-route)
      - [Version](https://gotenberg.dev/docs/routes#version-route)
    """

    @staticmethod
    def _get_client(
        base_url: str,
        timeout: float,
        user_agent: str,
        auth: AuthType = None,
        *,
        http2: bool,
        backend: BackendType,
    ) -> SyncClientProtocol:
        """
        Create and configure an HTTP client for synchronous requests.
        """
        return make_sync_client(backend, base_url, timeout, user_agent, auth, http2=http2)

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
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

    @property
    def version(self) -> SyncVersionApi:
        """
        Returns a new instance for reading the
        [Version](https://gotenberg.dev/docs/routes#version-route) route
        """
        return SyncVersionApi(self._client, self._log)

    @property
    def watermark(self) -> SyncWatermarkApi:
        """
        Returns a new instance for interacting with the
        [Watermark PDFs](https://gotenberg.dev/docs/manipulate-pdfs/watermark-pdfs) route
        """
        return SyncWatermarkApi(self._client, self._log)

    @property
    def stamp(self) -> SyncStampApi:
        """
        Returns a new instance for interacting with the
        [Stamp PDFs](https://gotenberg.dev/docs/manipulate-pdfs/stamp-pdfs) route
        """
        return SyncStampApi(self._client, self._log)

    @property
    def rotate(self) -> SyncRotateApi:
        """
        Returns a new instance for interacting with the
        [Rotate PDFs](https://gotenberg.dev/docs/manipulate-pdfs/rotate-pdfs) route
        """
        return SyncRotateApi(self._client, self._log)

    @property
    def encrypt(self) -> SyncEncryptApi:
        """
        Returns a new instance for interacting with the
        [Encrypt PDFs](https://gotenberg.dev/docs/manipulate-pdfs/encrypt-pdfs) route
        """
        return SyncEncryptApi(self._client, self._log)

    @property
    def embed(self) -> SyncEmbedApi:
        """
        Returns a new instance for interacting with the
        [Embed attachments](https://gotenberg.dev/docs/manipulate-pdfs/attachments) route
        """
        return SyncEmbedApi(self._client, self._log)

    @property
    def bookmarks(self) -> SyncBookmarksApi:
        """
        Returns a new instance for interacting with the
        [Bookmarks](https://gotenberg.dev/docs/manipulate-pdfs/read-bookmarks) routes
        for reading and writing PDF bookmarks
        """
        return SyncBookmarksApi(self._client, self._log)


class AsyncGotenbergClient(AbstractAsyncContextManager, BaseGotenbergClient[AsyncClientProtocol, AsyncBaseApi]):
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
      - [Watermark PDFs](https://gotenberg.dev/docs/manipulate-pdfs/watermark-pdfs)
      - [Stamp PDFs](https://gotenberg.dev/docs/manipulate-pdfs/stamp-pdfs)
      - [Rotate PDFs](https://gotenberg.dev/docs/manipulate-pdfs/rotate-pdfs)
      - [Encrypt PDFs](https://gotenberg.dev/docs/manipulate-pdfs/encrypt-pdfs)
      - [Embed Attachments](https://gotenberg.dev/docs/manipulate-pdfs/attachments)
      - [Read Bookmarks](https://gotenberg.dev/docs/manipulate-pdfs/read-bookmarks)
      - [Write Bookmarks](https://gotenberg.dev/docs/manipulate-pdfs/write-bookmarks)
      - [Health](https://gotenberg.dev/docs/routes#health-check-route)
      - [Version](https://gotenberg.dev/docs/routes#version-route)
    """

    @staticmethod
    def _get_client(
        base_url: str,
        timeout: float,
        user_agent: str,
        auth: AuthType = None,
        *,
        http2: bool,
        backend: BackendType,
    ) -> AsyncClientProtocol:
        """
        Create and configure an HTTP client for asynchronous requests.
        """
        return make_async_client(backend, base_url, timeout, user_agent, auth, http2=http2)

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
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
    def split(self) -> AsyncSplitApi:
        """
        Returns a new instance for interacting with
        [Split PDFs](https://gotenberg.dev/docs/routes#split-pdfs-route) route
        for splitting PDFs
        """
        return AsyncSplitApi(self._client, self._log)

    @property
    def flatten(self) -> AsyncFlattenApi:
        """
        Returns a new instance for interacting with
        [Flatten PDFs](https://gotenberg.dev/docs/routes#flatten-pdfs-route) route
        for flattening PDFs
        """
        return AsyncFlattenApi(self._client, self._log)

    @property
    def health(self) -> AsyncHealthCheckApi:
        """
        Returns a new instance for reading the [Health](https://gotenberg.dev/docs/routes#health-check-route) route
        """
        return AsyncHealthCheckApi(self._client, self._log)

    @property
    def version(self) -> AsyncVersionApi:
        """
        Returns a new instance for reading the
        [Version](https://gotenberg.dev/docs/routes#version-route) route
        """
        return AsyncVersionApi(self._client, self._log)

    @property
    def watermark(self) -> AsyncWatermarkApi:
        """
        Returns a new instance for interacting with the
        [Watermark PDFs](https://gotenberg.dev/docs/manipulate-pdfs/watermark-pdfs) route
        """
        return AsyncWatermarkApi(self._client, self._log)

    @property
    def stamp(self) -> AsyncStampApi:
        """
        Returns a new instance for interacting with the
        [Stamp PDFs](https://gotenberg.dev/docs/manipulate-pdfs/stamp-pdfs) route
        """
        return AsyncStampApi(self._client, self._log)

    @property
    def rotate(self) -> AsyncRotateApi:
        """
        Returns a new instance for interacting with the
        [Rotate PDFs](https://gotenberg.dev/docs/manipulate-pdfs/rotate-pdfs) route
        """
        return AsyncRotateApi(self._client, self._log)

    @property
    def encrypt(self) -> AsyncEncryptApi:
        """
        Returns a new instance for interacting with the
        [Encrypt PDFs](https://gotenberg.dev/docs/manipulate-pdfs/encrypt-pdfs) route
        """
        return AsyncEncryptApi(self._client, self._log)

    @property
    def embed(self) -> AsyncEmbedApi:
        """
        Returns a new instance for interacting with the
        [Embed attachments](https://gotenberg.dev/docs/manipulate-pdfs/attachments) route
        """
        return AsyncEmbedApi(self._client, self._log)

    @property
    def bookmarks(self) -> AsyncBookmarksApi:
        """
        Returns a new instance for interacting with the
        [Bookmarks](https://gotenberg.dev/docs/manipulate-pdfs/read-bookmarks) routes
        for reading and writing PDF bookmarks
        """
        return AsyncBookmarksApi(self._client, self._log)


GotenbergClient = SyncGotenbergClient
