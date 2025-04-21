# SPDX-FileCopyrightText: 2025-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0

from typing import TYPE_CHECKING
from typing import TypeVar

if TYPE_CHECKING:
    from httpx import AsyncClient
    from httpx import Client

from gotenberg_client._common.mixins import FlattenOptionMixin
from gotenberg_client._common.mixins import MetadataMixin
from gotenberg_client._common.mixins import PdfAFormat
from gotenberg_client._common.mixins import PdfFormatMixin
from gotenberg_client._common.mixins import PfdUniversalAccessMixin
from gotenberg_client._common.mixins import SplitModeMixin

ClientT = TypeVar("ClientT", bound="Client | AsyncClient")


__all__ = [
    "ClientT",
    "FlattenOptionMixin",
    "MetadataMixin",
    "PdfAFormat",
    "PdfFormatMixin",
    "PfdUniversalAccessMixin",
    "SplitModeMixin",
]
