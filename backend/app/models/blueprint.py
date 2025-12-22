"""
NCD INAI - Blueprint Models
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class Component(BaseModel):
    """Individual component within a section."""
    id: str
    type: str = Field(..., description="Component type (e.g., heading, paragraph, image, button)")
    content: Optional[str] = None
    properties: Dict[str, Any] = Field(default_factory=dict)


class Section(BaseModel):
    """Section within a page."""
    id: str
    type: str = Field(..., description="Section type (e.g., hero, features, about, contact)")
    title: Optional[str] = None
    components: List[Component] = Field(default_factory=list)
    properties: Dict[str, Any] = Field(default_factory=dict)


class Page(BaseModel):
    """Page in the website."""
    id: str
    title: str
    slug: str = Field(..., description="URL path for the page")
    sections: List[Section] = Field(default_factory=list)
    meta: Dict[str, str] = Field(default_factory=dict)


class Blueprint(BaseModel):
    """Complete website blueprint."""
    name: str
    description: str
    domain: str
    pages: List[Page] = Field(default_factory=list)
    theme: Dict[str, Any] = Field(default_factory=dict)
    global_styles: Dict[str, Any] = Field(default_factory=dict)


class BlueprintResponse(BaseModel):
    """API response for blueprint."""
    session_id: str
    blueprint: Blueprint
    editable: bool = True
