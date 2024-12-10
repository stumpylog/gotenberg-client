# SPDX-FileCopyrightText: 2023-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any
from typing import Dict
from typing import Final
from typing import Iterable
from typing import List
from typing import Optional
from typing import Union
from warnings import warn

from gotenberg_client._base import BaseSingleFileResponseRoute
from gotenberg_client._errors import InvalidKeywordError
from gotenberg_client._errors import InvalidPdfRevisionError
from gotenberg_client._types import PageScaleType
from gotenberg_client._types import Self
from gotenberg_client._types import WaitTimeType
from gotenberg_client.options import EmulatedMediaType
from gotenberg_client.options import PageMarginsType
from gotenberg_client.options import PageOrientation
from gotenberg_client.options import PageSize
from gotenberg_client.options import TrappedStatus

logger = logging.getLogger()


class PageSizeMixin:
    """
    https://gotenberg.dev/docs/routes#page-properties-chromium
    """

    def size(self, size: PageSize) -> Self:
        self._form_data.update(size.to_form())  # type: ignore[attr-defined,misc]
        return self


class MarginMixin:
    """
    https://gotenberg.dev/docs/routes#page-properties-chromium
    """

    def margins(self, margins: PageMarginsType) -> Self:
        self._form_data.update(margins.to_form())  # type: ignore[attr-defined,misc]
        return self


class PageOrientMixin:
    """
    https://gotenberg.dev/docs/routes#page-properties-chromium
    """

    def orient(self, orient: PageOrientation) -> Self:
        """
        Sets the page orientation, either Landscape or portrait
        """
        self._form_data.update(orient.to_form())  # type: ignore[attr-defined,misc]
        return self


class PageRangeMixin:
    """
    https://gotenberg.dev/docs/routes#page-properties-chromium
    """

    def page_ranges(self, ranges: str) -> Self:
        """
        Sets the page range string, allowing either some range or just a
        few pages
        """
        self._form_data.update({"nativePageRanges": ranges})  # type: ignore[attr-defined,misc]
        return self


class CssPageSizeMixin:
    """
    https://gotenberg.dev/docs/routes#page-properties-chromium
    """

    def prefer_css_page_size(self) -> Self:
        self._form_data.update({"preferCssPageSize": "true"})  # type: ignore[attr-defined,misc]
        return self

    def prefer_set_page_size(self) -> Self:
        self._form_data.update({"preferCssPageSize": "false"})  # type: ignore[attr-defined,misc]
        return self


class BackgroundControlMixin:
    """
    https://gotenberg.dev/docs/routes#page-properties-chromium
    """

    def background_graphics(self) -> Self:
        self._form_data.update({"printBackground": "true"})  # type: ignore[attr-defined,misc]
        return self

    def no_background_graphics(self) -> Self:
        self._form_data.update({"printBackground": "false"})  # type: ignore[attr-defined,misc]
        return self

    def hide_background(self) -> Self:
        self._form_data.update({"omitBackground": "true"})  # type: ignore[attr-defined,misc]
        return self

    def show_background(self) -> Self:
        self._form_data.update({"omitBackground": "false"})  # type: ignore[attr-defined,misc]
        return self


class ScaleMixin:
    """
    https://gotenberg.dev/docs/routes#page-properties-chromium
    """

    def scale(self, scale: PageScaleType) -> Self:
        self._form_data.update({"scale": str(scale)})  # type: ignore[attr-defined,misc]
        return self


class SinglePageMixin:
    """
    https://gotenberg.dev/docs/routes#page-properties-chromium
    """

    def single_page(self, *, use_single_page: bool) -> Self:
        self._form_data.update({"singlePage": str(use_single_page)})  # type: ignore[attr-defined,misc]
        return self


class PagePropertiesMixin(
    PageSizeMixin,
    MarginMixin,
    CssPageSizeMixin,
    BackgroundControlMixin,
    PageOrientMixin,
    PageRangeMixin,
    ScaleMixin,
    SinglePageMixin,
    BaseSingleFileResponseRoute,
):
    """
    https://gotenberg.dev/docs/routes#page-properties-chromium
    """


class HeaderFooterMixin:
    """
    https://gotenberg.dev/docs/routes#header-footer-chromium
    """

    def header(self, header: Path) -> Self:
        self._add_file_map(header, name="header.html")  # type: ignore[attr-defined]
        return self

    def footer(self, footer: Path) -> Self:
        self._add_file_map(footer, name="footer.html")  # type: ignore[attr-defined]
        return self


