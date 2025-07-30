"""Main authentication class for iProov Portal Authentication."""

import json
import http.client
import ssl
from typing import Optional, Dict, Any, cast

import requests
from google.auth.transport.requests import Request
from google.oauth2 import id_token
from requests import Timeout

from .config import AuthConfig, get_default_config
from .token_cache import TokenCache
from .exceptions import (
    AuthenticationError,
    TokenExpiredError,
    NetworkError,
    ConfigurationError,
)


class IProovPortalAuth:
    """Main authentication class for iProov Portal services."""
    
    def __init__(self, config: Optional[AuthConfig] = None):
        """Initialize authentication client.
        
        Args:
            config: Authentication configuration. If None, uses default config.
        """
        self.config = config or get_default_config()
        self.config.validate()
        
        self.token_cache = TokenCache()
        self._cached_user_data: Optional[Dict[str, Any]] = None
    
    def _exchange_google_id_token_for_gcip_id_token(self, google_open_id_connect_token: str) -> str:
        """Exchange Google ID token for GCIP ID token.
        
        Args:
            google_open_id_connect_token: Google OpenID Connect token
            
        Returns:
            GCIP ID token
            
        Raises:
            AuthenticationError: If token exchange fails
            NetworkError: If network request fails
        """
        url = f"{self.config.sign_in_with_idp_api}?key={self.config.api_key}"
        data = {
            "requestUri": self.config.request_uri,
            "returnSecureToken": True,
            "postBody": f"id_token={google_open_id_connect_token}&providerId=google.com",
        }
        
        try:
            response = requests.post(url=url, data=data, timeout=self.config.timeout)
        except Timeout as e:
            raise NetworkError(f"Request timed out after {self.config.timeout} seconds: {e}")
        except Exception as e:
            raise NetworkError(f"Request failed: {e}")
        
        if response.status_code == 200:
            try:
                token = response.json().get("idToken", "")
                return cast(str, token)
            except json.JSONDecodeError as e:
                raise AuthenticationError(f"Failed to parse JSON response: {e}")
        else:
            raise AuthenticationError(
                f"Failed to exchange token: {response.status_code} {response.text}"
            )
    
    def _exchange_id_token_for_session_cookie(self, id_token: str) -> str:
        """Exchange Firebase ID token for session cookie.
        
        Args:
            id_token: Firebase ID token
            
        Returns:
            Session cookie value
            
        Raises:
            AuthenticationError: If token exchange fails
            NetworkError: If network request fails
        """
        url = f"{self.config.base_url}/api/secure-token"
        data = {"idToken": id_token}
        headers = {"Content-Type": "application/json"}
        
        try:
            response = requests.post(
                url=url, 
                json=data, 
                headers=headers, 
                timeout=self.config.timeout
            )
        except Timeout as e:
            raise NetworkError(f"Request timed out after {self.config.timeout} seconds: {e}")
        except Exception as e:
            raise NetworkError(f"Request failed: {e}")
        
        if response.status_code == 200:
            try:
                # Extract session cookie from the response cookies
                for cookie in response.cookies:
                    if cookie.name == "session_token":
                        if cookie.value is None:
                            raise AuthenticationError("Session token cookie has no value")
                        return cookie.value
                
                raise AuthenticationError("No session_token cookie found in response")
            except Exception as e:
                raise AuthenticationError(f"Error processing response: {e}")
        else:
            raise AuthenticationError(
                f"Failed to get session cookie: {response.status_code} {response.text}"
            )
    
    def login(self, force_refresh: bool = False) -> str:
        """Login and get session token.
        
        Args:
            force_refresh: If True, forces a new token even if cached token exists
            
        Returns:
            Session token
            
        Raises:
            AuthenticationError: If authentication fails
            NetworkError: If network request fails
        """
        # Check for cached token first
        if not force_refresh:
            # client_id is guaranteed to be non-None after __post_init__
            assert self.config.client_id is not None
            cached_token = self.token_cache.get_token(
                self.config.client_id, 
                self.config.environment.value
            )
            if cached_token:
                return cached_token
        
        try:
            # Get Google OpenID Connect token
            # client_id is guaranteed to be non-None after __post_init__
            assert self.config.client_id is not None
            open_id_connect_token = id_token.fetch_id_token(
                request=Request(), 
                audience=self.config.client_id
            )
            
            # Exchange for GCIP ID token
            gcip_id_token = self._exchange_google_id_token_for_gcip_id_token(
                open_id_connect_token
            )
            
            # Exchange for session cookie
            session_token = self._exchange_id_token_for_session_cookie(gcip_id_token)
            
            # Cache the token
            # client_id is guaranteed to be non-None after __post_init__
            assert self.config.client_id is not None
            self.token_cache.save_token(
                self.config.client_id, 
                self.config.environment.value, 
                session_token
            )
            
            # Clear cached user data since we have a new token
            self._cached_user_data = None
            
            return session_token
            
        except Exception as e:
            if isinstance(e, (AuthenticationError, NetworkError)):
                raise
            raise AuthenticationError(f"Authentication failed: {e}")
    
    def _fetch_user_data(self, token: Optional[str] = None) -> Dict[str, Any]:
        """Fetch user data from verify endpoint.
        
        Args:
            token: Session token. If None, uses cached token or performs login.
            
        Returns:
            User data dictionary
            
        Raises:
            AuthenticationError: If authentication fails
            TokenExpiredError: If token is expired
            NetworkError: If network request fails
        """
        if token is None:
            token = self.login()
        
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            conn = http.client.HTTPSConnection(
                host=self.config.base_url.replace("https://", ""),
                context=ssl._create_unverified_context(),
                timeout=self.config.timeout,
            )
            conn.request(method="GET", url="/api/verify.json", headers=headers)
            response = conn.getresponse()
        except Exception as e:
            raise NetworkError(f"HTTP connection error: {e}")
        
        status = response.status
        
        try:
            raw_response = response.read().decode("utf-8")
        except UnicodeDecodeError as e:
            raise NetworkError(f"Error decoding response: {e}")
        
        if status == 401:
            # Token expired, clear cache and raise appropriate error
            # client_id is guaranteed to be non-None after __post_init__
            assert self.config.client_id is not None
            self.token_cache.clear_token(self.config.client_id, self.config.environment.value)
            self._cached_user_data = None
            raise TokenExpiredError("Token has expired")
        
        if status != 200:
            raise AuthenticationError(f"API returned status {status}: {raw_response}")
        
        try:
            user_data = cast(Dict[str, Any], json.loads(raw_response))
            # Remove sensitive information
            user_data_clean = user_data.copy()
            for sensitive_key in ["access_token", "refresh_token"]:
                user_data_clean.pop(sensitive_key, None)
            return user_data_clean
        except json.JSONDecodeError:
            raise AuthenticationError(f"Error parsing JSON response: {raw_response}")
    
    def get_user_details(self, force_refresh: bool = False) -> Dict[str, Any]:
        """Get user details from the verify endpoint.
        
        Args:
            force_refresh: If True, forces a fresh request even if data is cached
            
        Returns:
            User details dictionary
            
        Raises:
            AuthenticationError: If authentication fails
            TokenExpiredError: If token is expired
            NetworkError: If network request fails
        """
        if not force_refresh and self._cached_user_data:
            return self._cached_user_data
        
        try:
            user_data = self._fetch_user_data()
            self._cached_user_data = user_data
            return user_data
        except TokenExpiredError:
            # Try once more with fresh token
            token = self.login(force_refresh=True)
            user_data = self._fetch_user_data(token)
            self._cached_user_data = user_data
            return user_data
    
    def get_email(self) -> Optional[str]:
        """Get user email address.
        
        Returns:
            User email address or None if not available
        """
        user_data = self.get_user_details()
        return user_data.get("email")
    
    def get_name(self) -> Optional[str]:
        """Get user display name.
        
        Returns:
            User display name or None if not available
        """
        user_data = self.get_user_details()
        return user_data.get("displayName") or user_data.get("name")
    
    def get_picture(self) -> Optional[str]:
        """Get user profile picture URL.
        
        Returns:
            User profile picture URL or None if not available
        """
        user_data = self.get_user_details()
        return user_data.get("photoUrl") or user_data.get("picture")
    
    def get_roles(self) -> list:
        """Get user roles.
        
        Returns:
            List of user roles
        """
        user_data = self.get_user_details()
        
        # Try different possible keys for roles
        roles = user_data.get("roles", [])
        if not roles:
            roles = user_data.get("customClaims", {}).get("roles", [])
        if not roles:
            roles = user_data.get("custom_claims", {}).get("roles", [])
        
        return roles if isinstance(roles, list) else []
    
    def get_access_token(self) -> str:
        """Get access token.
        
        Returns:
            Always raises NotImplementedError as this method is not supported
            
        Raises:
            NotImplementedError: This method is not supported
        """
        raise NotImplementedError("Access token retrieval is not supported")
    
    def get_refresh_token(self) -> str:
        """Get refresh token.
        
        Returns:
            Always raises NotImplementedError as this method is not supported
            
        Raises:
            NotImplementedError: This method is not supported
        """
        raise NotImplementedError("Refresh token retrieval is not supported")
    
    def logout(self) -> None:
        """Logout and clear cached tokens."""
        # client_id is guaranteed to be non-None after __post_init__
        assert self.config.client_id is not None
        self.token_cache.clear_token(self.config.client_id, self.config.environment.value)
        self._cached_user_data = None
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated.
        
        Returns:
            True if user has valid authentication, False otherwise
        """
        try:
            self.get_user_details()
            return True
        except (AuthenticationError, TokenExpiredError, NetworkError):
            return False 