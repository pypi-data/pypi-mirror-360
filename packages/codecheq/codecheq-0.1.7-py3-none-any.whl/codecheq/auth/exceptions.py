"""
Authentication Exception Classes

Custom exceptions for handling authentication and API token verification errors.
"""


class AuthenticationError(Exception):
    """Base exception for all authentication-related errors."""
    pass


class TokenVerificationError(AuthenticationError):
    """Raised when token verification fails."""
    pass


class InvalidTokenError(TokenVerificationError):
    """Raised when the provided token is invalid or malformed."""
    pass


class TokenExpiredError(TokenVerificationError):
    """Raised when the token has expired."""
    pass


class NetworkError(AuthenticationError):
    """Raised when there are network issues communicating with the token portal."""
    pass


class TokenPortalError(AuthenticationError):
    """Raised when the token portal returns an error response."""
    pass 