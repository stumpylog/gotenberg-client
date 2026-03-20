# SPDX-FileCopyrightText: 2025-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
"""
Tests for the pluggable HTTP backend system that do NOT require Docker.
These verify backend selection and adapter wiring.
"""

from __future__ import annotations

from collections.abc import MutableMapping
from typing import TYPE_CHECKING

import httpx
import niquests
import niquests.exceptions
import pytest

from gotenberg_client import AsyncGotenbergClient
from gotenberg_client import HttpStatusError
from gotenberg_client import SyncGotenbergClient
from gotenberg_client._http_backends import _resolve_backend
from gotenberg_client._http_backends import _to_tuple_auth
from gotenberg_client._http_backends._httpx import HttpxAsyncAdapter
from gotenberg_client._http_backends._httpx import HttpxSyncAdapter
from gotenberg_client._http_backends._niquests import NiquestsAsyncAdapter
from gotenberg_client._http_backends._niquests import NiquestsResponseAdapter
from gotenberg_client._http_backends._niquests import NiquestsSyncAdapter

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


class TestAutoBackendSelection:
    def test_auto_selects_httpx_sync(self):
        """backend='auto' picks httpx when it is installed (test env always has it)."""
        with SyncGotenbergClient(host="http://localhost:3000", backend="auto") as client:
            assert isinstance(client._client, HttpxSyncAdapter)

    async def test_auto_selects_httpx_async(self):
        """backend='auto' picks httpx (async) when it is installed."""
        async with AsyncGotenbergClient(host="http://localhost:3000", backend="auto") as client:
            assert isinstance(client._client, HttpxAsyncAdapter)

    def test_explicit_httpx_sync(self):
        """backend='httpx' always uses the httpx adapter."""
        with SyncGotenbergClient(host="http://localhost:3000", backend="httpx") as client:
            assert isinstance(client._client, HttpxSyncAdapter)

    async def test_explicit_httpx_async(self):
        """backend='httpx' always uses the httpx adapter (async)."""
        async with AsyncGotenbergClient(host="http://localhost:3000", backend="httpx") as client:
            assert isinstance(client._client, HttpxAsyncAdapter)

    def test_explicit_niquests_sync(self):
        """backend='niquests' uses the niquests adapter when niquests is installed."""
        with SyncGotenbergClient(host="http://localhost:3000", backend="niquests") as client:
            assert isinstance(client._client, NiquestsSyncAdapter)

    async def test_explicit_niquests_async(self):
        """backend='niquests' uses the niquests adapter (async) when niquests is installed."""
        async with AsyncGotenbergClient(host="http://localhost:3000", backend="niquests") as client:
            assert isinstance(client._client, NiquestsAsyncAdapter)

    def test_tuple_auth_httpx(self):
        """Tuple auth is accepted and converted for the httpx backend."""
        with SyncGotenbergClient(host="http://localhost:3000", backend="httpx", auth=("user", "pass")) as client:
            assert isinstance(client._client, HttpxSyncAdapter)

    def test_tuple_auth_niquests(self):
        """Tuple auth is accepted for the niquests backend."""
        with SyncGotenbergClient(host="http://localhost:3000", backend="niquests", auth=("user", "pass")) as client:
            assert isinstance(client._client, NiquestsSyncAdapter)

    async def test_tuple_auth_niquests_async(self):
        """Tuple auth is accepted for the niquests backend (async)."""
        async with AsyncGotenbergClient(
            host="http://localhost:3000",
            backend="niquests",
            auth=("user", "pass"),
        ) as client:
            assert isinstance(client._client, NiquestsAsyncAdapter)

    def test_resolve_backend_httpx(self):
        """_resolve_backend returns 'httpx' when explicitly requested."""
        assert _resolve_backend("httpx") == "httpx"

    def test_resolve_backend_niquests(self):
        """_resolve_backend returns 'niquests' when explicitly requested."""
        assert _resolve_backend("niquests") == "niquests"

    def test_resolve_backend_auto_prefers_httpx(self):
        """_resolve_backend('auto') returns 'httpx' when httpx is installed."""
        assert _resolve_backend("auto") == "httpx"

    def test_to_tuple_auth_raises_for_basicauth(self):
        """Passing httpx.BasicAuth to _to_tuple_auth raises ValueError."""
        with pytest.raises(ValueError, match="niquests backend"):
            _to_tuple_auth(httpx.BasicAuth("user", "pass"))


class TestNiquestsAdapterUnit:
    """Unit tests for niquests adapter internals that don't require Docker."""

    def test_sync_adapter_headers(self):
        """NiquestsSyncAdapter.headers returns the session's header mapping."""
        session = niquests.Session()
        adapter = NiquestsSyncAdapter(session)
        assert isinstance(adapter.headers, MutableMapping)
        session.close()

    async def test_async_adapter_headers(self):
        """NiquestsAsyncAdapter.headers returns the session's header mapping."""
        session = niquests.AsyncSession()
        adapter = NiquestsAsyncAdapter(session)
        assert isinstance(adapter.headers, MutableMapping)
        await session.close()

    def test_response_is_server_error_true(self, mocker: MockerFixture):
        """NiquestsResponseAdapter.is_server_error is True for 5xx status."""
        mock_resp: niquests.Response = mocker.MagicMock()
        mock_resp.status_code = 500
        assert NiquestsResponseAdapter(mock_resp).is_server_error

    def test_response_is_server_error_false(self, mocker: MockerFixture):
        """NiquestsResponseAdapter.is_server_error is False for 2xx status."""
        mock_resp: niquests.Response = mocker.MagicMock()
        mock_resp.status_code = 200
        assert not NiquestsResponseAdapter(mock_resp).is_server_error

    def test_response_raise_for_status_converts_exception(self, mocker: MockerFixture):
        """raise_for_status wraps niquests.HTTPError as HttpStatusError."""
        mock_resp: niquests.Response = mocker.MagicMock()
        mock_resp.raise_for_status.side_effect = niquests.exceptions.HTTPError("500")
        adapter = NiquestsResponseAdapter(mock_resp)
        with pytest.raises(HttpStatusError):
            adapter.raise_for_status()
