# SPDX-FileCopyrightText: 2023-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
import shutil
import subprocess
import tempfile
from pathlib import Path

from httpx._multipart import DataField
from httpx._multipart import FileField
from httpx._multipart import MultipartStream


def verify_stream_contains(key: str, value: str, stream: MultipartStream) -> None:
    for item in stream.fields:
        if isinstance(item, FileField):
            continue
        elif isinstance(item, DataField) and item.name == key:
            actual_value = item.value
            if isinstance(actual_value, bytes):
                actual_value = actual_value.decode("utf-8")
            assert actual_value == value, f"Key '{actual_value}' /= {value}"
            return

    msg = f'Key "{key}" with value "{value}" not found in stream'
    raise AssertionError(msg)


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
            [  # noqa: S603
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
