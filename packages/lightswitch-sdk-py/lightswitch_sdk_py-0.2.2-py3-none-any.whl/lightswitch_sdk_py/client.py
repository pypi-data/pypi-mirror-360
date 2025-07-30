"""
HTTP client functions for the Lightswitch SDK.
"""
import requests
from typing import Dict, Any, Optional

from .core import get_auth_headers, get_base_url


def get_current_user(token: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve current user information using a JWT token.
    
    Args:
        token (str): JWT token for authentication
        
    Returns:
        dict: User data containing id, name, email, and custom_fields
              or None if the request fails
        
    Example response:
    {
        "id": 0,
        "name": "string",
        "email": "user@example.com",
        "custom_fields": {}
    }
    """
    url = f"{get_base_url()}api/v1/sdk/server/me"
    
    # Get base auth headers and add Authorization
    headers = get_auth_headers()
    headers["Authorization"] = f"Bearer {token}"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise exception for non-200 status codes
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching user data: {e}")
        return None


def check_entitlement(token: str, feature: str) -> bool:
    """
    Check if a user is entitled to use a specific feature.
    
    Args:
        token (str): JWT token for authentication
        feature (str): The feature to check entitlement for
        
    Returns:
        bool: True if the user is entitled, False otherwise
    """
    url = f"{get_base_url()}api/v1/sdk/server/entitled"
    
    # Get base auth headers and add Authorization
    headers = get_auth_headers()
    headers["Authorization"] = f"Bearer {token}"
    
    payload = {"feature": feature}
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data.get("entitled", False)
    except requests.RequestException as e:
        print(f"Error checking entitlement: {e}")
        return False


def log_usage(token: str, feature: str) -> bool:
    """
    Log the usage of a specific feature.
    
    Args:
        token (str): JWT token for authentication
        feature (str): The feature being used
        
    Returns:
        bool: True if the usage was successfully logged, False otherwise
    """
    url = f"{get_base_url()}api/v1/sdk/server/log-usage"
    
    # Get base auth headers and add Authorization
    headers = get_auth_headers()
    headers["Authorization"] = f"Bearer {token}"
    
    payload = {"feature": feature}
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data.get("success", False)
    except requests.RequestException as e:
        print(f"Error logging feature usage: {e}")
        return False 