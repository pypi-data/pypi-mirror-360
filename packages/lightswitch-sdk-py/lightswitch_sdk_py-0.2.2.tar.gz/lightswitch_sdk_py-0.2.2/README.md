# Lightswitch SDK for Python

A Python SDK for interacting with the Lightswitch backend services, providing authentication, authorization, and usage tracking capabilities.

## Features

- 🔐 **Authentication**: Validate JWT tokens and retrieve user information
- 🛡️ **Authorization**: Check user entitlements for specific features
- 📊 **Usage Tracking**: Log feature usage for analytics and billing
- ⚡ **FastAPI Integration**: Optional FastAPI dependencies for easy integration
- 🏗️ **Modular Design**: Use only what you need

## Installation

### Basic Installation
```bash
pip install lightswitch-sdk-py
```

### With FastAPI Support
```bash
pip install lightswitch-sdk-py[fastapi]
```

### Development Installation
```bash
pip install lightswitch-sdk-py[dev]
```

## Quick Start

### 1. Basic Usage (No FastAPI Required)

```python
import lightswitch_sdk_py as ls

# Initialize the SDK
ls.initialize_lightswitch("your-app-slug", "your-secret-key")

# Or use environment variables
# export LIGHTSWITCH_API_KEY="your-secret-key"
# ls.initialize_lightswitch("your-app-slug")

# Get current user from JWT token
user_data = ls.get_current_user(token)
print(f"User: {user_data}")

# Check if user is entitled to a feature
is_entitled = ls.check_entitlement(token, "premium_feature")
print(f"Entitled: {is_entitled}")

# Log feature usage
success = ls.log_usage(token, "premium_feature")
print(f"Usage logged: {success}")
```

### 2. FastAPI Integration

```python
from fastapi import FastAPI, Depends, Body
from typing import Dict, Any
from lightswitch_sdk_py.fastapi import (
    get_current_user_dependency, 
    require_entitlement_dependency,
    log_usage_dependency
)

app = FastAPI()

@app.get("/protected")
async def protected_route(
    user: Dict[str, Any] = Depends(get_current_user_dependency)
):
    """A protected route that requires authentication."""
    return {"message": f"Hello {user['name']}", "user": user}

@app.post("/premium-feature")
async def premium_feature(
    data: Dict[str, Any] = Body(...),
    user: Dict[str, Any] = Depends(get_current_user_dependency),
    # Check entitlement and log usage
    _entitlement: None = Depends(require_entitlement_dependency("premium_feature")),
    _usage: None = Depends(log_usage_dependency("premium_feature"))
):
    """A premium feature that requires entitlement and logs usage."""
    return {
        "message": "Premium feature accessed successfully",
        "user": user["name"],
        "data": data
    }
```

## API Reference

### Core Functions

#### `initialize_lightswitch(app_slug: str, secret_key: Optional[str] = None)`
Initialize the SDK with your app slug and secret key.

**Parameters:**
- `app_slug`: Your application slug from Lightswitch
- `secret_key`: Your secret API key (optional if `LIGHTSWITCH_API_KEY` env var is set)

#### `get_current_user(token: str) -> Optional[Dict[str, Any]]`
Retrieve current user information using a JWT token.

**Returns:**
```python
{
    "id": 0,
    "name": "string",
    "email": "user@example.com",
    "custom_fields": {}
}
```

#### `check_entitlement(token: str, feature: str) -> bool`
Check if a user is entitled to use a specific feature.

#### `log_usage(token: str, feature: str) -> bool`
Log the usage of a specific feature.

#### `is_initialized() -> bool`
Check if the SDK has been initialized.

#### `get_config() -> Dict[str, Any]`
Get the current SDK configuration.

### FastAPI Dependencies

#### `get_current_user_dependency`
FastAPI dependency that extracts and validates the user from the Authorization header.

#### `require_entitlement_dependency(feature: str)`
FastAPI dependency function that returns a dependency to check entitlement for a specific feature.

#### `log_usage_dependency(feature: str)`
FastAPI dependency function that returns a dependency to log usage for a specific feature.

## Configuration

### Environment Variables

- `LIGHTSWITCH_API_KEY`: Your secret API key
- `LS_SDK_BE_URL`: Base URL for the Lightswitch backend (default: `http://localhost:8001/`)

### Example `.env` file
```env
LIGHTSWITCH_API_KEY=your-secret-key-here
LS_SDK_BE_URL=https://api.lightswitch.com/
```

## Error Handling

The SDK handles errors gracefully:

- **Authentication errors**: Returns `None` for client functions, raises `HTTPException` for FastAPI dependencies
- **Network errors**: Logs errors and returns `False` for boolean functions
- **Initialization errors**: Raises `RuntimeError` if SDK is not initialized

## Examples

See `examples.py` for comprehensive usage examples including:
- Basic SDK usage
- FastAPI integration patterns
- Manual dependency setup

## Development

### Setup
```bash
git clone <repository-url>
cd lightswitch-sdk-py
pip install -e .[dev]
```

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black lightswitch_sdk_py/
flake8 lightswitch_sdk_py/
```

## Migration from v0.1.x

If you're upgrading from v0.1.x, update your imports and function calls:

```python
# Old (v0.1.x)
from lightswitch_sdk_py import get_current_user_dependency, security
import lightswitch_sdk_py as ls
ls.initialize("app-slug", "secret-key")

# New (v0.2.x)
from lightswitch_sdk_py.fastapi import get_current_user_dependency, require_entitlement_dependency
import lightswitch_sdk_py as ls
ls.initialize_lightswitch("app-slug", "secret-key")
```

Core client functions remain the same:
```python
# These work the same in both versions
user = ls.get_current_user(token)
entitled = ls.check_entitlement(token, "feature")
logged = ls.log_usage(token, "feature")
```

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
- GitHub Issues: [lightswitch-sdk-py/issues](https://github.com/lightswitch/lightswitch-sdk-py/issues)
- Documentation: [lightswitch-sdk-py](https://github.com/lightswitch/lightswitch-sdk-py)



## Publishing the SDK

### Clean previous builds
``rm -rf build/ dist/``

### Build new packages
``python setup.py sdist bdist_wheel``

### Test the package locally
``pip install dist/lightswitch_sdk_py-0.2.0-py3-none-any.whl``

### Publish to PyPI
``twine upload dist/*``

### Clean up after publishing (optional)
``rm -rf build/ dist/``