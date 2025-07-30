"""
Core functionality for the Lightswitch SDK.
"""
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get base URL from environment variable with fallback
LS_SDK_BE_URL = os.getenv("LS_SDK_BE_URL", "https://https://api.getlightswitch.com/")
# Ensure URL ends with a slash
if not LS_SDK_BE_URL.endswith("/"):
    LS_SDK_BE_URL += "/"

# Global configuration variables
_app_slug: Optional[str] = None
_secret_key: Optional[str] = None
_initialized: bool = False


def initialize_lightswitch(app_slug: str, secret_key: Optional[str] = None) -> None:
    """
    Initialize the Lightswitch SDK with app slug and secret key.
    
    Args:
        app_slug (str): The app slug for your application
        secret_key (str, optional): The secret API key. If not provided, 
                                   will try to read from LIGHTSWITCH_API_KEY environment variable
    
    Raises:
        ValueError: If secret_key is not provided and LIGHTSWITCH_API_KEY env var is not set
    """
    global _app_slug, _secret_key, _initialized
    
    _app_slug = app_slug
    
    if secret_key:
        _secret_key = secret_key
    else:
        _secret_key = os.getenv("LIGHTSWITCH_API_KEY")
        if not _secret_key:
            raise ValueError(
                "Secret key must be provided either as parameter or via LIGHTSWITCH_API_KEY environment variable"
            )
    
    _initialized = True
    print(f"Lightswitch SDK initialized for app: {app_slug}")


def get_auth_headers() -> Dict[str, str]:
    """
    Get the authentication headers for API requests.
    
    Returns:
        Dict[str, str]: Headers including X-App-Slug and X-Secret-Key
        
    Raises:
        RuntimeError: If SDK is not initialized
    """
    if not _initialized:
        raise RuntimeError(
            "Lightswitch SDK not initialized. Call lightswitch_sdk.initialize(app_slug, secret_key) first."
        )
    
    return {
        "X-App-Slug": _app_slug,
        "X-Secret-Key": _secret_key,
        "Content-Type": "application/json"
    }


def is_initialized() -> bool:
    """
    Check if the SDK has been initialized.
    
    Returns:
        bool: True if initialized, False otherwise
    """
    return _initialized


def get_config() -> Dict[str, Any]:
    """
    Get the current SDK configuration.
    
    Returns:
        Dict[str, Any]: Current configuration including app_slug and initialization status
    """
    return {
        "initialized": _initialized,
        "app_slug": _app_slug,
        "base_url": LS_SDK_BE_URL,
        "has_secret_key": _secret_key is not None
    }


def get_base_url() -> str:
    """
    Get the base URL for API requests.
    
    Returns:
        str: The base URL
    """
    return LS_SDK_BE_URL 