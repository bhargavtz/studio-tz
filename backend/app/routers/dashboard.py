"""
NCD INAI - Dashboard Router
API endpoints for user dashboard with project management
"""

import logging
from fastapi import APIRouter, HTTPException, Depends, Header, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import Optional, List
import uuid

from app.database.connection import get_db, AsyncSessionLocal
from app.database import crud
from app.database.models import User, Session as DBSession, GeneratedFile
from app.services.storage_quota import storage_quota_service
from app.config import settings


router = APIRouter()
logger = logging.getLogger(__name__)


# ==================== DATABASE CHECK ====================

def check_database_enabled():
    """Check if database is enabled and raise error if not."""
    if not settings.use_database or not AsyncSessionLocal:
        raise HTTPException(
            status_code=503,
            detail="Database not configured. Please set USE_DATABASE=true and DATABASE_URL in .env"
        )


# ==================== PYDANTIC MODELS ====================

class ProjectResponse(BaseModel):
    """Single project for dashboard."""
    session_id: str
    project_title: str
    project_description: Optional[str]
    thumbnail_url: Optional[str]
    created_at: str
    updated_at: str
    status: str
    domain: Optional[str]
    file_count: int
    total_size_bytes: int
    total_size_mb: str


class ProjectListResponse(BaseModel):
    """List of projects with pagination."""
    projects: List[ProjectResponse]
    pagination: dict


class StorageSummaryResponse(BaseModel):
    """Storage usage summary."""
    storage_used_bytes: int
    storage_limit_bytes: int
    storage_remaining_bytes: int
    storage_used_mb: str
    storage_limit_mb: str
    storage_remaining_mb: str
    usage_percentage: float
    total_projects: int
    top_projects: List[dict]
    is_near_limit: bool
    is_at_limit: bool


class DashboardSummaryResponse(BaseModel):
    """Full dashboard summary."""
    user_name: Optional[str]
    user_email: Optional[str]
    total_projects: int
    recent_project: Optional[ProjectResponse]
    storage: StorageSummaryResponse


class UpdateProjectRequest(BaseModel):
    """Request to update project metadata."""
    project_title: Optional[str] = None
    project_description: Optional[str] = None


class DeleteProjectResponse(BaseModel):
    """Response after deleting project."""
    success: bool
    message: str
    storage_reclaimed_bytes: int
    storage_reclaimed_mb: str


# ==================== HELPER FUNCTIONS ====================

