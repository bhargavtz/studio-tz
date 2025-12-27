"""
Advanced Website Editor with Targeted Updates
Uses Kimi model for intelligent, surgical code modifications.
"""

import os
import json
import re
from typing import Dict, Any
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from bs4 import BeautifulSoup
from app.config import settings

class AdvancedGroqEditor:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY", "")
        if api_key:
            # Use Kimi model for better code understanding
            self.llm = ChatGroq(
                api_key=api_key,
                model=settings.llm_model,  # moonshot/kimi-k2-instruct-0905
                temperature=0.2,  # Lower for precise code edits
                max_tokens=6000
            )
        else:
            self.llm = None
    
    async def modify_website(self, user_request: str, current_html: str, current_css: str = "") -> Dict[str, Any]:
        """
        Intelligently modify website with TARGETED updates.
        Only updates the specific section/element requested, not entire HTML.
        """
        
        if not self.llm:
            return {
                "success": False,
                "message": "AI not available",
                "html": current_html,
                "css": current_css
            }
        
        # Parse current HTML
        soup = BeautifulSoup(current_html, 'html.parser')
        
        # Analyze what user wants to modify
        modification_plan = await self._plan_modification(user_request, soup)
        
        if not modification_plan["success"]:
            return modification_plan
        
        # Apply targeted modifications
        try:
            plan_type = modification_plan["type"]
            
            if plan_type == "ADD_SECTION":
                new_html = await self._add_section(soup, user_request, modification_plan)
            elif plan_type == "MODIFY_SECTION":
                new_html = await self._modify_section(soup, user_request, modification_plan)
            elif plan_type == "UPDATE_CONTENT":
                new_html = await self._update_content(soup, user_request, modification_plan)
            elif plan_type == "STYLE_CHANGE":
                new_html, current_css = await self._modify_styles(soup, current_css, user_request)
            else:
                # Fallback: full update for complex changes
                new_html = await self._full_update(soup, user_request)
            
            return {
                "success": True,
                "message": f"✓ {modification_plan.get('description', 'Updated successfully')}",
                "html": str(new_html),
                "css": current_css,
                "description": modification_plan.get('description', user_request)
            }
            
        except Exception as e:
            print(f"Modification error: {e}")
            return {
                "success": False,
                "message": f"Error: {str(e)}",
                "html": current_html,
                "css": current_css
            }
    
    async def _plan_modification(self, request: str, soup: BeautifulSoup) -> Dict[str, Any]:
        """Determine what type of modification is needed."""
        
        structure = self._analyze_structure(soup)
        
        prompt = f"""Analyze this website edit request and classify it:

USER REQUEST: "{request}"

CURRENT WEBSITE:
{structure}

Classify the request as ONE of:
1. ADD_SECTION - Adding a new section (hero, features, gallery, contact, etc.)
2. MODIFY_SECTION - Changing an existing section
3. UPDATE_CONTENT - Changing text, images, or links
4. STYLE_CHANGE - Color, font, spacing changes
5. COMPLEX - Multiple changes requiring full rewrite

Return JSON:
{{
    "type": "ADD_SECTION|MODIFY_SECTION|UPDATE_CONTENT|STYLE_CHANGE|COMPLEX",
    "target_section": "hero|features|contact|etc or null",
    "description": "Brief description of what will change"
}}

Return ONLY valid JSON, no markdown."""

        try:
            response = self.llm.invoke(prompt)
            content = response.content.strip()
            content = content.replace('```json', '').replace('```', '').strip()
            plan = json.loads(content)
            plan["success"] = True
            return plan
        except Exception as e:
            print(f"Planning error: {e}")
            return {"success": False, "type": "COMPLEX"}
    
    async def _add_section(self, soup: BeautifulSoup, request: str, plan: Dict) -> BeautifulSoup:
        """Add a new section to the page."""
        
        prompt = f"""Generate ONLY the HTML for a new section based on this request:
"{request}"

RULES:
1. Return ONLY the section HTML (e.g., <section>...</section>)
2. Use Tailwind CSS classes for styling
3. Use placeholder images from https://picsum.photos/WIDTH/HEIGHT
4. Make it responsive and beautiful
5. Include proper spacing (py-20, px-6, etc.)
6. NO full HTML document - ONLY the section code

Return the HTML section code directly, no explanations."""

        response = self.llm.invoke(prompt)
        section_html = response.content.strip().replace('```html', '').replace('```', '').strip()
        
        # Parse new section
        new_section = BeautifulSoup(section_html, 'html.parser')
        
        # Insert before footer or at end of main/body
        main = soup.find('main')
        footer = soup.find('footer')
        
        if main:
            if footer and footer.parent == main:
                footer.insert_before(new_section)
            else:
                main.append(new_section)
        else:
            body = soup.find('body')
            if body:
                if footer:
                    footer.insert_before(new_section)
                else:
                    body.append(new_section)
        
        return soup
    
    async def _modify_section(self, soup: BeautifulSoup, request: str, plan: Dict) -> BeautifulSoup:
        """Modify an existing section."""
        
        target = plan.get("target_section", "")
        
        # Find section to modify (by id, class, or position)
        section = None
        if target:
            section = soup.find(id=target) or soup.find(class_=target)
        
        if not section:
            # Find first main section
            section = soup.find('section') or soup.find('main')
        
        if not section:
            return soup
        
        prompt = f"""Modify this HTML section based on request:
"{request}"

CURRENT SECTION:
{str(section)[:1500]}

Return the MODIFIED section HTML only. Keep structure but apply requested changes.
No explanations, just HTML."""

        response = self.llm.invoke(prompt)
        new_section_html = response.content.strip().replace('```html', '').replace('```', '').strip()
        
        # Replace section
        new_section = BeautifulSoup(new_section_html, 'html.parser').find()
        if new_section:
            section.replace_with(new_section)
        
        return soup
    
    async def _update_content(self, soup: BeautifulSoup, request: str, plan: Dict) -> BeautifulSoup:
        """Update specific content (text, images, links)."""
        
        # Use simpler text replacement for content updates
        prompt = f"""Update website content based on: "{request}"

Return a JSON object with specific changes:
{{
    "changes": [
        {{"element": "h1", "old": "Old Text", "new": "New Text"}},
        {{"element": "p", "old": "Old Para", "new": "New Para"}}
    ]
}}

Return ONLY JSON."""

        try:
            response = self.llm.invoke(prompt)
            content = response.content.strip().replace('```json', '').replace('```', '').strip()
            changes = json.loads(content)
            
            for change in changes.get("changes", []):
                element_type = change.get("element")
                old_text = change.get("old")
                new_text = change.get("new")
                
                # Find and update elements
                for elem in soup.find_all(element_type):
                    if old_text in elem.get_text():
                        elem.string = new_text
                        break
        except:
            pass
        
        return soup
    
    async def _modify_styles(self, soup: BeautifulSoup, current_css: str, request: str) -> tuple:
        """Modify CSS styles."""
        # This would update the <style> tag or separate CSS
        return soup, current_css
    
    async def _full_update(self, soup: BeautifulSoup, request: str) -> str:
        """Fallback: full HTML update for complex changes."""
        
        current_html = str(soup)
        
        prompt = f"""Update this website based on: "{request}"

CURRENT HTML (first 2000 chars):
{current_html[:2000]}

Return the COMPLETE updated HTML document. Keep existing good content.
Use modern styling. Return HTML only, no explanations."""

        response = self.llm.invoke(prompt)
        new_html = response.content.strip().replace('```html', '').replace('```', '').strip()
        
        if not new_html.startswith('<!DOCTYPE'):
            new_html = f"<!DOCTYPE html>\n{new_html}"
        
        return new_html
    
    def _analyze_structure(self, soup: BeautifulSoup) -> str:
        """Analyze current website structure."""
        info = []
        
        title = soup.find('title')
        if title:
            info.append(f"Title: {title.string}")
        
        for tag in ['h1', 'h2', 'h3']:
            elements = soup.find_all(tag)
            if elements:
                headings = [elem.get_text()[:30] for elem in elements[:3]]
                info.append(f"{tag.upper()}: {headings}")
        
        sections = soup.find_all('section')
        info.append(f"Sections: {len(sections)}")
        
        images = soup.find_all('img')
        info.append(f"Images: {len(images)}")
        
        return "\n".join(info)

# Global instance
advanced_editor = AdvancedGroqEditor()
