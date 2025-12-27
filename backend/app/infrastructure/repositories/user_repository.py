"""
NCD INAI - User Repository Implementation
Database operations for users
"""

from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.infrastructure.repositories import IUserRepository
from app.database.models import User


class UserRepository(IUserRepository):
    """SQLAlchemy implementation of user repository."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_or_create(
        self,
        clerk_user_id: str,
        email: Optional[str] = None,
        name: Optional[str] = None
    ) -> User:
        """Get existing user or create new one."""
        # Try to find existing user
        user = await self.get_by_clerk_id(clerk_user_id)
        
        if user:
            return user
        
        # Create new user with race condition handling
        try:
            user = User(
                clerk_user_id=clerk_user_id,
                email=email,
                name=name
            )
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            return user
        except Exception as e:
            # Handle race condition
            await self.db.rollback()
            
            # Try to fetch again
            user = await self.get_by_clerk_id(clerk_user_id)
            if user:
                return user
            
            raise e
    
    async def get_by_clerk_id(self, clerk_user_id: str) -> Optional[User]:
        """Get user by Clerk ID."""
        result = await self.db.execute(
            select(User).where(User.clerk_user_id == clerk_user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def update_storage_usage(self, user_id: UUID, bytes_delta: int) -> User:
        """Update user storage usage."""
        user = await self.get_by_id(user_id)
        if not user:
            raise ValueError(f"User not found: {user_id}")
        
        user.storage_used_bytes += bytes_delta
        await self.db.commit()
        await self.db.refresh(user)
        return user
