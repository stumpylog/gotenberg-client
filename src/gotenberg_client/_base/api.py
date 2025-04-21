# SPDX-FileCopyrightText: 2025-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0

import logging
from typing import Generic

from httpx import AsyncClient
from httpx import Client

from gotenberg_client._common import ClientT


class BaseApi(Generic[ClientT]):
    """
    Simple base class for an API, which wraps one or more routes, providing
    each with the client to use for Gotenberg service communication.

    This class serves as the foundation for both synchronous and asynchronous
    API implementations.
    """

    def __init__(self, client: ClientT, log: logging.Logger) -> None:
        """
        Initialize a new BaseApi instance.

        Args:
            client (ClientT): The HTTP client (sync or async) to use for requests.
            log (logging.Logger): Logger for recording operations.
        """
        self._client: ClientT = client
        self._log = log


class SyncBaseApi(BaseApi[Client]):
    """
    Synchronous implementation of the BaseApi.

    Provides a foundation for synchronous Gotenberg API routes using
    a synchronous HTTP client.
    """


class AsyncBaseApi(BaseApi[AsyncClient]):
    """
    Asynchronous implementation of the BaseApi.

    Provides a foundation for asynchronous Gotenberg API routes using
    an asynchronous HTTP client.
    """
