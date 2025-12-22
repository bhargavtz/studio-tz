"""
NCD INAI - Intent Router
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.session_manager import session_manager
from app.models.session import SessionStatus, DomainClassification
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
async def process_intent(request: IntentRequest):
    """Process user's initial intent and identify domain."""
    session = session_manager.get_session(request.session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Store intent
    session.intent = request.intent_text
    session.status = SessionStatus.INTENT_COLLECTED
    
    # Identify domain
    domain = await domain_identifier.identify(request.intent_text)
    session.domain = domain
    session.status = SessionStatus.DOMAIN_IDENTIFIED
    
    # Save vision.json
    session_manager.save_json_file(
        request.session_id,
        "vision.json",
        {
            "intent": request.intent_text,
            "domain": domain.model_dump()
        }
    )
    
    session_manager.update_session(session)
    
    return IntentResponse(
        session_id=session.id,
        status=session.status.value,
        domain=domain,
        message=f"Identified as a {domain.domain.replace('_', ' ')} website. Generating questions..."
    )
