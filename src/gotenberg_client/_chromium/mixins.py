# SPDX-FileCopyrightText: 2025-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0

# SPDX-FileCopyrightText: 2023-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
import json
from collections.abc import Iterable
from datetime import timedelta
from http import HTTPStatus
from pathlib import Path
from typing import Final
from typing import Literal

from gotenberg_client._common import PageScaleType
from gotenberg_client._common import WaitTimeType
from gotenberg_client._errors import NegativeWaitDurationError
from gotenberg_client._typing_compat import Self
from gotenberg_client._utils import bool_to_form
from gotenberg_client.options import ChromiumCookieJar
from gotenberg_client.options import PageMarginsType
from gotenberg_client.options import PageOrientation
from gotenberg_client.options import PageSize


class SinglePageMixin:
    """
    https://gotenberg.dev/docs/routes#page-properties-chromium
    """

    def single_page(self, *, use_single_page: bool) -> Self:
        self._form_data.update(bool_to_form("singlePage", use_single_page))  # type: ignore[attr-defined,misc]
        return self


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


class DocumentOutlineMixin:
    """
    https://gotenberg.dev/docs/routes#page-properties-chromium
    """

    def generate_document_outline(self, *, generate_document_outline: bool = False) -> Self:
        self._form_data.update(bool_to_form("generateDocumentOutline", generate_document_outline))  # type: ignore[attr-defined,misc]
        return self


class PrintBackgroundMixin:
    """
    https://gotenberg.dev/docs/routes#page-properties-chromium
    """

    def print_background(self, *, print_background: bool = False) -> Self:
        self._form_data.update(bool_to_form("printBackground", print_background))  # type: ignore[attr-defined,misc]
        return self

    def background_graphics(self) -> Self:
        return self.print_background(print_background=True)

    def no_background_graphics(self) -> Self:
        return self.print_background(print_background=False)


class OmitBackgroundMixin:
    """
    https://gotenberg.dev/docs/routes#page-properties-chromium
    """

    def omit_background(self, *, omit_background: bool = False) -> Self:
        self._form_data.update(bool_to_form("omitBackground", omit_background))  # type: ignore[attr-defined,misc]
        return self

    def hide_background(self) -> Self:
        return self.omit_background(omit_background=True)

    def show_background(self) -> Self:
        return self.omit_background(omit_background=False)


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


class ScaleMixin:
    """
    https://gotenberg.dev/docs/routes#page-properties-chromium
    """

    def scale(self, scale: PageScaleType) -> Self:
        self._form_data.update({"scale": str(scale)})  # type: ignore[attr-defined,misc]
        return self


class NativePageRangeMixin:
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
        time_s = wait.total_seconds() if isinstance(wait, timedelta) else wait
        if time_s < 0:
            raise NegativeWaitDurationError
        self._form_data.update({"waitDelay": f"{time_s}s"})  # type: ignore[attr-defined,misc]
        return self

    def render_expression(self, expr: str) -> Self:
        self._form_data.update({"waitForExpression": expr})  # type: ignore[attr-defined,misc]
        return self


class EmulatedMediaMixin:
    """
    https://gotenberg.dev/docs/routes#emulated-media-type-chromium
    """

    def media_type(self, media_type: Literal["print", "screen"]) -> Self:
        self._form_data.update({"emulatedMediaType": media_type})  # type: ignore[attr-defined,misc]
        return self


class CookiesMixin:
    """
    https://gotenberg.dev/docs/routes#cookies-chromium
    """

    def cookies(self, cookies: list[ChromiumCookieJar]) -> Self:
        cookie_dicts = [x.asdict() for x in cookies]
        self._form_data.update({"cookies": json.dumps(cookie_dicts)})  # type: ignore[attr-defined,misc]
        return self


class CustomHTTPHeaderMixin:
    """
    https://gotenberg.dev/docs/routes#custom-http-headers-chromium
    """

    def user_agent(self, agent: str) -> Self:
        self._form_data.update({"userAgent": agent})  # type: ignore[attr-defined,misc]
        return self

    def headers(self, headers: dict[str, str]) -> Self:
        json_str = json.dumps(headers)
        self._form_data.update({"extraHttpHeaders": json_str})  # type: ignore[attr-defined,misc]
        return self


class InvalidStatusCodesMixin:
    """
    https://gotenberg.dev/docs/routes#invalid-http-status-codes-chromium
    """

    def fail_on_status_codes(self, codes: Iterable[HTTPStatus]) -> Self:
        codes_str = ",".join([str(x) for x in codes])
        self._form_data.update({"failOnHttpStatusCodes": f"[{codes_str}]"})  # type: ignore[attr-defined,misc]
        return self


