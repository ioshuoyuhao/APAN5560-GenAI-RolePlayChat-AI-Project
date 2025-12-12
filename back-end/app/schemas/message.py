"""
Pydantic schemas for Message endpoints.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


MessageRole = Literal["user", "assistant", "system"]


class MessageCreate(BaseModel):
    """Schema for sending a new message."""

    content: str = Field(..., min_length=1, description="Message content")


class MessageRead(BaseModel):
    """Schema for reading a message (response)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    conversation_id: int
    role: MessageRole
    content: str
    created_at: datetime


class ChatRequest(BaseModel):
    """Schema for chat request (send message and get reply)."""

    content: str = Field(..., min_length=1, description="User message content")
    # Optional: attach knowledge bases for RAG
    kb_ids: list[int] | None = Field(None, description="Knowledge base IDs to use for RAG")


class ChatResponse(BaseModel):
    """Schema for chat response."""

    user_message: MessageRead
    assistant_message: MessageRead
    rag_snippets_used: int = Field(0, description="Number of RAG snippets injected")

