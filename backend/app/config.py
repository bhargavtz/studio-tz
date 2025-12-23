"""
NCD INAI Backend - Configuration Module
"""

import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""
    
    def __init__(self):
        # LLM Configuration
        self.groq_api_key: str = os.getenv("GROQ_API_KEY", "")
        
        # Validate required environment variables
        if not self.groq_api_key:
            raise ValueError(
                "GROQ_API_KEY environment variable is required. "
                "Please add it to your .env file in the backend directory."
            )
        
        # Main model for code generation, blueprints, etc. (Kimi)
        self.llm_model: str = os.getenv("LLM_MODEL", "moonshotai/kimi-k2-instruct-0905")
        
        # Question generation model (Llama - faster for simple tasks)
        self.question_model: str = os.getenv("QUESTION_MODEL", "llama-3.3-70b-versatile")
        
        self.llm_temperature: float = 0.7
        
        # Server Configuration
        self.host: str = os.getenv("HOST", "0.0.0.0")
        self.port: int = int(os.getenv("PORT", "8000"))
        self.debug: bool = os.getenv("DEBUG", "true").lower() == "true"
        
        # CORS Configuration
        cors_origins_str = os.getenv(
            "CORS_ORIGINS", 
            "http://localhost:3000,http://127.0.0.1:3000"
        )
        self.cors_origins: List[str] = [origin.strip() for origin in cors_origins_str.split(",")]
        
        # Projects Directory
        self.projects_dir: Path = Path(os.getenv("PROJECTS_DIR", "./projects"))
        
        # Session Settings
        self.session_expiry_hours: int = 24
        self.max_sessions: int = 100
        
        # Ensure projects directory exists
        self.projects_dir.mkdir(parents=True, exist_ok=True)



settings = Settings()
