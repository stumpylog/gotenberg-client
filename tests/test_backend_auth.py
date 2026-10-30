# SPDX-FileCopyrightText: 2025-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
"""Authentication through public clients and real backend request preparation, without servers."""

import subprocess
import sys
from hashlib import sha256
from io import BytesIO
from typing import get_type_hints

import httpx
import httpx2
import niquests
import niquests.auth
import pytest
import requests
import requests.auth

from gotenberg_client import AsyncGotenbergClient
from gotenberg_client import SingleFileResponse
from gotenberg_client import SyncGotenbergClient

_HOST = "https://gotenberg.invalid"
_PDF = b"%PDF-mocked"
_AUTH_KINDS = ["none", "tuple", "basic", "body"]
_AUTH_SELECTIONS = [(kind, "explicit") for kind in _AUTH_KINDS] + [(kind, "auto") for kind in ("basic", "body")]


@pytest.mark.parametrize(
    ("backend", "selection"),
    [("none", "explicit")]
    + [
        (backend, selection)
        for backend in ("httpx", "httpx2", "requests", "niquests")
        for selection in ("explicit", "auto")
    ],
)
def test_import_without_optional_backends(backend, selection):
    """Only the explicitly selected backend may be imported or required."""
    script = """
import asyncio
import importlib.abc
import importlib
import sys
from typing import get_type_hints

selected, selection = sys.argv[1:]
blocked = {'httpx', 'httpx2', 'requests', 'niquests'} - {selected}

class BlockBackends(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in blocked:
            raise ImportError(f'Unexpected backend import: {fullname}')

sys.meta_path.insert(0, BlockBackends())
from gotenberg_client import AuthType, AsyncGotenbergClient, SyncGotenbergClient

for client_class in (SyncGotenbergClient, AsyncGotenbergClient):
    assert 'auth' in get_type_hints(client_class.__init__)

if selected != 'none':
    module = importlib.import_module(selected)
    cls = module.BasicAuth if selected in {'httpx', 'httpx2'} else module.auth.HTTPBasicAuth
    auth = cls('user', 'secret')
    backend = selected if selection == 'explicit' else 'auto'
    with SyncGotenbergClient('https://gotenberg.invalid', backend=backend, auth=auth):
        pass
    if selected != 'requests':
        async def check_async():
            async with AsyncGotenbergClient('https://gotenberg.invalid', backend=backend, auth=auth):
                pass
        asyncio.run(check_async())
"""
    subprocess.run([sys.executable, "-c", script, backend, selection], check=True)  # noqa: S603


def _sign(request, body):
    request.headers["Authorization"] = f"Body {sha256(body).hexdigest()}"
    return request


def _httpx_auth(module, kind):
    if kind == "none":
        return None
    if kind == "tuple":
        return ("user", "secret")
    if kind == "basic":
        return module.BasicAuth("user", "secret")

    class BodyAuth(module.Auth):
        requires_request_body = True

        def auth_flow(self, request):
            yield _sign(request, request.content)

    return BodyAuth()


def _session_auth(module, kind):
    if kind == "none":
        return None
    if kind == "tuple":
        return ("user", "secret")
    if kind == "basic":
        return module.auth.HTTPBasicAuth("user", "secret")

    class BodyAuth(module.auth.AuthBase):
        def __call__(self, request):
            return _sign(request, request.body)

    return BodyAuth()


def _assert_upload(headers, body, kind, basic_html_file):
    assert headers["Content-Type"].startswith("multipart/form-data; boundary=")
    boundary = headers["Content-Type"].split("boundary=", 1)[1].encode()
    assert body.startswith(b"--" + boundary + b"\r\n")
    assert body.endswith(b"--" + boundary + b"--\r\n")
    assert b'filename="index.html"' in body
    assert basic_html_file.read_bytes() in body
    assert b'filename="style.css"' in body
    assert b"body {color: red}" in body
    assert b'name="printBackground"\r\n\r\ntrue' in body
    if kind == "none":
        assert "Authorization" not in headers
    elif kind in {"tuple", "basic"}:
        assert headers["Authorization"] == "Basic dXNlcjpzZWNyZXQ="
    else:
        # The signature must cover exactly the bytes received by the transport,
        # including the multipart boundaries, form fields and every uploaded file.
        assert headers["Authorization"] == f"Body {sha256(body).hexdigest()}"


