"""
NCD INAI - Common Dependencies
Shared dependency injection functions for routers
"""

from typing import Optional
from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.services.new_session_service import SessionService
from app.infrastructure.storage.file_store import UnifiedFileStore
from app.infrastructure.repositories.session_repository import SessionRepository
from app.infrastructure.repositories.user_repository import UserRepository
from app.infrastructure.repositories.file_repository import FileRepository


# ==================== Repository Dependencies ====================

def get_session_repository(db: AsyncSession = Depends(get_db)) -> SessionRepository:
    """Get session repository instance."""
    return SessionRepository(db)


def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    """Get user repository instance."""
    return UserRepository(db)


def get_file_repository(db: AsyncSession = Depends(get_db)) -> FileRepository:
    """Get file repository instance."""
    return FileRepository(db)


# ==================== Service Dependencies ====================

def get_file_store(db: AsyncSession = Depends(get_db)) -> UnifiedFileStore:
    """Get unified file store instance."""
    return UnifiedFileStore(db)


def get_session_service(db: AsyncSession = Depends(get_db)) -> SessionService:
    """Get session service instance."""
    return SessionService(db)


# ==================== Authentication Dependencies ====================

async def get_clerk_user_id(
    x_clerk_user_id: Optional[str] = Header(None, alias="X-Clerk-User-Id")
) -> Optional[str]:
    """
    Get Clerk user ID from header.
    
    This is a temporary implementation. In production, verify JWT token.
    """
    return x_clerk_user_id


async def require_clerk_user_id(
    x_clerk_user_id: Optional[str] = Header(None, alias="X-Clerk-User-Id")
) -> str:
    """
    Require Clerk user ID from header.
    
    Raises:
        UnauthorizedError: If no user ID provided
    """
    if not x_clerk_user_id:
        from app.core.exceptions import UnauthorizedError
        raise UnauthorizedError("User authentication required")
    
    return x_clerk_user_id
