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
from typing import Union

from gotenberg_client._errors import NegativeWaitDurationError
from gotenberg_client._typing_compat import Self
from gotenberg_client._utils import bool_to_form
from gotenberg_client.options import CookieJar
from gotenberg_client.options import PageMarginsType
from gotenberg_client.options import PageOrientation
from gotenberg_client.options import PageSize


class SinglePageMixin:
    """
    See [documentation](https://gotenberg.dev/docs/routes#page-properties-chromium) for more details

    Allows configuring the 'singlePage' property for Chromium-based conversions.
    This property instructs Chromium to render the output PDF as a single-page document.

    Note:  This setting can affect the rendering of complex documents, particularly those with
    embedded forms or interactive elements.  Experimentation may be necessary to
    achieve the desired outcome.
    """

    def single_page(self, *, use_single_page: bool) -> Self:
        """
        Sets the 'singlePage' property to True or False.

        Args:
            use_single_page:  Boolean value indicating whether to render the PDF as a single page.
                              True means treat the document as a single page; False means
                              render it as a multi-page document.

        Returns:
            self: The current instance of the route, allowing for method chaining.
        """
        self._form_data.update(bool_to_form("singlePage", use_single_page))  # type: ignore[attr-defined,misc]
        return self


class PageSizeMixin:
    """
    See [documentation](https://gotenberg.dev/docs/routes#page-properties-chromium) for more details

    Allows configuring the 'pageSize' property for Chromium-based conversions.
    This property defines the dimensions of the output PDF page.
    """

    def size(self, size: PageSize) -> Self:
        """
        Sets the 'pageSize' property to a specified page size.

        Args:
            size: A `PageSize` class representing the desired page size
                  with height, width and units

        Returns:
            self: The current instance of the class, allowing for method chaining.

        """
        self._form_data.update(size.to_form())  # type: ignore[attr-defined,misc]
        return self


class MarginMixin:
    """
    See [documentation](https://gotenberg.dev/docs/routes#page-properties-chromium) for more details.
    """

    def margins(self, margins: PageMarginsType) -> Self:
        """
        Sets the specified page margins.

        Args:
            margins: A `PageMarginsType` class representing the desired page margins.

        Returns:
            self: The current instance of the class, allowing for method chaining.
        """
        self._form_data.update(margins.to_form())  # type: ignore[attr-defined,misc]
        return self


class CssPageSizeMixin:
    """
    See [documentation](https://gotenberg.dev/docs/routes#page-properties-chromium) for more details.
    """

    def prefer_css_page_size(self) -> Self:
        """
        Sets the 'preferCssPageSize' property to 'true'.

        Returns:
            self: The current instance of the class, allowing for method chaining.
        """
        self._form_data.update(bool_to_form("preferCssPageSize", True))  # type: ignore[attr-defined,misc]
        return self

    def prefer_set_page_size(self) -> Self:
        """
        Sets the 'preferCssPageSize' property to 'false'.

        Returns:
            self: The current instance of the class, allowing for method chaining.
        """
        self._form_data.update(bool_to_form("preferCssPageSize", False))  # type: ignore[attr-defined,misc]
        return self


class DocumentOutlineMixin:
    """
    See [documentation](https://gotenberg.dev/docs/routes#page-properties-chromium) for more details.
    """

    def generate_document_outline(self, *, generate_document_outline: bool) -> Self:
        """
        Sets the 'generateDocumentOutline' property.

        Args:
            generate_document_outline:  Whether to generate a document outline

        Returns:
            self: The current instance of the class, allowing for method chaining.

        """
        self._form_data.update(bool_to_form("generateDocumentOutline", generate_document_outline))  # type: ignore[attr-defined,misc]
        return self


