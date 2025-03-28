# SPDX-FileCopyrightText: 2025-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0

import logging
from typing import Generic

from httpx import AsyncClient
from httpx import Client

from gotenberg_client._common.units import ClientT


class BaseApi(Generic[ClientT]):
    """
    Simple base class for an API, which wraps one or more routes, providing
    each with the client to use
    """

    def __init__(self, client: ClientT, log: logging.Logger) -> None:
        self._client: ClientT = client
        self._log = log


class SyncBaseApi(BaseApi[Client]):
    pass


class AsyncBaseApi(BaseApi[AsyncClient]):
    pass