def _configure(route, basic_html_file):
    return (
        route.index(basic_html_file)
        .string_resource("body {color: red}", "style.css", "text/css")
        .print_background(print_background=True)
    )


def _assert_response(response):
    assert isinstance(response, SingleFileResponse)
    assert response.content == _PDF
    assert response.status_code == 200


@pytest.fixture(params=[pytest.param(httpx, marks=pytest.mark.httpx), pytest.param(httpx2, marks=pytest.mark.httpx2)])
def http_backend(request, httpx_mock, mocker):
    module = request.param
    captured = []

    def handle(request):
        request.read()
        captured.append((request.headers, request.content))
        return module.Response(200, headers={"Content-Type": "application/pdf"}, content=_PDF)

    async def async_handle(request):
        await request.aread()
        return handle(request)

    if module is httpx:
        httpx_mock.add_callback(handle)
    else:
        mocker.patch.object(module.HTTPTransport, "handle_request", side_effect=handle)
        mocker.patch.object(module.AsyncHTTPTransport, "handle_async_request", side_effect=async_handle)
    return module, captured


@pytest.mark.parametrize(("kind", "selection"), _AUTH_SELECTIONS)
def test_httpx_auth_sync(http_backend, kind, selection, basic_html_file):
    module, captured = http_backend
    backend = module.__name__ if selection == "explicit" else "auto"
    with (
        SyncGotenbergClient(_HOST, backend=backend, auth=_httpx_auth(module, kind)) as client,
        client.chromium.html_to_pdf() as route,
    ):
        _assert_response(_configure(route, basic_html_file).run())
    assert len(captured) == 1
    _assert_upload(*captured[0], kind, basic_html_file)


@pytest.mark.async_route
@pytest.mark.parametrize(("kind", "selection"), _AUTH_SELECTIONS)
async def test_httpx_auth_async(http_backend, kind, selection, basic_html_file):
    module, captured = http_backend
    backend = module.__name__ if selection == "explicit" else "auto"
    async with (
        AsyncGotenbergClient(_HOST, backend=backend, auth=_httpx_auth(module, kind)) as client,
        client.chromium.html_to_pdf() as route,
    ):
        _assert_response(await _configure(route, basic_html_file).run())
    assert len(captured) == 1
    _assert_upload(*captured[0], kind, basic_html_file)


def _session_response(module, request):
    response = module.Response()
    response.status_code = 200
    response.headers["Content-Type"] = "application/pdf"
    response._content = _PDF
    response.raw = BytesIO(_PDF)
    response.request = request
    response.url = request.url
    return response


@pytest.mark.parametrize(
    "module",
    [pytest.param(requests, marks=pytest.mark.requests), pytest.param(niquests, marks=pytest.mark.niquests)],
)
@pytest.mark.parametrize(("kind", "selection"), _AUTH_SELECTIONS)
def test_session_auth_sync(module, kind, selection, basic_html_file, mocker):
    def send(request, **_kwargs):
        _assert_upload(request.headers, request.body, kind, basic_html_file)
        return _session_response(module, request)

    transport = mocker.patch.object(module.adapters.HTTPAdapter, "send", side_effect=send)
    backend = module.__name__ if selection == "explicit" else "auto"
    with (
        SyncGotenbergClient(_HOST, backend=backend, auth=_session_auth(module, kind)) as client,
        client.chromium.html_to_pdf() as route,
    ):
        _assert_response(_configure(route, basic_html_file).run())
    transport.assert_called_once()


