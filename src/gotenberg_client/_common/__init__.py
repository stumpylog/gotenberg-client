# SPDX-FileCopyrightText: 2025-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0

from typing import TYPE_CHECKING
from typing import TypeVar

if TYPE_CHECKING:
    from gotenberg_client._http_backends._protocols import AsyncClientProtocol
    from gotenberg_client._http_backends._protocols import SyncClientProtocol

from gotenberg_client._common.mixins import DownloadFromMixin
from gotenberg_client._common.mixins import EmbedsMixin
from gotenberg_client._common.mixins import EncryptMixin
from gotenberg_client._common.mixins import FlattenOptionMixin
from gotenberg_client._common.mixins import MetadataMixin
from gotenberg_client._common.mixins import PdfAFormat
from gotenberg_client._common.mixins import PdfFormatMixin
from gotenberg_client._common.mixins import PdfUniversalAccessMixin
from gotenberg_client._common.mixins import RotateMixin
from gotenberg_client._common.mixins import SplitModeMixin
from gotenberg_client._common.mixins import StampMixin
from gotenberg_client._common.mixins import WatermarkMixin

ClientT = TypeVar("ClientT", bound="SyncClientProtocol | AsyncClientProtocol")


__all__ = [
    "ClientT",
    "DownloadFromMixin",
    "EmbedsMixin",
    "EncryptMixin",
    "FlattenOptionMixin",
    "MetadataMixin",
    "PdfAFormat",
    "PdfFormatMixin",
    "PdfUniversalAccessMixin",
    "RotateMixin",
    "SplitModeMixin",
    "StampMixin",
    "WatermarkMixin",
]
