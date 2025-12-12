"""
Pydantic schemas for API Provider endpoints.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class ProviderTypeEnum(str, Enum):
    """Supported LLM API provider types."""

    OPENAI = "openai"  # OpenAI-compatible APIs (OpenAI, DeepSeek, Doubao, etc.)
    HUGGINGFACE = "huggingface"  # HuggingFace Inference API


class APIProviderBase(BaseModel):
    """Base schema with common fields."""

    name: str = Field(..., min_length=1, max_length=100, description="Provider name")
    provider_type: ProviderTypeEnum = Field(
        default=ProviderTypeEnum.OPENAI,
        description="Provider type: 'openai' for OpenAI-compatible APIs, 'huggingface' for HF Inference API",
    )
    base_url: str = Field(
        ..., min_length=1, max_length=500, description="API base URL"
    )
    api_key: str = Field(..., min_length=1, description="API key (stored securely)")
    chat_model_id: str = Field(
        ..., min_length=1, max_length=200, description="Chat model ID"
    )
    embedding_model_id: str = Field(
        default="",
        max_length=200,
        description="Embedding model ID (optional for HuggingFace)",
    )


class APIProviderCreate(APIProviderBase):
    """Schema for creating a new API provider."""

    pass


class APIProviderUpdate(BaseModel):
    """Schema for updating an API provider (all fields optional)."""

    name: str | None = Field(None, min_length=1, max_length=100)
    provider_type: ProviderTypeEnum | None = None
    base_url: str | None = Field(None, min_length=1, max_length=500)
    api_key: str | None = Field(None, min_length=1)
    chat_model_id: str | None = Field(None, min_length=1, max_length=200)
    embedding_model_id: str | None = Field(None, max_length=200)


class APIProviderRead(BaseModel):
    """Schema for reading an API provider (response)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    provider_type: ProviderTypeEnum
    base_url: str
    # Note: api_key is masked for security in responses
    api_key_masked: str = Field(description="Masked API key (e.g., sk-****xxxx)")
    chat_model_id: str
    embedding_model_id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_orm_with_masked_key(cls, obj) -> "APIProviderRead":
        """Create response with masked API key."""
        masked = cls._mask_api_key(obj.api_key)
        return cls(
            id=obj.id,
            name=obj.name,
            provider_type=ProviderTypeEnum(obj.provider_type),
            base_url=obj.base_url,
            api_key_masked=masked,
            chat_model_id=obj.chat_model_id,
            embedding_model_id=obj.embedding_model_id,
            is_active=obj.is_active,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )

    @staticmethod
    def _mask_api_key(key: str) -> str:
        """Mask API key for security (show first 3 and last 4 chars)."""
        if len(key) <= 8:
            return "*" * len(key)
        return f"{key[:3]}{'*' * (len(key) - 7)}{key[-4:]}"


class APIProviderTestResult(BaseModel):
    """Schema for API test result."""

    success: bool
    message: str
    latency_ms: float | None = None
    model_response: str | None = None