async def get_user_from_clerk_header(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Extract and validate Clerk user from Authorization header."""
    check_database_enabled()
    
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Authentication required. Please sign in."
        )
    
    clerk_user_id = authorization.replace("Bearer ", "")
    user = await crud.get_or_create_user(db, clerk_user_id)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user")
    
    return user


def format_project(session: DBSession, file_count: int = 0) -> ProjectResponse:
    """Format session as project response."""
    domain_name = None
    if session.domain and isinstance(session.domain, dict):
        domain_name = session.domain.get("domain")
    
    return ProjectResponse(
        session_id=str(session.id),
        project_title=session.display_title,
        project_description=session.project_description,
        thumbnail_url=session.thumbnail_r2_url,
        created_at=session.created_at.isoformat(),
        updated_at=session.updated_at.isoformat(),
        status=session.status,
        domain=domain_name,
        file_count=file_count,
        total_size_bytes=session.total_size_bytes or 0,
        total_size_mb=f"{storage_quota_service.bytes_to_mb(session.total_size_bytes or 0):.2f}"
    )


# ==================== ENDPOINTS ====================

@router.get("/projects", response_model=ProjectListResponse)
async def get_user_projects(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(12, ge=1, le=50, description="Items per page"),
    sort: str = Query("created_at_desc", description="Sort order"),
    search: Optional[str] = Query(None, description="Search in project titles"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_user_from_clerk_header)
):
    """Get all projects for authenticated user with pagination."""
    offset = (page - 1) * limit
    
    # Base query
    query = select(DBSession).where(DBSession.user_id == user.id)
    
    # Search filter
    if search:
        query = query.where(
            DBSession.project_title.ilike(f"%{search}%") |
            DBSession.intent.ilike(f"%{search}%")
        )
    
    # Sorting
    if sort == "created_at_desc":
        query = query.order_by(desc(DBSession.created_at))
    elif sort == "created_at_asc":
        query = query.order_by(DBSession.created_at)
    elif sort == "title_asc":
        query = query.order_by(DBSession.project_title)
    elif sort == "title_desc":
        query = query.order_by(desc(DBSession.project_title))
    elif sort == "size_desc":
        query = query.order_by(desc(DBSession.total_size_bytes))
    elif sort == "size_asc":
        query = query.order_by(DBSession.total_size_bytes)
    else:
        query = query.order_by(desc(DBSession.created_at))
    
    # Get total count
    count_query = select(func.count(DBSession.id)).where(DBSession.user_id == user.id)
    if search:
        count_query = count_query.where(
            DBSession.project_title.ilike(f"%{search}%") |
            DBSession.intent.ilike(f"%{search}%")
        )
    count_result = await db.execute(count_query)
    total = count_result.scalar()
    
    # Get page of sessions
    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    sessions = result.scalars().all()
    
    # Get file counts for each session
    projects = []
    for session in sessions:
        file_count_result = await db.execute(
            select(func.count(GeneratedFile.id))
            .where(GeneratedFile.session_id == session.id)
        )
        file_count = file_count_result.scalar()
        projects.append(format_project(session, file_count))
    
    return ProjectListResponse(
        projects=projects,
        pagination={
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit if total else 0
        }
    )


@router.get("/storage", response_model=StorageSummaryResponse)
async def get_storage_summary(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_user_from_clerk_header)
):
    """Get storage usage summary for authenticated user."""
    summary = await storage_quota_service.get_quota_summary(db, user.id)
    
    if "error" in summary:
        raise HTTPException(status_code=404, detail=summary["error"])
    
    return StorageSummaryResponse(**summary)


@router.get("/summary", response_model=DashboardSummaryResponse)
async def get_dashboard_summary(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_user_from_clerk_header)
):
    """Get full dashboard summary including recent project and storage."""
    # Get storage summary
    storage = await storage_quota_service.get_quota_summary(db, user.id)
    
    # Get most recent project
    recent_result = await db.execute(
        select(DBSession)
        .where(DBSession.user_id == user.id)
        .order_by(desc(DBSession.updated_at))
        .limit(1)
    )
    recent_session = recent_result.scalar_one_or_none()
    
    recent_project = None
    if recent_session:
        file_count_result = await db.execute(
            select(func.count(GeneratedFile.id))
            .where(GeneratedFile.session_id == recent_session.id)
        )
        file_count = file_count_result.scalar()
        recent_project = format_project(recent_session, file_count)
    
    return DashboardSummaryResponse(
        user_name=user.name,
        user_email=user.email,
        total_projects=storage.get("total_projects", 0),
        recent_project=recent_project,
        storage=StorageSummaryResponse(**storage)
    )


@router.get("/project/{session_id}", response_model=ProjectResponse)
async def get_project_details(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_user_from_clerk_header)
):
    """Get details for a specific project."""
    try:
        session_uuid = uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID")
    
    # Get session and verify ownership
    result = await db.execute(
        select(DBSession)
        .where(DBSession.id == session_uuid)
        .where(DBSession.user_id == user.id)
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get file count
    file_count_result = await db.execute(
        select(func.count(GeneratedFile.id))
        .where(GeneratedFile.session_id == session.id)
    )
    file_count = file_count_result.scalar()
    
    return format_project(session, file_count)


@router.patch("/project/{session_id}", response_model=ProjectResponse)
async def update_project_metadata(
    session_id: str,
    request: UpdateProjectRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_user_from_clerk_header)
):
    """Update project title or description."""
    try:
        session_uuid = uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID")
    
    # Get session and verify ownership
    result = await db.execute(
        select(DBSession)
        .where(DBSession.id == session_uuid)
        .where(DBSession.user_id == user.id)
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Update fields
    if request.project_title is not None:
        session.project_title = request.project_title
    if request.project_description is not None:
        session.project_description = request.project_description
    
    await db.commit()
    await db.refresh(session)
    
    # Get file count
    file_count_result = await db.execute(
        select(func.count(GeneratedFile.id))
        .where(GeneratedFile.session_id == session.id)
    )
    file_count = file_count_result.scalar()
    
    return format_project(session, file_count)


@router.delete("/project/{session_id}", response_model=DeleteProjectResponse)
async def delete_project(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_user_from_clerk_header)
):
    """Delete a project and reclaim storage quota."""
    try:
        session_uuid = uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID")
    
    # Get session and verify ownership
    result = await db.execute(
        select(DBSession)
        .where(DBSession.id == session_uuid)
        .where(DBSession.user_id == user.id)
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Calculate storage to reclaim
    storage_used = session.total_size_bytes or 0
    
    # Delete files from R2
    try:
        from app.services.storage_service import storage_service
        await storage_service.delete_session_files(db, session_uuid)
    except Exception as e:
        logger.warning(f"Failed to delete R2 files for session {session_uuid}: {e}")
    
    # Delete session (cascades to files, messages, etc.)
    await db.delete(session)
    
    # Update user's storage quota
    await storage_quota_service.update_user_quota(db, user.id, -storage_used)
    
    await db.commit()
    
    return DeleteProjectResponse(
        success=True,
        message=f"Project '{session.display_title}' deleted successfully",
        storage_reclaimed_bytes=storage_used,
        storage_reclaimed_mb=f"{storage_quota_service.bytes_to_mb(storage_used):.2f}"
    )


@router.get("/recent", response_model=List[ProjectResponse])
async def get_recent_projects(
    limit: int = Query(5, ge=1, le=10, description="Number of recent projects"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_user_from_clerk_header)
):
    """Get recently updated projects."""
    result = await db.execute(
        select(DBSession)
        .where(DBSession.user_id == user.id)
        .order_by(desc(DBSession.updated_at))
        .limit(limit)
    )
    sessions = result.scalars().all()
    
    projects = []
    for session in sessions:
        file_count_result = await db.execute(
            select(func.count(GeneratedFile.id))
            .where(GeneratedFile.session_id == session.id)
        )
        file_count = file_count_result.scalar()
        projects.append(format_project(session, file_count))
    
    return projects
