"""
NCD INAI - Generate Router
"""

from typing import List
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from app.services.session_manager import session_manager
from app.services.file_manager import file_manager
from app.models.session import SessionStatus
from app.agents.code_generator import code_generator
from app.agents.validator import validator

router = APIRouter()


class GenerateResponse(BaseModel):
    session_id: str
    success: bool
    files: List[str]
    preview_url: str
    message: str


class ValidationResult(BaseModel):
    valid: bool
    errors: dict


@router.post("/generate/{session_id}", response_model=GenerateResponse)
async def generate_website(session_id: str):
    """Generate website files from the confirmed blueprint."""
    session = session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if not session.blueprint_confirmed:
        raise HTTPException(
            status_code=400,
            detail="Blueprint not confirmed yet."
        )
    
    # Generate code
    code = await code_generator.generate(session.blueprint)
    
    # Validate code
    validation = validator.validate_all(
        code.get("html", ""),
        code.get("css", ""),
        code.get("js", "")
    )
    
    # Safety: Enforce correct paths in HTML
    import re
    if "html" in code:
        # Fix CSS link
        code["html"] = re.sub(
            r'<link[^>]+href=["\'](?!styles/main\.css)[^"\']+\.css["\'][^>]*>',
            '<link rel="stylesheet" href="styles/main.css">',
            code["html"]
        )
        # Fix JS script
        code["html"] = re.sub(
            r'<script[^>]+src=["\'](?!scripts/main\.js)[^"\']+\.js["\'][^>]*>.*?</script>',
            '<script src="scripts/main.js"></script>',
            code["html"],
            flags=re.DOTALL
        )
        # Fix asset paths (remove leading slash)
        code["html"] = re.sub(
            r'src=["\']/(assets/)',
            r'src="\1',
            code["html"]
        )
        
        # Fix navigation links (convert /page to page.html)
        # Match href="/something" but not href="/" or href="#" or external URLs
        def fix_nav_link(match):
            path = match.group(1)
            # Skip if it's root, anchor, external URL, or already has an extension
            if (path == "/" or 
                path.startswith("#") or 
                path.startswith("http") or
                path.endswith((".css", ".js", ".jpg", ".png", ".gif", ".svg", ".webp", ".ico", ".pdf"))):
                return match.group(0)
            # Remove leading slash and add .html if not present
            clean_path = path.lstrip("/")
            if not clean_path.endswith(".html"):
                clean_path += ".html"
            return f'href="{clean_path}"'
        
        code["html"] = re.sub(
            r'href=["\']([^"\']+)["\']',
            fix_nav_link,
            code["html"]
        )
    
    # Generate multi-page if needed
    from app.services.multi_page_generator import multi_page_generator
    from app.services.component_registry import ComponentRegistry
    from bs4 import BeautifulSoup
    
    session_dir = file_manager.get_session_path(session_id)
    registry = ComponentRegistry(session_dir)
    
    pages = multi_page_generator.generate_pages(
        blueprint=session.blueprint,
        base_html=code.get("html", ""),
        base_css=code.get("css", ""),
        base_js=code.get("js", "")
    )
    
    # Write files
    files_written = []
    
    # Write all HTML pages
    for filename, html_content in pages.items():
        file_manager.write_file(session_id, filename, html_content)
        files_written.append(filename)
        
        # Register components from this page
        soup = BeautifulSoup(html_content, 'html.parser')
        for element in soup.find_all(attrs={"data-ncd-id": True}):
            ncd_id = element.get("data-ncd-id")
            file_path = element.get("data-ncd-file", filename)
            edit_type = element.get("data-ncd-type", "element")
            
            registry.register(
                ncd_id=ncd_id,
                file_path=file_path,
                element_type=element.name,
                edit_type=edit_type,
                selector=f'[data-ncd-id="{ncd_id}"]',
                metadata={
                    "tag": element.name,
                    "classes": element.get("class", [])
                }
            )
    
    # CSS
    file_manager.write_file(session_id, "styles/main.css", code.get("css", "/* No CSS generated */"))
    files_written.append("styles/main.css")
    
    # JavaScript
    file_manager.write_file(session_id, "scripts/main.js", code.get("js", "// No JavaScript generated"))
    files_written.append("scripts/main.js")
    
    # Update session
    session.files_generated = files_written
    session.status = SessionStatus.WEBSITE_GENERATED
    session_manager.update_session(session)
    
    preview_url = file_manager.get_preview_url(session_id)
    
    return GenerateResponse(
        session_id=session.id,
        success=True,
        files=files_written,
        preview_url=preview_url,
        message="Website generated successfully!"
    )


@router.get("/preview/{session_id}")
async def get_preview_url(session_id: str):
    """Get the preview URL for a generated website."""
    session = session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if not session.files_generated:
        raise HTTPException(
            status_code=400,
            detail="Website not generated yet."
        )
    
    return {
        "session_id": session_id,
        "preview_url": file_manager.get_preview_url(session_id),
        "files": session.files_generated
    }


@router.get("/files/{session_id}/{file_path:path}")
async def get_file_content(session_id: str, file_path: str):
    """Get the content of a specific file."""
    session = session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    content = file_manager.read_file(session_id, file_path)
    
    if content is None:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Determine file type
    if file_path.endswith(".html"):
        file_type = "html"
    elif file_path.endswith(".css"):
        file_type = "css"
    elif file_path.endswith(".js"):
        file_type = "javascript"
    else:
        file_type = "text"
    
    return {
        "file_path": file_path,
        "file_type": file_type,
        "content": content
    }


@router.get("/validate/{session_id}", response_model=ValidationResult)
async def validate_website(session_id: str):
    """Validate the generated website code."""
    session = session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    html = file_manager.read_file(session_id, "index.html") or ""
    css = file_manager.read_file(session_id, "styles/main.css") or ""
    js = file_manager.read_file(session_id, "scripts/main.js") or ""
    
    result = validator.validate_all(html, css, js)
    
    return ValidationResult(
        valid=result["valid"],
        errors=result
    )
