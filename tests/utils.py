# SPDX-FileCopyrightText: 2023-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
import shutil
import subprocess
import tempfile
from http import HTTPStatus
from pathlib import Path
from typing import Union

from gotenberg_client.responses import SingleFileResponse
from gotenberg_client.responses import ZipFileResponse


def verify_basic_response_values_pdf(response: Union[SingleFileResponse, ZipFileResponse]) -> None:
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


def extract_text(pdf_path: Path) -> str:
    """
    Using pdftotext from poppler, extracts the text of a PDF into a file,
    then reads the file contents and returns it
    """
    pdf_to_text = shutil.which("pdftotext")
    assert pdf_to_text is not None
    with tempfile.NamedTemporaryFile(
        mode="w+",
    ) as tmp:
        subprocess.run(
            [
                pdf_to_text,
                "-q",
                "-layout",
                "-enc",
                "UTF-8",
                str(pdf_path),
                tmp.name,
            ],
            check=True,
        )
        return tmp.read()
