import shutil
import subprocess
import tempfile
import time
import warnings
from pathlib import Path

from httpx import HTTPStatusError
from httpx import Response
from httpx._multipart import DataField
from httpx._multipart import FileField
from httpx._multipart import MultipartStream

from gotenberg_client._base import BaseRoute


def verify_stream_contains(key: str, value: str, stream: MultipartStream):
    for item in stream.fields:
        if isinstance(item, FileField):
            continue
        elif isinstance(item, DataField) and item.name == key:
            assert item.value == value, f"Key {item.value} /= {value}"
            return

    msg = f'Key "{key}" with value "{value}" not found in stream'
    raise AssertionError(msg)


def call_run_with_server_error_handling(route: BaseRoute) -> Response:
    """
    For whatever reason, the images started during the test pipeline like to
    segfault sometimes, crash and otherwise fail randomly, when run with the
    exact files that usually pass.

    So, this function will retry the given method/function up to 3 times, with larger backoff
    periods between each attempt, in hopes the issue resolves itself during
    one attempt to parse.

    This will wait the following:
        - Attempt 1 - 5s following failure
        - Attempt 2 - 10s following failure
        - Attempt 3 - 20s following failure
        - Attempt 4 - 40s following failure
        - Attempt 5 - 80s following failure

    """
    result = None
    succeeded = False
    retry_time = 5.0
    retry_count = 0
    max_retry_count = 5

    while retry_count < max_retry_count and not succeeded:
        try:
            return route.run()
        except HTTPStatusError as e:  # pragma: no cover
            warnings.warn(f"HTTP error: {e}", stacklevel=1)
        except Exception as e:  # pragma: no cover
            warnings.warn(f"Unexpected error: {e}", stacklevel=1)

        retry_count = retry_count + 1

        time.sleep(retry_time)
        retry_time = retry_time * 2.0

    return result


def extract_text(pdf_path: Path) -> str:
    """
    Using pdftotext from poppler, extracts the text of a PDF into a file,
    then reads the file contents and returns it
    """
    with tempfile.NamedTemporaryFile(
        mode="w+",
    ) as tmp:
        subprocess.run(
            [  # noqa: S603
                shutil.which("pdftotext"),
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
