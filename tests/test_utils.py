# SPDX-FileCopyrightText: 2025-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
"""
Tests for MIME type detection helpers. No Docker required.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from gotenberg_client import _utils
from gotenberg_client._utils import guess_mime_type_magika

if TYPE_CHECKING:
    from pathlib import Path

    from pytest_mock import MockerFixture

HTML_BYTES = b"<!DOCTYPE html><html><head><title>t</title></head><body><p>hi</p></body></html>"
PDF_BYTES = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF\n"


class TestGuessMimeTypeMagika:
    @pytest.mark.parametrize(
        ("filename", "content", "expected"),
        [
            ("page.html", HTML_BYTES, "text/html"),
            ("data.json", b'{"a": 1, "b": [1, 2, 3], "c": {"d": "e"}}', "application/json"),
            ("doc.pdf", PDF_BYTES, "application/pdf"),
        ],
    )
    def test_detects_content(self, tmp_path: Path, filename: str, content: bytes, expected: str):
        path = tmp_path / filename
        path.write_bytes(content)
        assert guess_mime_type_magika(path) == expected

    def test_accepts_str_path(self, tmp_path: Path):
        path = tmp_path / "data.json"
        path.write_bytes(b'{"a": 1, "b": [1, 2, 3], "c": {"d": "e"}}')
        assert guess_mime_type_magika(str(path)) == "application/json"

    def test_model_is_loaded_once(self, tmp_path: Path, mocker: MockerFixture):
        _utils._get_magika.cache_clear()
        mocked = mocker.patch("magika.Magika")
        path = tmp_path / "a.txt"
        path.write_bytes(b"hello")
        guess_mime_type_magika(path)
        guess_mime_type_magika(path)
        mocked.assert_called_once()
        _utils._get_magika.cache_clear()


class TestSelectMimeGuesser:
    @pytest.mark.parametrize(
        ("installed", "expected"),
        [
            ({"magic", "magika"}, _utils.guess_mime_type_magic),
            ({"magic"}, _utils.guess_mime_type_magic),
            ({"magika"}, _utils.guess_mime_type_magika),
            (set(), _utils.guess_mime_type_stdlib),
        ],
    )
    def test_preference_order(self, mocker: MockerFixture, installed: set[str], expected: object):
        mocker.patch.object(_utils, "find_spec", side_effect=lambda name: object() if name in installed else None)
        assert _utils._select_mime_guesser() is expected
