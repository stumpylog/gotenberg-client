# SPDX-FileCopyrightText: 2025-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Mapping
from collections.abc import MutableMapping
from typing import TYPE_CHECKING
from typing import Any
from typing import BinaryIO
from typing import Protocol
from typing import TypeAlias
from typing import TypeVar

if TYPE_CHECKING:
    import httpx
    import httpx2
    import niquests.auth
    import requests.auth

    AuthType: TypeAlias = (
        tuple[str, str]
        | httpx.Auth
        | httpx2.Auth
        | requests.auth.AuthBase
        | niquests.auth.AuthBase
        | niquests.auth.AsyncAuthBase
        | None
    )
else:
    # Runtime introspection must work without importing optional backends.
    # The selected backend validates the actual authentication class.
    AuthType = tuple[str, str] | object | None

_AuthT = TypeVar("_AuthT")
_BASIC_AUTH_TUPLE_LENGTH = 2


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


def _validate_auth(
    auth: AuthType,
    auth_types: type[_AuthT] | tuple[type[_AuthT], ...],
    backend: str,
) -> _AuthT | tuple[str, str] | None:
    """Validate authentication before allocating an HTTP client or session."""
    if auth is None or isinstance(auth, auth_types):
        return auth
    if (
        isinstance(auth, tuple)
        and len(auth) == _BASIC_AUTH_TUPLE_LENGTH
        and all(isinstance(value, str) for value in auth)
    ):
        return auth
    classes = auth_types if isinstance(auth_types, tuple) else (auth_types,)
    expected = ", ".join(f"{cls.__module__}.{cls.__qualname__}" for cls in classes)
    msg = (
        f"Invalid auth for backend '{backend}': expected None, a (username, password) tuple of strings, "
        f"or an instance of {expected}; got {type(auth).__module__}.{type(auth).__qualname__}."
    )
    raise TypeError(msg)
