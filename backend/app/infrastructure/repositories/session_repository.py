"""
NCD INAI - Session Repository Implementation
Database operations for sessions
"""

from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.infrastructure.repositories import ISessionRepository
from app.database.models import Session as DBSession, SessionStatus
from app.core.exceptions import SessionNotFoundError, SessionUpdateError


class SessionRepository(ISessionRepository):
    """SQLAlchemy implementation of session repository."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, user_id: Optional[UUID], intent: Optional[str] = None) -> DBSession:
        """Create a new session."""
        session = DBSession(
            user_id=user_id,
            intent=intent,
            status=SessionStatus.CREATED
        )
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        return session
    
    async def get_by_id(self, session_id: UUID) -> Optional[DBSession]:
        """Get session by ID with relationships."""
        query = select(DBSession).where(DBSession.id == session_id)
        query = query.options(
            selectinload(DBSession.generated_files),
            selectinload(DBSession.chat_messages),
            selectinload(DBSession.themes)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def update(self, session: DBSession) -> DBSession:
        """Update session."""
        await self.db.commit()
        await self.db.refresh(session)
        return session
    
    async def delete(self, session_id: UUID) -> bool:
        """Delete session."""
        session = await self.get_by_id(session_id)
        if not session:
            return False
        
        await self.db.delete(session)
        await self.db.commit()
        return True
    
    async def get_user_sessions(self, user_id: UUID, limit: int = 50) -> List[DBSession]:
        """Get all sessions for a user."""
        result = await self.db.execute(
            select(DBSession)
            .where(DBSession.user_id == user_id)
            .order_by(DBSession.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def update_status(self, session_id: UUID, status: str) -> DBSession:
        """Update session status."""
        session = await self.get_by_id(session_id)
        if not session:
            raise SessionNotFoundError(str(session_id))
        
        session.status = status
        return await self.update(session)
    
    async def update_fields(self, session_id: UUID, **fields) -> DBSession:
        """Update specific session fields."""
        session = await self.get_by_id(session_id)
        if not session:
            raise SessionNotFoundError(str(session_id))
        
        for key, value in fields.items():
            if hasattr(session, key):
                setattr(session, key, value)
        
        return await self.update(session)
