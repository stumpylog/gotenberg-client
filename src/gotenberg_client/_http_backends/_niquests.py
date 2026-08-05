# SPDX-FileCopyrightText: 2025-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Mapping
from collections.abc import MutableMapping
from typing import Any

import niquests
import niquests.auth
import niquests.exceptions

from gotenberg_client._errors import HttpStatusError
from gotenberg_client._http_backends._protocols import AuthType
from gotenberg_client._http_backends._protocols import RequestFiles

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


def _build_niquests_auth(
    auth: AuthType,
) -> niquests.auth.HTTPBasicAuth | None:
    """Convert a (username, password) tuple to niquests HTTPBasicAuth."""
    if auth is None:
        return None
    return niquests.auth.HTTPBasicAuth(auth[0], auth[1])


def make_niquests_sync_client(
    base_url: str,
    timeout: float,
    user_agent: str,
    auth: AuthType,
    *,
    http2: bool,  # noqa: ARG001 — niquests uses HTTP/2 by default
) -> NiquestsSyncAdapter:
    session = niquests.Session()
    session.base_url = base_url
    session.timeout = timeout
    session.headers.update({"User-Agent": user_agent})
    niquests_auth = _build_niquests_auth(auth)
    if niquests_auth is not None:
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
    session = niquests.AsyncSession()
    session.base_url = base_url
    session.timeout = timeout
    session.headers.update({"User-Agent": user_agent})
    niquests_auth = _build_niquests_auth(auth)
    if niquests_auth is not None:
        session.auth = niquests_auth
    return NiquestsAsyncAdapter(session)
