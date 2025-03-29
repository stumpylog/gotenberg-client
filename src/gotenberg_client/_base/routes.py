# SPDX-FileCopyrightText: 2025-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
import asyncio
import logging
from abc import ABC
from abc import abstractmethod
from collections.abc import Coroutine
from contextlib import AbstractAsyncContextManager
from contextlib import AbstractContextManager
from contextlib import ExitStack
from pathlib import Path
from time import sleep
from types import TracebackType
from typing import Any
from typing import Generic
from typing import Optional

from httpx import AsyncClient
from httpx import Client
from httpx import HTTPStatusError
from httpx import Response
from httpx._types import RequestFiles

from gotenberg_client._common import ClientT
from gotenberg_client._errors import MaxRetriesExceededError
from gotenberg_client._errors import UnreachableCodeError
from gotenberg_client._typing_compat import Self
from gotenberg_client._utils import guess_mime_type
from gotenberg_client.responses import SingleFileResponse
from gotenberg_client.responses import ZipFileResponse


class BaseRoute(ABC, Generic[ClientT]):
    """
    The base implementation of a Gotenberg API route.  Anything shared between all routes,
    and common utilities such as posting the data or returning the response goes here
    """

    def __init__(self, client: ClientT, route_url: str, log: logging.Logger) -> None:
        self._client = client
        self._route_url = route_url
        self._log = log
        self._stack = ExitStack()
        self._response_is_zip: bool = False
        # These are the options that will be set to Gotenberg.  Things like PDF/A
        self._form_data: dict[str, str] = {}
        # These are the names of files, mapping to their Path
        self._file_map: dict[str, Path] = {}
        # Additional in memory resources, mapping the referenced name to the content and an optional mimetype
        self._in_memory_resources: dict[str, tuple[str, Optional[str]]] = {}
        # Any header that will also be sent
        self._headers: dict[str, str] = {}
        self._next = 1

    @abstractmethod
    def post_data(self) -> Response | Coroutine[Any, Any, Response]:
        """
        Executes the configured route against the server and returns the resulting
        Response.
        """

    @abstractmethod
    def post_data_with_retry(
        self,
        *,
        max_retry_count: int = 5,
        initial_retry_wait: float | int = 5.0,
        retry_scale: float | int = 2.0,
    ) -> Response | Coroutine[Any, Any, Response]:
        """
        For whatever reason, Gotenberg often returns HTTP 503 errors, even with the same files.
        Hopefully v8 will improve upon this with its updates, but this is provided for convenience.

        This function will retry the given method/function up to X times, with larger backoff
        periods between each attempt, in hopes the issue resolves itself during
        one attempt to parse.

        This will wait the following (by default):
            - Attempt 1 - 5s following failure
            - Attempt 2 - 10s following failure
            - Attempt 3 - 20s following failure
            - Attempt 4 - 40s following failure
            - Attempt 5 - 80s following failure

        """

    @abstractmethod
    def run(self) -> SingleFileResponse | ZipFileResponse | Coroutine[Any, Any, SingleFileResponse | ZipFileResponse]:
        """
        Execute the API request to Gotenberg.

        This method sends the configured request to the Gotenberg service and returns the response.

        Returns:
            SingleFileResponse: An object containing the response from the Gotenberg API

        Raises:
            httpx.Error: Any errors from httpx will be raised
        """

    @abstractmethod
    def run_with_retry(
        self,
        *,
        max_retry_count: int = 5,
        initial_retry_wait: float | int = 5.0,
        retry_scale: float | int = 2.0,
    ) -> SingleFileResponse | ZipFileResponse | Coroutine[Any, Any, SingleFileResponse | ZipFileResponse]:
        """
        Execute the API request with a retry mechanism.

        This method attempts to run the API request and automatically retries in case of failures.
        It uses an exponential backoff strategy for retries.

        Args:
            max_retry_count (int, optional): The maximum number of retry attempts. Defaults to 5.
            initial_retry_wait (float or int, optional): The initial wait time between retries in seconds.
                Defaults to 5. Can be int or float.
            retry_scale (float or int, optional): The scale factor for the exponential backoff.
                Defaults to 2. Can be int or float.

        Returns:
            SingleFileResponse: The response object containing the result of the API call.

        Raises:
            MaxRetriesExceededError: If the maximum number of retries is exceeded without a successful response.
        """

    def reset(self) -> None:
        """
        Calls all context manager __exit__ via the ExitStack and clears
        all set files and form data options
        """
        self._stack.close()
        self._form_data.clear()
        self._file_map.clear()
        self._headers.pop("Gotenberg-Output-Filename", None)
        self._headers.pop("Gotenberg-Trace", None)

    def close(self) -> None:
        """
        Alias for reset
        """
        self.reset()

    def _get_all_resources(self) -> RequestFiles:
        """
        Deals with opening all provided files for multi-part uploads, including
        pushing their new contexts onto the stack to ensure resources like file
        handles are cleaned up
        """
        resources = {}
        for filename in self._file_map:
            file_path = self._file_map[filename]

            # Helpful but not necessary to provide the mime type when possible
            mime_type = guess_mime_type(file_path)
            if mime_type is not None:
                resources.update(
                    {filename: (filename, self._stack.enter_context(file_path.open("rb")), mime_type)},
                )
            else:  # pragma: no cover
                resources.update({filename: (filename, self._stack.enter_context(file_path.open("rb")))})  # type: ignore [dict-item]

        for resource_name in self._in_memory_resources:
            data, mime_type = self._in_memory_resources[resource_name]
            if mime_type is not None:
                resources.update({resource_name: (resource_name, data, mime_type)})  # type: ignore [dict-item]
            else:
                resources.update({resource_name: (resource_name, data)})  # type: ignore [dict-item]

        return resources

    def _add_file_map(self, filepath: Path, *, name: Optional[str] = None) -> None:
        """
        Small helper to handle bookkeeping of files for later opening.  The name is
        optional to support those things which are required to have a certain name
        generally for ordering or just to be found at all
        """
        if name is None:
            name = filepath.name

        if name in self._file_map:  # pragma: no cover
            self._log.warning(f"{name} has already been provided, overwriting anyway")

        self._file_map[name] = filepath

    def _add_in_memory_file(self, data: str, *, name: str, mime_type: Optional[str] = None) -> None:
        """
        Adds a file with the given name and optional mime type, but its data is fully in memory
        """
        if name in self._in_memory_resources:  # pragma: no cover
            self._log.warning(f"{name} has already been provided, overwriting anyway")

        self._in_memory_resources[name] = (data, mime_type)

    def output_filename(self, filename: str) -> Self:
        """
        Sets the header for controlling the output filename.  See
        https://gotenberg.dev/docs/routes#output-filename

        Args:
            extra_headers (Dict[str, str]): A dictionary of additional headers to include in webhook calls.
        """
        self._client.headers.update({"Gotenberg-Output-Filename": filename})
        return self

    def trace_id(self, trace_id: str) -> Self:
        """
        Configures the trace ID for Gotenberg. See
        https://gotenberg.dev/docs/routes#request-tracing
        """
        self._client.headers.update({"Gotenberg-Trace": trace_id})
        return self


