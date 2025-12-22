"""
NCD INAI Backend - Main Application Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from app.config import settings
from app.routers import session, intent, questions, blueprint, generate, edit, deploy, theme, assets


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    print("🚀 NCD INAI Backend starting...")
    print(f"📁 Projects directory: {settings.projects_dir.absolute()}")
    yield
    # Shutdown
    print("👋 NCD INAI Backend shutting down...")


app = FastAPI(
    title="NCD INAI",
    description="AI-powered website builder backend",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for project previews
app.mount("/projects", StaticFiles(directory=str(settings.projects_dir)), name="projects")

# Register Routers
app.include_router(session.router, prefix="/api/session", tags=["Session"])
app.include_router(intent.router, prefix="/api", tags=["Intent"])
app.include_router(questions.router, prefix="/api", tags=["Questions"])
app.include_router(blueprint.router, prefix="/api", tags=["Blueprint"])
app.include_router(generate.router, prefix="/api", tags=["Generate"])
app.include_router(edit.router, prefix="/api", tags=["Edit"])
app.include_router(deploy.router, prefix="/api", tags=["Deploy"])
app.include_router(theme.router, prefix="/api", tags=["Theme"])
app.include_router(assets.router, prefix="/api", tags=["Assets"])


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "NCD INAI",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "llm_configured": bool(settings.groq_api_key),
        "projects_dir": str(settings.projects_dir.absolute())
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
