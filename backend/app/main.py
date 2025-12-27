"""
NCD INAI Backend - Main Application Entry Point
Production-ready with structured architecture
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.routers import session_database, intent, questions, blueprint, generate, edit, deploy, theme, assets, chat, dashboard

# Import new core infrastructure
from app.core.logging import setup_logging
from app.api.middleware.error_handler import setup_exception_handlers
from app.api.middleware.rate_limit import setup_rate_limiting

# Setup logging first
setup_logging(
    log_level="DEBUG" if settings.debug else "INFO",
    log_file="logs/ncd_inai.log" if not settings.debug else None,
    enable_colors=True
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("🚀 NCD INAI Backend starting...")
    logger.info(f"📁 Projects directory: {settings.projects_dir.absolute()}")
    logger.info(f"🗄️ Database: {'Enabled' if settings.use_database else 'Disabled'}")
    logger.info(f"☁️ R2 Storage: {'Enabled' if settings.use_r2_storage else 'Disabled'}")
    logger.info(f"🔧 Debug mode: {settings.debug}")
    
    yield
    
    # Shutdown
    logger.info("👋 NCD INAI Backend shutting down...")


app = FastAPI(
    title="NCD INAI",
    description="AI-powered website builder backend - Production Ready",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,  # Disable docs in production
    redoc_url="/redoc" if settings.debug else None
)

# ==================== MIDDLEWARE SETUP ====================

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate Limiting (60 requests per minute)
setup_rate_limiting(app, requests_per_minute=60)

# Exception Handlers (must be last)
setup_exception_handlers(app)

logger.info("✅ Middleware configured")

# ==================== STATIC FILES ====================

# Mount static files for project previews
app.mount("/projects", StaticFiles(directory=str(settings.projects_dir)), name="projects")

# ==================== ROUTER REGISTRATION ====================

app.include_router(session_database.router, prefix="/api/session", tags=["Session"])
app.include_router(intent.router, prefix="/api", tags=["Intent"])
app.include_router(questions.router, prefix="/api", tags=["Questions"])
app.include_router(blueprint.router, prefix="/api", tags=["Blueprint"])
app.include_router(generate.router, prefix="/api", tags=["Generate"])
app.include_router(edit.router, prefix="/api", tags=["Edit"])
app.include_router(deploy.router, prefix="/api", tags=["Deploy"])
app.include_router(theme.router, prefix="/api", tags=["Theme"])
app.include_router(assets.router, prefix="/api", tags=["Assets"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])

logger.info("✅ Routers registered")

# ==================== HEALTH ENDPOINTS ====================

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "NCD INAI",
        "version": "2.0.0",
        "architecture": "production-ready"
    }


@app.get("/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "services": {
            "llm": bool(settings.groq_api_key),
            "database": settings.use_database,
            "r2_storage": settings.use_r2_storage
        },
        "config": {
            "projects_dir": str(settings.projects_dir.absolute()),
            "debug_mode": settings.debug
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info"
    )
