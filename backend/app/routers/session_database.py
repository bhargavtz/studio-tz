"""
NCD INAI - Session Router (Database Version - NOT IN USE)
This is the database-integrated version for future use when database is fully setup.
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import uuid

from app.database.connection import get_db
from app.database import crud
from app.config import settings

router = APIRouter()


class CreateSessionRequest(BaseModel):
    """Request body for creating a session."""
    intent: Optional[str] = None


class CreateSessionResponse(BaseModel):
    session_id: str
    status: str
    message: str


class SessionStatusResponse(BaseModel):
    session_id: str
    status: str
    created_at: str
    intent: Optional[str]
    user_id: Optional[str]
    domain: Optional[dict] = None
    blueprint: Optional[dict] = None
    questions: list = []
    answers: dict = {}
    blueprint_confirmed: bool
    files_generated: list = []
    files_count: int


async def get_user_from_clerk_header(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
):
    """Extract Clerk user from Authorization header."""
    if authorization and authorization.startswith("Bearer "):
        clerk_user_id = authorization.replace("Bearer ", "")
        user = await crud.get_or_create_user(db, clerk_user_id)
        return user
    return None


@router.post("/create", response_model=CreateSessionResponse)
async def create_session(
    request: CreateSessionRequest = None,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_user_from_clerk_header)
):
    """Create a new website building session with database."""
    session = await crud.create_session(
        db=db,
        user_id=user.id if user else None,
        intent=request.intent if request else None
    )
    
    return CreateSessionResponse(
        session_id=str(session.id),
        status=session.status,
        message="Session created successfully"
    )


@router.get("/{session_id}/status", response_model=SessionStatusResponse)
async def get_session_status(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get session status from database."""
    try:
        session_uuid = uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID")
    
    session = await crud.get_session(db, session_uuid, load_relationships=True)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Build files_generated array from database
    files_generated = []
    for file in session.generated_files:
        files_generated.append({
            "id": str(file.id),
            "file_path": file.file_path,
            "file_type": file.file_type,
            "size_bytes": file.size_bytes
        })
    
    return SessionStatusResponse(
        session_id=str(session.id),
        status=session.status,
        created_at=session.created_at.isoformat(),
        intent=session.intent,
        user_id=str(session.user_id) if session.user_id else None,
        domain=session.domain,
        blueprint=session.blueprint,
        questions=session.questions or [],
        answers=session.answers or {},
        blueprint_confirmed=session.blueprint_confirmed,
        files_generated=files_generated,
        files_count=len(session.generated_files)
    )


class SessionDeleteResponse(BaseModel):
    success: bool
    message: str


@router.delete("/{session_id}", response_model=SessionDeleteResponse)
async def delete_session(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete session from database."""
    try:
        session_uuid = uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID")
    
    session = await crud.get_session(db, session_uuid)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    from app.services.storage_service import storage_service
    await storage_service.delete_session_files(db, session_uuid)
    
    await db.delete(session)
    await db.commit()
    
    return SessionDeleteResponse(
        success=True,
        message="Session deleted successfully"
    )
