# SPDX-FileCopyrightText: 2025-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
from typing import TYPE_CHECKING
from typing import Literal

from gotenberg_client._http_backends._httpx import HttpxAsyncAdapter
from gotenberg_client._http_backends._httpx import HttpxSyncAdapter
from gotenberg_client._http_backends._httpx import make_httpx_async_client
from gotenberg_client._http_backends._httpx import make_httpx_sync_client
from gotenberg_client._http_backends._protocols import AsyncClientProtocol
from gotenberg_client._http_backends._protocols import SyncClientProtocol

if TYPE_CHECKING:
    import httpx

BackendType = Literal["httpx", "niquests", "auto"]

__all__ = [
    "AsyncClientProtocol",
    "BackendType",
    "HttpxAsyncAdapter",
    "HttpxSyncAdapter",
    "SyncClientProtocol",
    "make_async_client",
    "make_sync_client",
]


def _to_tuple_auth(auth: "httpx.BasicAuth | tuple[str, str] | None") -> "tuple[str, str] | None":
    """Normalise auth to a (username, password) tuple accepted by niquests factories."""
    if auth is None or isinstance(auth, tuple):
        return auth
    # httpx.BasicAuth does not expose credentials publicly; require tuple[str, str] for niquests
    msg = "When using the niquests backend, provide auth as a (username, password) tuple instead of httpx.BasicAuth."
    raise ValueError(msg)


def make_sync_client(
    backend: BackendType,
    base_url: str,
    timeout: float,
    user_agent: str,
    auth: "httpx.BasicAuth | tuple[str, str] | None",
    *,
    http2: bool,
) -> SyncClientProtocol:
    """Factory that returns a SyncClientProtocol for the requested backend."""
    resolved = _resolve_backend(backend)
    if resolved == "httpx":
        return make_httpx_sync_client(base_url, timeout, user_agent, auth, http2=http2)
    # niquests — imported lazily so httpx-only installs don't pay the import cost
    from gotenberg_client._http_backends._niquests import make_niquests_sync_client  # noqa: PLC0415

    return make_niquests_sync_client(base_url, timeout, user_agent, _to_tuple_auth(auth), http2=http2)


def make_async_client(
    backend: BackendType,
    base_url: str,
    timeout: float,
    user_agent: str,
    auth: "httpx.BasicAuth | tuple[str, str] | None",
    *,
    http2: bool,
) -> AsyncClientProtocol:
    """Factory that returns an AsyncClientProtocol for the requested backend."""
    resolved = _resolve_backend(backend)
    if resolved == "httpx":
        return make_httpx_async_client(base_url, timeout, user_agent, auth, http2=http2)
    # niquests — imported lazily so httpx-only installs don't pay the import cost
    from gotenberg_client._http_backends._niquests import make_niquests_async_client  # noqa: PLC0415

    return make_niquests_async_client(base_url, timeout, user_agent, _to_tuple_auth(auth), http2=http2)


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
        "No HTTP backend available. Install either 'httpx' (pip install gotenberg-client) "
        "or 'niquests' (pip install gotenberg-client[niquests])."
    )
    raise ImportError(msg)  # no cov