class PrintBackgroundMixin:
    """
    See [documentation](https://gotenberg.dev/docs/routes#page-properties-chromium) for more details.
    """

    def print_background(self, *, print_background: bool) -> Self:
        """
        Enables or disables printing the page background.

        Args:
            print_background: True to print the background, False to not print it.

        Returns:
            self: The current instance of the class, allowing for method chaining.
        """
        self._form_data.update(bool_to_form("printBackground", print_background))  # type: ignore[attr-defined,misc]
        return self

    def background_graphics(self) -> Self:
        """
        Enables printing of the page background.  Equivalent to print_background(print_background=True).

        Returns:
            self: The current instance of the class, allowing for method chaining.
        """
        return self.print_background(print_background=True)

    def no_background_graphics(self) -> Self:
        """
        Disables printing of the page background. Equivalent to print_background(print_background=False).

        Returns:
            self: The current instance of the class, allowing for method chaining.
        """
        return self.print_background(print_background=False)


class OmitBackgroundMixin:
    """
    See [documentation](https://gotenberg.dev/docs/routes#page-properties-chromium) for more details.
    """

    def omit_background(self, *, omit_background: bool) -> Self:
        """
        Enables or disables the omission of the page background.

        Args:
            omit_background: True to omit the background, False to include it.

        Returns:
            self: The current instance of the class, allowing for method chaining.
        """
        self._form_data.update(bool_to_form("omitBackground", omit_background))  # type: ignore[attr-defined,misc]
        return self

    def hide_background(self) -> Self:
        """
        Omits the page background. Equivalent to omit_background(omit_background=True).

        Returns:
            self: The current instance of the class, allowing for method chaining.
        """
        return self.omit_background(omit_background=True)

    def show_background(self) -> Self:
        """
        Includes the page background. Equivalent to omit_background(omit_background=False).

        Returns:
            self: The current instance of the class, allowing for method chaining.
        """
        return self.omit_background(omit_background=False)


class PageOrientMixin:
    """
    See [documentation](https://gotenberg.dev/docs/routes#page-properties-chromium) for more details.
    """

    def orient(self, orient: PageOrientation) -> Self:
        """
        Sets the page orientation to either Portrait or Landscape.

        Args:
            orient: The desired PageOrientation (PageOrientation.Portrait or PageOrientation.Landscape).

        Returns:
            self: The current instance of the class, allowing for method chaining.
        """
        self._form_data.update(orient.to_form())  # type: ignore[attr-defined,misc]
        return self


class ScaleMixin:
    """
    See [documentation](https://gotenberg.dev/docs/routes#page-properties-chromium) for more details.

    Allows specifying a scale factor for the generated PDF. This can be used to
    increase or decrease the size of the content.
    """

    def scale(self, scale: Union[float, int]) -> Self:
        """
        Sets the scale factor for the generated PDF.

        Args:
            scale: The scale factor.  A float or integer representing the desired
                   scale.  For example, a scale of 2.0 will double the size,
                   while a scale of 0.5 will halve the size.

        Returns:
            self: The current instance of the class, allowing for method chaining.
        """
        self._form_data.update({"scale": str(scale)})  # type: ignore[attr-defined,misc]
        return self


class NativePageRangeMixin:
    """
     Allows for selecting specific pages or ranges of pages to be included in the output.

    See [documentation](https://gotenberg.dev/docs/routes#page-properties-chromium) for more details.
    """

    def page_ranges(self, ranges: str) -> Self:
        """
        Sets the native page range string.  Allows for specifying some range or
        just a few pages.

        Args:
            ranges: The native page range string.  This string follows the format
                    expected by the PDF engine.  Examples include "1-5", "1,3,5",
                    or "2-4,7".  Consult the documentation for the exact
                    expected format.

        Returns:
            self: The current instance of the class, allowing for method chaining.
        """
        self._form_data.update({"nativePageRanges": ranges})  # type: ignore[attr-defined,misc]
        return self


class HeaderFooterMixin:
    """
     Allows specifying a header and/or footer HTML file to be included in
    the generated PDF.

    See [documentation](https://gotenberg.dev/docs/routes#header-footer-chromium) for more details.

    """

    def header(self, header: Path) -> Self:
        """
        Adds a header HTML file to the generated PDF.

        Args:
            header: A Path object representing the path to the header HTML file.

        Returns:
            self: The current instance of the class, allowing for method chaining.
        """
        self._add_file_map(header, name="header.html")  # type: ignore[attr-defined]
        return self

    def footer(self, footer: Path) -> Self:
        """
        Adds a footer HTML file to the generated PDF.

        Args:
            footer: A Path object representing the path to the footer HTML file.

        Returns:
            self: The current instance of the class, allowing for method chaining.
        """
        self._add_file_map(footer, name="footer.html")  # type: ignore[attr-defined]
        return self


