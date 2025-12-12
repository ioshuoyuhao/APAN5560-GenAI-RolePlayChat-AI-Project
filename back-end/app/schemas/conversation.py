"""
Pydantic schemas for Conversation endpoints.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ConversationCreate(BaseModel):
    """Schema for creating a new conversation."""

    character_id: int = Field(..., description="ID of the character to chat with")
    api_provider_id: int | None = Field(None, description="ID of the API provider (uses active if not specified)")
    title: str | None = Field(None, max_length=200, description="Conversation title")
    similarity_threshold: float = Field(0.5, ge=0.0, le=1.0, description="RAG similarity threshold")
    top_k: int = Field(5, ge=1, le=20, description="Number of RAG documents to retrieve")


class ConversationUpdate(BaseModel):
    """Schema for updating a conversation."""

    title: str | None = Field(None, max_length=200)
    api_provider_id: int | None = None
    similarity_threshold: float | None = Field(None, ge=0.0, le=1.0)
    top_k: int | None = Field(None, ge=1, le=20)


class ConversationRead(BaseModel):
    """Schema for reading a conversation (response)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    character_id: int | None
    api_provider_id: int | None
    title: str | None
    similarity_threshold: float | None
    top_k: int | None
    created_at: datetime
    updated_at: datetime

    # Nested character info for display
    character_name: str | None = None
    character_avatar: str | None = None


class ConversationSummary(BaseModel):
    """Lightweight schema for conversation lists."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    character_id: int | None
    title: str | None
    updated_at: datetime
    character_name: str | None = None
    character_avatar: str | None = None
    last_message_preview: str | None = None

