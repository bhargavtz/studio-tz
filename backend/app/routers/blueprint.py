"""
NCD INAI - Blueprint Router
"""

from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.session_manager import session_manager
from app.models.session import SessionStatus
from app.agents.blueprint_architect import blueprint_architect

router = APIRouter()


class BlueprintResponse(BaseModel):
    session_id: str
    blueprint: Dict[str, Any]
    editable: bool = True


class BlueprintConfirmResponse(BaseModel):
    session_id: str
    status: str
    message: str


@router.get("/blueprint/{session_id}", response_model=BlueprintResponse)
async def get_blueprint(session_id: str):
    """Get or generate the website blueprint."""
    session = session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if not session.answers:
        raise HTTPException(
            status_code=400,
            detail="Answers not collected yet. Submit answers first."
        )
    
    # Check if blueprint already exists
    if session.blueprint:
        return BlueprintResponse(
            session_id=session.id,
            blueprint=session.blueprint,
            editable=not session.blueprint_confirmed
        )
    
    # Generate blueprint
    blueprint = await blueprint_architect.create_blueprint(
        domain=session.domain,
        intent=session.intent,
        answers=session.answers
    )
    
    session.blueprint = blueprint
    session.status = SessionStatus.BLUEPRINT_GENERATED
    
    # Save blueprint
    session_manager.save_json_file(
        session_id,
        "blueprint.json",
        blueprint
    )
    
    session_manager.update_session(session)
    
    return BlueprintResponse(
        session_id=session.id,
        blueprint=blueprint,
        editable=True
    )


class BlueprintUpdateRequest(BaseModel):
    blueprint: Dict[str, Any]


@router.put("/blueprint/{session_id}", response_model=BlueprintResponse)
async def update_blueprint(session_id: str, request: BlueprintUpdateRequest):
    """Update the blueprint before confirmation."""
    session = session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session.blueprint_confirmed:
        raise HTTPException(
            status_code=400,
            detail="Blueprint already confirmed. Cannot modify."
        )
    
    # Update blueprint
    session.blueprint = request.blueprint
    
    # Save updated blueprint
    session_manager.save_json_file(
        session_id,
        "blueprint.json",
        request.blueprint
    )
    
    session_manager.update_session(session)
    
    return BlueprintResponse(
        session_id=session.id,
        blueprint=session.blueprint,
        editable=True
    )


@router.post("/blueprint/{session_id}/confirm", response_model=BlueprintConfirmResponse)
async def confirm_blueprint(session_id: str):
    """Confirm the blueprint to proceed with code generation."""
    session = session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if not session.blueprint:
        raise HTTPException(
            status_code=400,
            detail="Blueprint not generated yet."
        )
    
    session.blueprint_confirmed = True
    session.status = SessionStatus.BLUEPRINT_CONFIRMED
    session_manager.update_session(session)
    
    return BlueprintConfirmResponse(
        session_id=session.id,
        status=session.status.value,
        message="Blueprint confirmed. Ready to generate website."
    )
