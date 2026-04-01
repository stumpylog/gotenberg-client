# SPDX-FileCopyrightText: 2025-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0

import json
from datetime import datetime
from pathlib import Path
from typing import Final
from typing import Literal

from gotenberg_client._errors import InvalidKeywordError
from gotenberg_client._errors import InvalidPdfRevisionError
from gotenberg_client._typing_compat import Self
from gotenberg_client._utils import bool_to_form
from gotenberg_client.options import DownloadFromUrl
from gotenberg_client.options import PdfAFormat
from gotenberg_client.options import RotateAngle
from gotenberg_client.options import TrappedStatus
from gotenberg_client.options import WatermarkStampOptions
from gotenberg_client.options import WatermarkStampSource


class PdfFormatMixin:
    """
    This mixin provides the form fields for the following route options:

      - https://gotenberg.dev/docs/routes#pdfa-chromium
      - https://gotenberg.dev/docs/routes#pdfa-libreoffice
      - https://gotenberg.dev/docs/routes#convert-into-pdfa--pdfua-route
      - https://gotenberg.dev/docs/routes#merge-pdfs-route
      - https://gotenberg.dev/docs/routes#split-pdfs-route

    which allow the user to configure the resulting PDF/A version.

    See [PDF/A](https://en.wikipedia.org/wiki/PDF/A) for more information.
    """

    def pdf_format(self, pdf_format: PdfAFormat) -> Self:
        """
        All routes provide the option to configure the output PDF as a
        PDF/A format
        """
        self._form_data.update(pdf_format.to_form())  # type: ignore[attr-defined,misc]
        return self


class PdfUniversalAccessMixin:
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
        """
        Enables or disables PDF/UA based on the provided boolean value.

        Args:
            universal_access (bool): Whether to enable or disable PDF/UA.
                - `True`: Enable PDF/UA
                - `False`: Disable PDF/UA

        Returns:
            Self: The instance with the updated form data.
        """
        self._form_data.update(bool_to_form("pdfua", universal_access))  # type: ignore[attr-defined,misc]
        return self

    def enable_universal_access(self) -> Self:
        """
        Enables PDF/UA for the route options.

        Returns:
            Self: The instance with the updated form data.
        """
        return self.universal_access(universal_access=True)

    def disable_universal_access(self) -> Self:
        """
        Disables PDF/UA for the route options.

        Returns:
            Self: The instance with the updated form data.
        """
        return self.universal_access(universal_access=False)


