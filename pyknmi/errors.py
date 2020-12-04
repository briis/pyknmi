"""Define package errors."""


class KnmiError(Exception):
    """Define a base error."""

    pass


class InvalidApiKey(KnmiError):
    """Define an error related to invalid or missing API Key."""

    pass


class RequestError(KnmiError):
    """Define an error related to invalid requests."""

    pass

class ResultError(KnmiError):
    """Define an error related to the result returned from a request."""

    pass
