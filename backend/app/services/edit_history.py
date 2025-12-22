"""
NCD INAI - Edit History Manager

Manages diff-based change history for undo/redo.
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import json
from datetime import datetime


class EditHistory:
    """Manages edit history with diff snapshots."""
    
    def __init__(self, session_dir: Path):
        self.session_dir = session_dir
        self.history_dir = session_dir / ".history"
        self.history_dir.mkdir(exist_ok=True)
        self.current_version = self._get_latest_version()
    
    def _get_latest_version(self) -> int:
        """Get the latest version number."""
        versions = [
            int(f.stem)
            for f in self.history_dir.glob("*.json")
            if f.stem.isdigit()
        ]
        return max(versions) if versions else 0
    
    def save_diff(
        self,
        file_path: str,
        ncd_id: str,
        before: Any,
        after: Any,
        edit_type: str
    ) -> int:
        """Save a diff snapshot."""
        self.current_version += 1
        
        diff = {
            "version": self.current_version,
            "file": file_path,
            "ncd_id": ncd_id,
            "edit_type": edit_type,
            "before": before,
            "after": after,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        diff_file = self.history_dir / f"{self.current_version:06d}.json"
        with open(diff_file, 'w') as f:
            json.dump(diff, f, indent=2)
        
        return self.current_version
    
    def get_diff(self, version: int) -> Optional[Dict[str, Any]]:
        """Get a specific diff."""
        diff_file = self.history_dir / f"{version:06d}.json"
        if diff_file.exists():
            with open(diff_file, 'r') as f:
                return json.load(f)
        return None
    
    def get_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent history."""
        history = []
        for version in range(self.current_version, max(0, self.current_version - limit), -1):
            diff = self.get_diff(version)
            if diff:
                history.append(diff)
        return history
    
    def rollback_to(self, version: int) -> List[Dict[str, Any]]:
        """Get all diffs needed to rollback to a version."""
        if version > self.current_version or version < 0:
            raise ValueError(f"Invalid version: {version}")
        
        # Get all diffs from current to target (in reverse)
        diffs_to_reverse = []
        for v in range(self.current_version, version, -1):
            diff = self.get_diff(v)
            if diff:
                diffs_to_reverse.append(diff)
        
        return diffs_to_reverse
