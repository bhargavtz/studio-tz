"""
NCD INAI - Projects Router
Compatibility layer for frontend - maps /api/projects/ to session endpoints
"""

import logging
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database.connection import get_db
from app.database import crud

router = APIRouter()
logger = logging.getLogger(__name__)


class ProjectCreateRequest(BaseModel):
    """Request for creating a new project."""
    name: str
    vision: Optional[str] = None


class ProjectResponse(BaseModel):
    """Response after creating a project."""
    id: str
    project_id: str
    session_id: str
    status: str
    created_at: str
    updated_at: str
    files_generated: list = []
    blueprint_confirmed: bool = False


@router.post("/", response_model=ProjectResponse)
async def create_project(
    request: ProjectCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new project (compatibility endpoint).
    Maps to database session creation
    """
    logger.info(f"Creating project via compatibility endpoint: {request.name}")
    
    # Create session directly using crud
    session = await crud.create_session(
        db=db,
        user_id=None,  # No user auth for now
        intent=request.vision
    )
    
    # Map session response to project response format
    return ProjectResponse(
        id=str(session.id),
        project_id=str(session.id),
        session_id=str(session.id),
        status=session.status,
        created_at=session.created_at.isoformat(),
        updated_at=session.updated_at.isoformat(),
        files_generated=[],
        blueprint_confirmed=False
    )


@router.get("/{project_id}")
async def get_project(
    project_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get project by ID (compatibility endpoint).
    Maps to database session retrieval
    """
    logger.info(f"Getting project via compatibility endpoint: {project_id}")
    
    import uuid
    try:
        session_uuid = uuid.UUID(project_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid project ID")
    
    # Get session using crud
    session = await crud.get_session(db, session_uuid, load_relationships=True)
    
    if not session:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Map session response to project response format
    return ProjectResponse(
        id=str(session.id),
        project_id=str(session.id),
        session_id=str(session.id),
        status=session.status,
        created_at=session.created_at.isoformat(),
        updated_at=session.updated_at.isoformat(),
        files_generated=[],
        blueprint_confirmed=session.blueprint_confirmed
    )

