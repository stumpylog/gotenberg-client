# SPDX-FileCopyrightText: 2025-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0

import json
from datetime import datetime
from typing import Final
from typing import Literal
from typing import Optional
from typing import Union

from gotenberg_client._errors import InvalidKeywordError
from gotenberg_client._errors import InvalidPdfRevisionError
from gotenberg_client._typing_compat import Self
from gotenberg_client._utils import bool_to_form
from gotenberg_client.options import PdfAFormat
from gotenberg_client.options import TrappedStatus


class PdfFormatMixin:
    """
    This mixin provides the form fields for the following route options:

      - https://gotenberg.dev/docs/routes#pdfa-chromium
      - https://gotenberg.dev/docs/routes#pdfa-libreoffice
      - https://gotenberg.dev/docs/routes#convert-into-pdfa--pdfua-route
      - https://gotenberg.dev/docs/routes#merge-pdfs-route
      - https://gotenberg.dev/docs/routes#split-pdfs-route

    which allow the user to configure the resulting PDF/A version.

    See https://en.wikipedia.org/wiki/PDF/A
    """

    def pdf_format(self, pdf_format: PdfAFormat) -> Self:
        """
        All routes provide the option to configure the output PDF as a
        PDF/A format
        """
        self._form_data.update(pdf_format.to_form())  # type: ignore[attr-defined,misc]
        return self


class PfdUniversalAccessMixin:
    """
    This mixin provides the form fields for the following route options:

      - https://gotenberg.dev/docs/routes#pdfa-chromium
      - https://gotenberg.dev/docs/routes#pdfa-libreoffice
      - https://gotenberg.dev/docs/routes#convert-into-pdfa--pdfua-route
      - https://gotenberg.dev/docs/routes#merge-pdfs-route
      - https://gotenberg.dev/docs/routes#split-pdfs-route

      which allow the user to enable or disable PDF/UA.

      See https://en.wikipedia.org/wiki/PDF/UA
    """

    def universal_access(self, *, universal_access: bool) -> Self:
        self._form_data.update(bool_to_form("pdfua", universal_access))  # type: ignore[attr-defined,misc]
        return self

    def enable_universal_access(self) -> Self:
        return self.universal_access(universal_access=True)

    def disable_universal_access(self) -> Self:
        return self.universal_access(universal_access=False)


class SplitModeMixin:
    """
    This mixin provides the form fields for the following route options:

      - https://gotenberg.dev/docs/routes#split-chromium
      - https://gotenberg.dev/docs/routes#split-libreoffice

    which allow the user to configure splitting operations
    """

    def split_mode(self, mode: Literal["intervals", "pages"]) -> Self:
        self._response_is_zip = True
        self._form_data.update({"splitMode": mode})  # type: ignore[attr-defined,misc]
        return self

    def split_span(self, span: str) -> Self:
        self._form_data.update({"splitSpan": span})  # type: ignore[attr-defined,misc]
        return self

    def split_unify(self, *, split_unify: bool) -> Self:
        self._response_is_zip = split_unify
        self._form_data.update(bool_to_form("splitUnify", split_unify))  # type: ignore[attr-defined,misc]
        return self


class MetadataMixin:
    """
    This mixin provides the form fields for the following route options:

      - https://gotenberg.dev/docs/routes#metadata-chromium
      - https://gotenberg.dev/docs/routes#metadata-libreoffice

    which allow the user to write metadata to the resulting PDFs
    """

    MIN_PDF_VERSION: Final[float] = 1.0
    MAX_PDF_VERSION: Final[float] = 2.0

    def metadata(
        self,
        author: Optional[str] = None,
        pdf_copyright: Optional[str] = None,
        creation_date: Optional[datetime] = None,
        creator: Optional[str] = None,
        keywords: Optional[list[str]] = None,
        marked: Optional[bool] = None,
        modification_date: Optional[datetime] = None,
        pdf_version: Optional[float] = None,
        producer: Optional[str] = None,
        subject: Optional[str] = None,
        title: Optional[str] = None,
        trapped: Optional[Union[bool, TrappedStatus]] = None,
    ) -> Self:
        """
        Sets PDF metadata for the document.

        Args:
            author: Document author name
            copyright: Copyright information
            creation_date: Document creation date (Note: Gotenberg will override this)
            creator: Name of the creating application
            keywords: List of keywords/tags for the document
            marked: Whether the PDF is marked for structure
            modification_date: Last modification date (Note: Gotenberg will override this)
            pdf_version: PDF version number (Note: Gotenberg will override this)
            producer: Name of the PDF producer
            subject: Document subject/description
            title: Document title
            trapped: Trapping status (bool or one of: 'True', 'False', 'Unknown')

        Returns:
            Self for method chaining

        Raises:
            InvalidPdfRevisionError: If the provided PDF revision is outside the valid range
            InvalidKeywordError: If any metadata keyword values are not allowed
            TypeError: If any metadata values have incorrect types
        """

        # Validate metadata values
        if pdf_version is not None and not (self.MIN_PDF_VERSION <= pdf_version <= self.MAX_PDF_VERSION):
            msg = "PDF version must be between 1.0 and 2.0"
            raise InvalidPdfRevisionError(msg)

        if trapped is not None and isinstance(trapped, bool):
            trapped = TrappedStatus.TRUE if trapped else TrappedStatus.FALSE

        if keywords is not None:
            if not all(isinstance(k, str) for k in keywords):
                raise InvalidKeywordError("All keywords must be strings")  # noqa: EM101, TRY003
            if any("," in k for k in keywords):
                raise InvalidKeywordError("Keywords cannot contain commas")  # noqa: EM101, TRY003

        # Get existing metadata if any
        existing_metadata: dict[str, Union[str, bool, float]] = {}
        if "metadata" in self._form_data:  # type: ignore[attr-defined,misc]
            existing_metadata = json.loads(self._form_data["metadata"])  # type: ignore[attr-defined,misc]

        # Convert validated metadata to dictionary
        metadata: dict[str, Union[str, bool, float]] = {}

        if author:
            metadata["Author"] = author
        if pdf_copyright:
            metadata["Copyright"] = pdf_copyright
        if creation_date:
            metadata["CreationDate"] = creation_date.isoformat()
        if creator:
            metadata["Creator"] = creator
        if keywords:
            metadata["Keywords"] = ", ".join(keywords)
        if marked is not None:
            metadata["Marked"] = marked
        if modification_date:
            metadata["ModDate"] = modification_date.isoformat()
        if pdf_version:
            metadata["PDFVersion"] = pdf_version
        if producer:
            metadata["Producer"] = producer
        if subject:
            metadata["Subject"] = subject
        if title:
            metadata["Title"] = title
        if trapped is not None:
            metadata["Trapped"] = trapped.value

        # Merge existing and new metadata into the form field
        self._form_data.update({"metadata": json.dumps({**existing_metadata, **metadata})})  # type: ignore[attr-defined,misc]

        return self
