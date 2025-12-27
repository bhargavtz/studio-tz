"""
NCD INAI - Repository Interfaces
Abstract base classes for data access
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

from app.database.models import Session as DBSession, User, GeneratedFile


class ISessionRepository(ABC):
    """Repository interface for Session operations."""
    
    @abstractmethod
    async def create(self, user_id: Optional[UUID], intent: Optional[str] = None) -> DBSession:
        """Create a new session."""
        pass
    
    @abstractmethod
    async def get_by_id(self, session_id: UUID) -> Optional[DBSession]:
        """Get session by ID."""
        pass
    
    @abstractmethod
    async def update(self, session: DBSession) -> DBSession:
        """Update session."""
        pass
    
    @abstractmethod
    async def delete(self, session_id: UUID) -> bool:
        """Delete session."""
        pass
    
    @abstractmethod
    async def get_user_sessions(self, user_id: UUID, limit: int = 50) -> List[DBSession]:
        """Get all sessions for a user."""
        pass
    
    @abstractmethod
    async def update_status(self, session_id: UUID, status: str) -> DBSession:
        """Update session status."""
        pass
    
    @abstractmethod
    async def update_fields(self, session_id: UUID, **fields) -> DBSession:
        """Update specific session fields."""
        pass


class IUserRepository(ABC):
    """Repository interface for User operations."""
    
    @abstractmethod
    async def get_or_create(
        self, 
        clerk_user_id: str, 
        email: Optional[str] = None,
        name: Optional[str] = None
    ) -> User:
        """Get existing user or create new one."""
        pass
    
    @abstractmethod
    async def get_by_clerk_id(self, clerk_user_id: str) -> Optional[User]:
        """Get user by Clerk ID."""
        pass
    
    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        pass
    
    @abstractmethod
    async def update_storage_usage(self, user_id: UUID, bytes_delta: int) -> User:
        """Update user storage usage."""
        pass


class IFileRepository(ABC):
    """Repository interface for File operations."""
    
    @abstractmethod
    async def create(
        self,
        session_id: UUID,
        file_name: str,
        file_path: str,
        file_type: str,
        r2_key: str,
        r2_url: str,
        size_bytes: int,
        mime_type: str
    ) -> GeneratedFile:
        """Create file record."""
        pass
    
    @abstractmethod
    async def get_by_id(self, file_id: UUID) -> Optional[GeneratedFile]:
        """Get file by ID."""
        pass
    
    @abstractmethod
    async def get_session_files(self, session_id: UUID) -> List[GeneratedFile]:
        """Get all files for a session."""
        pass
    
    @abstractmethod
    async def delete(self, file_id: UUID) -> bool:
        """Delete file record."""
        pass
    
    @abstractmethod
    async def delete_session_files(self, session_id: UUID) -> int:
        """Delete all files for a session. Returns count of deleted files."""
        pass
