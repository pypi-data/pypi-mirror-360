"""iProov Portal Authentication Library

A Python library for authenticating with iProov Portal services using Google OAuth2.
"""

from .auth import IProovPortalAuth
from .config import Environment, AuthConfig
from .exceptions import (
    IProovPortalAuthError,
    TokenExpiredError,
    AuthenticationError,
    ConfigurationError,
    NetworkError,
)

__version__ = "1.0.1"
__all__ = [
    "IProovPortalAuth",
    "Environment",
    "AuthConfig",
    "IProovPortalAuthError",
    "TokenExpiredError",
    "AuthenticationError",
    "ConfigurationError",
    "NetworkError",
] 