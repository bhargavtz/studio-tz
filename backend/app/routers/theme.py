"""
NCD INAI - Theme Router

Handles theme customization.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.session_manager import session_manager
from app.services.file_manager import file_manager
from app.services.safe_edit_engine import safe_edit_engine

router = APIRouter()


class ThemeColors(BaseModel):
    primaryColor: Optional[str] = None
    secondaryColor: Optional[str] = None
    backgroundColor: Optional[str] = None
    textColor: Optional[str] = None
    accentColor: Optional[str] = None


class ThemeUpdate(BaseModel):
    colors: Optional[ThemeColors] = None
    fontFamily: Optional[str] = None
    style: Optional[str] = None


class ThemeResponse(BaseModel):
    success: bool
    theme: dict
    preview_url: str


@router.get("/theme/{session_id}")
async def get_theme(session_id: str):
    """Get current theme."""
    session = session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if not session.blueprint:
        raise HTTPException(status_code=400, detail="Blueprint not generated yet")
    
    theme = session.blueprint.get("theme", {})
    
    return {
        "session_id": session_id,
        "theme": theme
    }


@router.post("/theme/{session_id}", response_model=ThemeResponse)
async def update_theme(session_id: str, theme_update: ThemeUpdate):
    """Update theme colors and styles."""
    session = session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if not session.files_generated:
        raise HTTPException(status_code=400, detail="Website not generated yet")
    
    session_dir = file_manager.get_session_path(session_id)
    css_file = session_dir / "styles" / "main.css"
    
    # Read current CSS
    css_content = file_manager.read_file(session_id, "styles/main.css")
    if not css_content:
        raise HTTPException(status_code=404, detail="CSS file not found")
    
    # Update CSS variables
    import re
    
    if theme_update.colors:
        colors = theme_update.colors.dict(exclude_none=True)
        
        for var_name, color_value in colors.items():
            # Convert camelCase to kebab-case
            css_var = var_name.replace('Color', '').lower()
            if css_var == 'background':
                css_var = 'background'
            elif css_var == 'text':
                css_var = 'text'
            else:
                css_var = css_var
            
            # Map to CSS variable names
            var_map = {
                'primary': '--primary',
                'secondary': '--secondary',
                'background': '--background',
                'text': '--text',
                'accent': '--accent'
            }
            
            css_variable = var_map.get(css_var)
            if css_variable:
                # Update in :root
                pattern = rf'({re.escape(css_variable)}:\s*)[^;]+;'
                replacement = rf'\g<1>{color_value};'
                css_content = re.sub(pattern, replacement, css_content)
    
    if theme_update.fontFamily:
        pattern = r'(--font-family:\s*)[^;]+;'
        replacement = rf"\g<1>'{theme_update.fontFamily}', sans-serif;"
        css_content = re.sub(pattern, replacement, css_content)
    
    # Write updated CSS
    file_manager.write_file(session_id, "styles/main.css", css_content)
    
    # Update blueprint
    if not session.blueprint.get("theme"):
        session.blueprint["theme"] = {}
    
    if theme_update.colors:
        session.blueprint["theme"].update(theme_update.colors.dict(exclude_none=True))
    
    if theme_update.fontFamily:
        session.blueprint["theme"]["fontFamily"] = theme_update.fontFamily
    
    if theme_update.style:
        session.blueprint["theme"]["style"] = theme_update.style
    
    session_manager.update_session(session)
    
    return ThemeResponse(
        success=True,
        theme=session.blueprint["theme"],
        preview_url=file_manager.get_preview_url(session_id)
    )


@router.get("/theme/{session_id}/presets")
async def get_theme_presets():
    """Get predefined theme presets."""
    presets = [
        {
            "name": "Ocean Blue",
            "colors": {
                "primaryColor": "#0ea5e9",
                "secondaryColor": "#0284c7",
                "backgroundColor": "#ffffff",
                "textColor": "#1e293b",
                "accentColor": "#06b6d4"
            },
            "fontFamily": "Inter",
            "style": "modern"
        },
        {
            "name": "Forest Green",
            "colors": {
                "primaryColor": "#10b981",
                "secondaryColor": "#059669",
                "backgroundColor": "#ffffff",
                "textColor": "#1f2937",
                "accentColor": "#34d399"
            },
            "fontFamily": "Inter",
            "style": "natural"
        },
        {
            "name": "Sunset Orange",
            "colors": {
                "primaryColor": "#f59e0b",
                "secondaryColor": "#d97706",
                "backgroundColor": "#ffffff",
                "textColor": "#1f2937",
                "accentColor": "#fbbf24"
            },
            "fontFamily": "Poppins",
            "style": "vibrant"
        },
        {
            "name": "Royal Purple",
            "colors": {
                "primaryColor": "#8b5cf6",
                "secondaryColor": "#7c3aed",
                "backgroundColor": "#ffffff",
                "textColor": "#1f2937",
                "accentColor": "#a78bfa"
            },
            "fontFamily": "Outfit",
            "style": "elegant"
        },
        {
            "name": "Dark Mode",
            "colors": {
                "primaryColor": "#6366f1",
                "secondaryColor": "#4f46e5",
                "backgroundColor": "#0f172a",
                "textColor": "#f1f5f9",
                "accentColor": "#818cf8"
            },
            "fontFamily": "Inter",
            "style": "dark"
        }
    ]
    
    return {"presets": presets}
