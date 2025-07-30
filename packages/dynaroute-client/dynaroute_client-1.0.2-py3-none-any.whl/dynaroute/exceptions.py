class DynaRouteError(Exception):
    """Base exception for all DynaRoute client errors."""

    pass


class AuthenticationError(DynaRouteError):
    """Raised when there is an authentication issue (e.g., invalid API key)."""

    pass


class APIError(DynaRouteError):
    """Raised for general API errors (e.g., server-side problems)."""

    pass


class InvalidRequestError(DynaRouteError):
    """Raised for errors in the request format (e.g., malformed JSON)."""

    pass
