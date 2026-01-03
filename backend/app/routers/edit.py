"""
NCD INAI - Edit Router (Surgical Edit System)
Migrated to UnifiedFileStore (Cloud Native)
"""

import logging
import json
from typing import Optional, Any, List
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from uuid import UUID

from app.services.new_session_service import SessionService
from app.infrastructure.storage.file_store import UnifiedFileStore
from app.api.dependencies import get_session_service, get_file_store
from app.services.safe_edit_engine import safe_edit_engine
from app.agents.editor import editor_planner
from app.database.models import SessionStatus

router = APIRouter()
logger = logging.getLogger(__name__)


class StructuredEditRequest(BaseModel):
    """Structured edit request with NCD ID."""
    ncd_id: str
    instruction: str
    current_value: Optional[str] = None


class ManualEditRequest(BaseModel):
    """Manual file edit request."""
    edit_type: str
    file_path: str
    selector: Optional[str] = None
    instruction: str
    value: Optional[Any] = None


class EditResponse(BaseModel):
    success: bool
    ncd_id: str
    action: str
    changes_description: str
    preview_url: str
    version: int


@router.post("/edit/{session_id}", response_model=EditResponse)
async def apply_manual_edit(
    session_id: str, 
    request: ManualEditRequest,
    session_service: SessionService = Depends(get_session_service),
    file_store: UnifiedFileStore = Depends(get_file_store)
):
    """Apply a manual direct edit to a file."""
    # Validate UUID
    try:
        session_uuid = UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID")
        
    session = await session_service.get_session(session_uuid)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # For manual edits, the value should contain the new content
    if request.edit_type != "manual":
        raise HTTPException(
            status_code=400,
            detail="This endpoint only supports manual edits. Use /structured for AI-assisted edits."
        )

    if not request.value or not isinstance(request.value, str):
        raise HTTPException(
            status_code=400,
            detail="Manual edits require a 'value' containing the new file content as a string."
        )

    # Save the new content directly to R2
    # Ensure correct file type mapping
    file_type = "text"
    if request.file_path.endswith('.html'): file_type = "html"
    elif request.file_path.endswith('.css'): file_type = "css"
    elif request.file_path.endswith('.js'): file_type = "javascript"
    
    try:
        file_info = await file_store.save_file(
            session_id=session_uuid,
            filename=request.file_path,
            content=request.value,
            file_type=file_type,
            user_id=session.user_id
        )
        
        # Update session status
        await session_service.update_session(session_uuid, status=SessionStatus.EDITING.value)

        return EditResponse(
            success=True,
            ncd_id="manual",
            action="OVERWRITE",
            changes_description=f"Manual edit to {request.file_path}",
            preview_url=file_info['r2_url'],
            version=0 # Versioning temporarily disabled
        )
    except Exception as e:
        logger.error(f"Manual edit failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/edit/{session_id}/structured", response_model=EditResponse)
async def structured_edit(
    session_id: str, 
    request: StructuredEditRequest,
    session_service: SessionService = Depends(get_session_service),
    file_store: UnifiedFileStore = Depends(get_file_store)
):
    """Apply a structured edit using NCD ID."""
    try:
        session_uuid = UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID")
        
    session = await session_service.get_session(session_uuid)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # We need to find which file contains this NCD ID.
    # In the legacy systems, we had a component registry.
    # For now, we'll assume it's in index.html unless specified otherwise,
    # or we should search all HTML files. 
    # To keep it simple for this migration: check index.html first.
    
    target_file = "index.html"
    content_bytes = await file_store.get_file(session_uuid, target_file)
    
    if not content_bytes:
        raise HTTPException(status_code=404, detail="index.html not found")
        
    content_str = content_bytes.decode('utf-8') if isinstance(content_bytes, bytes) else content_bytes
    
    # Get current value if not provided
    current_value = request.current_value or ""
    # We could extract it from new content_str similarly to legacy code
    # But let's proceed to planning.
    
    # Plan the edit using AI
    # Note: component["type"] and "file" are missing because we don't have the registry.
    # We'll infer type as 'unknown' for now.
    
    edit_plan = await editor_planner.plan_edit(
        ncd_id=request.ncd_id,
        file_path=target_file,
        element_type="unknown", 
        current_value=current_value,
        instruction=request.instruction
    )
    
    # Execute the edit using safe engine
    action = edit_plan.get("action")
    params = edit_plan.get("parameters", {})
    
    result = None
    updated_content = None
    changes_desc = edit_plan.get("reasoning", "Edit applied")
    
    try:
        if action == "UPDATE_TEXT":
            result = safe_edit_engine.update_html_text(
                content_str,
                request.ncd_id,
                params.get("new_text", "")
            )
            updated_content = result["content"]
            
        elif action == "UPDATE_STYLE":
            # For styles, we might need to edit CSS or HTML style block
            # If the engine supports CSS editing, we verify file type.
            # safe_edit_engine.update_css_property now handles CSS content string
            
            # If target is CSS file
            css_file = "styles/main.css"
            css_bytes = await file_store.get_file(session_uuid, css_file)
            
            if css_bytes:
                css_str = css_bytes.decode('utf-8') if isinstance(css_bytes, bytes) else css_bytes
                result = safe_edit_engine.update_css_property(
                    css_str,
                    request.ncd_id,
                    params.get("property", ""),
                    params.get("value", "")
                )
                
                # Save CSS
                await file_store.save_file(
                    session_id=session_uuid,
                    filename=css_file,
                    content=result["content"],
                    file_type="css",
                    user_id=session.user_id
                )
                
                return EditResponse(
                    success=True,
                    ncd_id=request.ncd_id,
                    action=action,
                    changes_description=changes_desc,
                    preview_url=(await file_store.get_file_url(session_uuid, target_file)) or "",
                    version=0
                )
            else:
                # Fallback to HTML style block if supported by engine
                # For now, simplistic fallback:
                raise HTTPException(status_code=400, detail="CSS file not found for style update")

        elif action == "UPDATE_ATTRIBUTE":
            result = safe_edit_engine.update_html_attribute(
                content_str,
                request.ncd_id,
                params.get("attribute", ""),
                params.get("value", "")
            )
            updated_content = result["content"]

        elif action == "ADD_CLASS":
            result = safe_edit_engine.add_html_class(
                content_str,
                request.ncd_id,
                params.get("class_name", "")
            )
            updated_content = result["content"]

        elif action == "REMOVE_CLASS":
            result = safe_edit_engine.remove_html_class(
                content_str,
                request.ncd_id,
                params.get("class_name", "")
            )
            updated_content = result["content"]
            
        else:
             raise ValueError(f"Unknown action: {action}")
             
        # Save updated HTML
        if updated_content:
            file_info = await file_store.save_file(
                session_id=session_uuid,
                filename=target_file,
                content=updated_content,
                file_type="html",
                user_id=session.user_id
            )
            
            await session_service.update_session(session_uuid, status=SessionStatus.EDITING.value)
            
            return EditResponse(
                success=True,
                ncd_id=request.ncd_id,
                action=action,
                changes_description=changes_desc,
                preview_url=file_info['r2_url'],
                version=0
            )
            
        raise HTTPException(status_code=500, detail="No content updated")

    except Exception as e:
        logger.error(f"Structured edit failed: {e}")
        raise HTTPException(status_code=500, detail=f"Edit failed: {str(e)}")


