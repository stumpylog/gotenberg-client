# SPDX-FileCopyrightText: 2023-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
import json
import logging
from pathlib import Path
from typing import Dict
from typing import Iterable
from warnings import warn

from gotenberg_client._base import BaseSingleFileResponseRoute
from gotenberg_client._types import PageScaleType
from gotenberg_client._types import Self
from gotenberg_client._types import WaitTimeType
from gotenberg_client.options import EmulatedMediaType
from gotenberg_client.options import PageMarginsType
from gotenberg_client.options import PageOrientation
from gotenberg_client.options import PageSize

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
