"""
NCD INAI - SQLAlchemy Database Models
"""

from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import (
    Column, String, Text, Boolean, BigInteger, 
    DateTime, ForeignKey, Enum as SQLEnum, Index, ARRAY
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET
from sqlalchemy.orm import relationship
import uuid
import enum

from app.database.connection import Base


class SessionStatus(str, enum.Enum):
    """Session workflow status."""
    CREATED = "created"
    INTENT_COLLECTED = "intent_collected"
    DOMAIN_IDENTIFIED = "domain_identified"
    QUESTIONS_GENERATED = "questions_generated"
    ANSWERS_COLLECTED = "answers_collected"
    BLUEPRINT_GENERATED = "blueprint_generated"
    BLUEPRINT_CONFIRMED = "blueprint_confirmed"
    WEBSITE_GENERATED = "website_generated"
    EDITING = "editing"


class User(Base):
    """User model - integrated with Clerk authentication."""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    clerk_user_id = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, index=True)
    name = Column(String)
    avatar_url = Column(String)
    
    # Storage quota tracking (200MB = 209715200 bytes)
    storage_used_bytes = Column(BigInteger, default=0, nullable=False)
    storage_limit_bytes = Column(BigInteger, default=209715200, nullable=False)  # 200MB
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    assets = relationship("Asset", back_populates="user", cascade="all, delete-orphan")
    
    @property
    def storage_remaining_bytes(self) -> int:
        """Calculate remaining storage in bytes."""
        return max(0, self.storage_limit_bytes - self.storage_used_bytes)
    
    @property
    def storage_usage_percentage(self) -> float:
        """Calculate storage usage as percentage."""
        if self.storage_limit_bytes == 0:
            return 100.0
        return (self.storage_used_bytes / self.storage_limit_bytes) * 100


class Session(Base):
    """Session model - website building session."""
    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    intent = Column(Text)
    status = Column(String, default=SessionStatus.CREATED.value, nullable=False, index=True)
    domain = Column(JSONB)
    questions = Column(JSONB, default=list)
    answers = Column(JSONB, default=dict)
    blueprint = Column(JSONB)
    blueprint_confirmed = Column(Boolean, default=False)
    
    # Project metadata for dashboard
    project_title = Column(String(255))
    project_description = Column(Text)
    thumbnail_r2_key = Column(String(500))
    thumbnail_r2_url = Column(String(1000))
    total_size_bytes = Column(BigInteger, default=0)  # Cached storage size
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="sessions")
    generated_files = relationship("GeneratedFile", back_populates="session", cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")
    themes = relationship("Theme", back_populates="session", cascade="all, delete-orphan")
    assets = relationship("Asset", back_populates="session", cascade="all, delete-orphan")
    
    @property
    def display_title(self) -> str:
        """Get display title for dashboard."""
        if self.project_title:
            return self.project_title
        if self.intent:
            return self.intent[:50] + ('...' if len(self.intent) > 50 else '')
        return "Untitled Project"


class GeneratedFile(Base):
    """Generated files stored in R2."""
    __tablename__ = "generated_files"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    file_path = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    file_type = Column(String, nullable=False, index=True)  # 'html', 'css', 'js', 'image'
    r2_key = Column(String, nullable=False)  # R2 object key
    r2_url = Column(String, nullable=False)  # Public URL
    size_bytes = Column(BigInteger)
    mime_type = Column(String)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    session = relationship("Session", back_populates="generated_files")


class ChatMessage(Base):
    """Chat messages with AI."""
    __tablename__ = "chat_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String, nullable=False)  # 'user', 'ai', 'system'
    content = Column(Text, nullable=False)
    message_metadata = Column(JSONB, default=dict)  # Renamed from 'metadata' (reserved in SQLAlchemy)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)

    # Relationships
    session = relationship("Session", back_populates="chat_messages")


class Theme(Base):
    """Theme customizations for sessions."""
    __tablename__ = "themes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    primary_color = Column(String, nullable=False)
    secondary_color = Column(String, nullable=False)
    accent_color = Column(String, nullable=False)
    font_family = Column(String, nullable=False)
    style = Column(String, nullable=False)  # 'modern', 'minimal', 'classic'
    custom_css = Column(Text)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    session = relationship("Session", back_populates="themes")


class Asset(Base):
    """User uploaded assets stored in R2."""
    __tablename__ = "assets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    asset_name = Column(String, nullable=False)
    asset_type = Column(String, nullable=False)  # 'image', 'logo', 'icon'
    r2_key = Column(String, nullable=False)
    r2_url = Column(String, nullable=False)
    size_bytes = Column(BigInteger)
    mime_type = Column(String)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    session = relationship("Session", back_populates="assets")
    user = relationship("User", back_populates="assets")


class ActivityLog(Base):
    """Activity logs for analytics."""
    __tablename__ = "activity_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="SET NULL"), nullable=True, index=True)
    action = Column(String, nullable=False)
    details = Column(JSONB, default=dict)
    ip_address = Column(INET)
    user_agent = Column(Text)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
