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


class CannotExtractHereError(BaseClientError):
    pass
