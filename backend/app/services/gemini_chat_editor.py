"""
Gemini AI-Powered Chat Editor
Natural language understanding for website editing
"""

import logging
import os
import re
from typing import Dict, Any, Optional
import google.generativeai as genai
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class GeminiChatEditor:
    def __init__(self):
        # Configure Gemini
        api_key = os.getenv("GEMINI_API_KEY", "")
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        else:
            self.model = None
    
    async def understand_edit_request(self, user_message: str, html_content: str) -> Dict[str, Any]:
        """
        Use Gemini to understand natural language edit requests
        Returns: {
            'action': 'modify_text' | 'modify_style' | 'add_element' | 'remove_element',
            'selector': 'CSS selector',
            'property': 'property name',
            'value': 'new value',
            'description': 'what was understood'
        }
        """
        
        if not self.model:
            # Fallback to pattern matching if Gemini not available
            return self._fallback_understanding(user_message)
        
        # Extract current page structure
        soup = BeautifulSoup(html_content, 'html.parser')
        elements_info = self._extract_elements_info(soup)
        
        prompt = f"""You are a website editor AI. Analyze this edit request and return a JSON response.

User Request: "{user_message}"

Current Page Elements:
{elements_info}

Analyze the request and return ONLY a JSON object with this exact structure:
{{
    "action": "modify_text|modify_style|add_element|remove_element",
    "selector": "CSS selector for the element",
    "property": "property to change (for style) or 'text' for text content",
    "value": "new value to set",
    "description": "brief description of what you understood"
}}

Examples:
- "Change heading to Welcome" → {{"action": "modify_text", "selector": "h1", "property": "text", "value": "Welcome", "description": "Change main heading text"}}
- "Make button blue" → {{"action": "modify_style", "selector": "button", "property": "background-color", "value": "blue", "description": "Change button background color"}}
- "Change background to red" → {{"action": "modify_style", "selector": "body", "property": "background-color", "value": "red", "description": "Change page background"}}

Return ONLY the JSON, no other text."""

        try:
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            
            # Extract JSON from response
            import json
            # Remove markdown code blocks if present
            result_text = re.sub(r'```json\s*|\s*```', '', result_text)
            result = json.loads(result_text)
            
            return result
        except Exception as e:
            logger.exception(f"Gemini error: {e}")
            return self._fallback_understanding(user_message)
    
    def _extract_elements_info(self, soup: BeautifulSoup) -> str:
        """Extract information about page elements"""
        info = []
        
        # Headings
        for tag in ['h1', 'h2', 'h3']:
            elements = soup.find_all(tag)
            if elements:
                info.append(f"{tag.upper()}: {', '.join([e.get_text()[:30] for e in elements[:3]])}")
        
        # Buttons
        buttons = soup.find_all('button')
        if buttons:
            info.append(f"BUTTONS: {', '.join([b.get_text()[:20] for b in buttons[:3]])}")
        
        # Links
        links = soup.find_all('a')
        if links:
            info.append(f"LINKS: {', '.join([a.get_text()[:20] for a in links[:3]])}")
        
        # Paragraphs
        paras = soup.find_all('p')
        if paras:
            info.append(f"PARAGRAPHS: {len(paras)} found")
        
        return "\n".join(info) if info else "No major elements found"
    
    def _fallback_understanding(self, message: str) -> Dict[str, Any]:
        """Fallback pattern matching when Gemini is not available"""
        message = message.lower()
        
        # Pattern matching
        patterns = [
            # Text changes
            (r"(?:change|update|set|make)\s+(?:the\s+)?(.+?)\s+(?:to|text to|heading to)\s+(.+)", 
             lambda m: {"action": "modify_text", "selector": self._get_selector(m.group(1)), 
                       "property": "text", "value": m.group(2).strip(), 
                       "description": f"Change {m.group(1)} text"}),
            
            # Color changes
            (r"(?:make|change|set)\s+(?:the\s+)?(.+?)\s+(?:color\s+)?(?:to\s+)?(\w+)",
             lambda m: {"action": "modify_style", "selector": self._get_selector(m.group(1)),
                       "property": "background-color" if "background" in m.group(1) else "color",
                       "value": m.group(2).strip(),
                       "description": f"Change {m.group(1)} color"}),
        ]
        
        for pattern, handler in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return handler(match)
        
        return {
            "action": "unknown",
            "selector": "",
            "property": "",
            "value": "",
            "description": "Could not understand the request"
        }
    
    def _get_selector(self, element_desc: str) -> str:
        """Convert element description to CSS selector"""
        element_desc = element_desc.lower().strip()
        
        selector_map = {
            "heading": "h1",
            "title": "h1",
            "main heading": "h1",
            "h1": "h1",
            "h2": "h2",
            "h3": "h3",
            "button": "button",
            "btn": "button",
            "link": "a",
            "links": "a",
            "paragraph": "p",
            "background": "body",
            "body": "body",
            "page": "body",
        }
        
        for key, value in selector_map.items():
            if key in element_desc:
                return value
        
        return element_desc

# Global instance
gemini_editor = GeminiChatEditor()
