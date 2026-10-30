# SPDX-FileCopyrightText: 2025-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Mapping
from collections.abc import MutableMapping
from typing import TYPE_CHECKING
from typing import Any
from typing import cast

import niquests
import niquests.auth
import niquests.exceptions

from gotenberg_client._errors import HttpStatusError
from gotenberg_client._http_backends._protocols import AuthType
from gotenberg_client._http_backends._protocols import RequestFiles
from gotenberg_client._http_backends._protocols import _validate_auth

if TYPE_CHECKING:
    from niquests.typing import HttpAuthenticationType

# Older Niquests versions do not expose asynchronous authentication classes.
_ASYNC_AUTH_BASE = cast("type[object] | None", getattr(niquests.auth, "AsyncAuthBase", None))
_SERVER_ERROR_STATUS_CODE = 500


class NiquestsResponseAdapter:
    """Wraps a niquests.Response to satisfy ResponseProtocol."""

    def __init__(self, response: niquests.Response) -> None:
        self._response = response

    @property
    def status_code(self) -> int:
        return self._response.status_code  # type: ignore[return-value]

    @property
    def headers(self) -> Mapping[str, str]:
        return self._response.headers

    @property
    def content(self) -> bytes:
        return self._response.content  # type: ignore[return-value]

    @property
    def is_server_error(self) -> bool:
        return self._response.status_code >= _SERVER_ERROR_STATUS_CODE  # type: ignore[operator]

    def raise_for_status(self) -> None:
        try:
            self._response.raise_for_status()
        except niquests.exceptions.HTTPError as e:  # type: ignore[misc]
            raise HttpStatusError(response=self) from e

    def json(self) -> Any:
        return self._response.json()  # type: ignore[misc]


class NiquestsSyncAdapter:
    """Wraps niquests.Session to satisfy SyncClientProtocol."""

    def __init__(self, session: niquests.Session) -> None:
        self._session = session

    @property
    def headers(self) -> MutableMapping[str, str]:
        return self._session.headers

    def post(
        self,
        url: str,
        *,
        headers: dict[str, str],
        data: dict[str, str],
        files: RequestFiles,
    ) -> NiquestsResponseAdapter:
        resp = self._session.post(url, data=data, files=files, headers=headers)  # type: ignore[arg-type]
        return NiquestsResponseAdapter(resp)

    def get(
        self,
        url: str,
        *,
        headers: dict[str, str],
    ) -> NiquestsResponseAdapter:
        resp = self._session.get(url, headers=headers)
        return NiquestsResponseAdapter(resp)

    def close(self) -> None:
        self._session.close()


class NiquestsAsyncAdapter:
    """Wraps niquests.AsyncSession to satisfy AsyncClientProtocol."""

    def __init__(self, session: niquests.AsyncSession) -> None:
        self._session = session

    @property
    def headers(self) -> MutableMapping[str, str]:
        return self._session.headers

    async def post(
        self,
        url: str,
        *,
        headers: dict[str, str],
        data: dict[str, str],
        files: RequestFiles,
    ) -> NiquestsResponseAdapter:
        resp = await self._session.post(url, data=data, files=files, headers=headers)  # type: ignore[arg-type]
        return NiquestsResponseAdapter(resp)

    async def get(
        self,
        url: str,
        *,
        headers: dict[str, str],
    ) -> NiquestsResponseAdapter:
        resp = await self._session.get(url, headers=headers)
        return NiquestsResponseAdapter(resp)

    async def aclose(self) -> None:
        await self._session.close()


def make_niquests_sync_client(
    base_url: str,
    timeout: float,
    user_agent: str,
    auth: AuthType,
    *,
    http2: bool,  # noqa: ARG001 — niquests uses HTTP/2 by default
) -> NiquestsSyncAdapter:
    if _ASYNC_AUTH_BASE is not None and isinstance(auth, _ASYNC_AUTH_BASE):
        msg = "Asynchronous Niquests auth requires AsyncGotenbergClient with backend='niquests'."
        raise TypeError(msg)
    niquests_auth = _validate_auth(auth, niquests.auth.AuthBase, "niquests")
    session = niquests.Session()
    session.base_url = base_url
    session.timeout = timeout
    session.headers["User-Agent"] = user_agent
    session.auth = niquests_auth
    return NiquestsSyncAdapter(session)


def make_niquests_async_client(
    base_url: str,
    timeout: float,
    user_agent: str,
    auth: AuthType,
    *,
    http2: bool,  # noqa: ARG001 — niquests uses HTTP/2 by default
) -> NiquestsAsyncAdapter:
    auth_types = (niquests.auth.AuthBase,) if _ASYNC_AUTH_BASE is None else (niquests.auth.AuthBase, _ASYNC_AUTH_BASE)
    niquests_auth = _validate_auth(auth, auth_types, "niquests")
    session = niquests.AsyncSession()
    session.base_url = base_url
    session.timeout = timeout
    session.headers["User-Agent"] = user_agent
    # AsyncSession inherits Session's sync-only annotation for this attribute.
    # Niquests also accepts native asynchronous auth here when supported.
    session.auth = cast("HttpAuthenticationType | None", niquests_auth)
    return NiquestsAsyncAdapter(session)
