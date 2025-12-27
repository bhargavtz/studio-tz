"""
NCD INAI - Authentication Middleware
Clerk JWT token verification and user extraction
"""

import logging
from typing import Optional
from fastapi import Request, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.exceptions import InvalidTokenError, UnauthorizedError

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer(auto_error=False)


async def get_current_user_id(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[str]:
    """
    Extract Clerk user ID from Authorization header.
    
    Args:
        request: FastAPI request object
        credentials: HTTP Bearer credentials
    
    Returns:
        Clerk user ID if authenticated, None otherwise
    
    Raises:
        InvalidTokenError: If token is invalid
    """
    # Check for token in header
    if not credentials:
        # For now, allow unauthenticated access (optional auth)
        # In production, you can make this required by raising UnauthorizedError
        return None
    
    token = credentials.credentials
    
    try:
        # TODO: Implement actual Clerk JWT verification
        # For now, we'll extract user_id from a custom header
        # In production, use Clerk's verification library
        
        # Temporary: Get user ID from custom header
        user_id = request.headers.get("X-Clerk-User-Id")
        
        if not user_id:
            logger.warning("Token provided but no user ID found")
            return None
        
        return user_id
    
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise InvalidTokenError("Invalid or expired authentication token")


async def require_auth(
    user_id: Optional[str] = Depends(get_current_user_id)
) -> str:
    """
    Require authentication. Raises error if not authenticated.
    
    Args:
        user_id: User ID from get_current_user_id dependency
    
    Returns:
        Authenticated user ID
    
    Raises:
        UnauthorizedError: If user is not authenticated
    """
    if not user_id:
        raise UnauthorizedError("Authentication required")
    
    return user_id


async def optional_auth(
    user_id: Optional[str] = Depends(get_current_user_id)
) -> Optional[str]:
    """
    Optional authentication. Returns None if not authenticated.
    
    Args:
        user_id: User ID from get_current_user_id dependency
    
    Returns:
        User ID if authenticated, None otherwise
    """
    return user_id


# TODO: Implement Clerk JWT verification
# from clerk_backend_api import Clerk
# 
# clerk = Clerk(bearer_auth=os.getenv("CLERK_SECRET_KEY"))
# 
# async def verify_clerk_token(token: str) -> dict:
#     """Verify Clerk JWT token and return user info."""
#     try:
#         # Verify token with Clerk
#         session = clerk.sessions.verify_token(token)
#         return {
#             "user_id": session.user_id,
#             "session_id": session.id
#         }
#     except Exception as e:
#         raise InvalidTokenError(f"Token verification failed: {e}")
