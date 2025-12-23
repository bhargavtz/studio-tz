"""
Groq AI-Powered Chat Editor
Fast natural language understanding for website editing using Groq
"""

import os
import re
import json
from typing import Dict, Any, Optional
from langchain_groq import ChatGroq
from bs4 import BeautifulSoup

class GroqChatEditor:
    def __init__(self):
        # Configure Groq
        api_key = os.getenv("GROQ_API_KEY", "")
        if api_key:
            self.llm = ChatGroq(
                api_key=api_key,
                model="llama-3.3-70b-versatile",
                temperature=0.1,
                max_tokens=500
            )
        else:
            self.llm = None
    
    async def understand_edit_request(self, user_message: str, html_content: str) -> Dict[str, Any]:
        """
        Use Groq to understand natural language edit requests
        Returns: {
            'action': 'modify_text' | 'modify_style' | 'add_element' | 'remove_element',
            'selector': 'CSS selector',
            'property': 'property name',
            'value': 'new value',
            'description': 'what was understood'
        }
        """
        
        if not self.llm:
            # Fallback to pattern matching if Groq not available
            return self._fallback_understanding(user_message)
        
        # Extract current page structure
        soup = BeautifulSoup(html_content, 'html.parser')
        elements_info = self._extract_elements_info(soup)
        
        prompt = f"""You are a website editor AI. Analyze this edit request and return ONLY a JSON object.

User Request: "{user_message}"

Current Page Elements:
{elements_info}

Return ONLY a valid JSON object (no markdown, no explanation) with this structure:
{{
    "action": "modify_text|modify_style",
    "selector": "CSS selector",
    "property": "text or CSS property name",
    "value": "new value",
    "description": "brief description"
}}

Examples:
User: "Change heading to Welcome"
{{"action": "modify_text", "selector": "h1", "property": "text", "value": "Welcome", "description": "Change main heading text"}}

User: "Make button blue"
{{"action": "modify_style", "selector": "button", "property": "background-color", "value": "blue", "description": "Change button color"}}

User: "Change background to red"
{{"action": "modify_style", "selector": "body", "property": "background-color", "value": "red", "description": "Change page background"}}

Return ONLY the JSON object, nothing else."""

        try:
            response = self.llm.invoke(prompt)
            result_text = response.content.strip()
            
            # Clean up response - remove markdown code blocks if present
            result_text = re.sub(r'```json\s*|\s*```', '', result_text)
            result_text = result_text.strip()
            
            # Parse JSON
            result = json.loads(result_text)
            
            # Validate required fields
            required_fields = ['action', 'selector', 'property', 'value', 'description']
            if all(field in result for field in required_fields):
                return result
            else:
                print(f"Invalid response structure: {result}")
                return self._fallback_understanding(user_message)
                
        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}, Response: {result_text}")
            return self._fallback_understanding(user_message)
        except Exception as e:
            print(f"Groq error: {e}")
            return self._fallback_understanding(user_message)
    
    def _extract_elements_info(self, soup: BeautifulSoup) -> str:
        """Extract information about page elements"""
        info = []
        
        # Headings
        for tag in ['h1', 'h2', 'h3']:
            elements = soup.find_all(tag)
            if elements:
                texts = [e.get_text()[:30] for e in elements[:3]]
                info.append(f"{tag.upper()}: {', '.join(texts)}")
        
        # Buttons
        buttons = soup.find_all('button')
        if buttons:
            texts = [b.get_text()[:20] for b in buttons[:3]]
            info.append(f"BUTTONS: {', '.join(texts)}")
        
        # Links
        links = soup.find_all('a')
        if links:
            texts = [a.get_text()[:20] for a in links[:3]]
            info.append(f"LINKS: {', '.join(texts)}")
        
        # Paragraphs
        paras = soup.find_all('p')
        if paras:
            info.append(f"PARAGRAPHS: {len(paras)} found")
        
        return "\n".join(info) if info else "No major elements found"
    
    def _fallback_understanding(self, message: str) -> Dict[str, Any]:
        """Fallback pattern matching when Groq is not available"""
        message = message.lower()
        
        # Pattern matching for common requests
        patterns = [
            # Text changes - "change/update X to Y"
            (r"(?:change|update|set|make)\s+(?:the\s+)?(.+?)\s+(?:to|text to|heading to)\s+(.+)", 
             lambda m: {
                 "action": "modify_text", 
                 "selector": self._get_selector(m.group(1)), 
                 "property": "text", 
                 "value": m.group(2).strip(), 
                 "description": f"Change {m.group(1)} text to {m.group(2).strip()}"
             }),
            
            # Color changes - "make X color" or "change X to color"
            (r"(?:make|change|set)\s+(?:the\s+)?(.+?)\s+(?:color\s+)?(?:to\s+)?(\w+)",
             lambda m: {
                 "action": "modify_style", 
                 "selector": self._get_selector(m.group(1)),
                 "property": "background-color" if "background" in m.group(1) or "button" in m.group(1) else "color",
                 "value": m.group(2).strip(),
                 "description": f"Change {m.group(1)} color to {m.group(2).strip()}"
             }),
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
            "main title": "h1",
            "h1": "h1",
            "h2": "h2",
            "h3": "h3",
            "button": "button",
            "btn": "button",
            "link": "a",
            "links": "a",
            "paragraph": "p",
            "para": "p",
            "background": "body",
            "body": "body",
            "page": "body",
        }
        
        for key, value in selector_map.items():
            if key in element_desc:
                return value
        
        return element_desc

# Global instance
groq_editor = GroqChatEditor()
