"""
NCD INAI - Blueprint Router (Refactored with New Architecture)
Uses SessionService and proper exception handling
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from uuid import UUID
import logging

from app.services.new_session_service import SessionService
from app.api.dependencies import get_session_service
from app.agents.blueprint_architect import blueprint_architect
from app.core.exceptions import ValidationError, BlueprintAlreadyConfirmedError
from app.database.models import SessionStatus

logger = logging.getLogger(__name__)

router = APIRouter()


# ==================== Request/Response Models ====================

class BlueprintResponse(BaseModel):
    session_id: str
    blueprint: Dict[str, Any]
    editable: bool = True


class BlueprintUpdateRequest(BaseModel):
    blueprint: Dict[str, Any]


class BlueprintConfirmResponse(BaseModel):
    session_id: str
    status: str
    message: str


# ==================== Endpoints ====================

@router.get("/blueprint/{session_id}", response_model=BlueprintResponse)
async def get_blueprint(
    session_id: str,
    session_service: SessionService = Depends(get_session_service)
):
    """
    Get or generate the website blueprint.
    
    If blueprint exists, return it. Otherwise, generate new blueprint
    using AI based on user's intent and answers.
    """
    # Parse UUID
    try:
        session_uuid = UUID(session_id)
    except ValueError:
        raise ValidationError("session_id", "Invalid UUID format")
    
    # Get session (raises SessionNotFoundError if not found)
    session = await session_service.get_session(session_uuid)
    
    # Validate that answers exist
    if not session.answers:
        raise ValidationError(
            "answers",
            "Answers not collected yet. Submit answers first."
        )
    
    # Check if blueprint already exists
    if session.blueprint:
        logger.info(f"Returning existing blueprint for session {session_id}")
        return BlueprintResponse(
            session_id=str(session.id),
            blueprint=session.blueprint,
            editable=not session.blueprint_confirmed
        )
    
    # Generate new blueprint
    logger.info(f"Generating blueprint for session {session_id}")
    
    from app.models.session import DomainClassification
    domain_obj = DomainClassification(**session.domain)
    
    blueprint = await blueprint_architect.create_blueprint(
        domain=domain_obj,
        intent=session.intent,
        answers=session.answers
    )
    
    # Save blueprint to session
    await session_service.update_session(
        session_uuid,
        blueprint=blueprint,
        status=SessionStatus.BLUEPRINT_GENERATED.value
    )
    
    logger.info(f"✅ Blueprint generated for session {session_id}")
    
    return BlueprintResponse(
        session_id=str(session.id),
        blueprint=blueprint,
        editable=True
    )


@router.put("/blueprint/{session_id}", response_model=BlueprintResponse)
async def update_blueprint(
    session_id: str,
    request: BlueprintUpdateRequest,
    session_service: SessionService = Depends(get_session_service)
):
    """
    Update the blueprint before confirmation.
    
    Allows users to modify the AI-generated blueprint before
    confirming and proceeding to code generation.
    """
    # Parse UUID
    try:
        session_uuid = UUID(session_id)
    except ValueError:
        raise ValidationError("session_id", "Invalid UUID format")
    
    # Get session
    session = await session_service.get_session(session_uuid)
    
    # Check if blueprint is already confirmed
    if session.blueprint_confirmed:
        raise BlueprintAlreadyConfirmedError(str(session_uuid))
    
    # Update blueprint
    updated_session = await session_service.update_session(
        session_uuid,
        blueprint=request.blueprint
    )
    
    logger.info(f"✅ Blueprint updated for session {session_id}")
    
    return BlueprintResponse(
        session_id=str(updated_session.id),
        blueprint=updated_session.blueprint,
        editable=True
    )


@router.post("/blueprint/{session_id}/confirm", response_model=BlueprintConfirmResponse)
async def confirm_blueprint(
    session_id: str,
    session_service: SessionService = Depends(get_session_service)
):
    """
    Confirm the blueprint to proceed with code generation.
    
    Once confirmed, the blueprint cannot be modified and
    the system will proceed to generate website code.
    """
    # Parse UUID
    try:
        session_uuid = UUID(session_id)
    except ValueError:
        raise ValidationError("session_id", "Invalid UUID format")
    
    # Get session
    session = await session_service.get_session(session_uuid)
    
    # Validate blueprint exists
    if not session.blueprint:
        raise ValidationError(
            "blueprint",
            "Blueprint not generated yet."
        )
    
    # Confirm blueprint
    updated_session = await session_service.confirm_blueprint(session_uuid)
    
    logger.info(f"✅ Blueprint confirmed for session {session_id}")
    
    return BlueprintConfirmResponse(
        session_id=str(updated_session.id),
        status=updated_session.status,
        message="Blueprint confirmed. Ready to generate website."
    )

