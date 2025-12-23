"""
NCD INAI - Website Models
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class GeneratedFile(BaseModel):
    """Generated website file."""
    path: str
    content: str
    file_type: str  # html, css, js


class WebsiteGenerationResult(BaseModel):
    """Result of website generation."""
    session_id: str
    success: bool
    files: list[GeneratedFile] = Field(default_factory=list)
    preview_url: Optional[str] = None
    message: str

class EditRequest(BaseModel):
    """Request to edit a website element."""
    edit_type: str = Field(..., description="Type of edit: text, style, layout, add, remove")
    selector: Optional[str] = Field(None, description="CSS selector for the element")
    file_path: Optional[str] = Field(None, description="Path to the file to edit")
    instruction: str = Field(..., description="Natural language edit instruction")
    value: Optional[Any] = Field(None, description="New value for direct edits")


class EditResult(BaseModel):
    """Result of an edit operation."""
    success: bool
    file_path: str
    changes_made: str
    preview_url: str
    rollback_id: Optional[str] = None
