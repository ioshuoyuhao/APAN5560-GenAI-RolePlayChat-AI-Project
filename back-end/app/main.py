"""
RPGChat.AI - FastAPI Backend Application

Main entry point for the FastAPI application.
Run with: uv run fastapi dev back-end/app/main.py
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.core.database import engine


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


# Import text for SQL execution
from sqlalchemy import text

app = FastAPI(
    title=settings.app_name,
    description="API for roleplay chatbot with RAG and OpenAI-compatible LLM support",
    version="0.1.0",
    lifespan=lifespan,
)


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


# TODO: Add routers as development progresses
# from app.routers import api_providers, prompt_templates, characters, conversations
# app.include_router(api_providers.router, prefix="/api/settings", tags=["API Providers"])
# app.include_router(prompt_templates.router, prefix="/api/settings", tags=["Prompt Templates"])