class SplitModeMixin:
    """
    This mixin provides the form fields for the following route options:

      - https://gotenberg.dev/docs/routes#split-chromium
      - https://gotenberg.dev/docs/routes#split-libreoffice

    which allow the user to configure splitting operations
    """

    def split_mode(self, mode: Literal["intervals", "pages"]) -> Self:
        """
        Configures the splitting operation for the route options.

        Args:
            mode (Literal["intervals", "pages"]): The type of splitting operation.
                - `intervals`: Split into intervals
                - `pages`: Split into pages

        Returns:
            Self: The instance with the updated form data.
        """
        self._form_data.update({"splitMode": mode})  # type: ignore[attr-defined,misc]
        return self

    def split_span(self, span: str) -> Self:
        """
        Configures the splitting span for the route options.

        Args:
            span (str): The splitting span.
                - Example: "1-3"

        Returns:
            Self: The instance with the updated form data.
        """
        self._form_data.update({"splitSpan": span})  # type: ignore[attr-defined,misc]
        return self

    def split_unify(self, *, split_unify: bool) -> Self:
        """
        Enables or disables splitting for the route options.

        Args:
            split_unify (bool): Whether to enable or disable splitting.
                - `True`: Enable splitting
                - `False`: Disable splitting

        Returns:
            Self: The instance with the updated form data.
        """
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
        author: str | None = None,
        pdf_copyright: str | None = None,
        creation_date: datetime | None = None,
        creator: str | None = None,
        keywords: list[str] | None = None,
        modification_date: datetime | None = None,
        pdf_version: float | None = None,
        producer: str | None = None,
        subject: str | None = None,
        title: str | None = None,
        *,
        marked: bool | None = None,
        trapped: bool | TrappedStatus | None = None,
    ) -> Self:
        """
        Sets PDF metadata for the document.

        Args:
            author: Document author name
            pdf_copyright: Copyright information
            creation_date: Document creation date
            creator: Name of the creating application
            keywords: List of keywords/tags for the document
            marked: Whether the PDF is marked for structure
            modification_date: Last modification date
            pdf_version: PDF version number
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
        existing_metadata: dict[str, str | bool | float] = {}
        if "metadata" in self._form_data:  # type: ignore[attr-defined,misc]
            existing_metadata = json.loads(self._form_data["metadata"])  # type: ignore[attr-defined,misc]

        # Convert validated metadata to dictionary
        metadata: dict[str, str | bool | float] = {}

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


class FlattenOptionMixin:
    """
    https://gotenberg.dev/docs/routes#flatten-libreoffice
    https://gotenberg.dev/docs/routes#merge-pdfs-route
    https://gotenberg.dev/docs/routes#split-pdfs-route
    """

    def flatten(self, *, flatten: bool = False) -> Self:
        """
        Enables or disables flattening for the route options.

        By default, flattening is disabled (`flatten=False`). This option controls
        whether to flatten PDF documents (e.g., remove page breaks).

        Args:
            flatten (bool): Whether to enable or disable flattening.
                - `True`: Enable flattening
                - `False` (default): Disable flattening

        Returns:
            Self: The instance with the updated form data.
        """
        self._form_data.update(bool_to_form("flatten", flatten))  # type: ignore[attr-defined,misc]
        return self


class WatermarkMixin:
    """
    https://gotenberg.dev/docs/manipulate-pdfs/watermark-pdfs
    Applies a watermark behind the content of each page.
    """

    def watermark_source(self, source: WatermarkStampSource) -> Self:
        self._form_data.update({"watermarkSource": source.value})  # type: ignore[attr-defined,misc]
        return self

    def watermark_expression(self, expression: str) -> Self:
        self._form_data.update({"watermarkExpression": expression})  # type: ignore[attr-defined,misc]
        return self

    def watermark_pages(self, pages: str) -> Self:
        self._form_data.update({"watermarkPages": pages})  # type: ignore[attr-defined,misc]
        return self

    def watermark_options(self, options: WatermarkStampOptions) -> Self:
        self._form_data.update({"watermarkOptions": options.to_json()})  # type: ignore[attr-defined,misc]
        return self

    def watermark_file(self, file_path: Path) -> Self:
        self._add_file_map(file_path, name="watermark")  # type: ignore[attr-defined]
        return self


class StampMixin:
    """
    https://gotenberg.dev/docs/manipulate-pdfs/stamp-pdfs
    Adds a stamp on top of the content of each page.
    """

    def stamp_source(self, source: WatermarkStampSource) -> Self:
        self._form_data.update({"stampSource": source.value})  # type: ignore[attr-defined,misc]
        return self

    def stamp_expression(self, expression: str) -> Self:
        self._form_data.update({"stampExpression": expression})  # type: ignore[attr-defined,misc]
        return self

    def stamp_pages(self, pages: str) -> Self:
        self._form_data.update({"stampPages": pages})  # type: ignore[attr-defined,misc]
        return self

    def stamp_options(self, options: WatermarkStampOptions) -> Self:
        self._form_data.update({"stampOptions": options.to_json()})  # type: ignore[attr-defined,misc]
        return self

    def stamp_file(self, file_path: Path) -> Self:
        self._add_file_map(file_path, name="stamp")  # type: ignore[attr-defined]
        return self


class RotateMixin:
    """
    https://gotenberg.dev/docs/manipulate-pdfs/rotate-pdfs
    Rotates pages by a given angle.
    """

    def rotate(self, angle: RotateAngle, pages: str | None = None) -> Self:
        self._form_data.update({"rotateAngle": angle.value})  # type: ignore[attr-defined,misc]
        if pages is not None:
            self._form_data.update({"rotatePages": pages})  # type: ignore[attr-defined,misc]
        return self


class EncryptMixin:
    """
    https://gotenberg.dev/docs/manipulate-pdfs/encrypt-pdfs
    Encrypts the output PDF with user and/or owner passwords.
    """

    def user_password(self, password: str) -> Self:
        self._form_data.update({"userPassword": password})  # type: ignore[attr-defined,misc]
        return self

    def owner_password(self, password: str) -> Self:
        self._form_data.update({"ownerPassword": password})  # type: ignore[attr-defined,misc]
        return self


class EmbedsMixin:
    """
    https://gotenberg.dev/docs/manipulate-pdfs/attachments
    Embeds external files as attachments inside the PDF container.
    """

    def embed(self, file_path: Path) -> Self:
        self._embed_files.append(("embeds", file_path))  # type: ignore[attr-defined,misc]
        return self

    def embed_files(self, file_paths: list[Path]) -> Self:
        for fp in file_paths:
            self.embed(fp)
        return self


class DownloadFromMixin:
    """
    Instructs Gotenberg to fetch files from URLs rather than requiring uploads.
    https://gotenberg.dev/docs/webhook-download
    """

    def download_from(self, urls: list[DownloadFromUrl]) -> Self:
        data = json.dumps([u.asdict() for u in urls])  # type: ignore[misc]
        self._form_data.update({"downloadFrom": data})  # type: ignore[attr-defined,misc]
        return self
