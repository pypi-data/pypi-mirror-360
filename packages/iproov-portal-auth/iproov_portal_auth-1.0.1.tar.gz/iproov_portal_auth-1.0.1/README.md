# iProov Portal Authentication Library

A Python library for authenticating with iProov Portal services using Google OAuth2.

## Features

- **Multi-environment support**: Production, UAT, and Development environments
- **Token caching**: Automatic local caching with smart expiration handling
- **Automatic token refresh**: Handles token expiration and renewal
- **Comprehensive error handling**: Detailed error messages for debugging
- **Type hints**: Full type annotation support
- **Secure by default**: Removes sensitive tokens from responses

## Installation

```bash
pip install iproov-portal-auth
```

## Quick Start

### Basic Usage

```python
import os
from iproov_portal_auth import IProovPortalAuth

# Make sure API key is set
os.environ['IPROOV_PORTAL_API_KEY'] = 'your-api-key'

# Initialize with default configuration
auth = IProovPortalAuth()

# Login and get session token
token = auth.login()
print(f"Session token: {token}")

# Get user details
user_details = auth.get_user_details()
print(f"User email: {user_details.get('email')}")
print(f"User name: {user_details.get('displayName')}")
```

### Custom Configuration

```python
from iproov_portal_auth import IProovPortalAuth, AuthConfig, Environment

# Create custom configuration
config = AuthConfig(
    client_id="your-client-id",
    api_key="your-api-key",
    environment=Environment.UAT,
    timeout=30.0
)

# Initialize with custom config
auth = IProovPortalAuth(config=config)
```

### Environment Variables

You can configure the library using environment variables:

```bash
export IPROOV_PORTAL_API_KEY="your-api-key"  # REQUIRED
export IPROOV_PORTAL_CLIENT_ID="your-client-id"  # Optional, uses environment defaults
export IPROOV_PORTAL_ENV="uat"  # prod, uat, or dev
export IPROOV_PORTAL_TIMEOUT="20.0"
```

**Note**: The `IPROOV_PORTAL_API_KEY` is required. The `IPROOV_PORTAL_CLIENT_ID` is optional and will use environment-specific defaults if not provided.

## API Reference

### IProovPortalAuth Class

#### Methods

##### `login(force_refresh: bool = False) -> str`

Authenticate and get a session token.

**Parameters:**
- `force_refresh`: If True, forces a new token even if cached token exists

**Returns:**
- Session token string

**Raises:**
- `AuthenticationError`: If authentication fails
- `NetworkError`: If network request fails

##### `get_user_details(force_refresh: bool = False) -> Dict[str, Any]`

Get user details from the verify endpoint.

**Parameters:**
- `force_refresh`: If True, forces a fresh request even if data is cached

**Returns:**
- Dictionary containing user details

##### `get_email() -> Optional[str]`

Get user email address.

**Returns:**
- User email address or None if not available

##### `get_name() -> Optional[str]`

Get user display name.

**Returns:**
- User display name or None if not available

##### `get_picture() -> Optional[str]`

Get user profile picture URL.

**Returns:**
- User profile picture URL or None if not available

##### `get_roles() -> List[str]`

Get user roles.

**Returns:**
- List of user roles

##### `logout() -> None`

Logout and clear cached tokens.

##### `is_authenticated() -> bool`

Check if user is authenticated.

**Returns:**
- True if user has valid authentication, False otherwise

### Configuration

#### AuthConfig Class

```python
@dataclass
class AuthConfig:
    api_key: str
    client_id: Optional[str] = None  # Uses environment-specific default if not provided
    environment: Environment = Environment.PRODUCTION
    timeout: float = 20.0
```

**Note:** When `client_id` is not provided, the library automatically uses environment-specific default client IDs:
- **Production**: `105336304952-n6ddad4ea9lc2hrc70791ibq6pfdfemc.apps.googleusercontent.com`
- **UAT**: `973312410545-63o5poolj5kocnu0lceocvagajak4sgf.apps.googleusercontent.com`
- **Development**: `568086550639-lq968h5moe814cf0o45oftn1p0ck0tgn.apps.googleusercontent.com`

#### Environment Enum

```python
class Environment(Enum):
    PRODUCTION = "prod"
    UAT = "uat"
    DEVELOPMENT = "dev"
```

### Exception Hierarchy