class SyncBaseRoute(BaseRoute[Client], AbstractContextManager):
    def __enter__(self) -> Self:
        self.reset()
        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        self.close()

    def post_data(self) -> Response:
        resp = self._client.post(
            url=self._route_url,
            headers=self._headers,
            data=self._form_data,
            files=self._get_all_resources(),
        )
        resp.raise_for_status()
        return resp

    def post_data_with_retry(
        self,
        *,
        max_retry_count: int = 5,
        initial_retry_wait: float | int = 5.0,
        retry_scale: float | int = 2.0,
    ) -> Response:
        retry_time = initial_retry_wait
        current_retry_count = 0

        while current_retry_count < max_retry_count:
            current_retry_count = current_retry_count + 1

            try:
                return self.post_data()
            except HTTPStatusError as e:
                self._log.warning(f"HTTP error: {e}", stacklevel=1)

                # This only handles status codes which are 5xx, indicating the server had a problem
                # Not 4xx, with probably means a problem with the request
                if not e.response.is_server_error:
                    raise

                # Don't do the extra waiting, return right away
                if current_retry_count >= max_retry_count:
                    raise MaxRetriesExceededError(response=e.response) from e

            except Exception as e:  # pragma: no cover
                self._log.warning(f"Unexpected error: {e}", stacklevel=1)
                if current_retry_count > -max_retry_count:
                    raise

            sleep(retry_time)
            retry_time = retry_time * retry_scale

        raise UnreachableCodeError  # pragma: no cover

    def run(self) -> SingleFileResponse | ZipFileResponse:
        response = self.post_data()
        if self._response_is_zip:
            return ZipFileResponse(response.status_code, response.headers, response.content)
        return SingleFileResponse(response.status_code, response.headers, response.content)

    def run_with_retry(
        self,
        *,
        max_retry_count: int = 5,
        initial_retry_wait: float | int = 5.0,
        retry_scale: float | int = 2.0,
    ) -> SingleFileResponse | ZipFileResponse:
        response = self.post_data_with_retry(
            max_retry_count=max_retry_count,
            initial_retry_wait=initial_retry_wait,
            retry_scale=retry_scale,
        )
        if self._response_is_zip:
            return ZipFileResponse(response.status_code, response.headers, response.content)
        return SingleFileResponse(response.status_code, response.headers, response.content)


