# SPDX-FileCopyrightText: 2025-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0

import logging
from typing import Final
from typing import Literal

from gotenberg_client._typing_compat import Self
from gotenberg_client._utils import bool_to_form
from gotenberg_client.options import PageOrientation

logger = logging.getLogger(__name__)


class LibreOfficePagePropertiesMixin:
    """
    https://gotenberg.dev/docs/routes#page-properties-libreoffice
    """

    def password(self, password: str) -> Self:
        self._form_data.update({"password": password})  # type: ignore[attr-defined,misc]
        return self

    def orient(self, orient: PageOrientation) -> Self:
        """
        Sets the page orientation, either Landscape or portrait
        """
        self._form_data.update(orient.to_form())  # type: ignore[attr-defined,misc]
        return self

    def page_ranges(self, ranges: str) -> Self:
        """
        Sets the page range string, allowing either some range or just a
        few pages
        """
        self._form_data.update({"nativePageRanges": ranges})  # type: ignore[attr-defined,misc]
        return self

    def update_indexes(self, *, update_indexes: bool = False) -> Self:
        self._form_data.update(bool_to_form("updateIndexes", update_indexes))  # type: ignore[attr-defined,misc]
        return self

    def export_form_fields(self, *, export_form_fields: bool = False) -> Self:
        self._form_data.update(bool_to_form("exportFormFields", export_form_fields))  # type: ignore[attr-defined,misc]
        return self

    def allow_duplicate_form_fields(self, *, allow_duplicate_form_fields: bool = False) -> Self:
        self._form_data.update(bool_to_form("allowDuplicateFieldNames", allow_duplicate_form_fields))  # type: ignore[attr-defined,misc]
        return self

    def export_bookmarks(self, *, export_bookmarks: bool = False) -> Self:
        self._form_data.update(bool_to_form("exportBookmarks", export_bookmarks))  # type: ignore[attr-defined,misc]
        return self

    def export_bookmarks_to_pdf_destination(self, *, export_bookmarks_to_pdf_destination: bool = False) -> Self:
        self._form_data.update(bool_to_form("exportBookmarksToPdfDestination", export_bookmarks_to_pdf_destination))  # type: ignore[attr-defined,misc]
        return self

    def export_notes(self, *, export_notes: bool = False) -> Self:
        self._form_data.update(bool_to_form("exportNotes", export_notes))  # type: ignore[attr-defined,misc]
        return self

    def export_notes_pages(self, *, export_notes_pages: bool = False) -> Self:
        self._form_data.update(bool_to_form("exportNotesPages", export_notes_pages))  # type: ignore[attr-defined,misc]
        return self

    def export_only_notes_pages(self, *, export_only_notes_pages: bool = False) -> Self:
        self._form_data.update(bool_to_form("exportOnlyNotesPages", export_only_notes_pages))  # type: ignore[attr-defined,misc]
        return self

    def export_notes_in_margin(self, *, export_notes_in_margin: bool = False) -> Self:
        self._form_data.update(bool_to_form("exportNotesInMargin", export_notes_in_margin))  # type: ignore[attr-defined,misc]
        return self

    def convert_ooo_target_to_pdf_target(self, *, convert_ooo_target_to_pdf_target: bool = False) -> Self:
        self._form_data.update(bool_to_form("convertOooTargetToPdfTarget", convert_ooo_target_to_pdf_target))  # type: ignore[attr-defined,misc]
        return self

    def export_links_relative_fsys(self, *, export_links_relative_fsys: bool = False) -> Self:
        self._form_data.update(bool_to_form("exportLinksRelativeFsys", export_links_relative_fsys))  # type: ignore[attr-defined,misc]
        return self

    def export_hidden_slides(self, *, export_hidden_slides: bool = False) -> Self:
        self._form_data.update(bool_to_form("exportHiddenSlides", export_hidden_slides))  # type: ignore[attr-defined,misc]
        return self

    def skip_empty_pages(self, *, skip_empty_pages: bool = False) -> Self:
        self._form_data.update(bool_to_form("skipEmptyPages", skip_empty_pages))  # type: ignore[attr-defined,misc]
        return self

    def add_original_document_as_stream(self, *, add_original_document_as_stream: bool = False) -> Self:
        self._form_data.update(bool_to_form("addOriginalDocumentAsStream", add_original_document_as_stream))  # type: ignore[attr-defined,misc]
        return self

    def single_page_sheets(self, *, single_page_sheets: bool = False) -> Self:
        self._form_data.update(bool_to_form("singlePageSheets", single_page_sheets))  # type: ignore[attr-defined,misc]
        return self


class LibreOfficeCompressOptionsMixin:
    """
    https://gotenberg.dev/docs/routes#compress-libreoffice
    """

    _QUALITY_MAX: Final[int] = 100
    _QUALITY_MIN: Final[int] = 1

    def lossless_image_compression(self, *, lossless_image_compression: bool = False) -> Self:
        self._form_data.update(bool_to_form("losslessImageCompression", lossless_image_compression))  # type: ignore[attr-defined,misc]
        return self

    def quality(self, quality: int) -> Self:
        """
        Sets the quality of the screenshot (0-100).

        Args:
            quality (int): The desired quality level (0-100).

        Returns:
            ScreenshotRoute: This object itself for method chaining.
        """

        if quality > self._QUALITY_MAX:
            logger.warning(f"quality {quality} is above {self._QUALITY_MAX}, resetting to {self._QUALITY_MAX}")
            quality = self._QUALITY_MAX
        elif quality < self._QUALITY_MIN:
            logger.warning(f"quality {quality} is below {self._QUALITY_MIN}, resetting to {self._QUALITY_MIN}")
            quality = self._QUALITY_MIN

        self._form_data.update({"quality": str(quality)})  # type: ignore[attr-defined,misc]
        return self

    def reduce_image_resolution(self, *, reduce_image_resolution: bool = False) -> Self:
        self._form_data.update(bool_to_form("reduceImageResolution", reduce_image_resolution))  # type: ignore[attr-defined,misc]
        return self

    def max_image_resolution(self, max_resolution: Literal[75, 150, 300, 600, 1200]) -> Self:
        self._form_data.update({"quality": str(max_resolution)})  # type: ignore[attr-defined,misc]
        return self


class LibreOfficeMergeOptionMixin:
    """
    https://gotenberg.dev/docs/routes#merge-libreoffice
    """

    def merge(self, *, merge: bool) -> Self:
        self._form_data.update(bool_to_form("merge", merge))  # type: ignore[attr-defined,misc]
        self._response_is_zip = not merge
        return self

    def no_merge(self) -> Self:
        self.merge(merge=False)
        return self

    def do_merge(self) -> Self:
        self.merge(merge=True)
        return self


class LibreOfficeFlattenOptionMixin:
    """
    https://gotenberg.dev/docs/routes#flatten-libreoffice
    """

    def flatten(self, *, flatten: bool = False) -> Self:
        self._form_data.update(bool_to_form("flatten", flatten))  # type: ignore[attr-defined,misc]
        return self
