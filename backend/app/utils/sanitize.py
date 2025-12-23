"""
NCD INAI - HTML Sanitization Utilities
"""

import html
import re
from typing import Any, Dict


def sanitize_html_content(content: str, max_length: int = 10000) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Args:
        content: Raw HTML content
        max_length: Maximum allowed length
        
    Returns:
        Sanitized HTML content
    """
    if not content:
        return ""
    
    # Limit length
    content = content[:max_length]
    
    # Escape HTML entities
    content = html.escape(content)
    
    return content


def sanitize_blueprint_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize blueprint data before using in HTML generation.
    
    Args:
        data: Blueprint dictionary
        
    Returns:
        Sanitized blueprint data
    """
    if isinstance(data, dict):
        return {k: sanitize_blueprint_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_blueprint_data(item) for item in data]
    elif isinstance(data, str):
        # Sanitize strings: escape HTML, limit length
        sanitized = html.escape(data[:5000])
        return sanitized
    else:        return data


def validate_file_path(path: str) -> bool:
    """
    Validate file path to prevent path traversal.
    
    Args:
        path: File path to validate
        
    Returns:
        True if valid, False otherwise
    """
    # Check for path traversal patterns
    dangerous_patterns = [
        '..',
        '~',
        '/etc/',
        '/var/',
        '/usr/',
        'C:\\',
        'D:\\',
    ]
    
    path_lower = path.lower()
    for pattern in dangerous_patterns:
        if pattern in path_lower:
            return False
    
    return True
