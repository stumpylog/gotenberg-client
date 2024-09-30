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
def sample_directory() -> Path:
    return Path(__file__).parent.resolve() / "samples"


@pytest.fixture(scope="session")
def output_file_save_directory() -> Path:
    return Path(__file__).parent.resolve() / "outputs"


@pytest.fixture(scope="session")
def save_output_files(output_file_save_directory: Path) -> bool:
    val = "SAVE_TEST_OUTPUT" in os.environ
    if val:
        shutil.rmtree(output_file_save_directory, ignore_errors=True)
        output_file_save_directory.mkdir()
    return val


@pytest.fixture
def output_saver_factory(request, save_output_files: bool, output_file_save_directory: Path):  # noqa: FBT001
    def _save_the_item(response: Union[SingleFileResponse, ZipFileResponse]):
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
