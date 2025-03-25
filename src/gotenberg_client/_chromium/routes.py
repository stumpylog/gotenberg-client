# SPDX-FileCopyrightText: 2025-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
from typing import Final


class UrlToPdfRoute:
    """
    https://gotenberg.dev/docs/routes#url-into-pdf-route
    """

    URL: Final[str] = "/forms/chromium/convert/url"


class HtmlToPdfRoute:
    """
    https://gotenberg.dev/docs/routes#html-file-into-pdf-route
    """

    URL: Final[str] = "/forms/chromium/convert/html"


class MarkdownToPdfRoute:
    """
    https://gotenberg.dev/docs/routes#markdown-files-into-pdf-route
    """

    URL: Final[str] = "/forms/chromium/convert/url"


class ScreenshotFromUrlRoute:
    """
    https://gotenberg.dev/docs/routes#screenshots-route
    """

    URL: Final[str] = "/forms/chromium/screenshot/url"


class ScreenshotFromHtmlRoute:
    """
    https://gotenberg.dev/docs/routes#screenshots-route
    """

    URL: Final[str] = "/forms/chromium/screenshot/html"


class ScreenshotFromMarkdownRoute:
    """
    https://gotenberg.dev/docs/routes#screenshots-route
    """

    URL: Final[str] = "/forms/chromium/screenshot/markdown"
