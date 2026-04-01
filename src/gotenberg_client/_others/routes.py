# SPDX-FileCopyrightText: 2025-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
from pathlib import Path
from typing import Final

from gotenberg_client._base import AsyncBaseRoute
from gotenberg_client._base import SyncBaseRoute
from gotenberg_client._common import DownloadFromMixin
from gotenberg_client._common import EmbedsMixin
from gotenberg_client._common import EncryptMixin
from gotenberg_client._common import FlattenOptionMixin
from gotenberg_client._common import MetadataMixin
from gotenberg_client._common import PdfFormatMixin
from gotenberg_client._common import PdfUniversalAccessMixin
from gotenberg_client._common import RotateMixin
from gotenberg_client._common import SplitModeMixin
from gotenberg_client._common import StampMixin
from gotenberg_client._common import WatermarkMixin
from gotenberg_client._typing_compat import Self


class _BaseSplitRoute(
    PdfFormatMixin,
    PdfUniversalAccessMixin,
    SplitModeMixin,
    MetadataMixin,
    FlattenOptionMixin,
    WatermarkMixin,
    StampMixin,
    RotateMixin,
    EncryptMixin,
    EmbedsMixin,
    DownloadFromMixin,
):
    """
    https://gotenberg.dev/docs/routes#split-pdfs-route
    """

    ENDPOINT_URL: Final[str] = "/forms/pdfengines/split"

    def split(self, file_path: Path) -> Self:
        """
        Adds a single PDF file for splitting
        """

        self._add_file_map(file_path)  # type: ignore[attr-defined]
        return self

    def split_files(self, file_paths: list[Path]) -> Self:
        """
        Adds multiple PDF files for splitting
        """

        for x in file_paths:
            self.split(x)
        return self


class SyncSplitRoute(_BaseSplitRoute, SyncBaseRoute):
    pass


class AsyncSplitRoute(_BaseSplitRoute, AsyncBaseRoute):
    pass


class _BaseFlattenRoute:
    """
    https://gotenberg.dev/docs/routes#flatten-pdfs-route
    """

    ENDPOINT_URL: Final[str] = "/forms/pdfengines/flatten"

    def flatten(self, file_path: Path) -> Self:
        """
        Adds a single PDF file for flattening
        """

        self._add_file_map(file_path)  # type: ignore[attr-defined]
        return self

    def flatten_files(self, file_paths: list[Path]) -> Self:
        """
        Adds multiple PDF files for flattening
        """

        for x in file_paths:
            self.flatten(x)
        return self


class SyncFlattenRoute(_BaseFlattenRoute, SyncBaseRoute):
    pass


class AsyncFlattenRoute(_BaseFlattenRoute, AsyncBaseRoute):
    pass


class _BaseWatermarkRoute(
    WatermarkMixin,
    StampMixin,
    RotateMixin,
    EncryptMixin,
    EmbedsMixin,
    DownloadFromMixin,
    PdfFormatMixin,
    PdfUniversalAccessMixin,
    MetadataMixin,
):
    """https://gotenberg.dev/docs/manipulate-pdfs/watermark-pdfs"""

    ENDPOINT_URL: Final[str] = "/forms/pdfengines/watermark"

    def add_file(self, file_path: Path) -> Self:
        self._add_file_map(file_path)  # type: ignore[attr-defined]
        return self

    def add_files(self, file_paths: list[Path]) -> Self:
        for fp in file_paths:
            self.add_file(fp)
        return self


class SyncWatermarkRoute(_BaseWatermarkRoute, SyncBaseRoute):
    pass


class AsyncWatermarkRoute(_BaseWatermarkRoute, AsyncBaseRoute):
    pass


class _BaseStampRoute(
    WatermarkMixin,
    StampMixin,
    RotateMixin,
    EncryptMixin,
    EmbedsMixin,
    DownloadFromMixin,
    PdfFormatMixin,
    PdfUniversalAccessMixin,
    MetadataMixin,
):
    """https://gotenberg.dev/docs/manipulate-pdfs/stamp-pdfs"""

    ENDPOINT_URL: Final[str] = "/forms/pdfengines/stamp"

    def add_file(self, file_path: Path) -> Self:
        self._add_file_map(file_path)  # type: ignore[attr-defined]
        return self

    def add_files(self, file_paths: list[Path]) -> Self:
        for fp in file_paths:
            self.add_file(fp)
        return self


class SyncStampRoute(_BaseStampRoute, SyncBaseRoute):
    pass


class AsyncStampRoute(_BaseStampRoute, AsyncBaseRoute):
    pass


class _BaseRotateRoute(
    RotateMixin,
    EncryptMixin,
    EmbedsMixin,
    DownloadFromMixin,
    PdfFormatMixin,
    PdfUniversalAccessMixin,
    MetadataMixin,
):
    """https://gotenberg.dev/docs/manipulate-pdfs/rotate-pdfs"""

    ENDPOINT_URL: Final[str] = "/forms/pdfengines/rotate"

    def add_file(self, file_path: Path) -> Self:
        self._add_file_map(file_path)  # type: ignore[attr-defined]
        return self

    def add_files(self, file_paths: list[Path]) -> Self:
        for fp in file_paths:
            self.add_file(fp)
        return self


class SyncRotateRoute(_BaseRotateRoute, SyncBaseRoute):
    pass


class AsyncRotateRoute(_BaseRotateRoute, AsyncBaseRoute):
    pass


class _BaseEncryptRoute(EncryptMixin, DownloadFromMixin):
    """https://gotenberg.dev/docs/manipulate-pdfs/encrypt-pdfs"""

    ENDPOINT_URL: Final[str] = "/forms/pdfengines/encrypt"

    def add_file(self, file_path: Path) -> Self:
        self._add_file_map(file_path)  # type: ignore[attr-defined]
        return self

    def add_files(self, file_paths: list[Path]) -> Self:
        for fp in file_paths:
            self.add_file(fp)
        return self


class SyncEncryptRoute(_BaseEncryptRoute, SyncBaseRoute):
    pass


class AsyncEncryptRoute(_BaseEncryptRoute, AsyncBaseRoute):
    pass


class _BaseEmbedRoute(EmbedsMixin, DownloadFromMixin):
    """
    https://gotenberg.dev/docs/manipulate-pdfs/attachments
    Embeds external files as attachments in existing PDFs.
    POST /forms/pdfengines/embed
    """

    ENDPOINT_URL: Final[str] = "/forms/pdfengines/embed"

    def add_pdf(self, file_path: Path) -> Self:
        """Add a PDF to receive the embedded attachments.
        Gotenberg requires the field name to be 'files' for the PDF inputs."""
        self._embed_files.append(("files", file_path))  # type: ignore[attr-defined,misc]
        return self

    def add_pdfs(self, file_paths: list[Path]) -> Self:
        for fp in file_paths:
            self.add_pdf(fp)
        return self


class SyncEmbedRoute(_BaseEmbedRoute, SyncBaseRoute):
    pass


class AsyncEmbedRoute(_BaseEmbedRoute, AsyncBaseRoute):
    pass
