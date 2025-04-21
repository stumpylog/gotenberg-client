# SPDX-FileCopyrightText: 2025-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0

from gotenberg_client._base.api import AsyncBaseApi
from gotenberg_client._base.api import SyncBaseApi
from gotenberg_client._base.routes import AsyncBaseRoute
from gotenberg_client._base.routes import SyncBaseRoute

__all__ = ["AsyncBaseApi", "AsyncBaseRoute", "SyncBaseApi", "SyncBaseRoute"]
