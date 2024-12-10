from httpx import Response


class BaseClientError(Exception):
    """
    Base exception for any errors raised directly by this library
    """


class UnreachableCodeError(BaseClientError):
    pass


class MaxRetriesExceededError(BaseClientError):
    """
    Raised if the number of retries exceeded the configured maximum
    """

    def __init__(self, *, response: Response) -> None:
        super().__init__()
        self.response = response


class CannotExtractHereError(BaseClientError):
    pass


class InvalidPdfRevisionError(BaseClientError):
    pass


class InvalidKeywordError(BaseClientError):
    pass
