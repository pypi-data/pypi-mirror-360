from typing import Callable, Dict, Any, Optional, List
from functools import wraps
from fastapi import Header, HTTPException

def requires_auth(provider: str, scope_bundle: str, required: bool = True):
    """Decorator to indicate that a tool requires authentication.

    Args:
        provider: Authentication provider (e.g., "google", "microsoft")
        scope_bundle: Scope bundle required (e.g., "calendar", "drive")
        required: Whether authentication is mandatory (default: True)

    Returns:
        Decorator function
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, authorization: Optional[str] = Header(None), **kwargs):
            if required and not authorization:
                raise HTTPException(status_code=401, detail="Authentication required")

            # The Tools Management Service will provide the appropriate token
            # in the Authorization header
            return await func(*args, authorization=authorization, **kwargs)

        # Store auth requirements in function metadata
        auth_req = {
            "provider": provider,
            "scope_bundle": scope_bundle,
            "required": required
        }

        # Initialize the list if it doesn't exist
        if not hasattr(wrapper, "__auth_requirements__"):
            wrapper.__auth_requirements__ = []

        # Add this auth requirement to the list
        wrapper.__auth_requirements__.append(auth_req)

        return wrapper

    return decorator
