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
    Provides configuration options for LibreOffice page properties in PDF conversion.

    Controls page orientation, ranges, bookmarks, notes, and various export options.

    See https://gotenberg.dev/docs/routes#page-properties-libreoffice
    """

    def password(self, password: str) -> Self:
        """
        Sets password for password-protected documents.

        Args:
            password (str): Document password for accessing protected content.

        Returns:
            Self: This object for method chaining.
        """
        self._form_data.update({"password": password})  # type: ignore[attr-defined,misc]
        return self

    def orient(self, orient: PageOrientation) -> Self:
        """
        Sets the page orientation for conversion.

        Args:
            orient (PageOrientation): Either PageOrientation.Portrait or PageOrientation.Landscape.

        Returns:
            Self: This object for method chaining.
        """
        self._form_data.update(orient.to_form())  # type: ignore[attr-defined,misc]
        return self

    def page_ranges(self, ranges: str) -> Self:
        """
        Specifies which pages to include in the conversion.

        Args:
            ranges (str): Page range string (e.g., "1-5,8,11-13").

        Returns:
            Self: This object for method chaining.
        """
        self._form_data.update({"nativePageRanges": ranges})  # type: ignore[attr-defined,misc]
        return self

    def update_indexes(self, *, update_indexes: bool = False) -> Self:
        """
        Controls whether document indexes should be updated.

        Args:
            update_indexes (bool): Whether to update document indexes.

        Returns:
            Self: This object for method chaining.
        """
        self._form_data.update(bool_to_form("updateIndexes", update_indexes))  # type: ignore[attr-defined,misc]
        return self

    def export_form_fields(self, *, export_form_fields: bool = False) -> Self:
        """
        Controls whether form fields should be exported.

        Args:
            export_form_fields (bool): Whether to export form fields.

        Returns:
            Self: This object for method chaining.
        """
        self._form_data.update(bool_to_form("exportFormFields", export_form_fields))  # type: ignore[attr-defined,misc]
        return self

    def allow_duplicate_form_fields(self, *, allow_duplicate_form_fields: bool = False) -> Self:
        """
        Controls whether duplicate form field names are allowed.

        Args:
            allow_duplicate_form_fields (bool): Whether to allow duplicate field names.

        Returns:
            Self: This object for method chaining.
        """
        self._form_data.update(bool_to_form("allowDuplicateFieldNames", allow_duplicate_form_fields))  # type: ignore[attr-defined,misc]
        return self

    def export_bookmarks(self, *, export_bookmarks: bool = False) -> Self:
        """
        Controls whether bookmarks should be exported.

        Args:
            export_bookmarks (bool): Whether to export bookmarks.

        Returns:
            Self: This object for method chaining.
        """
        self._form_data.update(bool_to_form("exportBookmarks", export_bookmarks))  # type: ignore[attr-defined,misc]
        return self

    def export_bookmarks_to_pdf_destination(self, *, export_bookmarks_to_pdf_destination: bool = False) -> Self:
        """
        Controls whether bookmarks should be exported as PDF destinations.

        Args:
            export_bookmarks_to_pdf_destination (bool): Whether to convert bookmarks to PDF destinations.

        Returns:
            Self: This object for method chaining.
        """
        self._form_data.update(bool_to_form("exportBookmarksToPdfDestination", export_bookmarks_to_pdf_destination))  # type: ignore[attr-defined,misc]
        return self

    def export_notes(self, *, export_notes: bool = False) -> Self:
        """
        Controls whether document notes should be exported.

        Args:
            export_notes (bool): Whether to export notes.

        Returns:
            Self: This object for method chaining.
        """
        self._form_data.update(bool_to_form("exportNotes", export_notes))  # type: ignore[attr-defined,misc]
        return self

    def export_notes_pages(self, *, export_notes_pages: bool = False) -> Self:
        """
        Controls whether notes pages should be exported.

        Args:
            export_notes_pages (bool): Whether to export notes pages.

        Returns:
            Self: This object for method chaining.
        """
        self._form_data.update(bool_to_form("exportNotesPages", export_notes_pages))  # type: ignore[attr-defined,misc]
        return self

    def export_only_notes_pages(self, *, export_only_notes_pages: bool = False) -> Self:
        """
        Controls whether only notes pages should be exported.

        Args:
            export_only_notes_pages (bool): Whether to export only notes pages.

        Returns:
            Self: This object for method chaining.
        """
        self._form_data.update(bool_to_form("exportOnlyNotesPages", export_only_notes_pages))  # type: ignore[attr-defined,misc]
        return self

    def export_notes_in_margin(self, *, export_notes_in_margin: bool = False) -> Self:
        """
        Controls whether notes should be exported in the margin.

        Args:
            export_notes_in_margin (bool): Whether to export notes in margin.

        Returns:
            Self: This object for method chaining.
        """
        self._form_data.update(bool_to_form("exportNotesInMargin", export_notes_in_margin))  # type: ignore[attr-defined,misc]
        return self

    def convert_ooo_target_to_pdf_target(self, *, convert_ooo_target_to_pdf_target: bool = False) -> Self:
        """
        Controls that target documents with .od[tpgs] extension, will have that extension changed to .pdf when the
        link is exported to PDF

        Args:
            convert_ooo_target_to_pdf_target (bool): Whether to convert OOo targets to PDF.

        Returns:
            Self: This object for method chaining.
        """
        self._form_data.update(bool_to_form("convertOooTargetToPdfTarget", convert_ooo_target_to_pdf_target))  # type: ignore[attr-defined,misc]
        return self

    def export_links_relative_fsys(self, *, export_links_relative_fsys: bool = False) -> Self:
        """
        Controls whether links relative to the filesystem should be exported.

        Args:
            export_links_relative_fsys (bool): Whether to export filesystem-relative links.

        Returns:
            Self: This object for method chaining.
        """
        self._form_data.update(bool_to_form("exportLinksRelativeFsys", export_links_relative_fsys))  # type: ignore[attr-defined,misc]
        return self

    def export_hidden_slides(self, *, export_hidden_slides: bool = False) -> Self:
        """
        Controls whether hidden slides should be exported (for presentations).

        Args:
            export_hidden_slides (bool): Whether to export hidden slides.

        Returns:
            Self: This object for method chaining.
        """
        self._form_data.update(bool_to_form("exportHiddenSlides", export_hidden_slides))  # type: ignore[attr-defined,misc]
        return self

    def skip_empty_pages(self, *, skip_empty_pages: bool = False) -> Self:
        """
        Controls whether empty pages should be skipped.

        Args:
            skip_empty_pages (bool): Whether to skip empty pages.

        Returns:
            Self: This object for method chaining.
        """
        self._form_data.update(bool_to_form("skipEmptyPages", skip_empty_pages))  # type: ignore[attr-defined,misc]
        return self

    def add_original_document_as_stream(self, *, add_original_document_as_stream: bool = False) -> Self:
        """
        Controls whether the original document should be added as a stream.

        Args:
            add_original_document_as_stream (bool): Whether to add original document as stream.

        Returns:
            Self: This object for method chaining.
        """
        self._form_data.update(bool_to_form("addOriginalDocumentAsStream", add_original_document_as_stream))  # type: ignore[attr-defined,misc]
        return self

    def single_page_sheets(self, *, single_page_sheets: bool = False) -> Self:
        """
        Controls whether sheets should be converted as single pages.

        Args:
            single_page_sheets (bool): Whether each sheet becomes a single page.

        Returns:
            Self: This object for method chaining.
        """
        self._form_data.update(bool_to_form("singlePageSheets", single_page_sheets))  # type: ignore[attr-defined,misc]
        return self


class LibreOfficeCompressOptionsMixin:
    """
    Provides image compression options for LibreOffice PDF conversion.

    Controls lossless compression, quality levels, and resolution settings.

    See https://gotenberg.dev/docs/routes#compress-libreoffice
    """

    _QUALITY_MAX: Final[int] = 100
    _QUALITY_MIN: Final[int] = 1

    def lossless_image_compression(self, *, lossless_image_compression: bool = False) -> Self:
        """
        Controls whether to use lossless image compression.

        Args:
            lossless_image_compression (bool): Whether to use lossless compression.

        Returns:
            Self: This object for method chaining.
        """
        self._form_data.update(bool_to_form("losslessImageCompression", lossless_image_compression))  # type: ignore[attr-defined,misc]
        return self

    def quality(self, quality: int) -> Self:
        """
        Sets the image quality level for compression.

        Args:
            quality (int): Quality level from 1 (lowest) to 100 (highest).

        Returns:
            Self: This object for method chaining.

        Note:
            Values outside the valid range will be clamped.
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
        """
        Controls whether image resolution should be reduced.

        Args:
            reduce_image_resolution (bool): Whether to reduce image resolution.

        Returns:
            Self: This object for method chaining.
        """
        self._form_data.update(bool_to_form("reduceImageResolution", reduce_image_resolution))  # type: ignore[attr-defined,misc]
        return self

    def max_image_resolution(self, max_resolution: Literal[75, 150, 300, 600, 1200]) -> Self:
        """
        Sets the maximum image resolution.

        Args:
            max_resolution: Maximum resolution in DPI (must be one of: 75, 150, 300, 600, 1200).

        Returns:
            Self: This object for method chaining.
        """
        self._form_data.update({"quality": str(max_resolution)})  # type: ignore[attr-defined,misc]
        return self


class LibreOfficeMergeOptionMixin:
    """
    Provides document merging options for LibreOffice conversions.

    Controls whether multiple documents should be merged into a single PDF.

    See https://gotenberg.dev/docs/routes#merge-libreoffice
    """

    def merge(self, *, merge: bool) -> Self:
        """
        Controls whether multiple documents should be merged.

        Args:
            merge (bool): Whether to merge documents.

        Returns:
            Self: This object for method chaining.
        """
        self._form_data.update(bool_to_form("merge", merge))  # type: ignore[attr-defined,misc]
        return self

    def no_merge(self) -> Self:
        """
        Disables document merging.

        Returns:
            Self: This object for method chaining.
        """
        self.merge(merge=False)
        return self

    def do_merge(self) -> Self:
        """
        Enables document merging.

        Returns:
            Self: This object for method chaining.
        """
        self.merge(merge=True)
        return self
