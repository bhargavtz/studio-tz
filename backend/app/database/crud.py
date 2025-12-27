"""
NCD INAI - Database CRUD Operations
Create, Read, Update, Delete operations for all models
"""

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
import uuid

from app.database.models import (
    User, Session as DBSession, GeneratedFile, 
    ChatMessage, Theme, Asset, SessionStatus
)


# ==================== USER OPERATIONS ====================

async def get_or_create_user(
    db: AsyncSession,
    clerk_user_id: str,
    email: Optional[str] = None,
    name: Optional[str] = None
) -> User:
    """Get existing user or create new one."""
    # Try to find existing user
    result = await db.execute(
        select(User).where(User.clerk_user_id == clerk_user_id)
    )
    user = result.scalar_one_or_none()
    
    if user:
        return user
    
    # Create new user - with race condition handling
    try:
        user = User(
            clerk_user_id=clerk_user_id,
            email=email,
            name=name
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
    except Exception as e:
        # Handle race condition - another request may have created the user
        await db.rollback()
        
        # Try to fetch the existing user
        result = await db.execute(
            select(User).where(User.clerk_user_id == clerk_user_id)
        )
        user = result.scalar_one_or_none()
        
        if user:
            return user
        
        # If still not found, re-raise the original error
        raise e


async def get_user_by_clerk_id(db: AsyncSession, clerk_user_id: str) -> Optional[User]:
    """Get user by Clerk ID."""
    result = await db.execute(
        select(User).where(User.clerk_user_id == clerk_user_id)
    )
    return result.scalar_one_or_none()


# ==================== SESSION OPERATIONS ====================

async def create_session(
    db: AsyncSession,
    user_id: Optional[uuid.UUID] = None,
    intent: Optional[str] = None
) -> DBSession:
    """Create a new website building session."""
    session = DBSession(
        user_id=user_id,
        intent=intent,
        status=SessionStatus.CREATED
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


async def get_session(
    db: AsyncSession,
    session_id: uuid.UUID,
    load_relationships: bool = False
) -> Optional[DBSession]:
    """Get session by ID."""
    query = select(DBSession).where(DBSession.id == session_id)
    
    if load_relationships:
        query = query.options(
            selectinload(DBSession.generated_files),
            selectinload(DBSession.chat_messages),
            selectinload(DBSession.themes)
        )
    
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def update_session(
    db: AsyncSession,
    session_id: uuid.UUID,
    **updates
) -> Optional[DBSession]:
    """Update session fields."""
    session = await get_session(db, session_id)
    if not session:
        return None
    
    for key, value in updates.items():
        if hasattr(session, key):
            setattr(session, key, value)
    
    await db.commit()
    await db.refresh(session)
    return session


async def get_user_sessions(
    db: AsyncSession,
    user_id: uuid.UUID,
    limit: int = 50
) -> List[DBSession]:
    """Get all sessions for a user."""
    result = await db.execute(
        select(DBSession)
        .where(DBSession.user_id == user_id)
        .order_by(DBSession.created_at.desc())
        .limit(limit)
    )
    return result.scalars().all()


# ==================== FILE OPERATIONS ====================

async def create_generated_file(
    db: AsyncSession,
    session_id: uuid.UUID,
    file_name: str,
    file_path: str,
    file_type: str,
    r2_key: str,
    r2_url: str,
    size_bytes: int,
    mime_type: str
) -> GeneratedFile:
    """Record a generated file in database."""
    file = GeneratedFile(
        session_id=session_id,
        file_name=file_name,
        file_path=file_path,
        file_type=file_type,
        r2_key=r2_key,
        r2_url=r2_url,
        size_bytes=size_bytes,
        mime_type=mime_type
    )
    db.add(file)
    await db.commit()
    await db.refresh(file)
    return file


async def get_session_files(
    db: AsyncSession,
    session_id: uuid.UUID
) -> List[GeneratedFile]:
    """Get all files for a session."""
    result = await db.execute(
        select(GeneratedFile)
        .where(GeneratedFile.session_id == session_id)
        .order_by(GeneratedFile.created_at.desc())
    )
    return result.scalars().all()


async def delete_session_files(
    db: AsyncSession,
    session_id: uuid.UUID
):
    """Delete all file records for a session."""
    await db.execute(
        delete(GeneratedFile).where(GeneratedFile.session_id == session_id)
    )
    await db.commit()


# ==================== CHAT OPERATIONS ====================

async def create_chat_message(
    db: AsyncSession,
    session_id: uuid.UUID,
    role: str,
    content: str,
    metadata: dict = None
) -> ChatMessage:
    """Create a chat message."""
    message = ChatMessage(
        session_id=session_id,
        role=role,
        content=content,
        message_metadata=metadata or {}
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return message


async def get_chat_history(
    db: AsyncSession,
    session_id: uuid.UUID,
    limit: int = 100
) -> List[ChatMessage]:
    """Get chat history for a session."""
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
        .limit(limit)
    )
    return result.scalars().all()


# ==================== THEME OPERATIONS ====================

async def create_or_update_theme(
    db: AsyncSession,
    session_id: uuid.UUID,
    primary_color: str,
    secondary_color: str,
    accent_color: str,
    font_family: str,
    style: str,
    custom_css: Optional[str] = None
) -> Theme:
    """Create or update theme for a session."""
    # Check if theme exists
    result = await db.execute(
        select(Theme).where(Theme.session_id == session_id)
    )
    theme = result.scalar_one_or_none()
    
    if theme:
        # Update existing
        theme.primary_color = primary_color
        theme.secondary_color = secondary_color
        theme.accent_color = accent_color
        theme.font_family = font_family
        theme.style = style
        theme.custom_css = custom_css
    else:
        # Create new
        theme = Theme(
            session_id=session_id,
            primary_color=primary_color,
            secondary_color=secondary_color,
            accent_color=accent_color,
            font_family=font_family,
            style=style,
            custom_css=custom_css
        )
        db.add(theme)
    
    await db.commit()
    await db.refresh(theme)
    return theme


async def get_session_theme(
    db: AsyncSession,
    session_id: uuid.UUID
) -> Optional[Theme]:
    """Get theme for a session."""
    result = await db.execute(
        select(Theme).where(Theme.session_id == session_id)
    )
    return result.scalar_one_or_none()
