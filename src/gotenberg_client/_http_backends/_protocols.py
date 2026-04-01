# SPDX-FileCopyrightText: 2025-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Mapping
from collections.abc import MutableMapping
from typing import Any
from typing import BinaryIO
from typing import Protocol

AuthType = tuple[str, str] | None

# Type alias for multipart file uploads compatible with httpx and niquests.
# Values are either (filename, content, mime_type) or (filename, content).
_FileContent = bytes | str | BinaryIO
_FileEntryWithMime = tuple[str, _FileContent, str]
_FileEntryWithoutMime = tuple[str, _FileContent]
_FileEntry = _FileEntryWithMime | _FileEntryWithoutMime
RequestFiles = list[tuple[str, _FileEntry]]


class ResponseProtocol(Protocol):  # no cov
    """Minimal HTTP response interface used by all routes."""

    @property
    def status_code(self) -> int: ...

    @property
    def headers(self) -> Mapping[str, str]: ...

    @property
    def content(self) -> bytes: ...

    @property
    def is_server_error(self) -> bool: ...

    def raise_for_status(self) -> None: ...

    def json(self) -> Any: ...


class SyncClientProtocol(Protocol):  # no cov
    """Minimal synchronous HTTP client interface."""

    @property
    def headers(self) -> MutableMapping[str, str]: ...

    def post(
        self,
        url: str,
        *,
        headers: dict[str, str],
        data: dict[str, str],
        files: RequestFiles,
    ) -> ResponseProtocol: ...

    def get(
        self,
        url: str,
        *,
        headers: dict[str, str],
    ) -> ResponseProtocol: ...

    def close(self) -> None: ...


class AsyncClientProtocol(Protocol):  # no cov
    """Minimal asynchronous HTTP client interface."""

    @property
    def headers(self) -> MutableMapping[str, str]: ...

    async def post(
        self,
        url: str,
        *,
        headers: dict[str, str],
        data: dict[str, str],
        files: RequestFiles,
    ) -> ResponseProtocol: ...

    async def get(
        self,
        url: str,
        *,
        headers: dict[str, str],
    ) -> ResponseProtocol: ...

    async def aclose(self) -> None: ...
