# SPDX-FileCopyrightText: 2025-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Mapping
from collections.abc import MutableMapping
from typing import Any
from typing import cast

import requests
import requests.auth
import requests.exceptions

from gotenberg_client._errors import HttpStatusError
from gotenberg_client._http_backends._protocols import AuthType
from gotenberg_client._http_backends._protocols import RequestFiles

_SERVER_ERROR_STATUS_CODE = 500


class RequestsResponseAdapter:
    """Wraps a requests.Response to satisfy ResponseProtocol."""

    def __init__(self, response: requests.Response) -> None:
        self._response = response

    @property
    def status_code(self) -> int:
        return self._response.status_code

    @property
    def headers(self) -> Mapping[str, str]:
        return self._response.headers

    @property
    def content(self) -> bytes:
        return self._response.content

    @property
    def is_server_error(self) -> bool:
        return self._response.status_code >= _SERVER_ERROR_STATUS_CODE

    def raise_for_status(self) -> None:
        try:
            self._response.raise_for_status()
        except requests.exceptions.HTTPError as e:  # type: ignore[misc]
            raise HttpStatusError(response=self) from e

    def json(self) -> Any:
        return self._response.json()  # type: ignore[misc]


class RequestsSyncAdapter:
    """Wraps requests.Session to satisfy SyncClientProtocol."""

    def __init__(self, session: requests.Session, base_url: str, timeout: float) -> None:
        self._session = session
        self._base_url = base_url
        self._timeout = timeout

    @property
    def headers(self) -> MutableMapping[str, str]:
        return cast("MutableMapping[str, str]", self._session.headers)

    def post(
        self,
        url: str,
        *,
        headers: dict[str, str],
        data: dict[str, str],
        files: RequestFiles,
    ) -> RequestsResponseAdapter:
        full_url = self._base_url.rstrip("/") + "/" + url.lstrip("/")
        resp = self._session.post(
            full_url,
            data=data,
            files=files,
            headers=headers,
            timeout=self._timeout,
        )
        return RequestsResponseAdapter(resp)

    def get(
        self,
        url: str,
        *,
        headers: dict[str, str],
    ) -> RequestsResponseAdapter:
        full_url = self._base_url.rstrip("/") + "/" + url.lstrip("/")
        resp = self._session.get(full_url, headers=headers, timeout=self._timeout)
        return RequestsResponseAdapter(resp)

    def close(self) -> None:
        self._session.close()


def _build_requests_auth(
    auth: AuthType,
) -> requests.auth.HTTPBasicAuth | None:
    """Convert a (username, password) tuple to requests HTTPBasicAuth."""
    if auth is None:
        return None
    return requests.auth.HTTPBasicAuth(auth[0], auth[1])


def make_requests_sync_client(
    base_url: str,
    timeout: float,
    user_agent: str,
    auth: AuthType,
    *,
    http2: bool,  # noqa: ARG001 — requests does not support HTTP/2
) -> RequestsSyncAdapter:
    session = requests.Session()
    session.headers.update({"User-Agent": user_agent})
    requests_auth = _build_requests_auth(auth)
    if requests_auth is not None:
        session.auth = requests_auth
    return RequestsSyncAdapter(session, base_url, timeout)
