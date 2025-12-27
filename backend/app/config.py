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
        
        # Database Configuration (Neon PostgreSQL)
        self.use_database: bool = os.getenv("USE_DATABASE", "false").lower() == "true"
        self.database_url: str = os.getenv("DATABASE_URL", "")
        self.database_pool_size: int = int(os.getenv("DATABASE_POOL_SIZE", "10"))
        self.database_max_overflow: int = int(os.getenv("DATABASE_MAX_OVERFLOW", "20"))
        
        # R2 Object Storage Configuration (Cloudflare)
        self.use_r2_storage: bool = os.getenv("USE_R2_STORAGE", "false").lower() == "true"
        self.r2_account_id: str = os.getenv("R2_ACCOUNT_ID", "")
        self.r2_access_key_id: str = os.getenv("R2_ACCESS_KEY_ID", "")
        self.r2_secret_access_key: str = os.getenv("R2_SECRET_ACCESS_KEY", "")
        self.r2_bucket_name: str = os.getenv("R2_BUCKET_NAME", "ncd-inai-files")
        self.r2_endpoint: str = os.getenv("R2_ENDPOINT", f"https://{self.r2_account_id}.r2.cloudflarestorage.com")
        self.r2_public_url: str = os.getenv("R2_PUBLIC_URL", "https://files.yourdomain.com")



settings = Settings()
