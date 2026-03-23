# SPDX-FileCopyrightText: 2025-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
from typing import Literal

from gotenberg_client._http_backends._protocols import AsyncClientProtocol
from gotenberg_client._http_backends._protocols import AuthType
from gotenberg_client._http_backends._protocols import SyncClientProtocol

BackendType = Literal["httpx", "niquests", "requests", "auto"]

__all__ = [
    "AsyncClientProtocol",
    "AuthType",
    "BackendType",
    "SyncClientProtocol",
    "make_async_client",
    "make_sync_client",
]


def make_sync_client(
    backend: BackendType,
    base_url: str,
    timeout: float,
    user_agent: str,
    auth: AuthType,
    *,
    http2: bool,
) -> SyncClientProtocol:
    """Factory that returns a SyncClientProtocol for the requested backend."""
    if backend == "requests":
        # requests — imported lazily so other backends don't pay the import cost
        from gotenberg_client._http_backends._requests import make_requests_sync_client  # noqa: PLC0415

        return make_requests_sync_client(base_url, timeout, user_agent, auth, http2=http2)
    resolved = _resolve_backend(backend)
    if resolved == "httpx":
        from gotenberg_client._http_backends._httpx import make_httpx_sync_client  # noqa: PLC0415

        return make_httpx_sync_client(base_url, timeout, user_agent, auth, http2=http2)
    # niquests — imported lazily so other backends don't pay the import cost
    from gotenberg_client._http_backends._niquests import make_niquests_sync_client  # noqa: PLC0415

    return make_niquests_sync_client(base_url, timeout, user_agent, auth, http2=http2)


def make_async_client(
    backend: BackendType,
    base_url: str,
    timeout: float,
    user_agent: str,
    auth: AuthType,
    *,
    http2: bool,
) -> AsyncClientProtocol:
    """Factory that returns an AsyncClientProtocol for the requested backend."""
    if backend == "requests":
        msg = (
            "The 'requests' backend only supports synchronous usage. "
            "Use 'httpx' or 'niquests' for AsyncGotenbergClient."
        )
        raise ValueError(msg)
    resolved = _resolve_backend(backend)
    if resolved == "httpx":
        from gotenberg_client._http_backends._httpx import make_httpx_async_client  # noqa: PLC0415

        return make_httpx_async_client(base_url, timeout, user_agent, auth, http2=http2)
    # niquests — imported lazily so other backends don't pay the import cost
    from gotenberg_client._http_backends._niquests import make_niquests_async_client  # noqa: PLC0415

    return make_niquests_async_client(base_url, timeout, user_agent, auth, http2=http2)


def _resolve_backend(backend: BackendType) -> Literal["httpx", "niquests"]:
    if backend == "httpx":
        return "httpx"
    if backend == "niquests":
        return "niquests"
    # "auto" — prefer httpx, fall back to niquests
    try:
        import httpx  # noqa: F401, PLC0415
    except ImportError:  # no cov
        pass
    else:
        return "httpx"
    try:
        import niquests  # noqa: F401, PLC0415
    except ImportError:  # no cov
        pass
    else:
        return "niquests"  # no cov
    msg = (  # no cov
        "No HTTP backend available. Install one with:\n"
        '  pip install "gotenberg-client[httpx]"      # recommended, includes HTTP/2 and async support\n'
        '  pip install "gotenberg-client[niquests]"   # alternative with HTTP/2 and async support\n'
        '  pip install "gotenberg-client[requests]"   # sync-only\n'
    )
    raise ImportError(msg)  # no cov
