# SPDX-FileCopyrightText: 2023-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from functools import lru_cache
from importlib.util import find_spec
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Final

if TYPE_CHECKING:
    from magika import Magika


# See https://github.com/psf/requests/issues/1081#issuecomment-428504128
class ForceMultipartList(list):
    def __bool__(self) -> bool:
        return True


def optional_to_form(value: bool | int | float | str | None, name: str) -> dict[str, str]:  # noqa: FBT001
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


def guess_mime_type_stdlib(url: str | Path) -> str | None:  # pragma: no cover
    """
    Guesses the MIME type of a URL using the standard library.

    Args:
        url: The URL to guess the MIME type for.

    Returns:
        The guessed MIME type, or None if it could not be determined.
    """

    import mimetypes  # noqa: PLC0415

    mime_type, _ = mimetypes.guess_type(str(url))  # Ensure URL is a string
    return mime_type


def guess_mime_type_magic(url: str | Path) -> str | None:
    """
    Guesses the MIME type of a file using libmagic.

    Args:
        url: The path to the file or URL to guess the MIME type for.

    Returns:
        The guessed MIME type, or None if it could not be determined.
    """

    import magic  # type: ignore[import-not-found]  # noqa: PLC0415

    try:
        return magic.from_file(str(url), mime=True)  # type: ignore[misc]
    except Exception:  # pragma: no cover
        # Handle libmagic exceptions gracefully
        return None


@lru_cache(maxsize=1)  # type: ignore[misc]
def _get_magika() -> "Magika":
    # Loading the model is expensive, so do it once and only when first needed
    import magika  # noqa: PLC0415

    return magika.Magika()


def guess_mime_type_magika(url: str | Path) -> str | None:
    """
    Guesses the MIME type of a file using Magika.

    Args:
        url: The path to the file to guess the MIME type for.

    Returns:
        The guessed MIME type, or None if it could not be determined.
    """

    try:
        return str(_get_magika().identify_path(Path(url)).output.mime_type)
    except Exception:  # pragma: no cover
        # Handle Magika exceptions gracefully
        return None


def _select_mime_guesser() -> Callable[[str | Path], str | None]:
    """
    Picks the best available MIME type detection: libmagic, then Magika, then the standard library.
    """
    if find_spec("magic") is not None:
        return guess_mime_type_magic
    if find_spec("magika") is not None:
        return guess_mime_type_magika
    return guess_mime_type_stdlib


# Use the best option
guess_mime_type = _select_mime_guesser()

FORCE_MULTIPART: Final = ForceMultipartList()
