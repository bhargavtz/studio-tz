"""
NCD INAI - Intent Router (Database Version)
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.database.connection import get_db
from app.database import crud
from app.models.session import DomainClassification
from app.agents.domain_identifier import domain_identifier

router = APIRouter()


class IntentRequest(BaseModel):
    session_id: str
    intent_text: str


class IntentResponse(BaseModel):
    session_id: str
    status: str
    domain: DomainClassification
    message: str


@router.post("/intent", response_model=IntentResponse)
async def process_intent(
    request: IntentRequest,
    db: AsyncSession = Depends(get_db)
):
    """Process user's initial intent and identify domain."""
    try:
        session_uuid = uuid.UUID(request.session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID")
    
    session = await crud.get_session(db, session_uuid)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Store intent
    session.intent = request.intent_text
    session.status = "intent_collected"
    
    # Identify domain
    domain = await domain_identifier.identify(request.intent_text)
    session.domain = domain.model_dump()
    session.status = "domain_identified"
    
    await db.commit()
    await db.refresh(session)
    
    return IntentResponse(
        session_id=str(session.id),
        status=session.status,
        domain=domain,
        message=f"Identified as a {domain.domain.replace('_', ' ')} website. Generating questions..."
    )