class RenderControlMixin:
    """
    https://gotenberg.dev/docs/routes#wait-before-rendering-chromium
    """

    def render_wait(self, wait: WaitTimeType) -> Self:
        self._form_data.update({"waitDelay": str(wait)})  # type: ignore[attr-defined,misc]
        return self

    def render_expr(self, expr: str) -> Self:
        self._form_data.update({"waitForExpression": expr})  # type: ignore[attr-defined,misc]
        return self


class EmulatedMediaMixin:
    """
    https://gotenberg.dev/docs/routes#emulated-media-type-chromium
    """

    def media_type(self, media_type: EmulatedMediaType) -> Self:
        self._form_data.update(media_type.to_form())  # type: ignore[attr-defined,misc]
        return self


class CustomHTTPHeaderMixin:
    """
    https://gotenberg.dev/docs/routes#custom-http-headers-chromium
    """

    def user_agent(self, agent: str) -> Self:
        warn("The Gotenberg userAgent field is deprecated", DeprecationWarning, stacklevel=2)
        self._form_data.update({"userAgent": agent})  # type: ignore[attr-defined,misc]
        return self

    def headers(self, headers: Dict[str, str]) -> Self:
        json_str = json.dumps(headers)
        self._form_data.update({"extraHttpHeaders": json_str})  # type: ignore[attr-defined,misc]
        return self


class InvalidStatusCodesMixin:
    """
    https://gotenberg.dev/docs/routes#invalid-http-status-codes-chromium
    """

    def fail_on_status_codes(self, codes: Iterable[int]) -> Self:
        if not codes:
            logger.warning("fail_on_status_codes was given not codes, ignoring")
            return self
        codes_str = ",".join([str(x) for x in codes])
        self._form_data.update({"failOnHttpStatusCodes": f"[{codes_str}]"})  # type: ignore[attr-defined,misc]
        return self


class ConsoleExceptionMixin:
    """
    https://gotenberg.dev/docs/routes#console-exceptions-chromium
    """

    def fail_on_exceptions(self) -> Self:
        self._form_data.update({"failOnConsoleExceptions": "true"})  # type: ignore[attr-defined,misc]
        return self

    def dont_fail_on_exceptions(self) -> Self:
        self._form_data.update({"failOnConsoleExceptions": "false"})  # type: ignore[attr-defined,misc]
        return self


class PerformanceModeMixin:
    """
    https://gotenberg.dev/docs/routes#performance-mode-chromium
    """

    def skip_network_idle(self) -> Self:
        self._form_data.update({"skipNetworkIdleEvent": "false"})  # type: ignore[attr-defined,misc]
        return self

    def use_network_idle(self) -> Self:
        self._form_data.update({"skipNetworkIdleEvent": "false"})  # type: ignore[attr-defined,misc]
        return self


class MetadataMixin:
    """
    Mixin for PDF metadata support.

    This mixin provides functionality to set PDF metadata for documents processed through
    the Gotenberg API (https://gotenberg.dev/docs/routes#metadata-chromium).

    Important Notes:
    - Gotenberg will use the current date/time for creation_date and modification_date,
      even if custom dates are provided.
    - Gotenberg will use its own pdf_version, even if a custom version is provided.

    Example:
        from gotenberg_client import GotenbergClient
        from datetime import datetime
        from zoneinfo import ZoneInfo
        from pathlib import Path

        with GotenbergClient('http://localhost:3000') as client:
            with client.chromium.url_to_pdf() as route:

                response = (
                    route.url('https://hello.world')
                    .metadata(
                        author='John Doe',
                        copyright='© 2024 My Company',
                        creation_date = datetime.now(tz=ZoneInfo("Europe/Berlin")),
                        creator='My Application',
                        keywords=['keyword', 'example'],
                        marked=True,
                        modification_date=datetime.now(tz=ZoneInfo("Europe/Berlin")),
                        pdf_version=1.7,
                        producer='PDF Producer',
                        subject='My Subject',
                        title='My Title',
                        trapped=True,
                    )
                )

                response.to_file(Path('my-world.pdf'))
    """

    MIN_PDF_VERSION: Final[float] = 1.0
    MAX_PDF_VERSION: Final[float] = 2.0

    def metadata(
        self,
        author: Optional[str] = None,
        pdf_copyright: Optional[str] = None,
        creation_date: Optional[datetime] = None,
        creator: Optional[str] = None,
        keywords: Optional[List[str]] = None,
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
        existing_metadata: Dict[str, Any] = {}
        if "metadata" in self._form_data:
            existing_metadata = json.loads(self._form_data["metadata"])

        # Convert validated metadata to dictionary
        metadata: Dict[str, Any] = {}

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

        # Merge existing and new metadata
        if metadata:
            self._form_data.update({"metadata": json.dumps({**existing_metadata, **metadata})})

        return self