```
IProovPortalAuthError
├── AuthenticationError
├── TokenExpiredError
├── NetworkError
└── ConfigurationError
```

## Usage Examples

### Basic Authentication Flow

```python
from iproov_portal_auth import IProovPortalAuth

# Initialize
auth = IProovPortalAuth()

try:
    # Login
    token = auth.login()
    print(f"Successfully authenticated with token: {token[:20]}...")
    
    # Get user information
    email = auth.get_email()
    name = auth.get_name()
    roles = auth.get_roles()
    
    print(f"User: {name} <{email}>")
    print(f"Roles: {', '.join(roles)}")
    
except Exception as e:
    print(f"Authentication failed: {e}")
```

### Environment-Specific Configuration

```python
from iproov_portal_auth import IProovPortalAuth, AuthConfig, Environment

# UAT environment with automatic client_id (recommended)
uat_config = AuthConfig(
    api_key="your-api-key",
    environment=Environment.UAT
)

auth = IProovPortalAuth(config=uat_config)

# Alternatively, you can specify a custom client_id
custom_config = AuthConfig(
    api_key="your-api-key",
    client_id="your-custom-client-id",
    environment=Environment.UAT
)

auth_custom = IProovPortalAuth(config=custom_config)
```

### Error Handling

```python
from iproov_portal_auth import IProovPortalAuth
from iproov_portal_auth.exceptions import (
    AuthenticationError,
    TokenExpiredError,
    NetworkError,
    ConfigurationError
)

auth = IProovPortalAuth()

try:
    user_details = auth.get_user_details()
    print(f"User authenticated: {user_details['email']}")
    
except TokenExpiredError:
    print("Token has expired, attempting to refresh...")
    try:
        # Force refresh and try again
        user_details = auth.get_user_details(force_refresh=True)
        print(f"Successfully refreshed: {user_details['email']}")
    except Exception as e:
        print(f"Refresh failed: {e}")
        
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
    
except NetworkError as e:
    print(f"Network error: {e}")
    
except ConfigurationError as e:
    print(f"Configuration error: {e}")
```

### Token Caching

The library automatically caches tokens locally to avoid unnecessary authentication requests:

```python
from iproov_portal_auth import IProovPortalAuth

auth = IProovPortalAuth()

# First call performs authentication
token1 = auth.login()
print("First login completed")

# Second call uses cached token
token2 = auth.login()
print("Second login used cached token")

# Tokens are the same
assert token1 == token2

# Force refresh to get new token
token3 = auth.login(force_refresh=True)
print("Third login forced refresh")
```

### Custom Token Cache Directory

```python
from iproov_portal_auth import IProovPortalAuth
from iproov_portal_auth.token_cache import TokenCache

# Custom cache directory
cache = TokenCache(cache_dir="/custom/cache/path")

# Note: Currently, you cannot pass custom cache to IProovPortalAuth
# This is for advanced use cases where you need to manage the cache manually
```

## Token Expiration

Tokens typically expire on Sunday midnight each week. The library automatically handles this by:

1. **Checking expiration** before returning cached tokens
2. **Automatic cleanup** of expired tokens
3. **Retry logic** when API returns 401 (Unauthorized)

## Development

### Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=iproov_portal_auth
```

### Code Quality

```bash
# Format code
black iproov_portal_auth/

# Lint code
flake8 iproov_portal_auth/

# Type checking
mypy iproov_portal_auth/
```

## Security Considerations

- **No sensitive data in responses**: Access tokens and refresh tokens are automatically removed from API responses
- **Local token storage**: Tokens are stored in `~/.iproov_portal_auth/` directory with appropriate permissions
- **SSL verification**: All HTTPS connections use proper SSL verification (except where explicitly disabled for testing)

## Environment URLs

| Environment | Login URL | Client ID |
|-------------|-----------|-----------|
| Production | `https://login.secure.iproov.me` | `105336304952-n6ddad4ea9lc2hrc70791ibq6pfdfemc.apps.googleusercontent.com` |
| UAT | `https://login.uat.secure.iproov.me` | `973312410545-63o5poolj5kocnu0lceocvagajak4sgf.apps.googleusercontent.com` |
| Development | `https://login.dev.secure.iproov.me` | `568086550639-lq968h5moe814cf0o45oftn1p0ck0tgn.apps.googleusercontent.com` |

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## Support

For issues and questions, please create an issue in the GitHub repository. 