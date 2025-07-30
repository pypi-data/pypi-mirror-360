"""
FastAPI dependencies for the Lightswitch SDK.

This module provides FastAPI-specific functionality and should only be imported
when using the SDK with FastAPI applications.
"""
from typing import Dict, Any, Optional, Callable

try:
    from fastapi import Header, HTTPException, status, Depends
except ImportError:
    raise ImportError(
        "FastAPI is required to use this module. Install it with: pip install fastapi"
    )

from .client import get_current_user, check_entitlement, log_usage


async def get_current_user_dependency(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """
    FastAPI dependency that extracts the user from the Authorization header.
    
    Args:
        authorization (str, optional): The Authorization header containing the Bearer token
        
    Returns:
        dict: The user data
        
    Raises:
        HTTPException: If authentication fails for any reason
    """
    # Check if authorization header exists
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if token format is correct
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme. Bearer token required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract token and get user data
    token = authorization.replace("Bearer ", "")
    user_data = get_current_user(token)
    
    # If fetching user data failed
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_data


def require_entitlement_dependency(feature: str) -> Callable:
    """
    FastAPI dependency function that checks if a user is entitled to use a specific feature.
    
    Args:
        feature (str): The feature to check entitlement for
        
    Returns:
        Callable: A dependency function that raises an exception if the user is not entitled
        
    Example:
        @router.post("/generate_ai_completion")
        async def generate_ai_completion(
            request_data: Dict[str, Any] = Body(...),
            user_data: Dict[str, Any] = Depends(get_current_user_dependency),
            _: None = Depends(require_entitlement_dependency("ai_auto_complete"))
        ):
            ...
    """
    async def check_entitlement_for_feature(authorization: str = Header(...)):
        if not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme. Bearer token required",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        token = authorization.replace("Bearer ", "")
        is_entitled = check_entitlement(token, feature)
        
        if not is_entitled:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You are not entitled to use this feature: {feature}",
                headers={"Feature": feature},
            )
        
        # Return None as this is just a validation dependency
        return None
    
    return check_entitlement_for_feature


def log_usage_dependency(feature: str) -> Callable:
    """
    FastAPI dependency function that logs the usage of a specific feature.
    
    Args:
        feature (str): The feature being used
        
    Returns:
        Callable: A dependency function that logs usage
        
    Example:
        @router.post("/generate_ai_completion")
        async def generate_ai_completion(
            request_data: Dict[str, Any] = Body(...),
            user_data: Dict[str, Any] = Depends(get_current_user_dependency),
            _: None = Depends(log_usage_dependency("ai_completion"))
        ):
            ...
    """
    async def log_feature_usage(authorization: str = Header(...)):
        if not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme. Bearer token required",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        token = authorization.replace("Bearer ", "")
        log_usage(token, feature)
        
        # Return None as this is just a logging dependency
        return None
    
    return log_feature_usage 