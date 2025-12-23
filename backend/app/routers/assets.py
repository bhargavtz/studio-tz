"""
NCD INAI - Assets Router

Handles image upload and asset management.
"""

from typing import List
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
import shutil
from pathlib import Path

from app.services.session_manager import session_manager
from app.services.file_manager import file_manager

router = APIRouter()


class AssetResponse(BaseModel):
    success: bool
    filename: str
    url: str
    size: int


class AssetsListResponse(BaseModel):
    assets: List[dict]


@router.post("/assets/{session_id}/upload", response_model=AssetResponse)
async def upload_asset(session_id: str, file: UploadFile = File(...)):
    """Upload an image or asset file."""
    session = session_manager.get_session(session_id)
    
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
    
    # Create assets directory
    session_dir = file_manager.get_session_path(session_id)
    assets_dir = session_dir / "assets"
    assets_dir.mkdir(exist_ok=True)
    
    # Save file
    file_path = assets_dir / file.filename
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    file_size = file_path.stat().st_size
    
    # Generate URL
    asset_url = f"/projects/{session_id}/assets/{file.filename}"
    
    return AssetResponse(
        success=True,
        filename=file.filename,
        url=asset_url,
        size=file_size
    )


@router.get("/assets/{session_id}", response_model=AssetsListResponse)
async def list_assets(session_id: str):
    """List all uploaded assets."""
    session = session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session_dir = file_manager.get_session_path(session_id)
    assets_dir = session_dir / "assets"
    
    if not assets_dir.exists():
        return AssetsListResponse(assets=[])
    
    assets = []
    for file_path in assets_dir.iterdir():
        if file_path.is_file():
            assets.append({
                "filename": file_path.name,
                "url": f"/projects/{session_id}/assets/{file_path.name}",
                "size": file_path.stat().st_size,
                "type": file_path.suffix[1:]  # Remove dot
            })
    
    return AssetsListResponse(assets=assets)


@router.delete("/assets/{session_id}/{filename}")
async def delete_asset(session_id: str, filename: str):
    """Delete an uploaded asset."""
    session = session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session_dir = file_manager.get_session_path(session_id)
    file_path = session_dir / "assets" / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Asset not found")
    
    file_path.unlink()
    
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
    session = session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # This is a placeholder - you would integrate with:
    # - DALL-E API
    # - Stable Diffusion
    # - Midjourney API
    # - Or use the generate_image tool available in the system
    
    return {
        "success": False,
        "message": "Image generation requires API integration (DALL-E, Stable Diffusion, etc.)",
        "prompt": request.prompt,
        "filename": request.filename
    }
