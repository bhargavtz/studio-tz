"""
NCD INAI - Session Manager Service
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict
import uuid

from app.config import settings
from app.models.session import Session, SessionStatus


class SessionManager:
    """Manages user sessions and their state."""
    
    def __init__(self):
        self._sessions: Dict[str, Session] = {}
        self._load_existing_sessions()
    
    def _load_existing_sessions(self):
        """Load existing sessions from disk."""
        if not settings.projects_dir.exists():
            return
        
        for session_dir in settings.projects_dir.iterdir():
            if session_dir.is_dir() and session_dir.name.startswith("session_"):
                session_id = session_dir.name.replace("session_", "")
                session_file = session_dir / "session.json"
                if session_file.exists():
                    try:
                        with open(session_file, "r") as f:
                            data = json.load(f)
                            self._sessions[session_id] = Session(**data)
                    except Exception as e:
                        print(f"Failed to load session {session_id}: {e}")
    
    def create_session(self) -> Session:
        """Create a new session."""
        session = Session()
        self._sessions[session.id] = session
        
        # Create session directory
        session_dir = self._get_session_dir(session.id)
        session_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (session_dir / "styles").mkdir(exist_ok=True)
        (session_dir / "scripts").mkdir(exist_ok=True)
        (session_dir / "assets").mkdir(exist_ok=True)
        
        # Save session state
        self._save_session(session)
        
        return session
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """Get a session by ID."""
        return self._sessions.get(session_id)
    
    def update_session(self, session: Session) -> Session:
        """Update a session."""
        session.updated_at = datetime.utcnow()
        self._sessions[session.id] = session
        self._save_session(session)
        return session
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            # Optionally delete files
            return True
        return False
    
    def _get_session_dir(self, session_id: str) -> Path:
        """Get the directory path for a session."""
        return settings.projects_dir / f"session_{session_id}"
    
    def _save_session(self, session: Session):
        """Save session state to disk."""
        session_dir = self._get_session_dir(session.id)
        session_file = session_dir / "session.json"
        
        with open(session_file, "w") as f:
            json.dump(session.model_dump(mode="json"), f, indent=2, default=str)
    
    def save_json_file(self, session_id: str, filename: str, data: dict):
        """Save a JSON file to session directory."""
        session_dir = self._get_session_dir(session_id)
        filepath = session_dir / filename
        
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
    
    def load_json_file(self, session_id: str, filename: str) -> Optional[dict]:
        """Load a JSON file from session directory."""
        session_dir = self._get_session_dir(session_id)
        filepath = session_dir / filename
        
        if filepath.exists():
            with open(filepath, "r") as f:
                return json.load(f)
        return None


# Global session manager instance
session_manager = SessionManager()
