# SPDX-FileCopyrightText: 2023-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
from importlib.util import find_spec
from pathlib import Path
from typing import Dict
from typing import Optional
from typing import Union


def optional_to_form(value: Optional[Union[bool, int, float, str]], name: str) -> Dict[str, str]:
    """
    Quick helper to convert an optional type into a form data field
    with the given name or no changes if the value is None
    """
    if value is None:
        return {}
    else:
        return {name: str(value).lower()}


def guess_mime_type_stdlib(url: Path) -> Optional[str]:  # pragma: no cover
    """
    Uses the standard library to guess a mimetype
    """
    import mimetypes

    mime_type, _ = mimetypes.guess_type(url)
    return mime_type


def guess_mime_type_magic(url: Path) -> Optional[str]:
    """
    Uses libmagic to guess the mimetype
    """
    import magic  # type: ignore [import-not-found]

    return magic.from_file(url, mime=True)  # type: ignore [misc]


# Use the best option
guess_mime_type = guess_mime_type_magic if find_spec("magic") is not None else guess_mime_type_stdlib