class RenderControlMixin:
    """

    Provides control over the rendering process, allowing to specify a delay
    before rendering begins and to specify an expression to wait for.


    See [documentation](https://gotenberg.dev/docs/routes#wait-before-rendering-chromium) for more details.

    """

    def render_wait(self, wait: Union[float, int, timedelta]) -> Self:
        """
        Specifies the delay before rendering begins.

        Args:
            wait: The delay before rendering begins. This can be a float or integer
                    representing seconds, or a timedelta object.

        Returns:
            self: The current instance of the class, allowing for method chaining.

        Raises:
            NegativeWaitDurationError: If the wait duration is negative.
        """
        time_s = wait.total_seconds() if isinstance(wait, timedelta) else wait
        if time_s < 0:
            raise NegativeWaitDurationError
        self._form_data.update({"waitDelay": f"{time_s}s"})  # type: ignore[attr-defined,misc]
        return self

    def render_expression(self, expr: str) -> Self:
        """
        Specifies an expression to wait for before rendering begins.

        Args:
            expr: The expression to wait for.  The exact format and behavior depend
                    on the underlying rendering engine.  Consult the Gotenberg
                    documentation for details.

        Returns:
            self: The current instance of the class, allowing for method chaining.
        """
        self._form_data.update({"waitForExpression": expr})  # type: ignore[attr-defined,misc]
        return self


class EmulatedMediaMixin:
    """
    Allows to emulate different media types (print or screen) during rendering.

    See [documentation](https://gotenberg.dev/docs/routes#emulated-media-type-chromium) for more details.
    """

    def media_type(self, media_type: Literal["print", "screen"]) -> Self:
        """
        Specifies the emulated media type.

        Args:
          media_type: The media type to emulate.  Must be either "print" or "screen".

        Returns:
          self: The current instance of the class, allowing for method chaining.
        """
        self._form_data.update({"emulatedMediaType": media_type})  # type: ignore[attr-defined,misc]
        return self


class CookiesMixin:
    """
    Allows to set cookies for the route

    See [documentation](https://gotenberg.dev/docs/routes#cookies-chromium) for more details.
    """

    def cookies(self, cookies: list[CookieJar]) -> Self:
        """
        Sets cookies for the rendering process.

        Args:
          cookies: A list of CookieJar objects, each representing a cookie.

        Returns:
          self: The current instance of the class, allowing for method chaining.
        """
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
        codes_str = ",".join([str(int(x)) for x in codes])
        self._form_data.update({"failOnHttpStatusCodes": f"[{codes_str}]"})  # type: ignore[attr-defined,misc]
        return self


class NetworkErrorsMixin:
    """
    https://gotenberg.dev/docs/routes#network-errors-chromium
    """

    def fail_on_resource_loading_failed(self, *, fail_on_resource_loading_failed: bool) -> Self:
        self._form_data.update(bool_to_form("failOnResourceLoadingFailed", fail_on_resource_loading_failed))  # type: ignore[attr-defined,misc]
        return self


class ConsoleExceptionMixin:
    """
    https://gotenberg.dev/docs/routes#console-exceptions-chromium
    """

    def fail_on_console_exception(self, *, fail_on_console_exception: bool) -> Self:
        """
        Enable or disable failing on console exceptions
        """
        self._form_data.update(bool_to_form("failOnConsoleExceptions", fail_on_console_exception))  # type: ignore[attr-defined,misc]
        return self

    def fail_on_exceptions(self) -> Self:
        """
        Enable failing on console exceptions
        """
        return self.fail_on_console_exception(fail_on_console_exception=True)

    def dont_fail_on_exceptions(self) -> Self:
        """
        Disable failing on console exceptions
        """
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

    def image_optimize(self, *, optimize_for_speed: bool) -> Self:
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
