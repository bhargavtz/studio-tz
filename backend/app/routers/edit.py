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
            css_file = session_dir / "styles" / "main.css"
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
    """Apply edits via natural language chat (simplified)."""
    session = session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if not session.files_generated:
        raise HTTPException(
            status_code=400,
            detail="Website not generated yet."
        )
    
    try:
        # Simple pattern matching for common edit requests
        message = request.message.lower()
        changes = []
        
        import re
        
        # Enhanced patterns to match more variations
        patterns = [
            # "update/change the [element] text/color to [value]"
            r"(?:update|change)\s+(?:the\s+)?(.+?)\s+(?:text|color|to)\s+(.+)",
            # "make the [element] [value]"
            r"make\s+(?:the\s+)?(.+?)\s+(.+)",
            # "[element] should be [value]"
            r"(.+?)\s+should\s+be\s+(.+)",
            # "set [element] to [value]"
            r"set\s+(?:the\s+)?(.+?)\s+to\s+(.+)",
        ]
        
        match = None
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                break
        
        if match:
            element_part = match.group(1).strip()
            new_value = match.group(2).strip()
            
            # Enhanced element mapping
            selector_map = {
                "title": "h1",
                "heading": "h1",
                "main title": "h1",
                "main heading": "h1",
                "header": "h1",
                "h1": "h1",
                "button": "button",
                "btn": "button",
                "background": "body",
                "background color": "body",
                "bg": "body",
                "text": "body",
                "body text": "body",
                "paragraph": "p",
                "p": "p",
                "link": "a",
                "links": "a",
            }
            
            # Try to find matching selector
            selector = None
            for key, value in selector_map.items():
                if key in element_part:
                    selector = value
                    break
            
            if not selector:
                selector = element_part  # Use as-is if no match
            
            # Determine edit type based on keywords
            edit_type = "text"
            style_property = None
            
            if any(word in message for word in ["color", "colour"]):
                edit_type = "style"
                style_property = "color"
            elif any(word in message for word in ["background", "bg"]):
                edit_type = "style"
                style_property = "background-color"
            elif "text" not in message or any(word in message for word in ["make", "set"]):
                # If it's "make button red" without "text", assume it's style
                if any(color in new_value for color in ["red", "blue", "green", "yellow", "black", "white", "purple", "orange", "pink", "gray", "grey"]):
                    edit_type = "style"
                    style_property = "background-color"
            
            # Try to apply the edit
            try:
                if edit_type == "style" and style_property:
                    # For style edits, we need to modify CSS or inline styles
                    html_content = file_manager.read_file(session_id, "index.html") or ""
                    
                    # Simple approach: add inline style
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(html_content, 'html.parser')
                    
                    elements = soup.select(selector)
                    if elements:
                        for elem in elements[:1]:  # Apply to first match
                            current_style = elem.get('style', '')
                            # Remove existing property if present
                            style_dict = {}
                            if current_style:
                                for item in current_style.split(';'):
                                    if ':' in item:
                                        key, val = item.split(':', 1)
                                        style_dict[key.strip()] = val.strip()
                            
                            style_dict[style_property] = new_value
                            new_style = '; '.join([f"{k}: {v}" for k, v in style_dict.items()])
                            elem['style'] = new_style
                        
                        # Save modified HTML
                        file_manager.write_file(session_id, "index.html", str(soup))
                        
                        changes.append(FileChange(
                            file="index.html",
                            change_type="modified",
                            description=f"Updated {element_part} {style_property}"
                        ))
                        
                        edit_history.add_edit(
                            session_id=session_id,
                            edit_type="chat",
                            description=request.message,
                            changes=[{"file": "index.html", "type": "modified"}]
                        )
                        
                        return ChatEditResponse(
                            success=True,
                            changes=changes,
                            message=f"✓ Updated the {element_part} {style_property} to {new_value}!",
                            preview_url=file_manager.get_preview_url(session_id)
                        )
                else:
                    # Text edit
                    html_content = file_manager.read_file(session_id, "index.html") or ""
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(html_content, 'html.parser')
                    
                    elements = soup.select(selector)
                    if elements:
                        elements[0].string = new_value
                        file_manager.write_file(session_id, "index.html", str(soup))
                        
                        changes.append(FileChange(
                            file="index.html",
                            change_type="modified",
                            description=f"Updated {element_part} text"
                        ))
                        
                        edit_history.add_edit(
                            session_id=session_id,
                            edit_type="chat",
                            description=request.message,
                            changes=[{"file": "index.html", "type": "modified"}]
                        )
                        
                        return ChatEditResponse(
                            success=True,
                            changes=changes,
                            message=f"✓ Updated the {element_part} to '{new_value}'!",
                            preview_url=file_manager.get_preview_url(session_id)
                        )
                    
            except Exception as e:
                print(f"Edit application error: {e}")
        
        # If we couldn't parse or apply the edit
        return ChatEditResponse(
            success=False,
            changes=[],
            message="I couldn't understand that request. Try:\n• 'Change the heading to Welcome'\n• 'Make the button red'\n• 'Update the title text to My Site'",
            preview_url=file_manager.get_preview_url(session_id)
        )
        
    except Exception as e:
        print(f"Chat edit error: {e}")
        import traceback
        traceback.print_exc()
        return ChatEditResponse(
            success=False,
            changes=[],
            message=f"Sorry, something went wrong. Please try again.",
            preview_url=file_manager.get_preview_url(session_id)
        )
