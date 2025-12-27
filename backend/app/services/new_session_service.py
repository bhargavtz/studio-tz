"""
NCD INAI - New Session Service
Production-ready session management using repository pattern
This REPLACES the old services/session_manager.py
"""

import logging
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.repositories.session_repository import SessionRepository
from app.infrastructure.repositories.user_repository import UserRepository
from app.infrastructure.storage.file_store import UnifiedFileStore
from app.database.models import Session as DBSession, SessionStatus
from app.core.exceptions import SessionNotFoundError, SessionCreationError

logger = logging.getLogger(__name__)


class SessionService:
    """
    Session service with clean architecture.
    
    This is the NEW session service that replaces session_manager.py.
    It uses repository pattern and dependency injection.
    """
    
    def __init__(
        self,
        db: AsyncSession,
        file_store: Optional[UnifiedFileStore] = None
    ):
        """
        Initialize session service.
        
        Args:
            db: Database session
            file_store: Optional file store (will be created if not provided)
        """
        self.db = db
        self.session_repo = SessionRepository(db)
        self.user_repo = UserRepository(db)
        self.file_store = file_store or UnifiedFileStore(db)
    
    async def create_session(
        self,
        user_id: Optional[UUID] = None,
        clerk_user_id: Optional[str] = None,
        intent: Optional[str] = None
    ) -> DBSession:
        """
        Create a new website building session.
        
        Args:
            user_id: User UUID (optional)
            clerk_user_id: Clerk user ID (will create/get user)
            intent: User's website intent
        
        Returns:
            Created session
        
        Raises:
            SessionCreationError: If creation fails
        """
        try:
            # Get or create user if clerk_user_id provided
            if clerk_user_id and not user_id:
                user = await self.user_repo.get_or_create(clerk_user_id)
                user_id = user.id
            
            # Create session
            session = await self.session_repo.create(
                user_id=user_id,
                intent=intent
            )
            
            logger.info(f"✅ Created session: {session.id}")
            return session
        
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            raise SessionCreationError(str(e))
    
    async def get_session(self, session_id: UUID) -> DBSession:
        """
        Get session by ID.
        
        Args:
            session_id: Session UUID
        
        Returns:
            Session object
        
        Raises:
            SessionNotFoundError: If session not found
        """
        session = await self.session_repo.get_by_id(session_id)
        
        if not session:
            raise SessionNotFoundError(str(session_id))
        
        return session
    
    async def get_session_optional(self, session_id: UUID) -> Optional[DBSession]:
        """
        Get session by ID, returns None if not found.
        
        Args:
            session_id: Session UUID
        
        Returns:
            Session object or None
        """
        return await self.session_repo.get_by_id(session_id)
    
    async def update_session(
        self,
        session_id: UUID,
        **fields
    ) -> DBSession:
        """
        Update session fields.
        
        Args:
            session_id: Session UUID
            **fields: Fields to update
        
        Returns:
            Updated session
        """
        return await self.session_repo.update_fields(session_id, **fields)
    
    async def update_status(
        self,
        session_id: UUID,
        status: SessionStatus
    ) -> DBSession:
        """
        Update session status.
        
        Args:
            session_id: Session UUID
            status: New status
        
        Returns:
            Updated session
        """
        return await self.session_repo.update_status(session_id, status.value)
    
    async def delete_session(
        self,
        session_id: UUID,
        delete_files: bool = True
    ) -> bool:
        """
        Delete a session.
        
        Args:
            session_id: Session UUID
            delete_files: Whether to delete associated files
        
        Returns:
            True if deleted, False if not found
        """
        if delete_files:
            # Get session to find user_id
            session = await self.get_session_optional(session_id)
            user_id = session.user_id if session else None
            
            # Delete all files
            await self.file_store.delete_session_files(session_id, user_id)
        
        return await self.session_repo.delete(session_id)
    
    async def get_user_sessions(
        self,
        user_id: UUID,
        limit: int = 50
    ) -> List[DBSession]:
        """
        Get all sessions for a user.
        
        Args:
            user_id: User UUID
            limit: Maximum number of sessions
        
        Returns:
            List of sessions
        """
        return await self.session_repo.get_user_sessions(user_id, limit)
    
    async def get_user_sessions_by_clerk_id(
        self,
        clerk_user_id: str,
        limit: int = 50
    ) -> List[DBSession]:
        """
        Get all sessions for a user by Clerk ID.
        
        Args:
            clerk_user_id: Clerk user ID
            limit: Maximum number of sessions
        
        Returns:
            List of sessions
        """
        user = await self.user_repo.get_by_clerk_id(clerk_user_id)
        if not user:
            return []
        
        return await self.session_repo.get_user_sessions(user.id, limit)
    
    async def save_session_data(
        self,
        session_id: UUID,
        data_type: str,
        data: Dict[str, Any]
    ) -> DBSession:
        """
        Save JSON data to session (intent, domain, answers, blueprint).
        
        Args:
            session_id: Session UUID
            data_type: Type of data (intent, domain, answers, blueprint)
            data: Data to save
        
        Returns:
            Updated session
        """
        field_mapping = {
            'intent': 'intent',
            'domain': 'domain',
            'answers': 'answers',
            'blueprint': 'blueprint'
        }
        
        field_name = field_mapping.get(data_type)
        if not field_name:
            raise ValueError(f"Invalid data type: {data_type}")
        
        return await self.update_session(session_id, **{field_name: data})
    
    async def confirm_blueprint(self, session_id: UUID) -> DBSession:
        """
        Confirm the blueprint for a session.
        
        Args:
            session_id: Session UUID
        
        Returns:
            Updated session
        """
        return await self.update_session(
            session_id,
            blueprint_confirmed=True,
            status=SessionStatus.BLUEPRINT_CONFIRMED.value
        )
    
    async def get_session_files(self, session_id: UUID) -> List[Dict[str, Any]]:
        """
        Get all files for a session.
        
        Args:
            session_id: Session UUID
        
        Returns:
            List of file info dicts
        """
        return await self.file_store.list_session_files(session_id)


# Factory function for dependency injection
def get_session_service(db: AsyncSession) -> SessionService:
    """
    Factory function to create SessionService instance.
    
    Args:
        db: Database session
    
    Returns:
        SessionService instance
    """
    return SessionService(db)
