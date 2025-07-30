"""Configuration management for iProov Portal Authentication."""

import os
from enum import Enum
from typing import Optional
from dataclasses import dataclass

from .exceptions import ConfigurationError


class Environment(Enum):
    """Available environments for iProov Portal."""
    PRODUCTION = "prod"
    UAT = "uat"
    DEVELOPMENT = "dev"


@dataclass
class AuthConfig:
    """Configuration for iProov Portal Authentication."""
    
    api_key: str
    client_id: Optional[str] = None
    environment: Environment = Environment.PRODUCTION
    timeout: float = 20.0
    
    def __post_init__(self) -> None:
        """Set default client_id if not provided."""
        if self.client_id is None:
            self.client_id = self.get_default_client_id(self.environment)
    
    @property
    def base_url(self) -> str:
        """Get the base URL for the current environment."""
        base_urls = {
            Environment.PRODUCTION: "https://login.secure.iproov.me",
            Environment.UAT: "https://login.uat.secure.iproov.me",
            Environment.DEVELOPMENT: "https://login.dev.secure.iproov.me",
        }
        return base_urls[self.environment]
    
    @property
    def sign_in_with_idp_api(self) -> str:
        """Get the sign in with IDP API URL."""
        return "https://identitytoolkit.googleapis.com/v1/accounts:signInWithIdp"
    
    @property
    def request_uri(self) -> str:
        """Get the request URI for the current environment."""
        if self.environment == Environment.PRODUCTION:
            return "https://login.secure.iproov.me/api/token"
        elif self.environment == Environment.UAT:
            return "https://login.uat.secure.iproov.me/api/token"
        else:  # Development
            return "https://login.dev.secure.iproov.me/api/token"
    
    @classmethod
    def get_default_client_id(cls, environment: Environment) -> str:
        """Get the default client ID for the given environment."""
        default_client_ids = {
            Environment.PRODUCTION: "105336304952-n6ddad4ea9lc2hrc70791ibq6pfdfemc.apps.googleusercontent.com",
            Environment.UAT: "973312410545-63o5poolj5kocnu0lceocvagajak4sgf.apps.googleusercontent.com",
            Environment.DEVELOPMENT: "568086550639-lq968h5moe814cf0o45oftn1p0ck0tgn.apps.googleusercontent.com",
        }
        return default_client_ids[environment]
    
    @classmethod
    def from_environment(cls, environment: Optional[str] = None) -> "AuthConfig":
        """Create configuration from environment variables."""
        # Determine environment first
        env_str = environment or os.getenv("IPROOV_PORTAL_ENV", "prod")
        if env_str is None:
            env_str = "prod"  # This should never happen due to default, but satisfy mypy
        try:
            env = Environment(env_str.lower())
        except ValueError:
            raise ConfigurationError(f"Invalid environment: {env_str}")
        
        # Get client ID (use default if not provided)
        client_id = os.getenv("IPROOV_PORTAL_CLIENT_ID")
        if not client_id:
            client_id = cls.get_default_client_id(env)
        
        # Get API key (required, no default)
        api_key = os.getenv("IPROOV_PORTAL_API_KEY")
        if not api_key:
            raise ConfigurationError("IPROOV_PORTAL_API_KEY environment variable is required")
        
        # Get timeout
        timeout_str = os.getenv("IPROOV_PORTAL_TIMEOUT", "20.0")
        try:
            timeout = float(timeout_str)
        except ValueError:
            raise ConfigurationError(f"Invalid timeout value: {timeout_str}")
        
        return cls(
            client_id=client_id,
            api_key=api_key,
            environment=env,
            timeout=timeout,
        )
    
    def validate(self) -> None:
        """Validate the configuration."""
        if not self.client_id:
            raise ConfigurationError("Client ID is required")
        
        if not self.api_key:
            raise ConfigurationError("API key is required")
        
        if self.timeout <= 0:
            raise ConfigurationError("Timeout must be positive")


# Default configuration using environment variables
def get_default_config() -> AuthConfig:
    """Get default configuration with fallback values."""
    # Determine environment
    env_str = os.getenv("IPROOV_PORTAL_ENV", "prod")
    if env_str is None:
        env_str = "prod"  # This should never happen due to default, but satisfy mypy
    try:
        env = Environment(env_str.lower())
    except ValueError:
        raise ConfigurationError(f"Invalid environment: {env_str}")
    
    # Get client ID (use default if not provided)
    client_id = os.getenv("IPROOV_PORTAL_CLIENT_ID")
    if not client_id:
        client_id = AuthConfig.get_default_client_id(env)
    
    # Get API key (required, no default)
    api_key = os.getenv("IPROOV_PORTAL_API_KEY")
    if not api_key:
        raise ConfigurationError("IPROOV_PORTAL_API_KEY environment variable is required")
    
    return AuthConfig(
        client_id=client_id,
        api_key=api_key,
        environment=env,
        timeout=float(os.getenv("IPROOV_PORTAL_TIMEOUT", "20.0")),
    ) 