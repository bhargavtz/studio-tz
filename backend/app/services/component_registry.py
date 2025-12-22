"""
NCD INAI - Component Registry

Tracks all editable components in generated websites.
"""

from typing import Dict, List, Any, Optional
from pathlib import Path
import json
from datetime import datetime


class ComponentRegistry:
    """Registry for tracking editable components with NCD IDs."""
    
    def __init__(self, session_dir: Path):
        self.session_dir = session_dir
        self.registry_file = session_dir / "component_registry.json"
        self.components: Dict[str, Dict[str, Any]] = {}
        self._load()
    
    def _load(self):
        """Load registry from disk."""
        if self.registry_file.exists():
            with open(self.registry_file, 'r') as f:
                self.components = json.load(f)
    
    def _save(self):
        """Save registry to disk."""
        with open(self.registry_file, 'w') as f:
            json.dump(self.components, f, indent=2)
    
    def register(
        self,
        ncd_id: str,
        file_path: str,
        element_type: str,
        edit_type: str,
        selector: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Register a component."""
        self.components[ncd_id] = {
            "file": file_path,
            "type": element_type,
            "edit_type": edit_type,
            "selector": selector,
            "metadata": metadata or {},
            "created_at": datetime.utcnow().isoformat()
        }
        self._save()
    
    def get(self, ncd_id: str) -> Optional[Dict[str, Any]]:
        """Get component info by NCD ID."""
        return self.components.get(ncd_id)
    
    def get_by_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Get all components in a file."""
        return [
            {"ncd_id": ncd_id, **info}
            for ncd_id, info in self.components.items()
            if info["file"] == file_path
        ]
    
    def list_all(self) -> Dict[str, Dict[str, Any]]:
        """List all registered components."""
        return self.components
