"""
NCD INAI - File Manager Service
"""

import os
import shutil
from pathlib import Path
from typing import Optional, List, Dict
import zipfile
import io

from app.config import settings


class FileManager:
    """Manages website files for sessions."""
    
    def __init__(self):
        self._ensure_projects_dir()
    
    def _ensure_projects_dir(self):
        """Ensure projects directory exists."""
        settings.projects_dir.mkdir(parents=True, exist_ok=True)
    
    def get_session_path(self, session_id: str) -> Path:
        """Get the path to a session's project directory."""
        return settings.projects_dir / f"session_{session_id}"
    
    def write_file(self, session_id: str, relative_path: str, content: str) -> str:
        """Write content to a file in the session's project."""
        session_path = self.get_session_path(session_id)
        file_path = (session_path / relative_path).resolve()
        
        # Security: Ensure file_path is within session_path (prevent path traversal)
        try:
            file_path.relative_to(session_path.resolve())
        except ValueError:
            raise ValueError(
                f"Invalid file path: {relative_path}. "
                f"Path traversal detected. File must be within session directory."
            )
        
        # Ensure parent directories exist
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        return str(file_path)

    
    def read_file(self, session_id: str, relative_path: str) -> Optional[str]:
        """Read content from a file in the session's project."""
        session_path = self.get_session_path(session_id)
        file_path = (session_path / relative_path).resolve()
        
        # Security: Ensure file_path is within session_path (prevent path traversal)
        try:
            file_path.relative_to(session_path.resolve())
        except ValueError:
            raise ValueError(
                f"Invalid file path: {relative_path}. "
                f"Path traversal detected. File must be within session directory."
            )
        
        if not file_path.exists():
            return None
        
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    
    def delete_file(self, session_id: str, relative_path: str) -> bool:
        """Delete a file from the session's project."""
        session_path = self.get_session_path(session_id)
        file_path = session_path / relative_path
        
        if file_path.exists():
            file_path.unlink()
            return True
        return False
    
    def list_files(self, session_id: str, extensions: Optional[List[str]] = None) -> List[str]:
        """List all files in a session's project (excluding internal metadata files)."""
        session_path = self.get_session_path(session_id)
        
        if not session_path.exists():
            return []
        
        # Internal files that should not be shown to users
        INTERNAL_FILES = {
            'answers.json',
            'blueprint.json',
            'domain.json',
            'questions.json',
            'session.json',
            'vision.json'
        }
        
        files = []
        for path in session_path.rglob("*"):
            if path.is_file():
                # Skip internal metadata files
                if path.name in INTERNAL_FILES:
                    continue
                
                # Skip backup directory
                if '.backups' in path.parts:
                    continue
                
                relative = path.relative_to(session_path)
                if extensions is None or path.suffix in extensions:
                    files.append(str(relative))
        
        return files
    
    def get_preview_url(self, session_id: str) -> str:
        """Get the preview URL for a session's website."""
        return f"/projects/session_{session_id}/index.html"
    
    def create_zip(self, session_id: str) -> bytes:
        """Create a ZIP archive of the session's project (excluding internal metadata)."""
        session_path = self.get_session_path(session_id)
        
        # Internal files that should not be included in download
        INTERNAL_FILES = {
            'answers.json',
            'blueprint.json',
            'domain.json',
            'questions.json',
            'session.json',
            'vision.json'
        }
        
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for file_path in session_path.rglob("*"):
                if file_path.is_file():
                    # Skip internal metadata files
                    if file_path.name in INTERNAL_FILES:
                        continue
                    
                    # Skip backup directory
                    if '.backups' in file_path.parts:
                        continue
                    
                    arcname = file_path.relative_to(session_path)
                    zf.write(file_path, arcname)
        
        buffer.seek(0)
        return buffer.getvalue()
    
    def backup_file(self, session_id: str, relative_path: str) -> Optional[str]:
        """Create a backup of a file before editing."""
        session_path = self.get_session_path(session_id)
        file_path = session_path / relative_path
        
        if not file_path.exists():
            return None
        
        backup_dir = session_path / ".backups"
        backup_dir.mkdir(exist_ok=True)
        
        # Create timestamped backup
        import time
        timestamp = int(time.time())
        backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
        backup_path = backup_dir / backup_name
        
        shutil.copy2(file_path, backup_path)
        return str(backup_path)
    
    def restore_backup(self, session_id: str, backup_path: str, original_path: str) -> bool:
        """Restore a file from backup."""
        session_path = self.get_session_path(session_id)
        full_backup_path = Path(backup_path)
        full_original_path = session_path / original_path
        
        if full_backup_path.exists():
            shutil.copy2(full_backup_path, full_original_path)
            return True
        return False


# Global file manager instance
file_manager = FileManager()
