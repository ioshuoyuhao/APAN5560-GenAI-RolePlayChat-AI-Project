"""
Pydantic schemas for Knowledge Base endpoints.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class KnowledgeBaseBase(BaseModel):
    """Base schema with common fields."""

    name: str = Field(..., min_length=1, max_length=100, description="KB name")
    description: str | None = Field(None, description="Optional description")


class KnowledgeBaseCreate(KnowledgeBaseBase):
    """Schema for creating a new knowledge base."""

    pass


class KnowledgeBaseUpdate(BaseModel):
    """Schema for updating a knowledge base (all fields optional)."""

    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = None


class KBDocumentRead(BaseModel):
    """Schema for reading a KB document (response)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    kb_id: int
    source_filename: str | None
    chunk_index: int
    chunk_text: str
    has_embedding: bool = Field(default=False, description="Whether this chunk has an embedding")
    created_at: datetime

    @classmethod
    def model_validate(cls, obj, **kwargs):
        """Custom validation to compute has_embedding from ORM object."""
        # Check if embedding exists
        has_emb = obj.embedding is not None if hasattr(obj, "embedding") else False
        
        return cls(
            id=obj.id,
            kb_id=obj.kb_id,
            source_filename=obj.source_filename,
            chunk_index=obj.chunk_index,
            chunk_text=obj.chunk_text,
            has_embedding=has_emb,
            created_at=obj.created_at,
        )


class KnowledgeBaseRead(BaseModel):
    """Schema for reading a knowledge base (response)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    document_count: int = Field(default=0, description="Number of documents in this KB")
    created_at: datetime
    updated_at: datetime


class KnowledgeBaseWithDocuments(KnowledgeBaseRead):
    """Schema for reading a knowledge base with its documents."""

    documents: list[KBDocumentRead] = []


class UploadResponse(BaseModel):
    """Schema for file upload response."""

    success: bool
    message: str
    filename: str | None = None
    chunks_created: int = 0
    chunks_embedded: int = 0
    warning: str | None = None
