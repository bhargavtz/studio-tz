"""
NCD INAI - Deploy Router
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import io

from app.services.session_manager import session_manager
from app.services.file_manager import file_manager
from app.config import settings

router = APIRouter()


class DownloadResponse(BaseModel):
    session_id: str
    filename: str
    size_bytes: int


@router.get("/download/{session_id}")
async def download_project(session_id: str):
    """Download the project as a ZIP file."""
    session = session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if not session.files_generated:
        raise HTTPException(
            status_code=400,
            detail="Website not generated yet."
        )
    
    # Create ZIP
    zip_bytes = file_manager.create_zip(session_id)
    
    # Get project name for filename
    project_name = "website"
    if session.blueprint:
        project_name = session.blueprint.get("name", "website").lower().replace(" ", "_")
    
    return StreamingResponse(
        io.BytesIO(zip_bytes),
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename={project_name}.zip"
        }
    )


class PreviewUrlResponse(BaseModel):
    session_id: str
    preview_url: str
    full_url: str


@router.get("/preview-url/{session_id}", response_model=PreviewUrlResponse)
async def get_public_preview_url(session_id: str):
    """Get the public preview URL for the website."""
    session = session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if not session.files_generated:
        raise HTTPException(
            status_code=400,
            detail="Website not generated yet."
        )
    
    preview_path = file_manager.get_preview_url(session_id)
    full_url = f"http://{settings.host}:{settings.port}{preview_path}"
    
    return PreviewUrlResponse(
        session_id=session_id,
        preview_url=preview_path,
        full_url=full_url
    )


class ProjectFilesResponse(BaseModel):
    session_id: str
    files: list
    total_files: int


@router.get("/project-files/{session_id}", response_model=ProjectFilesResponse)
async def list_project_files(session_id: str):
    """List all files in the project."""
    session = session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    files = file_manager.list_files(
        session_id,
        extensions=[".html", ".css", ".js", ".json"]
    )
    
    return ProjectFilesResponse(
        session_id=session_id,
        files=files,
        total_files=len(files)
    )
