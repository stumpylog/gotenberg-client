# SPDX-FileCopyrightText: 2025-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
from typing import Final


class ReadPdfMetadataRoute:
    """
    https://gotenberg.dev/docs/routes#read-pdf-metadata-route
    """

    URL: Final[str] = "/forms/pdfengines/metadata/read"


class WritePdfMetadataRoute:
    """
    https://gotenberg.dev/docs/routes#write-pdf-metadata-route
    """

    URL: Final[str] = "/forms/pdfengines/metadata/write"
