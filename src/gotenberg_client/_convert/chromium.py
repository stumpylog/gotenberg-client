# SPDX-FileCopyrightText: 2023-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
import logging
from pathlib import Path
from typing import List
from typing import Literal

from gotenberg_client._base import BaseApi
from gotenberg_client._base import BaseSingleFileResponseRoute
from gotenberg_client._convert.common import ConsoleExceptionMixin
from gotenberg_client._convert.common import CustomHTTPHeaderMixin
from gotenberg_client._convert.common import EmulatedMediaMixin
from gotenberg_client._convert.common import HeaderFooterMixin
from gotenberg_client._convert.common import InvalidStatusCodesMixin
from gotenberg_client._convert.common import PageOrientMixin
from gotenberg_client._convert.common import PagePropertiesMixin
from gotenberg_client._convert.common import PerformanceModeMixin
from gotenberg_client._convert.common import RenderControlMixin
from gotenberg_client._types import Self
from gotenberg_client._utils import FORCE_MULTIPART
from gotenberg_client._utils import ForceMultipartDict

logger = logging.getLogger()


class _FileBasedRoute(BaseSingleFileResponseRoute):
    def index(self, index: Path) -> Self:
        self._add_file_map(index, "index.html")
        return self


class _RouteWithResources(BaseSingleFileResponseRoute):
    def resource(self, resource: Path) -> Self:
        self._add_file_map(resource)
        return self

    def resources(self, resources: List[Path]) -> Self:
        for x in resources:
            self.resource(x)
        return self


class HtmlRoute(
    PagePropertiesMixin,
    HeaderFooterMixin,
    RenderControlMixin,
    PageOrientMixin,
    _RouteWithResources,
    _FileBasedRoute,
):
    """
    https://gotenberg.dev/docs/routes#html-file-into-pdf-route
    """


class UrlRoute(
    PagePropertiesMixin,
    HeaderFooterMixin,
    RenderControlMixin,
    ConsoleExceptionMixin,
    EmulatedMediaMixin,
    CustomHTTPHeaderMixin,
    PageOrientMixin,
    BaseSingleFileResponseRoute,
):
    """
    https://gotenberg.dev/docs/routes#url-into-pdf-route
    """

    def url(self, url: str) -> Self:
        self._form_data["url"] = url
        return self

    def _get_files(self) -> ForceMultipartDict:
        return FORCE_MULTIPART


class MarkdownRoute(PagePropertiesMixin, HeaderFooterMixin, _RouteWithResources, _FileBasedRoute):
    """
    https://gotenberg.dev/docs/routes#markdown-files-into-pdf-route
    """

    def markdown_file(self, markdown_file: Path) -> Self:
        self._add_file_map(markdown_file)
        return self

    def markdown_files(self, markdown_files: List[Path]) -> Self:
        for x in markdown_files:
            self.markdown_file(x)
        return self


class ScreenshotRoute(
    RenderControlMixin,
    EmulatedMediaMixin,
    CustomHTTPHeaderMixin,
    InvalidStatusCodesMixin,
    ConsoleExceptionMixin,
    PerformanceModeMixin,
    PageOrientMixin,
    BaseSingleFileResponseRoute,
):
    """
    https://gotenberg.dev/docs/routes#screenshots-route
    """

    _QUALITY_MAX = 100
    _QUALITY_MIN = 0

    def output_format(self, output_format: Literal["png", "jpeg", "webp"] = "png") -> Self:
        self._form_data.update({"format": output_format})
        return self

    def quality(self, quality: int) -> Self:
        if quality > self._QUALITY_MAX:
            logger.warning(f"quality {quality} is above {self._QUALITY_MAX}, resetting to {self._QUALITY_MAX}")
            quality = self._QUALITY_MAX
        elif quality < self._QUALITY_MIN:
            logger.warning(f"quality {quality} is below {self._QUALITY_MIN}, resetting to {self._QUALITY_MIN}")
            quality = self._QUALITY_MIN
        self._form_data.update({"quality": str(quality)})
        return self

    def optimize_speed(self) -> Self:
        self._form_data.update({"optimizeForSpeed": "true"})
        return self

    def optimize_size(self) -> Self:
        self._form_data.update({"optimizeForSpeed": "false"})
        return self


class ScreenshotRouteUrl(ScreenshotRoute):
    def url(self, url: str) -> Self:
        self._form_data.update({"url": url})
        return self

    def _get_files(self) -> ForceMultipartDict:
        return FORCE_MULTIPART


class ScreenshotRouteHtml(_FileBasedRoute, _RouteWithResources, ScreenshotRoute):
    pass


class ScreenshotRouteMarkdown(_FileBasedRoute, _RouteWithResources, ScreenshotRoute):
    pass


class ChromiumApi(BaseApi):
    _URL_CONVERT_ENDPOINT = "/forms/chromium/convert/url"
    _HTML_CONVERT_ENDPOINT = "/forms/chromium/convert/html"
    _MARKDOWN_CONVERT_ENDPOINT = "/forms/chromium/convert/markdown"
    _SCREENSHOT_URL = "/forms/chromium/screenshot/url"
    _SCREENSHOT_HTML = "/forms/chromium/screenshot/html"
    _SCREENSHOT_MARK_DOWN = "/forms/chromium/screenshot/markdown"

    def html_to_pdf(self) -> HtmlRoute:
        return HtmlRoute(self._client, self._HTML_CONVERT_ENDPOINT)

    def url_to_pdf(self) -> UrlRoute:
        return UrlRoute(self._client, self._URL_CONVERT_ENDPOINT)

    def markdown_to_pdf(self) -> MarkdownRoute:
        return MarkdownRoute(self._client, self._MARKDOWN_CONVERT_ENDPOINT)

    def screenshot_url(self) -> ScreenshotRouteUrl:
        return ScreenshotRouteUrl(self._client, self._SCREENSHOT_URL)

    def screenshot_html(self) -> ScreenshotRouteHtml:
        return ScreenshotRouteHtml(self._client, self._SCREENSHOT_HTML)

    def screenshot_markdown(self) -> ScreenshotRouteMarkdown:
        return ScreenshotRouteMarkdown(self._client, self._SCREENSHOT_MARK_DOWN)
