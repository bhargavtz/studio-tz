"""
Surgical Groq AI Website Editor
Makes TARGETED, PRECISE edits - only changes what user requests!
"""

import logging
import os
import json
import re
from typing import Dict, Any
from langchain_groq import ChatGroq
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class SurgicalGroqEditor:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY", "")
        if api_key:
            self.llm = ChatGroq(
                api_key=api_key,
                model="llama-3.3-70b-versatile",
                temperature=0.2,
                max_tokens=2000
            )
        else:
            self.llm = None
    
    async def modify_website(self, user_request: str, current_html: str, current_css: str = "") -> Dict[str, Any]:
        """
        Make SURGICAL edits to website - ONLY change what user requests!
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
        
        # Step 1: Understand what user wants to change
        analysis_prompt = f"""You are analyzing a user's edit request for a website.

USER REQUEST: "{user_request}"

Analyze and return a JSON response with:
1. What type of edit? (text_change, color_change, add_section, style_change, add_element, remove_element)
2. What specific element(s) to target?
3. What exact change to make?

CRITICAL RULES:
- If user says "change color" - ONLY change that color, nothing else
- If user says "change text" - ONLY change that text
- If user says "add section" - add that section without changing existing content
- DO NOT modify anything user didn't mention!

Return JSON format:
{{
    "edit_type": "text_change|color_change|add_section|style_change|add_element|remove_element",
    "target": "description of what to change (e.g., 'primary color', 'main heading', 'background color')",
    "selector": "CSS selector or element type (e.g., ':root', 'h1', 'body', 'button')",
    "property": "CSS property or 'textContent' (e.g., '--primary', 'background-color', 'textContent')",
    "new_value": "the new value to set",
    "reasoning": "why this interpretation"
}}

Examples:
"Make primary color blue" → {{"edit_type":"color_change","target":"primary color","selector":":root","property":"--primary","new_value":"#3b82f6","reasoning":"User wants to change CSS variable --primary"}}
"Change heading to Welcome" → {{"edit_type":"text_change","target":"main heading","selector":"h1","property":"textContent","new_value":"Welcome","reasoning":"Change h1 text only"}}

Return ONLY JSON, no explanation."""

        try:
            # Get AI analysis
            analysis_response = self.llm.invoke(analysis_prompt)
            analysis_text = analysis_response.content.strip()
            
            # Clean JSON
            analysis_text = re.sub(r'```json\s*|\s*```', '', analysis_text).strip()
            analysis = json.loads(analysis_text)
            
            logger.debug("AI analysis result", extra={"analysis": analysis})
            
            # Step 2: Apply the SURGICAL edit
            edit_type = analysis.get("edit_type")
            selector = analysis.get("selector")
            property_name = analysis.get("property")
            new_value = analysis.get("new_value")
            
            modified = False
            description = ""
            
            if edit_type == "color_change":
                # Modify CSS variables or inline styles
                if selector == ":root" or property_name.startswith("--"):
                    modified, description = self._modify_css_variable(soup, property_name, new_value)
                else:
                    modified, description = self._modify_style_property(soup, selector, property_name, new_value)
            
            elif edit_type == "text_change":
                modified, description = self._modify_text_content(soup, selector, new_value)
            
            elif edit_type == "style_change":
                modified, description = self._modify_style_property(soup, selector, property_name, new_value)
            
            elif edit_type == "add_section":
                modified, description = await self._add_new_section(soup, user_request, new_value)
            
            elif edit_type == "add_element":
                modified, description = await self._add_new_element(soup, user_request, selector, new_value)
            
            else:
                description = f"Unsupported edit type: {edit_type}"
            
            if modified:
                new_html = str(soup)
                return {
                    "success": True,
                    "message": f"✓ {description}",
                    "html": new_html,
                    "css": current_css,
                    "description": description
                }
            else:
                return {
                    "success": False,
                    "message": f"Could not apply edit: {description}",
                    "html": current_html,
                    "css": current_css
                }
                
        except Exception as e:
            logger.exception("Surgical edit failed", extra={"error": str(e)})
            return {
                "success": False,
                "message": f"Error: {str(e)}",
                "html": current_html,
                "css": current_css
            }
    
    def _modify_css_variable(self, soup: BeautifulSoup, var_name: str, new_value: str) -> tuple[bool, str]:
        """Modify a CSS variable in <style> tag"""
        style_tag = soup.find('style')
        if not style_tag:
            return False, "No <style> tag found"
        
        css_content = style_tag.string or ""
        
        # Find :root block
        if ":root" in css_content:
            # Replace the variable value
            pattern = rf"({var_name}\s*:\s*)[^;]+(;)"
            if re.search(pattern, css_content):
                new_css = re.sub(pattern, rf"\1{new_value}\2", css_content)
                style_tag.string = new_css
                return True, f"Changed {var_name} to {new_value}"
            else:
                # Add variable if not found
                css_content = css_content.replace(":root {", f":root {{\n  {var_name}: {new_value};")
                style_tag.string = css_content
                return True, f"Added {var_name}: {new_value}"
        
        return False, f"Could not find :root in CSS"
    
    def _modify_style_property(self, soup: BeautifulSoup, selector: str, property_name: str, new_value: str) -> tuple[bool, str]:
        """Modify a style property for elements matching selector"""
        elements = soup.select(selector)
        if not elements:
            return False, f"No elements found matching '{selector}'"
        
        for element in elements:
            current_style = element.get('style', '')
            # Parse existing styles
            styles = {}
            if current_style:
                for style_rule in current_style.split(';'):
                    if ':' in style_rule:
                        prop, val = style_rule.split(':', 1)
                        styles[prop.strip()] = val.strip()
            
            # Update property
            styles[property_name] = new_value
            
            # Rebuild style string
            new_style = '; '.join([f"{k}: {v}" for k, v in styles.items()])
            element['style'] = new_style
        
        return True, f"Changed {property_name} to {new_value} for {len(elements)} element(s)"
    
    def _modify_text_content(self, soup: BeautifulSoup, selector: str, new_text: str) -> tuple[bool, str]:
        """Change text content of matching elements"""
        elements = soup.select(selector)
        if not elements:
            return False, f"No elements found matching '{selector}'"
        
        for element in elements:
            element.string = new_text
        
        return True, f"Changed text of {len(elements)} {selector} element(s) to '{new_text}'"
    
    async def _add_new_section(self, soup: BeautifulSoup, user_request: str, section_type: str) -> tuple[bool, str]:
        """Add a new section to the page"""
        # Generate section HTML using AI
        prompt = f"""Generate ONLY the HTML for this section: "{user_request}"

Section type: {section_type}

Return ONLY the HTML code for this section, wrapped in a <section> tag. Nothing else.
Use inline styles for beauty. Keep it simple and practical.
"""
        try:
            response = self.llm.invoke(prompt)
            section_html = response.content.strip()
            section_html = section_html.replace('```html', '').replace('```', '').strip()
            
            # Insert before closing body tag
            body = soup.find('body')
            if body:
                new_section = BeautifulSoup(section_html, 'html.parser')
                body.append(new_section)
                return True, f"Added new section: {section_type}"
        except Exception as e:
            return False, f"Failed to generate section: {e}"
        
        return False, "Could not add section"
    
    async def _add_new_element(self, soup: BeautifulSoup, user_request: str, parent_selector: str, element_type: str) -> tuple[bool, str]:
        """Add a new element to the page"""
        # Similar to add_section but targets specific parent
        return self._add_new_section(soup, user_request, element_type)

# Global instance
surgical_editor = SurgicalGroqEditor()
