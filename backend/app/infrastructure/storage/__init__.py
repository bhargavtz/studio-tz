"""
NCD INAI - Storage Infrastructure
"""

from app.infrastructure.storage.file_store import UnifiedFileStore, get_file_store

__all__ = ["UnifiedFileStore", "get_file_store"]
