"""
NCD INAI - Edit Router (Surgical Edit System)
"""

from typing import Optional, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from bs4 import BeautifulSoup

from app.services.session_manager import session_manager
from app.services.file_manager import file_manager
from app.services.component_registry import ComponentRegistry
from app.services.edit_history import EditHistory
from app.services.safe_edit_engine import safe_edit_engine
from app.models.session import SessionStatus
from app.agents.editor import editor_planner

router = APIRouter()


class StructuredEditRequest(BaseModel):
    """Structured edit request with NCD ID."""
    ncd_id: str
    instruction: str
    current_value: Optional[str] = None


class EditResponse(BaseModel):
    success: bool
    ncd_id: str
    action: str
    changes_description: str
    preview_url: str
    version: int


@router.post("/edit/{session_id}/structured", response_model=EditResponse)
async def structured_edit(session_id: str, request: StructuredEditRequest):
    """Apply a structured edit using NCD ID."""
    session = session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if not session.files_generated:
        raise HTTPException(
            status_code=400,
            detail="Website not generated yet."
        )
    
    # Get session directory
    session_dir = file_manager.get_session_path(session_id)
    
    # Initialize registry and history
    registry = ComponentRegistry(session_dir)
    history = EditHistory(session_dir)
    
    # Get component info
    component = registry.get(request.ncd_id)
    if not component:
        raise HTTPException(
            status_code=404,
            detail=f"Component {request.ncd_id} not found in registry"
        )
    
    # Get current value if not provided
    current_value = request.current_value or ""
    if not current_value and component["edit_type"] == "text":
        # Read from file
        file_content = file_manager.read_file(session_id, component["file"])
        if file_content:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(file_content, 'html.parser')
            element = soup.find(attrs={"data-ncd-id": request.ncd_id})
            if element:
                current_value = element.get_text(strip=True)
    
    # Plan the edit using AI
    edit_plan = await editor_planner.plan_edit(
        ncd_id=request.ncd_id,
        file_path=component["file"],
        element_type=component["type"],
        current_value=current_value,
        instruction=request.instruction
    )
    
    # Execute the edit using safe engine
    file_path = session_dir / component["file"]
    action = edit_plan.get("action")
    params = edit_plan.get("parameters", {})
    
    try:
        if action == "UPDATE_TEXT":
            result = safe_edit_engine.update_html_text(
                file_path,
                request.ncd_id,
                params.get("new_text", "")
            )
            
            # Save to history
            version = history.save_diff(
                file_path=component["file"],
                ncd_id=request.ncd_id,
                before=result["old_value"],
                after=result["new_value"],
                edit_type="text"
            )
        
        elif action == "UPDATE_STYLE":
            # Determine CSS file
            css_file = session_dir / "styles/main.css"
            result = safe_edit_engine.update_css_property(
                css_file,
                request.ncd_id,
                params.get("property", ""),
                params.get("value", "")
            )
            
            version = history.save_diff(
                file_path="styles/main.css",
                ncd_id=request.ncd_id,
                before=result["old_value"],
                after=result["new_value"],
                edit_type="style"
            )
        
        elif action == "UPDATE_ATTRIBUTE":
            result = safe_edit_engine.update_html_attribute(
                file_path,
                request.ncd_id,
                params.get("attribute", ""),
                params.get("value", "")
            )
            
            version = history.save_diff(
                file_path=component["file"],
                ncd_id=request.ncd_id,
                before=result["old_value"],
                after=result["new_value"],
                edit_type="attribute"
            )
        
        elif action == "ADD_CLASS":
            result = safe_edit_engine.add_html_class(
                file_path,
                request.ncd_id,
                params.get("class_name", "")
            )
            
            version = history.save_diff(
                file_path=component["file"],
                ncd_id=request.ncd_id,
                before="",
                after=params.get("class_name", ""),
                edit_type="add_class"
            )
        
        elif action == "REMOVE_CLASS":
            result = safe_edit_engine.remove_html_class(
                file_path,
                request.ncd_id,
                params.get("class_name", "")
            )
            
            version = history.save_diff(
                file_path=component["file"],
                ncd_id=request.ncd_id,
                before=params.get("class_name", ""),
                after="",
                edit_type="remove_class"
            )
        
        else:
            raise ValueError(f"Unknown action: {action}")
        
        # Update session status
        session.status = SessionStatus.EDITING
        session_manager.update_session(session)
        
        return EditResponse(
            success=True,
            ncd_id=request.ncd_id,
            action=action,
            changes_description=edit_plan.get("reasoning", "Edit applied"),
            preview_url=file_manager.get_preview_url(session_id),
            version=version
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Edit failed: {str(e)}"
        )


