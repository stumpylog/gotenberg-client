# SPDX-FileCopyrightText: 2025-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
import json
from pathlib import Path
from typing import Any
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
from gotenberg_client._common import StampMixin
from gotenberg_client._common import WatermarkMixin
from gotenberg_client._typing_compat import Self
from gotenberg_client._utils import bool_to_form


class _BaseMergePdfFilesRoute(
    PdfFormatMixin,
    PdfUniversalAccessMixin,
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
    Represents the Gotenberg route for converting PDFs to PDF/A format.

    This class allows converting a single or multiple PDF files to the
    specified PDF/A format (e.g., PDF/A-1b, PDF/A-2b).

    See the Gotenberg documentation for details on supported PDF/A formats.

    https://gotenberg.dev/docs/routes#convert-into-pdfa--pdfua-route
    """

    ENDPOINT_URL: Final[str] = "/forms/pdfengines/merge"

    def merge(self, files: list[Path]) -> Self:
        """
        Add the given files to the merge operation.

        This method maintains the ordering of the provided list of files. Note that calling
        this method multiple times may not result in the expected merge order.

        For more details on merging PDFs with Gotenberg, see:
        https://gotenberg.dev/docs/routes#merge-pdfs-route

        Args:
            files (List[Path]): A list of Path objects representing the PDF files to be merged.

        Returns:
            Self: The instance itself, allowing for method chaining.

        Note:
            - The files must be valid PDF documents.
            - The order of the files in the list determines the order in the merged PDF.
        """
        for filepath in files:
            # Include index to enforce ordering
            self._add_file_map(filepath, name=f"{self._next:05d}_{filepath.name}")  # type: ignore[attr-defined,misc]
            self._next += 1  # type: ignore[attr-defined,misc]
        return self

    def auto_index_bookmarks(self, *, enable: bool) -> Self:
        """
        Auto-extract bookmarks from input PDFs and offset their page numbers
        to match the merged document's page numbers.
        https://gotenberg.dev/docs/manipulate-pdfs/merge-pdfs
        """
        self._form_data.update(bool_to_form("autoIndexBookmarks", enable))  # type: ignore[attr-defined,misc]
        return self

    def merge_bookmarks(self, bookmark_list: list[dict[str, Any]]) -> Self:
        """
        Set custom bookmarks for the merged PDF.
        Each bookmark: {"title": str, "page": int, "children": [...]}
        https://gotenberg.dev/docs/manipulate-pdfs/merge-pdfs
        """
        self._form_data.update({"bookmarks": json.dumps(bookmark_list)})  # type: ignore[attr-defined,misc]
        return self


class SyncMergePdfsRoute(_BaseMergePdfFilesRoute, SyncBaseRoute):
    pass


class AsyncMergePdfsRoute(_BaseMergePdfFilesRoute, AsyncBaseRoute):
    pass
