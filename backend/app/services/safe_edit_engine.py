"""
NCD INAI - Safe Edit Engine

Surgical mutations without breaking layout.
"""

from typing import Dict, Any, Optional
from pathlib import Path
from bs4 import BeautifulSoup
import re


class SafeEditEngine:
    """Safe mutation engine for HTML/CSS/JS files."""
    
    def update_html_text(
        self,
        file_path: Path,
        ncd_id: str,
        new_text: str
    ) -> Dict[str, Any]:
        """Safely update text content of an HTML element."""
        with open(file_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
        
        # Find element by data-ncd-id
        element = soup.find(attrs={"data-ncd-id": ncd_id})
        if not element:
            raise ValueError(f"Element with ncd_id '{ncd_id}' not found")
        
        # Store old value
        old_text = element.get_text(strip=True)
        
        # Update text
        element.string = new_text
        
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(str(soup.prettify()))
        
        return {
            "success": True,
            "old_value": old_text,
            "new_value": new_text,
            "ncd_id": ncd_id
        }
    
    def update_html_attribute(
        self,
        file_path: Path,
        ncd_id: str,
        attribute: str,
        new_value: str
    ) -> Dict[str, Any]:
        """Safely update an HTML attribute."""
        with open(file_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
        
        element = soup.find(attrs={"data-ncd-id": ncd_id})
        if not element:
            raise ValueError(f"Element with ncd_id '{ncd_id}' not found")
        
        old_value = element.get(attribute, '')
        element[attribute] = new_value
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(str(soup.prettify()))
        
        return {
            "success": True,
            "old_value": old_value,
            "new_value": new_value,
            "attribute": attribute
        }
    
    def update_css_property(
        self,
        file_path: Path,
        ncd_id: str,
        property_name: str,
        new_value: str
    ) -> Dict[str, Any]:
        """Safely update a CSS property for scoped selector."""
        with open(file_path, 'r', encoding='utf-8') as f:
            css_content = f.read()
        
        # Selector for this specific element
        selector = f'[data-ncd-id="{ncd_id}"]'
        
        # Find the rule block
        pattern = re.compile(
            rf'{re.escape(selector)}\s*\{{([^}}]*)\}}',
            re.MULTILINE | re.DOTALL
        )
        
        match = pattern.search(css_content)
        
        if match:
            # Rule exists, update property
            rule_content = match.group(1)
            prop_pattern = re.compile(
                rf'{re.escape(property_name)}\s*:\s*([^;]+);'
            )
            
            old_value = None
            if prop_pattern.search(rule_content):
                # Property exists, replace it
                old_match = prop_pattern.search(rule_content)
                old_value = old_match.group(1).strip()
                new_rule = prop_pattern.sub(
                    f'{property_name}: {new_value};',
                    rule_content
                )
            else:
                # Property doesn't exist, add it
                old_value = None
                new_rule = rule_content.rstrip() + f'\n  {property_name}: {new_value};\n'
            
            # Replace the entire rule
            new_css = css_content.replace(
                match.group(0),
                f'{selector} {{{new_rule}}}'
            )
        else:
            # Rule doesn't exist, create it
            old_value = None
            new_rule = f'\n{selector} {{\n  {property_name}: {new_value};\n}}\n'
            new_css = css_content + new_rule
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_css)
        
        return {
            "success": True,
            "old_value": old_value,
            "new_value": new_value,
            "property": property_name
        }
    
    def add_html_class(
        self,
        file_path: Path,
        ncd_id: str,
        class_name: str
    ) -> Dict[str, Any]:
        """Add a class to an element."""
        with open(file_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
        
        element = soup.find(attrs={"data-ncd-id": ncd_id})
        if not element:
            raise ValueError(f"Element with ncd_id '{ncd_id}' not found")
        
        current_classes = element.get('class', [])
        if class_name not in current_classes:
            current_classes.append(class_name)
            element['class'] = current_classes
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(str(soup.prettify()))
        
        return {
            "success": True,
            "class_added": class_name,
            "classes": current_classes
        }
    
    def remove_html_class(
        self,
        file_path: Path,
        ncd_id: str,
        class_name: str
    ) -> Dict[str, Any]:
        """Remove a class from an element."""
        with open(file_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
        
        element = soup.find(attrs={"data-ncd-id": ncd_id})
        if not element:
            raise ValueError(f"Element with ncd_id '{ncd_id}' not found")
        
        current_classes = element.get('class', [])
        if class_name in current_classes:
            current_classes.remove(class_name)
            element['class'] = current_classes
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(str(soup.prettify()))
        
        return {
            "success": True,
            "class_removed": class_name,
            "classes": current_classes
        }


# Singleton instance
safe_edit_engine = SafeEditEngine()