class ChatEditRequest(BaseModel):
    message: str


class ChatEditResponse(BaseModel):
    success: bool
    changes: list
    message: str
    preview_url: str


@router.post("/edit/{session_id}/chat", response_model=ChatEditResponse)
async def chat_edit(
    session_id: str, 
    request: ChatEditRequest,
    session_service: SessionService = Depends(get_session_service),
    file_store: UnifiedFileStore = Depends(get_file_store)
):
    """Apply ANY edits via natural language."""
    try:
        session_uuid = UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID")
        
    session = await session_service.get_session(session_uuid)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    try:
        from app.services.surgical_groq_editor import surgical_editor
        
        # Read HTML and CSS
        html_bytes = await file_store.get_file(session_uuid, "index.html")
        css_bytes = await file_store.get_file(session_uuid, "styles/main.css")
        
        html_content = html_bytes.decode('utf-8') if html_bytes else ""
        css_content = css_bytes.decode('utf-8') if css_bytes else ""
        
        # Use Surgical AI
        result = await surgical_editor.modify_website(
            user_request=request.message,
            current_html=html_content,
            current_css=css_content
        )
        
        if not result['success']:
             # In case of failure, check if we have a preview URL to return
            preview_url = await file_store.get_file_url(session_uuid, "index.html")
            return ChatEditResponse(
                success=False,
                changes=[],
                message=result['message'],
                preview_url=preview_url or ""
            )
            
        # Save modified files
        changes = []
        preview_url = ""
        
        # Save HTML
        if result.get('html') and result['html'] != html_content:
            file_info = await file_store.save_file(
                session_id=session_uuid,
                filename="index.html",
                content=result['html'],
                file_type="html",
                user_id=session.user_id
            )
            changes.append({
                "file": "index.html",
                "change_type": "modified",
                "description": "Updated HTML"
            })
            preview_url = file_info['r2_url']
            
        # Save CSS
        if result.get('css') and result['css'] != css_content:
            await file_store.save_file(
                session_id=session_uuid,
                filename="styles/main.css",
                content=result['css'],
                file_type="css",
                user_id=session.user_id
            )
            changes.append({
                "file": "styles/main.css",
                "change_type": "modified",
                "description": "Updated CSS"
            })

        await session_service.update_session(session_uuid, status=SessionStatus.EDITING.value)
        
        return ChatEditResponse(
            success=True,
            changes=changes,
            message=result['message'],
            preview_url=preview_url
        )
        
    except Exception as e:
        logger.exception(f"Chat edit failed: {e}")
        # Try getting preview url even on error
        p_url = await file_store.get_file_url(session_uuid, "index.html")
        return ChatEditResponse(
            success=False,
            changes=[],
            message=f"Error: {str(e)}",
            preview_url=p_url or ""
        )


# Backward compatibility stubs for rollback/history
class RollbackRequest(BaseModel):
    version: int

class RollbackResponse(BaseModel):
    success: bool
    message: str
    current_version: int

@router.post("/edit/{session_id}/rollback", response_model=RollbackResponse)
async def rollback_edit(session_id: str, request: RollbackRequest):
    """Rollback - Placeholder."""
    return RollbackResponse(
        success=False,
        message="Versioning temporarily provided via database backups only.",
        current_version=0
    )


class HistoryResponse(BaseModel):
    versions: list
    current_version: int

@router.get("/edit/{session_id}/history", response_model=HistoryResponse)
async def get_edit_history(session_id: str):
    """Get history - Placeholder."""
    return HistoryResponse(
        versions=[],
        current_version=0
    )
