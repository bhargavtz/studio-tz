"""
NCD INAI - Session Models
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
import uuid


class SessionStatus(str, Enum):
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


class DomainClassification(BaseModel):
    """Domain classification result from AI."""
    domain: str = Field(..., description="Primary domain (e.g., flower_shop, restaurant)")
    industry: str = Field(..., description="Industry category")
    business_type: str = Field(..., description="Type of business")
    keywords: List[str] = Field(default_factory=list, description="Relevant keywords")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class Session(BaseModel):
    """User session data model."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: SessionStatus = SessionStatus.CREATED
    
    # User intent
    intent: Optional[str] = None
    
    # Domain classification
    domain: Optional[DomainClassification] = None
    
    # Questions and answers
    questions: List[Dict[str, Any]] = Field(default_factory=list)
    answers: Dict[str, Any] = Field(default_factory=dict)
    
    # Blueprint
    blueprint: Optional[Dict[str, Any]] = None
    blueprint_confirmed: bool = False
    
    # Generated files tracking
    files_generated: List[str] = Field(default_factory=list)
    
    class Config:
        use_enum_values = True


class CreateSessionResponse(BaseModel):
    """Response for session creation."""
    session_id: str
    status: str
    message: str


class SessionStatusResponse(BaseModel):
    """Response for session status check."""
    session_id: str
    status: SessionStatus
    created_at: datetime
    intent: Optional[str]
    domain: Optional[DomainClassification]
    blueprint_confirmed: bool
    files_generated: List[str]
