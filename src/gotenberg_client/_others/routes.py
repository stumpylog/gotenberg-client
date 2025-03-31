# SPDX-FileCopyrightText: 2025-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
from pathlib import Path
from typing import Final

from gotenberg_client._base import AsyncBaseRoute
from gotenberg_client._base import SyncBaseRoute
from gotenberg_client._common import FlattenOptionMixin
from gotenberg_client._common import MetadataMixin
from gotenberg_client._common import PdfFormatMixin
from gotenberg_client._common import PfdUniversalAccessMixin
from gotenberg_client._common import SplitModeMixin
from gotenberg_client._typing_compat import Self


class _BaseSplitRoute(PdfFormatMixin, PfdUniversalAccessMixin, SplitModeMixin, MetadataMixin, FlattenOptionMixin):
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
