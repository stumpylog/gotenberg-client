# SPDX-FileCopyrightText: 2023-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
import logging
import os
import shutil
from pathlib import Path
from typing import Final
from typing import Generator

import pytest

from gotenberg_client import GotenbergClient

GOTENBERG_URL: Final[str] = os.getenv("GOTENBERG_URL", "http://localhost:3000")

SAMPLE_DIR: Final[Path] = Path(__file__).parent.resolve() / "samples"
SAVE_DIR: Final[Path] = Path(__file__).parent.resolve() / "outputs"
SAVE_OUTPUTS: Final[bool] = "SAVE_TEST_OUTPUT" in os.environ

if SAVE_OUTPUTS:
    shutil.rmtree(SAVE_DIR, ignore_errors=True)
    SAVE_DIR.mkdir()


@pytest.fixture()
def client() -> Generator[GotenbergClient, None, None]:
    with GotenbergClient(host=GOTENBERG_URL, log_level=logging.INFO) as client:
        yield client
