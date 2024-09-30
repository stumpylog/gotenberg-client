# SPDX-FileCopyrightText: 2023-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
import logging
import os
import shutil
from pathlib import Path
from typing import Generator
from typing import Union

import pytest

from gotenberg_client import GotenbergClient
from gotenberg_client import SingleFileResponse
from gotenberg_client import ZipFileResponse


@pytest.fixture(scope="session")
def gotenberg_host() -> str:
    return os.getenv("GOTENBERG_URL", "http://localhost:3000")


@pytest.fixture(scope="session")
def web_server_host() -> str:
    return os.getenv("WEBSERVER_HOST", "http://localhost:8888")


@pytest.fixture(scope="session")
def sample_directory() -> Path:
    return Path(__file__).parent.resolve() / "samples"


@pytest.fixture(scope="session")
def basic_html_file(sample_directory: Path) -> Path:
    return sample_directory / "basic.html"


@pytest.fixture(scope="session")
def footer_html_file(sample_directory: Path) -> Path:
    return sample_directory / "footer.html"


@pytest.fixture(scope="session")
def complex_html_file(sample_directory: Path) -> Path:
    return sample_directory / "complex.html"


@pytest.fixture(scope="session")
def header_html_file(sample_directory: Path) -> Path:
    return sample_directory / "header.html"


@pytest.fixture(scope="session")
def img_gif_file(sample_directory: Path) -> Path:
    return sample_directory / "img.gif"


@pytest.fixture(scope="session")
def font_file(sample_directory: Path) -> Path:
    return sample_directory / "font.woff"


@pytest.fixture(scope="session")
def css_style_file(sample_directory: Path) -> Path:
    return sample_directory / "style.css"


@pytest.fixture(scope="session")
def markdown_index_file(sample_directory: Path) -> Path:
    return sample_directory / "markdown_index.html"


@pytest.fixture(scope="session")
def markdown_sample_one_file(sample_directory: Path) -> Path:
    return sample_directory / "markdown1.md"


@pytest.fixture(scope="session")
def markdown_sample_two_file(sample_directory: Path) -> Path:
    return sample_directory / "markdown2.md"


@pytest.fixture(scope="session")
def docx_sample_file(sample_directory: Path) -> Path:
    return sample_directory / "sample.docx"


@pytest.fixture(scope="session")
def odt_sample_file(sample_directory: Path) -> Path:
    return sample_directory / "sample.odt"


@pytest.fixture(scope="session")
def xlsx_sample_file(sample_directory: Path) -> Path:
    return sample_directory / "sample.xlsx"


@pytest.fixture(scope="session")
def ods_sample_file(sample_directory: Path) -> Path:
    return sample_directory / "sample.ods"


@pytest.fixture(scope="session")
def pdf_sample_one_file(sample_directory: Path) -> Path:
    return sample_directory / "sample1.pdf"


@pytest.fixture(scope="session")
def output_file_save_directory() -> Path:
    return Path(__file__).parent.resolve() / "outputs"


@pytest.fixture(scope="session")
def save_output_files(output_file_save_directory: Path) -> bool:
    val = True
    if val:
        shutil.rmtree(output_file_save_directory, ignore_errors=True)
        output_file_save_directory.mkdir()
    return val


@pytest.fixture
def output_saver_factory(request, save_output_files: bool, output_file_save_directory: Path):  # noqa: FBT001
    def _save_the_item(response: Union[SingleFileResponse, ZipFileResponse], extra: str = ""):  # noqa: ARG001
        if save_output_files:
            extension_mapping = {
                "application/zip": ".zip",
                "application/pdf": ".pdf",
                "image/png": ".png",
            }
            extension = extension_mapping[response.headers["Content-Type"]]
            response.to_file(output_file_save_directory / f"{request.node.originalname}{extension}")

    return _save_the_item


@pytest.fixture
def client(gotenberg_host: str) -> Generator[GotenbergClient, None, None]:
    with GotenbergClient(host=gotenberg_host, log_level=logging.INFO) as client:
        yield client
