"""Tests for configuration module."""

import os
import pytest
from unittest.mock import patch

from iproov_portal_auth.config import Environment, AuthConfig, get_default_config
from iproov_portal_auth.exceptions import ConfigurationError


class TestEnvironment:
    """Test Environment enum."""
    
    def test_environment_values(self):
        """Test environment enum values."""
        assert Environment.PRODUCTION.value == "prod"
        assert Environment.UAT.value == "uat"
        assert Environment.DEVELOPMENT.value == "dev"


class TestAuthConfig:
    """Test AuthConfig class."""
    
    def test_init_with_defaults(self):
        """Test config initialization with default values."""
        config = AuthConfig(
            client_id="test-client-id",
            api_key="test-api-key"
        )
        assert config.client_id == "test-client-id"
        assert config.api_key == "test-api-key"
        assert config.environment == Environment.PRODUCTION
        assert config.timeout == 20.0
    
    def test_init_with_custom_values(self):
        """Test config initialization with custom values."""
        config = AuthConfig(
            client_id="test-client-id",
            api_key="test-api-key",
            environment=Environment.UAT,
            timeout=30.0
        )
        assert config.environment == Environment.UAT
        assert config.timeout == 30.0
    
    def test_base_url_production(self):
        """Test base URL for production environment."""
        config = AuthConfig(
            client_id="test-client-id",
            api_key="test-api-key",
            environment=Environment.PRODUCTION
        )
        assert config.base_url == "https://login.secure.iproov.me"
    
    def test_base_url_uat(self):
        """Test base URL for UAT environment."""
        config = AuthConfig(
            client_id="test-client-id",
            api_key="test-api-key",
            environment=Environment.UAT
        )
        assert config.base_url == "https://login.uat.secure.iproov.me"
    
    def test_base_url_development(self):
        """Test base URL for development environment."""
        config = AuthConfig(
            client_id="test-client-id",
            api_key="test-api-key",
            environment=Environment.DEVELOPMENT
        )
        assert config.base_url == "https://login.dev.secure.iproov.me"
    
    def test_request_uri_production(self):
        """Test request URI for production environment."""
        config = AuthConfig(
            client_id="test-client-id",
            api_key="test-api-key",
            environment=Environment.PRODUCTION
        )
        assert config.request_uri == "https://login.secure.iproov.me/api/token"
    
    def test_request_uri_uat(self):
        """Test request URI for UAT environment."""
        config = AuthConfig(
            client_id="test-client-id",
            api_key="test-api-key",
            environment=Environment.UAT
        )
        assert config.request_uri == "https://login.uat.secure.iproov.me/api/token"
    
    def test_request_uri_development(self):
        """Test request URI for development environment."""
        config = AuthConfig(
            client_id="test-client-id",
            api_key="test-api-key",
            environment=Environment.DEVELOPMENT
        )
        assert config.request_uri == "https://login.dev.secure.iproov.me/api/token"
    
    def test_sign_in_with_idp_api(self):
        """Test sign in with IDP API URL."""
        config = AuthConfig(
            client_id="test-client-id",
            api_key="test-api-key"
        )
        expected_url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithIdp"
        assert config.sign_in_with_idp_api == expected_url
    
    def test_validate_success(self):
        """Test successful validation."""
        config = AuthConfig(
            client_id="test-client-id",
            api_key="test-api-key"
        )
        config.validate()  # Should not raise
    
    def test_validate_missing_client_id(self):
        """Test validation with missing client ID."""
        config = AuthConfig(
            client_id="",
            api_key="test-api-key"
        )
        with pytest.raises(ConfigurationError, match="Client ID is required"):
            config.validate()
    
    def test_validate_missing_api_key(self):
        """Test validation with missing API key."""
        config = AuthConfig(
            client_id="test-client-id",
            api_key=""
        )
        with pytest.raises(ConfigurationError, match="API key is required"):
            config.validate()
    
    def test_validate_invalid_timeout(self):
        """Test validation with invalid timeout."""
        config = AuthConfig(
            client_id="test-client-id",
            api_key="test-api-key",
            timeout=-1.0
        )
        with pytest.raises(ConfigurationError, match="Timeout must be positive"):
            config.validate()
    
    def test_get_default_client_id_production(self):
        """Test getting default client ID for production."""
        client_id = AuthConfig.get_default_client_id(Environment.PRODUCTION)
        assert client_id == "105336304952-n6ddad4ea9lc2hrc70791ibq6pfdfemc.apps.googleusercontent.com"
    
    def test_get_default_client_id_uat(self):
        """Test getting default client ID for UAT."""
        client_id = AuthConfig.get_default_client_id(Environment.UAT)
        assert client_id == "973312410545-63o5poolj5kocnu0lceocvagajak4sgf.apps.googleusercontent.com"
    
    def test_get_default_client_id_development(self):
        """Test getting default client ID for development."""
        client_id = AuthConfig.get_default_client_id(Environment.DEVELOPMENT)
        assert client_id == "568086550639-lq968h5moe814cf0o45oftn1p0ck0tgn.apps.googleusercontent.com"
    
    @patch.dict(os.environ, {
        "IPROOV_PORTAL_CLIENT_ID": "env-client-id",
        "IPROOV_PORTAL_API_KEY": "env-api-key",
        "IPROOV_PORTAL_ENV": "uat",
        "IPROOV_PORTAL_TIMEOUT": "25.0"
    })
    def test_from_environment_success(self):
        """Test creating config from environment variables."""
        config = AuthConfig.from_environment()
        assert config.client_id == "env-client-id"
        assert config.api_key == "env-api-key"
        assert config.environment == Environment.UAT
        assert config.timeout == 25.0
    
    @patch.dict(os.environ, {
        "IPROOV_PORTAL_API_KEY": "env-api-key",
    }, clear=True)
    def test_from_environment_missing_client_id_uses_default(self):
        """Test creating config from environment with missing client ID uses default."""
        config = AuthConfig.from_environment()
        # Should use default client ID for production environment
        assert config.client_id == "105336304952-n6ddad4ea9lc2hrc70791ibq6pfdfemc.apps.googleusercontent.com"
        assert config.api_key == "env-api-key"
        assert config.environment == Environment.PRODUCTION
    
    @patch.dict(os.environ, {
        "IPROOV_PORTAL_API_KEY": "env-api-key",
        "IPROOV_PORTAL_ENV": "uat"
    }, clear=True)
    def test_from_environment_missing_client_id_uses_default_uat(self):
        """Test creating config from environment with missing client ID uses UAT default."""
        config = AuthConfig.from_environment()
        # Should use default client ID for UAT environment
        assert config.client_id == "973312410545-63o5poolj5kocnu0lceocvagajak4sgf.apps.googleusercontent.com"
        assert config.api_key == "env-api-key"
        assert config.environment == Environment.UAT
    
    @patch.dict(os.environ, {}, clear=True)
    def test_from_environment_missing_api_key(self):
        """Test creating config from environment with missing API key."""
        with pytest.raises(ConfigurationError, match="IPROOV_PORTAL_API_KEY environment variable is required"):
            AuthConfig.from_environment()
    
    @patch.dict(os.environ, {
        "IPROOV_PORTAL_CLIENT_ID": "env-client-id",
        "IPROOV_PORTAL_API_KEY": "env-api-key",
        "IPROOV_PORTAL_ENV": "invalid-env"
    })
    def test_from_environment_invalid_environment(self):
        """Test creating config from environment with invalid environment."""
        with pytest.raises(ConfigurationError, match="Invalid environment: invalid-env"):
            AuthConfig.from_environment()
    
    @patch.dict(os.environ, {
        "IPROOV_PORTAL_CLIENT_ID": "env-client-id",
        "IPROOV_PORTAL_API_KEY": "env-api-key",
        "IPROOV_PORTAL_TIMEOUT": "invalid-timeout"
    })
    def test_from_environment_invalid_timeout(self):
        """Test creating config from environment with invalid timeout."""
        with pytest.raises(ConfigurationError, match="Invalid timeout value: invalid-timeout"):
            AuthConfig.from_environment()
    
    def test_from_environment_override_env_param(self):
        """Test overriding environment with parameter."""
        with patch.dict(os.environ, {
            "IPROOV_PORTAL_CLIENT_ID": "env-client-id",
            "IPROOV_PORTAL_API_KEY": "env-api-key",
            "IPROOV_PORTAL_ENV": "prod"
        }):
            config = AuthConfig.from_environment(environment="dev")
            assert config.environment == Environment.DEVELOPMENT


