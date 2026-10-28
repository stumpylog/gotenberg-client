# SPDX-FileCopyrightText: 2023-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
import re
import time
from http import HTTPStatus
from pathlib import Path

import httpx
import pytest
from pypdf import PdfReader

from gotenberg_client.responses import SingleFileResponse
from gotenberg_client.responses import ZipFileResponse


def verify_basic_response_values_pdf(response: SingleFileResponse | ZipFileResponse) -> None:
    assert response.status_code == HTTPStatus.OK
    assert "Content-Type" in response.headers
    assert response.headers["Content-Type"] == "application/pdf"


def verify_stream_contains(request, key: str, value: str) -> None:
    content_type = request.headers["Content-Type"]
    assert "multipart/form-data" in content_type

    boundary = content_type.split("boundary=")[1]

    parts = request.content.split(f"--{boundary}".encode())

    form_field_found = any(f'name="{key}"'.encode() in part and value.encode() in part for part in parts)
    assert form_field_found, f'Key "{key}" with value "{value}" not found in stream'


def extract_text(pdf_path: Path) -> list[str]:
    """
    Extracts text from a PDF and returns it as a list of lines.
    All whitespace (tabs, multiple spaces) is normalized to single spaces.
    """
    with PdfReader(pdf_path) as reader:
        return [re.sub(r"\s+", " ", line) for page in reader.pages for line in page.extract_text().splitlines()]


def ensure_gotenberg_healthy(url: str, *, timeout: float = 60.0) -> None:
    """
    Waits until Gotenberg's /health reports up.

    Gotenberg only restarts a failed Chromium when the next Chromium conversion arrives, so after any
    Chromium failure /health returns 503 until then, however long it is polled. A trivial conversion
    makes Gotenberg restart it.
    """
    deadline = time.monotonic() + timeout
    last = "no response"
    while True:
        try:
            response = httpx.get(f"{url}/health")
        except httpx.HTTPError as e:
            last = repr(e)
        else:
            if response.status_code == HTTPStatus.OK:
                return
            last = f"{response.status_code} {response.text}"
            httpx.post(
                f"{url}/forms/chromium/convert/html",
                files={"index.html": ("index.html", b"<html></html>", "text/html")},
                timeout=timeout,
            )
        if time.monotonic() >= deadline:
            pytest.fail(f"Gotenberg not healthy after {timeout}s, last response: {last}")
        time.sleep(1)
