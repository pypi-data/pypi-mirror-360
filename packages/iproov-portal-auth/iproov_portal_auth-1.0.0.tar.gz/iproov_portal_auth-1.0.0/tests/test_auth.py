"""Tests for authentication module."""

import json
import tempfile
from unittest.mock import patch, MagicMock, Mock
import pytest

from iproov_portal_auth.auth import IProovPortalAuth
from iproov_portal_auth.config import AuthConfig, Environment
from iproov_portal_auth.exceptions import (
    AuthenticationError,
    TokenExpiredError,
    NetworkError,
    ConfigurationError,
)


class TestIProovPortalAuth:
    """Test IProovPortalAuth class."""
    
    def create_test_config(self):
        """Create test configuration."""
        return AuthConfig(
            client_id="test-client-id",
            api_key="test-api-key",
            environment=Environment.UAT,
            timeout=10.0
        )
    
    def test_init_with_config(self):
        """Test initialization with provided config."""
        config = self.create_test_config()
        auth = IProovPortalAuth(config=config)
        assert auth.config == config
        assert auth.token_cache is not None
        assert auth._cached_user_data is None
    
    def test_init_with_default_config(self):
        """Test initialization with default config."""
        with patch('iproov_portal_auth.auth.get_default_config') as mock_get_config:
            mock_config = self.create_test_config()
            mock_get_config.return_value = mock_config
            
            auth = IProovPortalAuth()
            assert auth.config == mock_config
            mock_get_config.assert_called_once()
    
    def test_init_invalid_config(self):
        """Test initialization with invalid config."""
        invalid_config = AuthConfig(
            client_id="",  # Invalid empty client ID
            api_key="test-api-key"
        )
        
        with pytest.raises(ConfigurationError):
            IProovPortalAuth(config=invalid_config)
    
    @patch('requests.post')
    def test_exchange_google_id_token_success(self, mock_post):
        """Test successful Google ID token exchange."""
        config = self.create_test_config()
        auth = IProovPortalAuth(config=config)
        
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"idToken": "gcip-id-token"}
        mock_post.return_value = mock_response
        
        result = auth._exchange_google_id_token_for_gcip_id_token("google-token")
        
        assert result == "gcip-id-token"
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_exchange_google_id_token_network_error(self, mock_post):
        """Test Google ID token exchange with network error."""
        config = self.create_test_config()
        auth = IProovPortalAuth(config=config)
        
        mock_post.side_effect = Exception("Network error")
        
        with pytest.raises(NetworkError, match="Request failed"):
            auth._exchange_google_id_token_for_gcip_id_token("google-token")
    
    @patch('requests.post')
    def test_exchange_google_id_token_timeout(self, mock_post):
        """Test Google ID token exchange with timeout."""
        config = self.create_test_config()
        auth = IProovPortalAuth(config=config)
        
        from requests import Timeout
        mock_post.side_effect = Timeout("Request timed out")
        
        with pytest.raises(NetworkError, match="Request timed out"):
            auth._exchange_google_id_token_for_gcip_id_token("google-token")
    
    @patch('requests.post')
    def test_exchange_google_id_token_http_error(self, mock_post):
        """Test Google ID token exchange with HTTP error."""
        config = self.create_test_config()
        auth = IProovPortalAuth(config=config)
        
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad request"
        mock_post.return_value = mock_response
        
        with pytest.raises(AuthenticationError, match="Failed to exchange token"):
            auth._exchange_google_id_token_for_gcip_id_token("google-token")
    
    @patch('requests.post')
    def test_exchange_google_id_token_json_error(self, mock_post):
        """Test Google ID token exchange with JSON decode error."""
        config = self.create_test_config()
        auth = IProovPortalAuth(config=config)
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_post.return_value = mock_response
        
        with pytest.raises(AuthenticationError, match="Failed to parse JSON response"):
            auth._exchange_google_id_token_for_gcip_id_token("google-token")
    
    @patch('requests.post')
    def test_exchange_id_token_for_session_cookie_success(self, mock_post):
        """Test successful ID token to session cookie exchange."""
        config = self.create_test_config()
        auth = IProovPortalAuth(config=config)
        
        # Mock successful response with session cookie
        mock_response = Mock()
        mock_response.status_code = 200
        mock_cookie = Mock()
        mock_cookie.name = "session_token"
        mock_cookie.value = "session-cookie-value"
        mock_response.cookies = [mock_cookie]
        mock_post.return_value = mock_response
        
        result = auth._exchange_id_token_for_session_cookie("id-token")
        
        assert result == "session-cookie-value"
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_exchange_id_token_for_session_cookie_no_cookie(self, mock_post):
        """Test ID token to session cookie exchange with no session cookie."""
        config = self.create_test_config()
        auth = IProovPortalAuth(config=config)
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.cookies = []  # No cookies
        mock_post.return_value = mock_response
        
        with pytest.raises(AuthenticationError, match="No session_token cookie found"):
            auth._exchange_id_token_for_session_cookie("id-token")
    
    @patch('requests.post')
    def test_exchange_id_token_for_session_cookie_http_error(self, mock_post):
        """Test ID token to session cookie exchange with HTTP error."""
        config = self.create_test_config()
        auth = IProovPortalAuth(config=config)
        
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad request"
        mock_post.return_value = mock_response
        
        with pytest.raises(AuthenticationError, match="Failed to get session cookie"):
            auth._exchange_id_token_for_session_cookie("id-token")
    
    @patch('iproov_portal_auth.auth.id_token')
    def test_login_success_with_cache(self, mock_id_token):
        """Test successful login using cached token."""
        config = self.create_test_config()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('iproov_portal_auth.auth.TokenCache') as mock_cache_class:
                mock_cache = Mock()
                mock_cache.get_token.return_value = "cached-token"
                mock_cache_class.return_value = mock_cache
                
                auth = IProovPortalAuth(config=config)
                result = auth.login()
                
                assert result == "cached-token"
                mock_cache.get_token.assert_called_once_with("test-client-id", "uat")
    
    @patch('iproov_portal_auth.auth.id_token')
    def test_login_success_fresh_token(self, mock_id_token):
        """Test successful login with fresh token."""
        config = self.create_test_config()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('iproov_portal_auth.auth.TokenCache') as mock_cache_class:
                mock_cache = Mock()
                mock_cache.get_token.return_value = None  # No cached token
                mock_cache_class.return_value = mock_cache
                
                # Mock Google ID token fetch
                mock_id_token.fetch_id_token.return_value = "google-token"
                
                auth = IProovPortalAuth(config=config)
                
                # Mock the exchange methods
                auth._exchange_google_id_token_for_gcip_id_token = Mock(return_value="gcip-token")
                auth._exchange_id_token_for_session_cookie = Mock(return_value="session-token")
                
                result = auth.login()
                
                assert result == "session-token"
                mock_cache.save_token.assert_called_once_with("test-client-id", "uat", "session-token")
    
    @patch('iproov_portal_auth.auth.id_token')
    def test_login_force_refresh(self, mock_id_token):
        """Test login with force refresh."""
        config = self.create_test_config()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('iproov_portal_auth.auth.TokenCache') as mock_cache_class:
                mock_cache = Mock()
                mock_cache.get_token.return_value = "cached-token"
                mock_cache_class.return_value = mock_cache
                
                mock_id_token.fetch_id_token.return_value = "google-token"
                
                auth = IProovPortalAuth(config=config)
                auth._exchange_google_id_token_for_gcip_id_token = Mock(return_value="gcip-token")
                auth._exchange_id_token_for_session_cookie = Mock(return_value="fresh-token")
                
                result = auth.login(force_refresh=True)
                
                assert result == "fresh-token"
                # Should not call get_token when force_refresh is True
                mock_cache.get_token.assert_not_called()
    
    @patch('http.client.HTTPSConnection')
    def test_fetch_user_data_success(self, mock_https_conn):
        """Test successful user data fetch."""
        config = self.create_test_config()
        auth = IProovPortalAuth(config=config)
        
        # Mock HTTP connection
        mock_conn = Mock()
        mock_response = Mock()
        mock_response.status = 200
        mock_response.read.return_value = json.dumps({
            "email": "test@example.com",
            "name": "Test User",
            "access_token": "sensitive",
            "refresh_token": "sensitive"
        }).encode()
        mock_conn.getresponse.return_value = mock_response
        mock_https_conn.return_value = mock_conn
        
        result = auth._fetch_user_data("test-token")
        
        assert result["email"] == "test@example.com"
        assert result["name"] == "Test User"
        assert "access_token" not in result
        assert "refresh_token" not in result
    
    @patch('http.client.HTTPSConnection')
    def test_fetch_user_data_token_expired(self, mock_https_conn):
        """Test user data fetch with expired token."""
        config = self.create_test_config()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('iproov_portal_auth.auth.TokenCache') as mock_cache_class:
                mock_cache = Mock()
                mock_cache_class.return_value = mock_cache
                
                auth = IProovPortalAuth(config=config)
                
                # Mock HTTP connection
                mock_conn = Mock()
                mock_response = Mock()
                mock_response.status = 401
                mock_response.read.return_value = b"Unauthorized"
                mock_conn.getresponse.return_value = mock_response
                mock_https_conn.return_value = mock_conn
                
                with pytest.raises(TokenExpiredError, match="Token has expired"):
                    auth._fetch_user_data("expired-token")
                
                # Should clear cache when token expires
                mock_cache.clear_token.assert_called_once()
    
    @patch('http.client.HTTPSConnection')
    def test_fetch_user_data_network_error(self, mock_https_conn):
        """Test user data fetch with network error."""
        config = self.create_test_config()
        auth = IProovPortalAuth(config=config)
        
        mock_https_conn.side_effect = Exception("Connection failed")
        
        with pytest.raises(NetworkError, match="HTTP connection error"):
            auth._fetch_user_data("test-token")
    
    def test_get_user_details_cached(self):
        """Test getting user details from cache."""
        config = self.create_test_config()
        auth = IProovPortalAuth(config=config)
        
        cached_data = {"email": "test@example.com", "name": "Test User"}
        auth._cached_user_data = cached_data
        
        result = auth.get_user_details()
        assert result == cached_data
    
    def test_get_user_details_fresh(self):
        """Test getting fresh user details."""
        config = self.create_test_config()
        auth = IProovPortalAuth(config=config)
        
        user_data = {"email": "test@example.com", "name": "Test User"}
        auth._fetch_user_data = Mock(return_value=user_data)
        
        result = auth.get_user_details()
        assert result == user_data
        assert auth._cached_user_data == user_data
    
    def test_get_user_details_token_expired_retry(self):
        """Test getting user details with token expired retry."""
        config = self.create_test_config()
        auth = IProovPortalAuth(config=config)
        
        user_data = {"email": "test@example.com", "name": "Test User"}
        
        # First call raises TokenExpiredError, second succeeds
        auth._fetch_user_data = Mock(side_effect=[TokenExpiredError("Token expired"), user_data])
        auth.login = Mock(return_value="fresh-token")
        
        result = auth.get_user_details()
        assert result == user_data
        auth.login.assert_called_once_with(force_refresh=True)
    
    def test_get_email(self):
        """Test getting user email."""
        config = self.create_test_config()
        auth = IProovPortalAuth(config=config)
        
        auth.get_user_details = Mock(return_value={"email": "test@example.com"})
        
        result = auth.get_email()
        assert result == "test@example.com"
    
    def test_get_name(self):
        """Test getting user name."""
        config = self.create_test_config()
        auth = IProovPortalAuth(config=config)
        
        auth.get_user_details = Mock(return_value={"displayName": "Test User"})
        
        result = auth.get_name()
        assert result == "Test User"
    
    def test_get_name_fallback(self):
        """Test getting user name with fallback."""
        config = self.create_test_config()
        auth = IProovPortalAuth(config=config)
        
        auth.get_user_details = Mock(return_value={"name": "Test User"})
        
        result = auth.get_name()
        assert result == "Test User"
    
    def test_get_picture(self):
        """Test getting user picture."""
        config = self.create_test_config()
        auth = IProovPortalAuth(config=config)
        
        auth.get_user_details = Mock(return_value={"photoUrl": "https://example.com/photo.jpg"})
        
        result = auth.get_picture()
        assert result == "https://example.com/photo.jpg"
    
    def test_get_picture_fallback(self):
        """Test getting user picture with fallback."""
        config = self.create_test_config()
        auth = IProovPortalAuth(config=config)
        
        auth.get_user_details = Mock(return_value={"picture": "https://example.com/photo.jpg"})
        
        result = auth.get_picture()
        assert result == "https://example.com/photo.jpg"
    
    def test_get_roles(self):
        """Test getting user roles."""
        config = self.create_test_config()
        auth = IProovPortalAuth(config=config)
        
        auth.get_user_details = Mock(return_value={"roles": ["admin", "user"]})
        
        result = auth.get_roles()
        assert result == ["admin", "user"]
    
    def test_get_roles_custom_claims(self):
        """Test getting user roles from custom claims."""
        config = self.create_test_config()
        auth = IProovPortalAuth(config=config)
        
        auth.get_user_details = Mock(return_value={
            "customClaims": {"roles": ["admin", "user"]}
        })
        
        result = auth.get_roles()
        assert result == ["admin", "user"]
    
    def test_get_roles_fallback(self):
        """Test getting user roles with fallback."""
        config = self.create_test_config()
        auth = IProovPortalAuth(config=config)
        
        auth.get_user_details = Mock(return_value={
            "custom_claims": {"roles": ["admin", "user"]}
        })
        
        result = auth.get_roles()
        assert result == ["admin", "user"]
    
    def test_get_roles_empty(self):
        """Test getting user roles when none exist."""
        config = self.create_test_config()
        auth = IProovPortalAuth(config=config)
        
        auth.get_user_details = Mock(return_value={})
        
        result = auth.get_roles()
        assert result == []
    
    def test_get_access_token_not_supported(self):
        """Test that get_access_token raises NotImplementedError."""
        config = self.create_test_config()
        auth = IProovPortalAuth(config=config)
        
        with pytest.raises(NotImplementedError):
            auth.get_access_token()
    
    def test_get_refresh_token_not_supported(self):
        """Test that get_refresh_token raises NotImplementedError."""
        config = self.create_test_config()
        auth = IProovPortalAuth(config=config)
        
        with pytest.raises(NotImplementedError):
            auth.get_refresh_token()
    
    def test_logout(self):
        """Test logout functionality."""
        config = self.create_test_config()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('iproov_portal_auth.auth.TokenCache') as mock_cache_class:
                mock_cache = Mock()
                mock_cache_class.return_value = mock_cache
                
                auth = IProovPortalAuth(config=config)
                auth._cached_user_data = {"email": "test@example.com"}
                
                auth.logout()
                
                mock_cache.clear_token.assert_called_once_with("test-client-id", "uat")
                assert auth._cached_user_data is None
    
    def test_is_authenticated_true(self):
        """Test is_authenticated returns True when authenticated."""
        config = self.create_test_config()
        auth = IProovPortalAuth(config=config)
        
        auth.get_user_details = Mock(return_value={"email": "test@example.com"})
        
        assert auth.is_authenticated() is True
    
    def test_is_authenticated_false(self):
        """Test is_authenticated returns False when not authenticated."""
        config = self.create_test_config()
        auth = IProovPortalAuth(config=config)
        
        auth.get_user_details = Mock(side_effect=AuthenticationError("Not authenticated"))
        
        assert auth.is_authenticated() is False 