"""Token caching functionality for iProov Portal Authentication."""

import os
import json
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, cast
from pathlib import Path

from .exceptions import TokenExpiredError


class TokenCache:
    """Manages local token caching with expiration."""
    
    def __init__(self, cache_dir: Optional[str] = None):
        """Initialize token cache.
        
        Args:
            cache_dir: Directory to store cache files. Defaults to user's home directory.
        """
        if cache_dir is None:
            cache_dir = os.path.join(os.path.expanduser("~"), ".iproov_portal_auth")
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / "token_cache.json"
    
    def _get_cache_key(self, client_id: str, environment: str) -> str:
        """Generate cache key for given client and environment."""
        return f"{client_id}_{environment}"
    
    def _load_cache(self) -> Dict[str, Any]:
        """Load cache from file."""
        if not self.cache_file.exists():
            return {}
        
        try:
            with open(self.cache_file, 'r') as f:
                data = json.load(f)
                return cast(Dict[str, Any], data)
        except (json.JSONDecodeError, IOError):
            return {}
    
    def _save_cache(self, cache_data: Dict[str, Any]) -> None:
        """Save cache to file."""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
        except IOError:
            pass  # Silently fail if we can't write cache
    
    def _is_token_expired(self, cached_token: Dict[str, Any]) -> bool:
        """Check if token is expired."""
        if 'expires_at' not in cached_token:
            return True
        
        expires_at = cast(float, cached_token['expires_at'])
        
        # Check if token expires before next Sunday midnight
        # Tokens typically expire on Sunday midnight
        now = datetime.now()
        next_sunday = now + timedelta(days=(6 - now.weekday()))
        next_sunday_midnight = next_sunday.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Add some buffer (1 hour) to avoid edge cases
        expiry_threshold = next_sunday_midnight - timedelta(hours=1)
        
        return expires_at < expiry_threshold.timestamp()
    
    def get_token(self, client_id: str, environment: str) -> Optional[str]:
        """Get cached token if it exists and is valid.
        
        Args:
            client_id: OAuth client ID
            environment: Environment name
            
        Returns:
            Cached token if valid, None otherwise
        """
        cache_key = self._get_cache_key(client_id, environment)
        cache_data = self._load_cache()
        
        if cache_key not in cache_data:
            return None
        
        cached_token = cache_data[cache_key]
        
        if self._is_token_expired(cached_token):
            # Remove expired token from cache
            del cache_data[cache_key]
            self._save_cache(cache_data)
            return None
        
        return cast(Optional[str], cached_token.get('token'))
    
    def save_token(self, client_id: str, environment: str, token: str) -> None:
        """Save token to cache.
        
        Args:
            client_id: OAuth client ID
            environment: Environment name
            token: Token to cache
        """
        cache_key = self._get_cache_key(client_id, environment)
        cache_data = self._load_cache()
        
        # Calculate expiry time (next Sunday midnight)
        now = datetime.now()
        next_sunday = now + timedelta(days=(6 - now.weekday()))
        next_sunday_midnight = next_sunday.replace(hour=0, minute=0, second=0, microsecond=0)
        
        cache_data[cache_key] = {
            'token': token,
            'created_at': time.time(),
            'expires_at': next_sunday_midnight.timestamp(),
        }
        
        self._save_cache(cache_data)
    
    def clear_token(self, client_id: str, environment: str) -> None:
        """Clear cached token.
        
        Args:
            client_id: OAuth client ID
            environment: Environment name
        """
        cache_key = self._get_cache_key(client_id, environment)
        cache_data = self._load_cache()
        
        if cache_key in cache_data:
            del cache_data[cache_key]
            self._save_cache(cache_data)
    
    def clear_all(self) -> None:
        """Clear all cached tokens."""
        if self.cache_file.exists():
            self.cache_file.unlink()
    
    def get_token_info(self, client_id: str, environment: str) -> Optional[Dict[str, Any]]:
        """Get token information including expiry.
        
        Args:
            client_id: OAuth client ID
            environment: Environment name
            
        Returns:
            Token info dict with creation time, expiry time, etc.
        """
        cache_key = self._get_cache_key(client_id, environment)
        cache_data = self._load_cache()
        
        if cache_key not in cache_data:
            return None
        
        cached_token = cache_data[cache_key]
        
        return {
            'created_at': datetime.fromtimestamp(cached_token['created_at']),
            'expires_at': datetime.fromtimestamp(cached_token['expires_at']),
            'is_expired': self._is_token_expired(cached_token),
            'token_available': True,
        } 