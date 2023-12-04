# SPDX-FileCopyrightText: 2023-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
import logging

from gotenberg_client._base import BaseRoute
from gotenberg_client._typing_compat import Self
from gotenberg_client.options import PageOrientation

logger = logging.getLogger()


class ConvertBaseRoute(BaseRoute):
    """
    All 3 convert routes provide control over orientation and page ranges
    """

    def orient(self, orient: PageOrientation) -> Self:
        """
        Sets the page orientation, either Landscape or portrait
        """
        self._form_data.update(orient.to_form())
        return self

    def page_ranges(self, ranges: str) -> Self:
        """
        Sets the page range string, allowing either some range or just a
        few pages
        """
        self._form_data.update({"nativePageRanges": ranges})
        return self
