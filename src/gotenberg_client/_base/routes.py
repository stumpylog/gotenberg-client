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
from typing import Union

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
    The base implementation of a Gotenberg API route.

    This abstract class provides shared functionality between all routes and common
    utilities for posting data and processing responses. It handles file management,
    form data, headers, and other common operations.

    Attributes:
        _client (ClientT): The HTTP client used to connect to Gotenberg.
        _route_url (str): The URL of the specific Gotenberg route.
        _log (logging.Logger): Logger for recording operations.
        _stack (ExitStack): Context manager stack for resource management.
        _form_data (dict): Form data options to be sent to Gotenberg.
        _file_map (dict): Mapping of file names to their Path objects.
        _in_memory_resources (dict): Mapping of resource names to their content and MIME types.
    """

    def __init__(self, client: ClientT, route_url: str, log: logging.Logger) -> None:
        """
        Initialize a new BaseRoute instance.

        Args:
            client (ClientT): The HTTP client used to connect to Gotenberg.
            route_url (str): The URL of the specific Gotenberg route.
            log (logging.Logger): Logger for recording operations.
        """
        self._client = client
        self._route_url = route_url
        self._log = log
        self._stack = ExitStack()
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
    def _post_data(self) -> Union[Response, Coroutine[Any, Any, Response]]:
        """
        Execute the configured route request against the Gotenberg server.

        This method sends the request with all configured files, form data, and headers
        to the Gotenberg API endpoint.

        Returns:
            Response or Coroutine[Any, Any, Response]: The HTTP response from Gotenberg
                or a coroutine that will return the response.

        Raises:
            httpx.HTTPStatusError: If the HTTP request returns an error status code.
        """

    @abstractmethod
    def _post_data_with_retry(
        self,
        *,
        max_retry_count: int = 5,
        initial_retry_wait: Union[float, int] = 5.0,
        retry_scale: Union[float, int] = 2.0,
    ) -> Union[Response, Coroutine[Any, Any, Response]]:
        """
        Execute the route request with automatic retries for server errors.

        Gotenberg sometimes returns HTTP 503 errors even with valid inputs. This method
        implements an exponential backoff strategy to retry the request multiple times
        in case of server errors.

        The default retry pattern waits the following times between attempts:
            - Attempt 1 - 5s following failure
            - Attempt 2 - 10s following failure
            - Attempt 3 - 20s following failure
            - Attempt 4 - 40s following failure
            - Attempt 5 - 80s following failure

        Args:
            max_retry_count (int, optional): Maximum number of retry attempts. Defaults to 5.
            initial_retry_wait (float or int, optional): Initial wait time in seconds. Defaults to 5.0.
            retry_scale (float or int, optional): Multiplier for wait time after each attempt. Defaults to 2.0.

        Returns:
            Response or Coroutine[Any, Any, Response]: The successful HTTP response or a
                coroutine that will return the response.

        Raises:
            MaxRetriesExceededError: If all retry attempts fail with server errors.
            httpx.HTTPStatusError: If the request fails with a client error (4xx).
        """

    @abstractmethod
    def run(
        self,
    ) -> Union[SingleFileResponse, ZipFileResponse, Coroutine[Any, Any, Union[SingleFileResponse, ZipFileResponse]]]:
        """
        Execute the API request to Gotenberg and process the response.

        This method sends the configured request to the Gotenberg service and returns
        an appropriate response object based on the content type of the response.

        Returns:
            SingleFileResponse, ZipFileResponse, or Coroutine: A response object containing
                the result from Gotenberg, or a coroutine that will return such an object.

        Raises:
            httpx.Error: Any errors from the HTTP client will be raised.
        """

    @abstractmethod
    def run_with_retry(
        self,
        *,
        max_retry_count: int = 5,
        initial_retry_wait: Union[float, int] = 5.0,
        retry_scale: Union[float, int] = 2.0,
    ) -> Union[SingleFileResponse, ZipFileResponse, Coroutine[Any, Any, Union[SingleFileResponse, ZipFileResponse]]]:
        """
        Execute the API request with automatic retries and process the response.

        This method combines post_data_with_retry() with response processing to provide
        a complete operation with retry capability for server errors.

        Args:
            max_retry_count (int, optional): Maximum number of retry attempts. Defaults to 5.
            initial_retry_wait (float or int, optional): Initial wait time in seconds. Defaults to 5.0.
            retry_scale (float or int, optional): Multiplier for wait time after each attempt. Defaults to 2.0.

        Returns:
            SingleFileResponse, ZipFileResponse, or Coroutine: A response object containing
                the result from Gotenberg, or a coroutine that will return such an object.

        Raises:
            MaxRetriesExceededError: If all retry attempts fail with server errors.
            httpx.HTTPStatusError: If the request fails with a client error (4xx).
        """

    def reset(self) -> None:
        """
        Reset the route to its initial state.

        Closes all context managers via the ExitStack and clears all set files,
        form data options, and route-specific headers.
        """
        self._stack.close()
        self._form_data.clear()
        self._file_map.clear()
        self._headers.pop("Gotenberg-Output-Filename", None)
        self._headers.pop("Gotenberg-Trace", None)

    def close(self) -> None:
        """
        Close and clean up resources used by this route.

        This is an alias for reset().
        """
        self.reset()

    def _get_all_resources(self) -> RequestFiles:
        """
        Prepare all file resources for upload to Gotenberg.

        Opens all provided files for multi-part uploads and manages their contexts
        to ensure proper resource cleanup. Handles both file system files and
        in-memory resources.

        Returns:
            RequestFiles: A dictionary suitable for use as the 'files' parameter
                in httpx request methods.
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
        Add a file path to the file map for later processing.

        Args:
            filepath (Path): Path to the file to be uploaded.
            name (Optional[str], optional): Name to use for the file in the request.
                If None, the file's basename will be used. Defaults to None.
        """
        if name is None:
            name = filepath.name

        if name in self._file_map:  # pragma: no cover
            self._log.warning(f"{name} has already been provided, overwriting anyway")

        self._file_map[name] = filepath

    def _add_in_memory_file(self, data: str, *, name: str, mime_type: Optional[str] = None) -> None:
        """
        Add an in-memory file to the resources to be uploaded.

        Args:
            data (str): The content of the file.
            name (str): Name to use for the file in the request.
            mime_type (Optional[str], optional): MIME type of the file. Defaults to None.
        """
        if name in self._in_memory_resources:  # pragma: no cover
            self._log.warning(f"{name} has already been provided, overwriting anyway")

        self._in_memory_resources[name] = (data, mime_type)

    def output_filename(self, filename: str) -> Self:
        """
        Set the desired output filename for the generated file.

        Sets the Gotenberg-Output-Filename header to control the output filename.
        See [documentation](https://gotenberg.dev/docs/routes#output-filename) for more details.

        Args:
            filename (str): The desired filename for the output file.

        Returns:
            Self: The route instance for method chaining.

        Note:
            This setting will only be applied for the current route instantiation.
        """
        self._headers.update({"Gotenberg-Output-Filename": filename})
        return self

    def trace_id(self, trace_id: str) -> Self:
        """
        Set a trace ID for request tracing in Gotenberg.

        Sets the Gotenberg-Trace header for request tracing.
        See [documentation](https://gotenberg.dev/docs/routes#request-tracing) for more details.

        Args:
            trace_id (str): The trace ID to use for the request.

        Returns:
            Self: The route instance for method chaining.

        Note:
            This setting will only be applied for the current route instantiation.
        """
        self._headers.update({"Gotenberg-Trace": trace_id})
        return self


class SyncBaseRoute(BaseRoute[Client], AbstractContextManager):
    """
    Synchronous implementation of the BaseRoute for the Gotenberg API.

    This class implements the BaseRoute abstract methods using synchronous HTTP
    requests. It can be used as a context manager for automatic resource cleanup.
    """

    def __enter__(self) -> Self:
        """
        Enter the context manager scope.

        Resets the route state and returns the route instance.

        Returns:
            Self: The route instance.
        """
        self.reset()
        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        """
        Exit the context manager scope.

        Performs cleanup by calling close() to release resources.

        Args:
            exc_type: The exception type, if an exception was raised.
            exc_val: The exception instance, if an exception was raised.
            exc_tb: The traceback, if an exception was raised.
        """
        self.close()

    def _post_data(self) -> Response:
        """
        Send the configured request data to the Gotenberg server synchronously.

        Executes a POST request with all configured files, form data, and headers
        to the Gotenberg API endpoint.

        Returns:
            Response: The HTTP response from Gotenberg.

        Raises:
            httpx.HTTPStatusError: If the HTTP request returns an error status code.
        """
        resp = self._client.post(
            url=self._route_url,
            headers=self._headers,
            data=self._form_data,
            files=self._get_all_resources(),
        )
        resp.raise_for_status()
        return resp

    def _post_data_with_retry(
        self,
        *,
        max_retry_count: int = 5,
        initial_retry_wait: Union[float, int] = 5.0,
        retry_scale: Union[float, int] = 2.0,
    ) -> Response:
        """
        Send the request to Gotenberg with automatic retries for server errors.

        Implements an exponential backoff retry strategy for handling server errors.

        Args:
            max_retry_count (int, optional): Maximum number of retry attempts. Defaults to 5.
            initial_retry_wait (float or int, optional): Initial wait time in seconds. Defaults to 5.0.
            retry_scale (float or int, optional): Multiplier for wait time after each attempt. Defaults to 2.0.

        Returns:
            Response: The successful HTTP response from Gotenberg.

        Raises:
            MaxRetriesExceededError: If all retry attempts fail with server errors.
            httpx.HTTPStatusError: If the request fails with a client error (4xx).

        Note:
            Only 5xx server errors will trigger retries; 4xx client errors will be raised immediately.

        """
        retry_time = initial_retry_wait
        current_retry_count = 0

        while current_retry_count < max_retry_count:
            current_retry_count = current_retry_count + 1

            try:
                return self._post_data()
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

    def run(self) -> Union[SingleFileResponse, ZipFileResponse]:
        """
        Execute the API request to Gotenberg and process the response.

        Sends the request and returns an appropriate response object based on the
        content type of the response (either SingleFileResponse or ZipFileResponse).

        Returns:
            SingleFileResponse or ZipFileResponse: A response object containing the result.

        Raises:
            httpx.Error: Any errors from the HTTP client will be raised.
        """
        response = self._post_data()
        if "Content-Type" in response.headers and response.headers["Content-Type"] == "application/zip":
            return ZipFileResponse(response.status_code, response.headers, response.content)
        return SingleFileResponse(response.status_code, response.headers, response.content)

    def run_with_retry(
        self,
        *,
        max_retry_count: int = 5,
        initial_retry_wait: Union[float, int] = 5.0,
        retry_scale: Union[float, int] = 2.0,
    ) -> Union[SingleFileResponse, ZipFileResponse]:
        """
        Execute the API request with retries and process the response.

        Combines post_data_with_retry() with response processing to provide a complete
        operation with retry capability for server errors.

        Args:
            max_retry_count (int, optional): Maximum number of retry attempts. Defaults to 5.
            initial_retry_wait (float or int, optional): Initial wait time in seconds. Defaults to 5.0.
            retry_scale (float or int, optional): Multiplier for wait time after each attempt. Defaults to 2.0.

        Returns:
            SingleFileResponse or ZipFileResponse: A response object containing the result.

        Raises:
            MaxRetriesExceededError: If all retry attempts fail with server errors.
            httpx.HTTPStatusError: If the request fails with a client error (4xx).
        """
        response = self._post_data_with_retry(
            max_retry_count=max_retry_count,
            initial_retry_wait=initial_retry_wait,
            retry_scale=retry_scale,
        )
        if "Content-Type" in response.headers and response.headers["Content-Type"] == "application/zip":
            return ZipFileResponse(response.status_code, response.headers, response.content)
        return SingleFileResponse(response.status_code, response.headers, response.content)


class AsyncBaseRoute(BaseRoute[AsyncClient], AbstractAsyncContextManager):
    """
    Asynchronous implementation of the BaseRoute for the Gotenberg API.

    This class implements the BaseRoute abstract methods using asynchronous HTTP
    requests. It can be used as an async context manager for automatic resource cleanup.
    """

    async def __aenter__(self) -> Self:
        """
        Enter the async context manager scope.

        Resets the route state and returns the route instance.

        Returns:
            Self: The route instance.
        """
        self.reset()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        """
        Exit the async context manager scope.

        Performs cleanup by calling close() to release resources.

        Args:
            exc_type: The exception type, if an exception was raised.
            exc_val: The exception instance, if an exception was raised.
            exc_tb: The traceback, if an exception was raised.
        """
        self.close()

    async def _post_data(self) -> Response:
        """
        Send the configured request data to the Gotenberg server asynchronously.

        Executes an asynchronous POST request with all configured files, form data,
        and headers to the Gotenberg API endpoint.

        Returns:
            Response: The HTTP response from Gotenberg.

        Raises:
            httpx.HTTPStatusError: If the HTTP request returns an error status code.
        """
        resp = await self._client.post(
            url=self._route_url,
            headers=self._headers,
            data=self._form_data,
            files=self._get_all_resources(),
        )
        resp.raise_for_status()
        return resp

    async def _post_data_with_retry(
        self,
        *,
        max_retry_count: int = 5,
        initial_retry_wait: Union[float, int] = 5.0,
        retry_scale: Union[float, int] = 2.0,
    ) -> Response:
        """
        Send the request to Gotenberg asynchronously with automatic retries.

        Implements an asynchronous exponential backoff retry strategy for handling
        server errors.

        Args:
            max_retry_count (int, optional): Maximum number of retry attempts. Defaults to 5.
            initial_retry_wait (float or int, optional): Initial wait time in seconds. Defaults to 5.0.
            retry_scale (float or int, optional): Multiplier for wait time after each attempt. Defaults to 2.0.

        Returns:
            Response: The successful HTTP response from Gotenberg.

        Raises:
            MaxRetriesExceededError: If all retry attempts fail with server errors.
            httpx.HTTPStatusError: If the request fails with a client error (4xx).

        Note:
            Only 5xx server errors will trigger retries; 4xx client errors will be raised immediately.
        """
        retry_time = initial_retry_wait
        current_retry_count = 0

        while current_retry_count < max_retry_count:
            current_retry_count = current_retry_count + 1

            try:
                return await self._post_data()
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

    async def run(self) -> Union[SingleFileResponse, ZipFileResponse]:
        """
        Execute the asynchronous API request and process the response.

        Sends the request asynchronously and returns an appropriate response object
        based on the content type of the response.

        Returns:
            SingleFileResponse or ZipFileResponse: A response object containing the result.

        Raises:
            httpx.Error: Any errors from the HTTP client will be raised.
        """
        response = await self._post_data()
        if "Content-Type" in response.headers and response.headers["Content-Type"] == "application/zip":
            return ZipFileResponse(response.status_code, response.headers, response.content)
        return SingleFileResponse(response.status_code, response.headers, response.content)

    async def run_with_retry(
        self,
        *,
        max_retry_count: int = 5,
        initial_retry_wait: Union[float, int] = 5.0,
        retry_scale: Union[float, int] = 2.0,
    ) -> Union[SingleFileResponse, ZipFileResponse]:
        """
        Execute the asynchronous API request with retries and process the response.

        Combines post_data_with_retry() with response processing to provide a complete
        asynchronous operation with retry capability for server errors.

        Args:
            max_retry_count (int, optional): Maximum number of retry attempts. Defaults to 5.
            initial_retry_wait (float or int, optional): Initial wait time in seconds. Defaults to 5.0.
            retry_scale (float or int, optional): Multiplier for wait time after each attempt. Defaults to 2.0.

        Returns:
            SingleFileResponse or ZipFileResponse: A response object containing the result.

        Raises:
            MaxRetriesExceededError: If all retry attempts fail with server errors.
            httpx.HTTPStatusError: If the request fails with a client error (4xx).
        """
        response = await self._post_data_with_retry(
            max_retry_count=max_retry_count,
            initial_retry_wait=initial_retry_wait,
            retry_scale=retry_scale,
        )
        if "Content-Type" in response.headers and response.headers["Content-Type"] == "application/zip":
            return ZipFileResponse(response.status_code, response.headers, response.content)
        return SingleFileResponse(response.status_code, response.headers, response.content)
