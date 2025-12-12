"""
RPGChat.AI - FastAPI Backend Application

Main entry point for the FastAPI application.
Run with: uv run fastapi dev back-end/app/main.py
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.config import settings
from app.core.database import engine
from app.routers import (
    api_providers_router,
    prompt_templates_router,
    knowledge_bases_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    - Startup: Verify database connection
    - Shutdown: Dispose database engine
    """
    # Startup: Test database connection
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("   Make sure PostgreSQL is running: docker compose up -d db")

    yield

    # Shutdown: Clean up database connections
    engine.dispose()
    print("🔌 Database connections closed")


app = FastAPI(
    title=settings.app_name,
    description="API for roleplay chatbot with RAG and OpenAI-compatible LLM support",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:5175"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(api_providers_router, prefix="/api/settings")
app.include_router(prompt_templates_router, prefix="/api/settings")
app.include_router(knowledge_bases_router, prefix="/api/settings")


@app.get("/")
def root():
    """Root endpoint - API status check."""
    return {
        "status": "API is running!",
        "version": "0.1.0",
        "app_name": settings.app_name,
    }


@app.get("/health")
def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy"}


@app.get("/health/db")
def health_check_db():
    """Database health check endpoint."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}
