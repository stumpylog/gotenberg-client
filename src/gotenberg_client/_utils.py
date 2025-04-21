# SPDX-FileCopyrightText: 2023-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
from importlib.util import find_spec
from pathlib import Path
from typing import Final
from typing import Optional
from typing import Union


# See https://github.com/psf/requests/issues/1081#issuecomment-428504128
class ForceMultipartDict(dict):
    def __bool__(self) -> bool:
        return True


def optional_to_form(value: Optional[Union[bool, int, float, str]], name: str) -> dict[str, str]:
    """
    Converts an optional value to a form data field with the given name,
    handling None values gracefully.

    Args:
        value: The optional value to be converted.
        name: The name of the form data field.

    Returns:
        A dictionary containing the form data field with the given name and its converted value,
        or an empty dictionary if the value is None.
    """
    if value is None:  # pragma: no cover
        return {}
    else:
        return {name: str(value).lower()}


def bool_to_form(name: str, value: bool) -> dict[str, str]:  # noqa: FBT001
    """
    Converts an boolean value to a form data field with the given name, correcting the casing
    """
    bool_to_form_name: Final[dict[bool, str]] = {
        True: "true",
        False: "false",
    }
    return {name: bool_to_form_name[value]}


def guess_mime_type_stdlib(url: Union[str, Path]) -> Optional[str]:  # pragma: no cover
    """
    Guesses the MIME type of a URL using the standard library.

    Args:
        url: The URL to guess the MIME type for.

    Returns:
        The guessed MIME type, or None if it could not be determined.
    """

    import mimetypes

    mime_type, _ = mimetypes.guess_type(str(url))  # Ensure URL is a string
    return mime_type


def guess_mime_type_magic(url: Union[str, Path]) -> Optional[str]:
    """
    Guesses the MIME type of a file using libmagic.

    Args:
        url: The path to the file or URL to guess the MIME type for.

    Returns:
        The guessed MIME type, or None if it could not be determined.
    """

    import magic  # type: ignore[import-not-found]

    try:
        return magic.from_file(str(url), mime=True)  # type: ignore[misc]
    except Exception:  # pragma: no cover
        # Handle libmagic exceptions gracefully
        return None


# Use the best option
guess_mime_type = guess_mime_type_magic if find_spec("magic") is not None else guess_mime_type_stdlib

FORCE_MULTIPART: Final = ForceMultipartDict()
