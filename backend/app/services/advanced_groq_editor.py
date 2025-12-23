"""
Advanced Groq AI Website Editor
Full website modification with natural language - add sections, images, change anything!
"""

import os
import json
from typing import Dict, Any
from langchain_groq import ChatGroq
from bs4 import BeautifulSoup

class AdvancedGroqEditor:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY", "")
        if api_key:
            self.llm = ChatGroq(
                api_key=api_key,
                model="llama-3.3-70b-versatile",
                temperature=0.3,
                max_tokens=4000
            )
        else:
            self.llm = None
    
    async def modify_website(self, user_request: str, current_html: str, current_css: str = "") -> Dict[str, Any]:
        """
        Modify entire website based on natural language request
        Can add sections, images, change layout, anything!
        """
        
        if not self.llm:
            return {
                "success": False,
                "message": "AI not available",
                "html": current_html,
                "css": current_css
            }
        
        # Extract current structure
        soup = BeautifulSoup(current_html, 'html.parser')
        current_structure = self._analyze_structure(soup)
        
        prompt = f"""You are an expert web developer. Modify the website based on user's request.

USER REQUEST: "{user_request}"

CURRENT WEBSITE STRUCTURE:
{current_structure}

CURRENT HTML:
{current_html[:2000]}...

CURRENT CSS (if any):
{current_css[:1000] if current_css else "No separate CSS"}

TASK: Modify the HTML to fulfill the user's request. You can:
- Add new sections (hero, features, gallery, contact, etc.)
- Add images (use placeholder URLs like https://picsum.photos/800/600)
- Change layout and styling
- Add or remove any elements
- Modify text content
- Add forms, buttons, cards, etc.

IMPORTANT RULES:
1. Keep existing good content unless user wants to remove it
2. Use inline CSS in <style> tag in <head>
3. Use modern, beautiful design with good colors
4. Make it responsive
5. Add proper spacing and padding
6. Use placeholder images from https://picsum.photos/WIDTH/HEIGHT
7. Return ONLY valid HTML (complete document with <!DOCTYPE html>)

Return ONLY the complete HTML code, nothing else. No explanations, no markdown."""

        try:
            response = self.llm.invoke(prompt)
            new_html = response.content.strip()
            
            # Clean up response
            new_html = new_html.replace('```html', '').replace('```', '').strip()
            
            # Validate it's HTML
            if not new_html.startswith('<!DOCTYPE') and not new_html.startswith('<html'):
                new_html = f"<!DOCTYPE html>\n{new_html}"
            
            # Extract CSS if in style tag
            new_soup = BeautifulSoup(new_html, 'html.parser')
            style_tag = new_soup.find('style')
            extracted_css = style_tag.string if style_tag else ""
            
            return {
                "success": True,
                "message": "✓ Website updated successfully!",
                "html": new_html,
                "css": extracted_css,
                "description": f"Modified website based on: {user_request}"
            }
            
        except Exception as e:
            print(f"AI modification error: {e}")
            return {
                "success": False,
                "message": f"Error: {str(e)}",
                "html": current_html,
                "css": current_css
            }
    
    def _analyze_structure(self, soup: BeautifulSoup) -> str:
        """Analyze current website structure"""
        info = []
        
        # Title
        title = soup.find('title')
        if title:
            info.append(f"Title: {title.string}")
        
        # Headings
        for tag in ['h1', 'h2', 'h3']:
            elements = soup.find_all(tag)
            if elements:
                info.append(f"{tag.upper()}: {len(elements)} found")
        
        # Sections
        sections = soup.find_all(['section', 'div'])
        info.append(f"Sections/Divs: {len(sections)} found")
        
        # Images
        images = soup.find_all('img')
        info.append(f"Images: {len(images)} found")
        
        # Buttons
        buttons = soup.find_all('button')
        info.append(f"Buttons: {len(buttons)} found")
        
        # Forms
        forms = soup.find_all('form')
        info.append(f"Forms: {len(forms)} found")
        
        return "\n".join(info)

# Global instance
advanced_editor = AdvancedGroqEditor()
