"""
NCD INAI - Chat Router

Handles chat-based interactions for dynamic page creation and editing.
"""

import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.session_manager import session_manager
from app.services.file_manager import file_manager
from app.agents.page_creator import page_creator
from app.services.nav_updater import nav_updater

router = APIRouter()
logger = logging.getLogger(__name__)


class ChatMessage(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    success: bool
    action: str  # "page_created", "page_updated", "general_response"
    data: Dict[str, Any]
    message: str


@router.post("/message", response_model=ChatResponse)
async def handle_chat_message(request: ChatMessage):
    """Handle chat messages and perform appropriate actions."""
    session = session_manager.get_session(request.session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Detect intent
    intent = _detect_intent(request.message)
    
    if intent == "create_page":
        return await _handle_page_creation(request.session_id, request.message, session)
    else:
        # General response for now
        return ChatResponse(
            success=True,
            action="general_response",
            data={},
            message="मैं समझ नहीं पाया। कृपया 'contact page बनाओ' या 'pricing page चाहिए' जैसा कहें।"
        )


def _detect_intent(message: str) -> str:
    """Detect user intent from message."""
    message_lower = message.lower()
    
    # Page creation keywords
    create_keywords = [
        "page बनाओ", "create page", "add page",
        "चाहिए", "need", "want",
        "form", "pricing", "about", "contact",
        "gallery", "portfolio", "faq"
    ]
    
    if any(keyword in message_lower for keyword in create_keywords):
        return "create_page"
    
    return "general"


async def _handle_page_creation(
    session_id: str,
    message: str,
    session: Any
) -> ChatResponse:
    """Handle page creation request."""
    try:
        # Get existing theme from blueprint
        theme = session.blueprint.get("theme", {}) if session.blueprint else {}
        
        if not theme:
            # Fallback theme
            theme = {
                "primaryColor": "#3B82F6",
                "backgroundColor": "#FFFFFF",
                "textColor": "#1F2937",
                "fontFamily": "Inter",
                "style": "modern"
            }
        
        # Create page using AI
        page_data = await page_creator.create_page(message, theme)
        
        # Save the page file
        file_manager.write_file(
            session_id,
            page_data['filename'],
            page_data['html_content']
        )
        
        # Update navigation in all existing pages
        session_dir = file_manager.get_session_path(session_id)
        updated_count = nav_updater.update_all_pages(
            session_dir,
            {
                'filename': page_data['filename'],
                'nav_link_text': page_data['nav_link_text']
            }
        )
        
        # Update session files list
        if page_data['filename'] not in session.files_generated:
            session.files_generated.append(page_data['filename'])
            session_manager.update_session(session)
        
        preview_url = f"/preview/{session_id}/{page_data['filename']}"
        
        return ChatResponse(
            success=True,
            action="page_created",
            data={
                "filename": page_data['filename'],
                "title": page_data['page_title'],
                "preview_url": preview_url,
                "nav_updated_count": updated_count
            },
            message=f"✅ {page_data['page_title']} page बनाया गया और {updated_count} pages में navigation update किया गया!"
        )
    
    except Exception as e:
        logger.exception("Page creation failed", extra={
            "session_id": session_id,
            "message": message,
            "error": str(e)
        })
        raise HTTPException(
            status_code=500,
            detail=f"Page creation failed: {str(e)}"
        )