class TestGetDefaultConfig:
    """Test get_default_config function."""
    
    @patch.dict(os.environ, {
        "IPROOV_PORTAL_CLIENT_ID": "env-client-id",
        "IPROOV_PORTAL_API_KEY": "env-api-key",
        "IPROOV_PORTAL_ENV": "uat"
    })
    def test_get_default_config_from_env(self):
        """Test getting default config from environment."""
        config = get_default_config()
        assert config.client_id == "env-client-id"
        assert config.api_key == "env-api-key"
        assert config.environment == Environment.UAT
    
    @patch.dict(os.environ, {
        "IPROOV_PORTAL_API_KEY": "env-api-key"
    }, clear=True)
    def test_get_default_config_fallback(self):
        """Test getting default config with fallback values."""
        config = get_default_config()
        assert config.client_id == "105336304952-n6ddad4ea9lc2hrc70791ibq6pfdfemc.apps.googleusercontent.com"
        assert config.api_key == "env-api-key"
        assert config.environment == Environment.PRODUCTION
        assert config.timeout == 20.0
    
    @patch.dict(os.environ, {}, clear=True)
    def test_get_default_config_missing_api_key(self):
        """Test getting default config with missing API key raises error."""
        with pytest.raises(ConfigurationError, match="IPROOV_PORTAL_API_KEY environment variable is required"):
            get_default_config() 