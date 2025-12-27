"""
NCD INAI - Middleware
Error handling, authentication, and other middleware
"""

from app.api.middleware.error_handler import setup_exception_handlers

__all__ = ["setup_exception_handlers"]
