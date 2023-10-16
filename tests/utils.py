import time
import warnings

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
        - Attempt 1 - 20s following failure
        - Attempt 2 - 40s following failure
        - Attempt 3 - 80s following failure
        - Attempt 4 - 160s
        - Attempt 5 - 320s

    """
    result = None
    succeeded = False
    retry_time = 20.0
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
