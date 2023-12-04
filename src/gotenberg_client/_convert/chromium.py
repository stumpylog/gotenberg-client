# SPDX-FileCopyrightText: 2023-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
import json
import logging
from pathlib import Path
from typing import Dict
from typing import Final
from typing import List
from typing import Union

from gotenberg_client._base import BaseApi
from gotenberg_client._convert.common import ConvertBaseRoute
from gotenberg_client._typing_compat import Self
from gotenberg_client.options import EmulatedMediaType
from gotenberg_client.options import Margin
from gotenberg_client.options import PageSize

logger = logging.getLogger()


# See https://github.com/psf/requests/issues/1081#issuecomment-428504128
class ForceMultipartDict(Dict):
    def __bool__(self) -> bool:
        return True


FORCE_MULTIPART: Final = ForceMultipartDict()


class ChromiumBaseRoute(ConvertBaseRoute):
    """
    https://gotenberg.dev/docs/routes#convert-with-chromium
    """

    def header(self, header: Path) -> Self:
        self._add_file_map(header, "header.html")
        return self

    def footer(self, footer: Path) -> Self:
        self._add_file_map(footer, "footer.html")
        return self

    def resource(self, resource: Path) -> Self:
        self._add_file_map(resource)
        return self

    def resources(self, resources: List[Path]) -> Self:
        for x in resources:
            self.resource(x)
        return self

    def size(self, size: PageSize) -> Self:
        self._form_data.update(size.to_form())
        return self

    page_size = size

    def margins(self, margins: Margin) -> Self:
        self._form_data.update(margins.to_form())
        return self

    def prefer_css_page_size(self) -> Self:
        self._form_data.update({"preferCssPageSize": "true"})
        return self

    def prefer_set_page_size(self) -> Self:
        self._form_data.update({"preferCssPageSize": "false"})
        return self

    def background_graphics(self) -> Self:
        self._form_data.update({"printBackground": "true"})
        return self

    def no_background_graphics(self) -> Self:
        self._form_data.update({"printBackground": "false"})
        return self

    def hide_background(self) -> Self:
        self._form_data.update({"omitBackground": "true"})
        return self

    def show_background(self) -> Self:
        self._form_data.update({"omitBackground": "false"})
        return self

    def scale(self, scale: Union[int, float]) -> Self:
        self._form_data.update({"scale": str(scale)})
        return self

    def render_wait(self, wait: Union[int, float]) -> Self:
        self._form_data.update({"waitDelay": str(wait)})
        return self

    def render_expr(self, expr: str) -> Self:
        self._form_data.update({"waitForExpression": expr})
        return self

    def media_type(self, media_type: EmulatedMediaType) -> Self:
        self._form_data.update(media_type.to_form())
        return self

    def user_agent(self, agent: str) -> Self:
        self._form_data.update({"userAgent": agent})
        return self

    def headers(self, headers: Dict[str, str]) -> Self:
        json_str = json.dumps(headers)
        # TODO: Need to check this
        self._form_data.update({"extraHttpHeaders": json_str})
        return self

    def fail_on_exceptions(self) -> Self:
        self._form_data.update({"failOnConsoleExceptions": "true"})
        return self

    def dont_fail_on_exceptions(self) -> Self:
        self._form_data.update({"failOnConsoleExceptions": "false"})
        return self


class _FileBasedRoute(ChromiumBaseRoute):
    def index(self, index: Path) -> Self:
        self._add_file_map(index, "index.html")
        return self


class HtmlRoute(_FileBasedRoute):
    """
    https://gotenberg.dev/docs/routes#html-file-into-pdf-route
    """


class UrlRoute(ChromiumBaseRoute):
    """
    https://gotenberg.dev/docs/routes#url-into-pdf-route
    """

    def url(self, url: str) -> Self:
        self._form_data["url"] = url
        return self

    def _get_files(self) -> ForceMultipartDict:
        return FORCE_MULTIPART


class MarkdownRoute(_FileBasedRoute):
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


class ChromiumApi(BaseApi):
    _URL_CONVERT_ENDPOINT = "/forms/chromium/convert/url"
    _HTML_CONVERT_ENDPOINT = "/forms/chromium/convert/html"
    _MARKDOWN_CONVERT_ENDPOINT = "/forms/chromium/convert/markdown"

    def html_to_pdf(self) -> HtmlRoute:
        return HtmlRoute(self._client, self._HTML_CONVERT_ENDPOINT)

    def url_to_pdf(self) -> UrlRoute:
        return UrlRoute(self._client, self._URL_CONVERT_ENDPOINT)

    def markdown_to_pdf(self) -> MarkdownRoute:
        return MarkdownRoute(self._client, self._MARKDOWN_CONVERT_ENDPOINT)
