# SPDX-FileCopyrightText: 2025-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
from gotenberg_client._bookmarks.api import AsyncBookmarksApi
from gotenberg_client._bookmarks.api import SyncBookmarksApi
from gotenberg_client._bookmarks.routes import BookmarkEntry

__all__ = ["AsyncBookmarksApi", "BookmarkEntry", "SyncBookmarksApi"]
