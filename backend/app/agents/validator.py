"""
NCD INAI - Validator Agent

Validates generated and edited code.
"""

from typing import Dict, Any, List, Tuple
from html.parser import HTMLParser
import re


class ValidatorAgent:
    """Agent that validates website code."""
    
    def validate_html(self, html_content: str) -> Tuple[bool, List[str]]:
        """Validate HTML content."""
        errors = []
        
        # Check for DOCTYPE
        if not html_content.strip().startswith("<!DOCTYPE"):
            errors.append("Missing DOCTYPE declaration")
        
        # Check for required tags
        required_tags = ["html", "head", "body"]
        parser = TagChecker()
        parser.feed(html_content)
        for tag in required_tags:
            if tag not in parser.start_tags:
                errors.append(f"Missing required opening tag: <{tag}>")
            if tag not in parser.end_tags:
                errors.append(f"Missing required closing tag: </{tag}>")
        
        # Check for title
        if "<title>" not in html_content.lower():
            errors.append("Missing <title> tag")
        
        return len(errors) == 0, errors
    
    def validate_css(self, css_content: str) -> Tuple[bool, List[str]]:
        """Validate CSS content."""
        errors = []
        
        # Check for common syntax errors
        if ';;' in css_content:
            errors.append("Double semicolons found")
        
        # Check for empty rules
        empty_rule = re.search(r'{\s*}', css_content)
        if empty_rule:
            errors.append("Empty CSS rule found")
        
        return len(errors) == 0, errors
    
    def validate_js(self, js_content: str) -> Tuple[bool, List[str]]:
        """Validate JavaScript content."""
        errors = []
        
        # Check for balanced braces
        open_braces = js_content.count('{')
        close_braces = js_content.count('}')
        
        if open_braces != close_braces:
            errors.append(f"Unbalanced braces: {open_braces} open, {close_braces} close")
        
        # Check for balanced parentheses
        open_parens = js_content.count('(')
        close_parens = js_content.count(')')
        
        if open_parens != close_parens:
            errors.append(f"Unbalanced parentheses: {open_parens} open, {close_parens} close")
        
        # Check for balanced brackets
        open_brackets = js_content.count('[')
        close_brackets = js_content.count(']')
        
        if open_brackets != close_brackets:
            errors.append(f"Unbalanced brackets: {open_brackets} open, {close_brackets} close")
        
        # Check for common errors
        if 'undefined' in js_content and 'typeof' not in js_content:
            # Not necessarily an error, just a warning
            pass
        
        return len(errors) == 0, errors
    
    def validate_all(
        self,
        html: str,
        css: str,
        js: str
    ) -> Dict[str, Any]:
        """Validate all code files."""
        html_valid, html_errors = self.validate_html(html)
        css_valid, css_errors = self.validate_css(css)
        js_valid, js_errors = self.validate_js(js)
        
        all_valid = html_valid and css_valid and js_valid
        
        return {
            "valid": all_valid,
            "html": {
                "valid": html_valid,
                "errors": html_errors
            },
            "css": {
                "valid": css_valid,
                "errors": css_errors
            },
            "js": {
                "valid": js_valid,
                "errors": js_errors
            }
        }
    
    def fix_common_issues(self, code: str, file_type: str) -> str:
        """Attempt to fix common issues automatically."""
        if file_type == "html":
            # Add DOCTYPE if missing
            if not code.strip().startswith("<!DOCTYPE"):
                code = "<!DOCTYPE html>\n" + code
        
        elif file_type == "css":
            # Remove double semicolons
            code = code.replace(';;', ';')
        
        elif file_type == "js":
            # Add missing semicolons at end of statements (basic)
            lines = code.split('\n')
            fixed_lines = []
            for line in lines:
                stripped = line.rstrip()
                if stripped and not stripped.endswith((';', '{', '}', ',', ':', '//')):
                    if not stripped.startswith(('if', 'else', 'for', 'while', 'function', '//')):
                        line = stripped + ';'
                fixed_lines.append(line)
            code = '\n'.join(fixed_lines)
        
        return code


class TagChecker(HTMLParser):
    def __init__(self):
        super().__init__()
        self.start_tags = set()
        self.end_tags = set()

    def handle_starttag(self, tag, attrs):
        self.start_tags.add(tag.lower())

    def handle_endtag(self, tag):
        self.end_tags.add(tag.lower())


# Singleton instance
validator = ValidatorAgent()
