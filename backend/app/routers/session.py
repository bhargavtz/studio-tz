"""
NCD INAI - Session Router
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.session_manager import session_manager
from app.models.session import CreateSessionResponse, SessionStatusResponse, SessionStatus

router = APIRouter()


@router.post("/create", response_model=CreateSessionResponse)
async def create_session():
    """Create a new session."""
    session = session_manager.create_session()
    
    return CreateSessionResponse(
        session_id=session.id,
        status=session.status.value,
        message="Session created successfully. Ask user: What kind of website do you want to build?"
    )


@router.get("/{session_id}/status", response_model=SessionStatusResponse)
async def get_session_status(session_id: str):
    """Get the current status of a session."""
    session = session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return SessionStatusResponse(
        session_id=session.id,
        status=session.status,
        created_at=session.created_at,
        intent=session.intent,
        domain=session.domain,
        blueprint_confirmed=session.blueprint_confirmed,
        files_generated=session.files_generated
    )


class SessionDeleteResponse(BaseModel):
    success: bool
    message: str


@router.delete("/{session_id}", response_model=SessionDeleteResponse)
async def delete_session(session_id: str):
    """Delete a session."""
    success = session_manager.delete_session(session_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return SessionDeleteResponse(
        success=True,
        message="Session deleted successfully"
    )
