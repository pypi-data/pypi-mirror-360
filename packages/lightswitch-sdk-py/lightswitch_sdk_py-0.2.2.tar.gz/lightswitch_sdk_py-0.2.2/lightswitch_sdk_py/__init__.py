"""
Lightswitch SDK for interacting with the Lightswitch backend services.

This SDK provides both core functionality and optional FastAPI integrations.

Basic usage:
    import lightswitch_sdk_py as ls
    
    # Initialize the SDK
    ls.initialize_lightswitch("your-app-slug", "your-secret-key")
    
    # Use core functions
    user_data = ls.get_current_user(token)
    is_entitled = ls.check_entitlement(token, "feature_name")
    ls.log_usage(token, "feature_name")

FastAPI usage:
    from lightswitch_sdk_py.fastapi import get_current_user_dependency, require_entitlement_dependency
    
    @app.get("/protected")
    async def protected_route(
        user: dict = Depends(get_current_user_dependency),
        _: None = Depends(require_entitlement_dependency("premium_feature"))
    ):
        return {"user": user}
"""

# Core functionality - always available
from .core import (
    initialize_lightswitch,
    is_initialized,
    get_config,
    get_base_url,
)

# Client functions - always available
from .client import (
    get_current_user,
    check_entitlement,
    log_usage,
)

# Version info
__version__ = "0.2.0"
__author__ = "Lightswitch Team"
__email__ = "sunny@getlightswitch.com"
__license__ = "MIT"

# Public API
__all__ = [
    # Core functions
    "initialize_lightswitch",
    "is_initialized", 
    "get_config",
    "get_base_url",
    
    # Client functions
    "get_current_user",
    "check_entitlement",
    "log_usage",
    
    # Version info
    "__version__",
    "__author__",
    "__email__",
    "__license__",
]


def greet():
    """
    A simple greeting function for testing.
    
    Returns:
        None: Prints 'Hello World' to the console
    """
    print("Hello World")


# Add greet to public API
__all__.append("greet") 