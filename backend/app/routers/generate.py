"""
NCD INAI - Generate Router (Refactored with New Architecture)
Complete rewrite using SessionService and UnifiedFileStore
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from uuid import UUID
from bs4 import BeautifulSoup
import re
import logging

from app.services.new_session_service import SessionService
from app.infrastructure.storage.file_store import UnifiedFileStore
from app.api.dependencies import get_session_service, get_file_store
from app.agents.code_generator import code_generator
from app.agents.validator import validator
from app.services.multi_page_generator import multi_page_generator
from app.services.enhanced_multipage_generator import enhanced_multi_page_generator
from app.core.exceptions import ValidationError, BlueprintNotFoundError
from app.database.models import SessionStatus

logger = logging.getLogger(__name__)

router = APIRouter()


# ==================== Response Models ====================

class GenerateResponse(BaseModel):
    session_id: str
    success: bool
    files: List[str]
    preview_urls: Dict[str, str]  # Changed to dict of file -> URL
    message: str


class PreviewResponse(BaseModel):
    session_id: str
    preview_urls: Dict[str, str]
    files: List[str]


class FileContentResponse(BaseModel):
    file_path: str
    file_type: str
    content: str


class ValidationResult(BaseModel):
    valid: bool
    errors: dict


# ==================== Helper Functions ====================

def fix_html_structure(html_code: str) -> str:
    """
    Fix HTML structure issues:
    - Ensure correct CSS/JS paths
    - Add Tailwind CDN
    - Fix asset paths
    - Fix navigation links
    """
    soup = BeautifulSoup(html_code, 'html.parser')
    
    # Get head element
    head = soup.find('head')
    if not head:
        logger.warning("No <head> tag found in HTML")
        return html_code
    
    # CRITICAL FIX: Ensure Tailwind CDN script exists
    tailwind_script = soup.find('script', src=re.compile(r'cdn\.tailwindcss\.com'))
    if not tailwind_script:
        new_tailwind = soup.new_tag('script', src='https://cdn.tailwindcss.com')
        last_meta = head.find_all('meta')
        if last_meta:
            last_meta[-1].insert_after(new_tailwind)
        else:
            head.insert(0, new_tailwind)
        logger.info("✅ Added Tailwind CDN script")
    
    # CRITICAL FIX: Ensure CSS link tag exists
    css_link = soup.find('link', href='styles/main.css')
    if not css_link:
        any_css_link = soup.find('link', rel='stylesheet')
        if any_css_link and 'main.css' not in str(any_css_link.get('href', '')):
            any_css_link['href'] = 'styles/main.css'
            any_css_link['rel'] = 'stylesheet'
        else:
            new_css_link = soup.new_tag('link', rel='stylesheet', href='styles/main.css')
            tailwind = soup.find('script', src=re.compile(r'cdn\.tailwindcss\.com'))
            if tailwind:
                tailwind.insert_after(new_css_link)
            else:
                head.append(new_css_link)
        logger.info("✅ Fixed CSS link")
    
    # Fix scripts: Keep CDN scripts and main.js only
    scripts = soup.find_all('script')
    for script in scripts:
        src = script.get('src', '')
        if not (src == 'scripts/main.js' or 
                'cdn.tailwindcss.com' in src or
                'googleapis.com' in src or
                src.startswith('http')):
            script.decompose()
    
    # Ensure there's at least one main.js script
    if not soup.find('script', src='scripts/main.js'):
        new_script = soup.new_tag('script', src='scripts/main.js')
        if soup.body:
            soup.body.append(new_script)
        else:
            soup.append(new_script)
        logger.info("✅ Added main.js script")
    
    html_code = str(soup)
    
    # Fix asset paths (remove leading slash)
    html_code = re.sub(r'src=["\']/(assets/)', r'src="\1', html_code)
    html_code = re.sub(r'href=["\']/(assets/)', r'href="\1', html_code)
    
    # Fix navigation links for multi-page support
    def fix_nav_link(match):
        full_match = match.group(0)
        path = match.group(1)
        
        if path.endswith('.html'):
            return full_match
        
        if (path == "/" or path.startswith("http") or
            path.endswith((".css", ".js", ".jpg", ".png", ".gif", ".svg", ".webp", ".ico", ".pdf"))):
            return full_match
        
        page_names = ['about', 'services', 'contact', 'portfolio', 'products', 'blog', 'pricing', 'team', 'gallery']
        
        if path.startswith("#"):
            page_name = path.lstrip("#").lower()
            if page_name in page_names:
                return f'href="{page_name}.html"'
        elif path.startswith("/"):
            clean_path = path.lstrip("/")
            if not clean_path.endswith(".html"):
                clean_path += ".html"
            return f'href="{clean_path}"'
        
        return full_match
    
    html_code = re.sub(r'href=["\']([^"\']+)["\']', fix_nav_link, html_code)
    
    return html_code


# ==================== Endpoints ====================

@router.post("/generate/{session_id}", response_model=GenerateResponse)
async def generate_website(
    session_id: str,
    session_service: SessionService = Depends(get_session_service),
    file_store: UnifiedFileStore = Depends(get_file_store)
):
    """
    Generate website files from the confirmed blueprint.
    
    This endpoint:
    1. Validates blueprint is confirmed
    2. Generates HTML/CSS/JS using AI
    3. Processes and fixes the code
    4. Generates multi-page if needed
    5. Saves all files to R2 + Database
    6. Returns file URLs
    """
    # Parse UUID
    try:
        session_uuid = UUID(session_id)
    except ValueError:
        raise ValidationError("session_id", "Invalid UUID format")
    
    # Get session
    session = await session_service.get_session(session_uuid)
    
    # Validate blueprint is confirmed
    if not session.blueprint_confirmed:
        raise ValidationError(
            "blueprint",
            "Blueprint not confirmed yet. Please confirm blueprint first."
        )
    
    if not session.blueprint:
        raise BlueprintNotFoundError(str(session_uuid))
    
    logger.info(f"🚀 Starting website generation for session {session_id}")
    
    # Generate code using AI
    logger.info("🤖 Generating code with AI...")
    code = await code_generator.generate(session.blueprint)
    
    # Validate code (non-blocking - just log warnings)
    validation = validator.validate_all(
        code.get("html", ""),
        code.get("css", ""),
        code.get("js", "")
    )
    
    if not validation.get("valid", False):
        logger.warning(f"⚠️ Validation warnings: {validation.get('errors', {})}")
    
    # Fix HTML structure
    if "html" in code:
        logger.info("🔧 Fixing HTML structure...")
        code["html"] = fix_html_structure(code["html"])
    
    # Generate multi-page if needed
    logger.info("📄 Generating pages...")
    pages = {}
    blueprint_pages = session.blueprint.get("pages", [])
    
    if len(blueprint_pages) > 1:
        # Multi-page site - use enhanced generator for unique pages
        logger.info(f"🎨 Generating {len(blueprint_pages)} unique pages using enhanced generator...")
        theme = session.blueprint.get("theme", {})
        
        # Extract brand name from blueprint
        brand_name = session.blueprint.get("name", "YourBrand")
        
        for page in blueprint_pages:
            page_slug = page.get("slug", "/")
            
            # Determine filename
            if page_slug == "/" or page_slug == "index":
                filename = "index.html"
            else:
                filename = f"{page_slug.strip('/').replace('/', '-')}.html"
            
            # Generate unique content for this page
            logger.info(f"  🎯 Generating unique content for {page.get('title', filename)} with brand: {brand_name}...")
            page_html = await enhanced_multi_page_generator.generate_page(
                page=page,
                all_pages=blueprint_pages,
                theme=theme,
                brand_name=brand_name
            )
            pages[filename] = page_html
            logger.info(f"  ✅ Generated {filename}")
    else:
        # Single page site - use base HTML
        logger.info("Single page site detected - using base HTML")
        pages = {"index.html": code.get("html", "")}
    
    # Save all files to R2 + Database
    files_written = []
    preview_urls = {}
    
    logger.info(f"💾 Saving {len(pages)} HTML pages to R2...")
    
    # Save HTML pages
    for filename, html_content in pages.items():
        file_info = await file_store.save_file(
            session_id=session_uuid,
            filename=filename,
            content=html_content,
            file_type="html",
            user_id=session.user_id
        )
        files_written.append(filename)
        preview_urls[filename] = file_info['r2_url']
        logger.info(f"  ✅ Saved {filename}")
    
    # Save CSS
    css_file = await file_store.save_file(
        session_id=session_uuid,
        filename="styles/main.css",
        content=code.get("css", "/* No CSS generated */"),
        file_type="css",
        user_id=session.user_id
    )
    files_written.append("styles/main.css")
    preview_urls["styles/main.css"] = css_file['r2_url']
    logger.info("  ✅ Saved styles/main.css")
    
    # Save JavaScript
    js_file = await file_store.save_file(
        session_id=session_uuid,
        filename="scripts/main.js",
        content=code.get("js", "// No JavaScript generated"),
        file_type="js",
        user_id=session.user_id
    )
    files_written.append("scripts/main.js")
    preview_urls["scripts/main.js"] = js_file['r2_url']
    logger.info("  ✅ Saved scripts/main.js")
    
    # Update session status
    await session_service.update_session(
        session_uuid,
        status=SessionStatus.WEBSITE_GENERATED.value
    )
    
    logger.info(f"✅ Website generation complete! {len(files_written)} files saved")
    
    return GenerateResponse(
        session_id=str(session_uuid),
        success=True,
        files=files_written,
        preview_urls=preview_urls,
        message=f"Website generated successfully! {len(files_written)} files created."
    )


@router.get("/preview/{session_id}", response_model=PreviewResponse)
async def get_preview_url(
    session_id: str,
    session_service: SessionService = Depends(get_session_service),
    file_store: UnifiedFileStore = Depends(get_file_store)
):
    """
    Get the preview URLs for a generated website.
    
    Returns URLs for all generated files.
    """
    # Parse UUID
    try:
        session_uuid = UUID(session_id)
    except ValueError:
        raise ValidationError("session_id", "Invalid UUID format")
    
    # Get session
    session = await session_service.get_session(session_uuid)
    
    # Get all files
    files = await file_store.list_session_files(session_uuid)
    
    if not files:
        raise ValidationError(
            "files",
            "Website not generated yet. Generate website first."
        )
    
    # Build preview URLs dict
    preview_urls = {f['filename']: f['r2_url'] for f in files}
    filenames = [f['filename'] for f in files]
    
    return PreviewResponse(
        session_id=str(session_uuid),
        preview_urls=preview_urls,
        files=filenames
    )


@router.get("/files/{session_id}/{file_path:path}", response_model=FileContentResponse)
async def get_file_content(
    session_id: str,
    file_path: str,
    file_store: UnifiedFileStore = Depends(get_file_store)
):
    """
    Get the content of a specific file.
    
    Downloads file from R2 and returns its content.
    """
    # Parse UUID
    try:
        session_uuid = UUID(session_id)
    except ValueError:
        raise ValidationError("session_id", "Invalid UUID format")
    
    # Get file content
    content = await file_store.get_file(session_uuid, file_path)
    
    if content is None:
        raise ValidationError("file_path", f"File not found: {file_path}")
    
    # Determine file type
    if file_path.endswith(".html"):
        file_type = "html"
    elif file_path.endswith(".css"):
        file_type = "css"
    elif file_path.endswith(".js"):
        file_type = "javascript"
    else:
        file_type = "text"
    
    # Decode bytes to string
    if isinstance(content, bytes):
        content = content.decode('utf-8')
    
    return FileContentResponse(
        file_path=file_path,
        file_type=file_type,
        content=content
    )


@router.get("/validate/{session_id}", response_model=ValidationResult)
async def validate_website(
    session_id: str,
    file_store: UnifiedFileStore = Depends(get_file_store)
):
    """
    Validate the generated website code.
    
    Checks HTML/CSS/JS for common issues.
    """
    # Parse UUID
    try:
        session_uuid = UUID(session_id)
    except ValueError:
        raise ValidationError("session_id", "Invalid UUID format")
    
    # Get files
    html = await file_store.get_file(session_uuid, "index.html")
    css = await file_store.get_file(session_uuid, "styles/main.css")
    js = await file_store.get_file(session_uuid, "scripts/main.js")
    
    # Decode if bytes
    html_str = html.decode('utf-8') if html and isinstance(html, bytes) else (html or "")
    css_str = css.decode('utf-8') if css and isinstance(css, bytes) else (css or "")
    js_str = js.decode('utf-8') if js and isinstance(js, bytes) else (js or "")
    
    # Validate
    result = validator.validate_all(html_str, css_str, js_str)
    
    return ValidationResult(
        valid=result["valid"],
        errors=result
    )