@pytest.mark.niquests
@pytest.mark.async_route
@pytest.mark.parametrize(
    ("kind", "selection"),
    _AUTH_SELECTIONS + [("async_body", selection) for selection in ("explicit", "auto")],
)
async def test_niquests_auth_async(kind, selection, basic_html_file, mocker):
    if kind == "async_body":

        class AsyncBodyAuth(niquests.auth.AsyncAuthBase):
            async def __call__(self, request):
                return _sign(request, request.body)

        auth = AsyncBodyAuth()
    else:
        auth = _session_auth(niquests, kind)

    async def send(request, **_kwargs):
        _assert_upload(request.headers, request.body, kind, basic_html_file)
        return _session_response(niquests, request)

    transport = mocker.patch.object(niquests.adapters.AsyncHTTPAdapter, "send", side_effect=send)
    backend = "niquests" if selection == "explicit" else "auto"
    async with (
        AsyncGotenbergClient(_HOST, backend=backend, auth=auth) as client,
        client.chromium.html_to_pdf() as route,
    ):
        _assert_response(await _configure(route, basic_html_file).run())
    transport.assert_awaited_once()


_NATIVE_AUTH_CLASSES = {
    "httpx": httpx.BasicAuth,
    "httpx2": httpx2.BasicAuth,
    "requests": requests.auth.HTTPBasicAuth,
    "niquests": niquests.auth.HTTPBasicAuth,
}


_CLIENT_BACKENDS = [
    (client_class, backend)
    for client_class in (SyncGotenbergClient, AsyncGotenbergClient)
    for backend in _NATIVE_AUTH_CLASSES
    if client_class is SyncGotenbergClient or backend != "requests"
]


@pytest.mark.parametrize(
    ("client_class", "backend", "auth_class"),
    [
        (client_class, backend, auth_class)
        for client_class, backend in _CLIENT_BACKENDS
        for auth_backend, auth_class in _NATIVE_AUTH_CLASSES.items()
        if auth_backend != backend
    ],
)
def test_auth_backend_mismatch(client_class, backend, auth_class):
    auth = auth_class("user", "secret")
    with pytest.raises(TypeError, match=f"Invalid auth for backend '{backend}'") as error:
        client_class(_HOST, backend=backend, auth=auth)
    assert f"{auth_class.__module__}.{auth_class.__qualname__}" in str(error.value)
    assert "tuple of strings" in str(error.value)


@pytest.mark.parametrize(("client_class", "backend"), _CLIENT_BACKENDS)
@pytest.mark.parametrize(
    "auth",
    [object(), "token", lambda request: request, ("user",), ("user", 123), ("u", "p", "x")],
)
def test_invalid_auth(client_class, backend, auth):
    with pytest.raises(TypeError, match=f"Invalid auth for backend '{backend}'"):
        client_class(_HOST, backend=backend, auth=auth)


@pytest.mark.parametrize("backend", ["niquests", "auto"])
@pytest.mark.parametrize("auth_class", [niquests.auth.AsyncAuthBase, niquests.auth.AsyncHTTPDigestAuth])
def test_niquests_async_auth_rejected_by_sync_client(auth_class, backend):
    auth = auth_class("user", "secret") if auth_class is niquests.auth.AsyncHTTPDigestAuth else auth_class()
    with pytest.raises(TypeError, match="Asynchronous Niquests auth requires AsyncGotenbergClient"):
        SyncGotenbergClient(_HOST, backend=backend, auth=auth)


@pytest.mark.niquests
@pytest.mark.async_route
async def test_niquests_without_async_auth_base(mocker):
    """Niquests versions predating AsyncAuthBase must still accept sync auth."""
    mocker.patch("gotenberg_client._http_backends._niquests._ASYNC_AUTH_BASE", None)
    async with AsyncGotenbergClient(_HOST, backend="niquests", auth=niquests.auth.HTTPBasicAuth("user", "secret")):
        pass


@pytest.mark.parametrize("client_class", [SyncGotenbergClient, AsyncGotenbergClient])
def test_client_auth_type_hints(client_class):
    assert "auth" in get_type_hints(client_class.__init__)


@pytest.mark.parametrize("auth", [requests.auth.HTTPBasicAuth("user", "secret"), _session_auth(requests, "body")])
def test_auto_requests_auth_rejected_by_async_client(auth):
    with pytest.raises(ValueError, match="only supports synchronous usage"):
        AsyncGotenbergClient(_HOST, auth=auth)
