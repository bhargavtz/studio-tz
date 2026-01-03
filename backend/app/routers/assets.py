"""
NCD INAI - Assets Router

Handles image upload and asset management via R2 and Database.
"""

from typing import List, Dict
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from pydantic import BaseModel
from pathlib import Path
from uuid import UUID

from app.services.new_session_service import SessionService
from app.infrastructure.storage.file_store import UnifiedFileStore
from app.api.dependencies import get_session_service, get_file_store
from app.core.exceptions import ValidationError

router = APIRouter()


class AssetResponse(BaseModel):
    success: bool
    filename: str
    url: str
    size: int


class AssetsListResponse(BaseModel):
    assets: List[dict]


@router.post("/assets/{session_id}/upload", response_model=AssetResponse)
async def upload_asset(
    session_id: str, 
    file: UploadFile = File(...),
    session_service: SessionService = Depends(get_session_service),
    file_store: UnifiedFileStore = Depends(get_file_store)
):
    """Upload an image or asset file to Cloud Storage."""
    # Validate session UUID
    try:
        session_uuid = UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID")
        
    session = await session_service.get_session(session_uuid)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Validate file type
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.ico'}
    file_ext = Path(file.filename).suffix.lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file_ext} not allowed. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Read file content
    content = await file.read()
    
    # Save to R2 via UnifiedFileStore
    try:
        file_info = await file_store.save_file(
            session_id=session_uuid,
            filename=f"assets/{file.filename}",  # Store in assets/ folder
            content=content,
            file_type="image",
            user_id=session.user_id
        )
        
        return AssetResponse(
            success=True,
            filename=file.filename,
            url=file_info['r2_url'],
            size=file_info['size_bytes']
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/assets/{session_id}", response_model=AssetsListResponse)
async def list_assets(
    session_id: str,
    session_service: SessionService = Depends(get_session_service),
    file_store: UnifiedFileStore = Depends(get_file_store)
):
    """List all uploaded assets."""
    try:
        session_uuid = UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID")
        
    session = await session_service.get_session(session_uuid)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    files = await file_store.list_session_files(session_uuid)
    
    # Filter only assets (images)
    assets = []
    for f in files:
        # Check if it's an image or in assets folder
        is_asset = f['filename'].startswith('assets/') or f.get('file_type') == 'image'
        
        if is_asset:
            clean_filename = f['filename'].replace('assets/', '')
            assets.append({
                "filename": clean_filename,
                "url": f['r2_url'],
                "size": f['size_bytes'],
                "type": Path(clean_filename).suffix.lstrip('.') if '.' in clean_filename else 'unknown'
            })
    
    return AssetsListResponse(assets=assets)


@router.delete("/assets/{session_id}/{filename}")
async def delete_asset(
    session_id: str, 
    filename: str,
    session_service: SessionService = Depends(get_session_service),
    file_store: UnifiedFileStore = Depends(get_file_store)
):
    """Delete an uploaded asset."""
    try:
        session_uuid = UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID")
        
    session = await session_service.get_session(session_uuid)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Try deleting with assets/ prefix
    success = await file_store.delete_file(
        session_id=session_uuid,
        filename=f"assets/{filename}",
        user_id=session.user_id
    )
    
    if not success:
         # Try without prefix just in case
         success = await file_store.delete_file(
            session_id=session_uuid,
            filename=filename,
            user_id=session.user_id
        )
    
    if not success:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    return {
        "success": True,
        "message": f"Asset {filename} deleted"
    }


class ImageGenerationRequest(BaseModel):
    prompt: str
    filename: str


@router.post("/assets/{session_id}/generate")
async def generate_image(session_id: str, request: ImageGenerationRequest):
    """Generate an image using AI (placeholder - requires image generation API)."""
    # Placeholder remains same as before until Image Service is ready
    return {
        "success": False,
        "message": "Image generation requires API integration (DALL-E, Stable Diffusion, etc.)",
        "prompt": request.prompt,
        "filename": request.filename
    }