class RollbackRequest(BaseModel):
    version: int


class RollbackResponse(BaseModel):
    success: bool
    message: str
    current_version: int


@router.post("/edit/{session_id}/rollback", response_model=RollbackResponse)
async def rollback_edit(session_id: str, request: RollbackRequest):
    """Rollback to a previous version."""
    session = session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session_dir = file_manager.get_session_path(session_id)
    history = EditHistory(session_dir)
    
    try:
        # Get diffs to reverse
        diffs_to_reverse = history.rollback_to(request.version)
        
        # Apply each diff in reverse
        for diff in diffs_to_reverse:
            file_path = session_dir / diff["file"]
            ncd_id = diff["ncd_id"]
            
            if diff["edit_type"] == "text":
                safe_edit_engine.update_html_text(
                    file_path,
                    ncd_id,
                    diff["before"]
                )
            elif diff["edit_type"] == "style":
                css_file = session_dir / "styles" / "main.css"
                # Extract property from diff metadata
                safe_edit_engine.update_css_property(
                    css_file,
                    ncd_id,
                    diff.get("property", ""),
                    diff["before"] or ""
                )
        
        history.current_version = request.version
        
        return RollbackResponse(
            success=True,
            message=f"Rolled back to version {request.version}",
            current_version=request.version
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Rollback failed: {str(e)}"
        )


class HistoryResponse(BaseModel):
    versions: list
    current_version: int


@router.get("/edit/{session_id}/history", response_model=HistoryResponse)
async def get_edit_history(session_id: str, limit: int = 20):
    """Get edit history."""
    session = session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session_dir = file_manager.get_session_path(session_id)
    history = EditHistory(session_dir)
    
    versions = history.get_history(limit=limit)
    
    return HistoryResponse(
        versions=versions,
        current_version=history.current_version
    )


# Keep old chat endpoint for backward compatibility
class ChatEditRequest(BaseModel):
    message: str


class ChatEditResponse(BaseModel):
    success: bool
    changes: list
    message: str
    preview_url: str


@router.post("/edit/{session_id}/chat", response_model=ChatEditResponse)
async def chat_edit(session_id: str, request: ChatEditRequest):
    """Apply ANY edits via natural language - add sections, images, change layout, anything!"""
    session = session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if not session.files_generated:
        raise HTTPException(
            status_code=400,
            detail="Website not generated yet."
        )
    
    try:
        from app.services.advanced_groq_editor import advanced_editor
        
        # Get current files
        html_content = file_manager.read_file(session_id, "index.html") or ""
        css_content = file_manager.read_file(session_id, "styles.css") or ""
        
        print(f"User request: {request.message}")
        
        # Use Advanced AI to modify entire website
        result = await advanced_editor.modify_website(
            user_request=request.message,
            current_html=html_content,
            current_css=css_content
        )
        
        if not result['success']:
            return ChatEditResponse(
                success=False,
                changes=[],
                message=result['message'],
                preview_url=file_manager.get_preview_url(session_id)
            )
        
        # Save modified files
        changes = []
        
        # Save HTML
        file_manager.write_file(session_id, "index.html", result['html'])
        changes.append({
            "file": "index.html",
            "change_type": "modified",
            "description": "Updated HTML based on AI modifications"
        })
        
        # Save CSS if extracted
        if result.get('css'):
            file_manager.write_file(session_id, "styles.css", result['css'])
            changes.append({
                "file": "styles.css",
                "change_type": "modified",
                "description": "Updated CSS styles"
            })
        
        success_message = f"✓ {result['description']}\n\n{result['message']}"
        
        return ChatEditResponse(
            success=True,
            changes=changes,
            message=success_message,
            preview_url=file_manager.get_preview_url(session_id)
        )
        
    except Exception as e:
        print(f"Chat edit error: {e}")
        import traceback
        traceback.print_exc()
        return ChatEditResponse(
            success=False,
            changes=[],
            message=f"Error: {str(e)}",
            preview_url=file_manager.get_preview_url(session_id)
        )
