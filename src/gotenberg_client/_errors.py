from httpx import Response


class BaseClientError(Exception):
    """
    Base exception for any errors raised directly by this library.

    All custom exceptions in this library inherit from this class,
    allowing for more granular exception handling.
    """


class UnreachableCodeError(BaseClientError):
    """
    Raised when execution reaches code that should be unreachable.

    This exception indicates a logical error in the code flow,
    signaling that a branch of code that should never be executed was reached.

    This error is internal only, only for coverage/mypy
    """


class MaxRetriesExceededError(BaseClientError):
    """
    Raised if the number of retries exceeded the configured maximum.

    This exception occurs when an operation fails repeatedly and
    exhausts all retry attempts allowed by the configuration.

    Attributes:
        response (Response): The last failed response that triggered this exception.
    """

    def __init__(self, *, response: Response) -> None:
        super().__init__()
        self.response = response


class CannotExtractHereError(BaseClientError):
    """
    Raised when extraction of a ZipFileResponse cannot be performed at the specified location.
    """


class InvalidPdfRevisionError(BaseClientError):
    """
    Raised when attempting to set the PDF version using the metadata to an invalid value.
    """


class InvalidKeywordError(BaseClientError):
    """
    Raised when an invalid keyword is provided to the PDF metadata
    """


class NegativeWaitDurationError(BaseClientError):
    """
    Raised when a negative wait duration is provided as a waiting time.
    """