class AsyncBaseRoute(BaseRoute[AsyncClient], AbstractAsyncContextManager):
    async def __aenter__(self) -> Self:
        self.reset()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        self.close()

    async def post_data(self) -> Response:
        """
        Sends the configured data to the Gotenberg server
        """
        resp = await self._client.post(
            url=self._route_url,
            headers=self._headers,
            data=self._form_data,
            files=self._get_all_resources(),
        )
        resp.raise_for_status()
        return resp

    async def post_data_with_retry(
        self,
        *,
        max_retry_count: int = 5,
        initial_retry_wait: float | int = 5.0,
        retry_scale: float | int = 2.0,
    ) -> Response:
        retry_time = initial_retry_wait
        current_retry_count = 0

        while current_retry_count < max_retry_count:
            current_retry_count = current_retry_count + 1

            try:
                return await self.post_data()
            except HTTPStatusError as e:
                self._log.warning(f"HTTP error: {e}", stacklevel=1)

                # This only handles status codes which are 5xx, indicating the server had a problem
                # Not 4xx, with probably means a problem with the request
                if not e.response.is_server_error:
                    raise

                # Don't do the extra waiting, return right away
                if current_retry_count >= max_retry_count:
                    raise MaxRetriesExceededError(response=e.response) from e

            except Exception as e:  # pragma: no cover
                self._log.warning(f"Unexpected error: {e}", stacklevel=1)
                if current_retry_count > -max_retry_count:
                    raise

            await asyncio.sleep(retry_time)
            retry_time = retry_time * retry_scale

        raise UnreachableCodeError  # pragma: no cover

    async def run(self) -> SingleFileResponse | ZipFileResponse:
        response = await self.post_data()
        if self._response_is_zip:
            return ZipFileResponse(response.status_code, response.headers, response.content)
        return SingleFileResponse(response.status_code, response.headers, response.content)

    async def run_with_retry(
        self,
        *,
        max_retry_count: int = 5,
        initial_retry_wait: float | int = 5.0,
        retry_scale: float | int = 2.0,
    ) -> SingleFileResponse | ZipFileResponse:
        response = await self.post_data_with_retry(
            max_retry_count=max_retry_count,
            initial_retry_wait=initial_retry_wait,
            retry_scale=retry_scale,
        )
        if self._response_is_zip:
            return ZipFileResponse(response.status_code, response.headers, response.content)
        return SingleFileResponse(response.status_code, response.headers, response.content)