class NetworkErrorsMixin:
    """
    https://gotenberg.dev/docs/routes#network-errors-chromium
    """

    def fail_on_resource_loading_failed(self, *, fail_on_resource_loading_failed: bool = False) -> Self:
        self._form_data.update(bool_to_form("failOnResourceLoadingFailed", fail_on_resource_loading_failed))  # type: ignore[attr-defined,misc]
        return self


class ConsoleExceptionMixin:
    """
    https://gotenberg.dev/docs/routes#console-exceptions-chromium
    """

    def fail_on_console_exception(self, *, fail_on_console_exception: bool = False) -> Self:
        self._form_data.update(bool_to_form("failOnConsoleExceptions", fail_on_console_exception))  # type: ignore[attr-defined,misc]
        return self

    def fail_on_exceptions(self) -> Self:
        return self.fail_on_console_exception(fail_on_console_exception=True)

    def dont_fail_on_exceptions(self) -> Self:
        return self.fail_on_console_exception(fail_on_console_exception=False)


class PerformanceModeMixin:
    """
    https://gotenberg.dev/docs/routes#performance-mode-chromium
    """

    def performance_mode(self, *, use_performance_mode: bool) -> Self:
        self._form_data.update(bool_to_form("skipNetworkIdleEvent", use_performance_mode))  # type: ignore[attr-defined,misc]
        return self

    def skip_network_idle(self) -> Self:
        return self.performance_mode(use_performance_mode=True)

    def use_network_idle(self) -> Self:
        return self.performance_mode(use_performance_mode=False)


class ScreenShotSettingsMixin:
    """
    https://gotenberg.dev/docs/routes#screenshots-route
    """

    QUALITY_MAX: Final[int] = 100
    QUALITY_MIN: Final[int] = 0

    def width(self, width: int) -> Self:
        self._form_data.update({"width": str(width)})  # type: ignore[attr-defined,misc]
        return self

    def height(self, height: int) -> Self:
        self._form_data.update({"height": str(height)})  # type: ignore[attr-defined,misc]
        return self

    def clip(self, *, clip: bool) -> Self:
        self._form_data.update(bool_to_form("clip", clip))  # type: ignore[attr-defined,misc]
        return self

    def clip_to_dimensions(self) -> Self:
        return self.clip(clip=True)

    def no_clip_to_dimensions(self) -> Self:
        return self.clip(clip=False)

    def output_format(self, output_format: Literal["png", "jpeg", "webp"] = "png") -> Self:
        """
        Sets the output format for the screenshot.

        Args:
            output_format (Literal["png", "jpeg", "webp"], optional): The desired output format. Defaults to "png".

        Returns:
            ScreenshotRoute: This object itself for method chaining.
        """

        self._form_data.update({"format": output_format})  # type: ignore[attr-defined,misc]
        return self

    def quality(self, quality: int) -> Self:
        """
        Sets the quality of the screenshot (0-100).

        Args:
            quality (int): The desired quality level (0-100).

        Returns:
            ScreenshotRoute: This object itself for method chaining.
        """

        if quality > self.QUALITY_MAX:
            self._log.warning(f"quality {quality} is above {self.QUALITY_MAX}, resetting to {self.QUALITY_MAX}")  # type: ignore[attr-defined,misc]
            quality = self.QUALITY_MAX
        elif quality < self.QUALITY_MIN:
            self._log.warning(f"quality {quality} is below {self.QUALITY_MIN}, resetting to {self.QUALITY_MIN}")  # type: ignore[attr-defined,misc]
            quality = self.QUALITY_MIN

        self._form_data.update({"quality": str(quality)})  # type: ignore[attr-defined,misc]
        return self

    def image_optimize(self, *, optimize_for_speed: bool = False) -> Self:
        self._form_data.update(bool_to_form("optimizeForSpeed", optimize_for_speed))  # type: ignore[attr-defined,misc]
        return self

    def image_optimize_for_speed(self) -> Self:
        """
        Sets the optimization mode to prioritize speed.

        Returns:
            ScreenshotRoute: This object itself for method chaining.
        """
        return self.image_optimize(optimize_for_speed=True)

    def image_optimize_for_quality(self) -> Self:
        """
        Sets the optimization mode to prioritize size reduction.

        Returns:
            ScreenshotRoute: This object itself for method chaining.
        """
        return self.image_optimize(optimize_for_speed=False)
