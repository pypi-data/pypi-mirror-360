"""Tests for token cache module."""

import os
import json
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from iproov_portal_auth.token_cache import TokenCache


class TestTokenCache:
    """Test TokenCache class."""
    
    def test_init_default_cache_dir(self):
        """Test initialization with default cache directory."""
        with patch('os.path.expanduser') as mock_expanduser, \
             patch('pathlib.Path.mkdir') as mock_mkdir:
            mock_expanduser.return_value = '/home/user'
            cache = TokenCache()
            expected_dir = Path('/home/user/.iproov_portal_auth')
            assert cache.cache_dir == expected_dir
            mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
    
    def test_init_custom_cache_dir(self):
        """Test initialization with custom cache directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = TokenCache(cache_dir=temp_dir)
            assert cache.cache_dir == Path(temp_dir)
    
    def test_get_cache_key(self):
        """Test cache key generation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = TokenCache(cache_dir=temp_dir)
            key = cache._get_cache_key("client-id", "prod")
            assert key == "client-id_prod"
    
    def test_load_cache_no_file(self):
        """Test loading cache when file doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = TokenCache(cache_dir=temp_dir)
            cache_data = cache._load_cache()
            assert cache_data == {}
    
    def test_load_cache_valid_file(self):
        """Test loading cache from valid file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = TokenCache(cache_dir=temp_dir)
            
            # Create a valid cache file
            test_data = {"test_key": {"token": "test_token"}}
            with open(cache.cache_file, 'w') as f:
                json.dump(test_data, f)
            
            cache_data = cache._load_cache()
            assert cache_data == test_data
    
    def test_load_cache_invalid_json(self):
        """Test loading cache from invalid JSON file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = TokenCache(cache_dir=temp_dir)
            
            # Create an invalid JSON file
            with open(cache.cache_file, 'w') as f:
                f.write("invalid json")
            
            cache_data = cache._load_cache()
            assert cache_data == {}
    
    def test_save_cache(self):
        """Test saving cache to file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = TokenCache(cache_dir=temp_dir)
            
            test_data = {"test_key": {"token": "test_token"}}
            cache._save_cache(test_data)
            
            # Verify file was created and contains correct data
            assert cache.cache_file.exists()
            with open(cache.cache_file, 'r') as f:
                saved_data = json.load(f)
            assert saved_data == test_data
    
    def test_save_cache_io_error(self):
        """Test saving cache when IO error occurs."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = TokenCache(cache_dir=temp_dir)
            
            # Make cache file read-only to cause IO error
            cache.cache_file.touch()
            cache.cache_file.chmod(0o444)
            
            test_data = {"test_key": {"token": "test_token"}}
            # Should not raise exception
            cache._save_cache(test_data)
    
    def test_is_token_expired_no_expires_at(self):
        """Test token expiry check with missing expires_at."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = TokenCache(cache_dir=temp_dir)
            
            cached_token = {"token": "test_token"}
            assert cache._is_token_expired(cached_token) is True
    
    def test_is_token_expired_not_expired(self):
        """Test token expiry check with valid token."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = TokenCache(cache_dir=temp_dir)
            
            # Token expires well after next Sunday midnight (2 weeks from now)
            future_timestamp = time.time() + (14 * 24 * 3600)  # 2 weeks from now
            cached_token = {"token": "test_token", "expires_at": future_timestamp}
            assert cache._is_token_expired(cached_token) is False
    
    def test_is_token_expired_expired(self):
        """Test token expiry check with expired token."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = TokenCache(cache_dir=temp_dir)
            
            # Token expired in the past
            past_timestamp = time.time() - 86400  # 24 hours ago
            cached_token = {"token": "test_token", "expires_at": past_timestamp}
            assert cache._is_token_expired(cached_token) is True
    
    def test_get_token_not_found(self):
        """Test getting token when it doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = TokenCache(cache_dir=temp_dir)
            
            token = cache.get_token("client-id", "prod")
            assert token is None
    
    def test_get_token_expired(self):
        """Test getting token when it's expired."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = TokenCache(cache_dir=temp_dir)
            
            # Create expired token
            past_timestamp = time.time() - 86400
            cache_data = {
                "client-id_prod": {
                    "token": "test_token",
                    "expires_at": past_timestamp
                }
            }
            cache._save_cache(cache_data)
            
            token = cache.get_token("client-id", "prod")
            assert token is None
            
            # Verify expired token was removed
            remaining_data = cache._load_cache()
            assert "client-id_prod" not in remaining_data
    
    def test_get_token_valid(self):
        """Test getting valid token."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = TokenCache(cache_dir=temp_dir)
            
            # Create valid token that expires well after next Sunday midnight
            future_timestamp = time.time() + (14 * 24 * 3600)  # 2 weeks from now
            cache_data = {
                "client-id_prod": {
                    "token": "test_token",
                    "expires_at": future_timestamp
                }
            }
            cache._save_cache(cache_data)
            
            token = cache.get_token("client-id", "prod")
            assert token == "test_token"
    
    def test_save_token(self):
        """Test saving token to cache."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = TokenCache(cache_dir=temp_dir)
            
            with patch('time.time') as mock_time:
                mock_time.return_value = 1234567890.0
                
                cache.save_token("client-id", "prod", "test_token")
                
                cache_data = cache._load_cache()
                assert "client-id_prod" in cache_data
                
                saved_token = cache_data["client-id_prod"]
                assert saved_token["token"] == "test_token"
                assert saved_token["created_at"] == 1234567890.0
                assert "expires_at" in saved_token
    
    def test_clear_token(self):
        """Test clearing specific token."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = TokenCache(cache_dir=temp_dir)
            
            # Create multiple tokens
            cache_data = {
                "client-id_prod": {"token": "token1"},
                "client-id_uat": {"token": "token2"}
            }
            cache._save_cache(cache_data)
            
            # Clear one token
            cache.clear_token("client-id", "prod")
            
            # Verify only one token was removed
            remaining_data = cache._load_cache()
            assert "client-id_prod" not in remaining_data
            assert "client-id_uat" in remaining_data
    
    def test_clear_token_not_found(self):
        """Test clearing token that doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = TokenCache(cache_dir=temp_dir)
            
            # Should not raise exception
            cache.clear_token("client-id", "prod")
    
    def test_clear_all(self):
        """Test clearing all tokens."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = TokenCache(cache_dir=temp_dir)
            
            # Create cache file
            cache_data = {"client-id_prod": {"token": "token1"}}
            cache._save_cache(cache_data)
            
            # Clear all tokens
            cache.clear_all()
            
            # Verify cache file was deleted
            assert not cache.cache_file.exists()
    
    def test_clear_all_no_file(self):
        """Test clearing all tokens when file doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = TokenCache(cache_dir=temp_dir)
            
            # Should not raise exception
            cache.clear_all()
    
    def test_get_token_info_not_found(self):
        """Test getting token info when token doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = TokenCache(cache_dir=temp_dir)
            
            info = cache.get_token_info("client-id", "prod")
            assert info is None
    
    def test_get_token_info_valid(self):
        """Test getting token info for valid token."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = TokenCache(cache_dir=temp_dir)
            
            created_at = 1234567890.0
            expires_at = 1234567890.0 + 86400
            
            cache_data = {
                "client-id_prod": {
                    "token": "test_token",
                    "created_at": created_at,
                    "expires_at": expires_at
                }
            }
            cache._save_cache(cache_data)
            
            info = cache.get_token_info("client-id", "prod")
            assert info is not None
            assert info["created_at"] == datetime.fromtimestamp(created_at)
            assert info["expires_at"] == datetime.fromtimestamp(expires_at)
            assert info["token_available"] is True
            assert "is_expired" in info
    
    def test_sunday_expiry_calculation(self):
        """Test that tokens expire on Sunday midnight."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = TokenCache(cache_dir=temp_dir)
            
            # Mock datetime to a Wednesday
            with patch('iproov_portal_auth.token_cache.datetime') as mock_datetime:
                # Wednesday, June 7, 2023, 10:00 AM
                mock_now = datetime(2023, 6, 7, 10, 0, 0)
                mock_datetime.now.return_value = mock_now
                
                cache.save_token("client-id", "prod", "test_token")
                
                cache_data = cache._load_cache()
                saved_token = cache_data["client-id_prod"]
                
                # Should expire on next Sunday (June 11, 2023) at midnight
                expected_expiry = datetime(2023, 6, 11, 0, 0, 0)
                actual_expiry = datetime.fromtimestamp(saved_token["expires_at"])
                
                assert actual_expiry == expected_expiry 