# SPDX-FileCopyrightText: 2025-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
"""
An in-memory upload must be sent in full on every attempt of run_with_retry, whichever backend is used.
A local server stands in for Gotenberg, as pytest-httpx only intercepts the httpx backend.
"""

import threading
from collections.abc import Generator
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
from io import BytesIO

import pytest

from gotenberg_client import BackendType
from gotenberg_client import SyncGotenbergClient

PAYLOAD = b"in-memory-docx-bytes"


@pytest.fixture
def flaky_server() -> Generator[tuple[str, list[bytes]], None, None]:
    """
    Serves a 503 to the first POST and a PDF to every later one, recording each request body.
    """
    bodies: list[bytes] = []

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self) -> None:
            bodies.append(self.rfile.read(int(self.headers["Content-Length"])))
            self.send_response(HTTPStatus.SERVICE_UNAVAILABLE if len(bodies) == 1 else HTTPStatus.OK)
            self.send_header("Content-Type", "application/pdf")
            self.send_header("Content-Length", "4")
            self.end_headers()
            self.wfile.write(b"%PDF")

        def log_message(self, format: str, *args: object) -> None:  # noqa: A002
            pass

    server = HTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_port}", bodies
    server.shutdown()
    server.server_close()
    thread.join()


class TestInMemoryRetry:
    @pytest.mark.parametrize(
        "backend",
        [
            pytest.param("httpx", marks=pytest.mark.httpx),
            pytest.param("niquests", marks=pytest.mark.niquests),
            pytest.param("requests", marks=pytest.mark.requests),
        ],
    )
    def test_retry_resends_the_whole_stream(
        self,
        flaky_server: tuple[str, list[bytes]],
        backend: BackendType,
    ):
        pytest.importorskip(backend)
        host, bodies = flaky_server

        with SyncGotenbergClient(host=host, backend=backend) as client, client.libre_office.to_pdf() as route:
            resp = route.convert_in_memory_file(BytesIO(PAYLOAD), name="a.docx").run_with_retry(
                initial_retry_wait=0.01,
            )

        assert resp.status_code == HTTPStatus.OK
        assert [PAYLOAD in body for body in bodies] == [True, True]
