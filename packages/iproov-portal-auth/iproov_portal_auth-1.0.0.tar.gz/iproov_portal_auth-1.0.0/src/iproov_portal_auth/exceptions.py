"""Custom exceptions for iProov Portal Authentication."""


class IProovPortalAuthError(Exception):
    """Base exception for iProov Portal authentication errors."""
    pass


class TokenExpiredError(IProovPortalAuthError):
    """Raised when a token has expired."""
    pass


class AuthenticationError(IProovPortalAuthError):
    """Raised when authentication fails."""
    pass


class ConfigurationError(IProovPortalAuthError):
    """Raised when configuration is invalid."""
    pass


class NetworkError(IProovPortalAuthError):
    """Raised when network requests fail."""
    pass 