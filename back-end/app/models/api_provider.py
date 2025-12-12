"""
APIProvider model - Stores OpenAI-compatible LLM API provider configurations.
"""

from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ProviderType(str, Enum):
    """Supported LLM API provider types."""

    OPENAI = "openai"  # OpenAI-compatible APIs (OpenAI, DeepSeek, Doubao, etc.)
    HUGGINGFACE = "huggingface"  # HuggingFace Inference API


class APIProvider(Base):
    """
    Stores configuration for LLM API providers.

    Supports both OpenAI-compatible APIs and HuggingFace Inference API.
    Users can configure multiple providers and mark one as active for conversations.
    """

    __tablename__ = "api_providers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    provider_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default=ProviderType.OPENAI.value
    )
    base_url: Mapped[str] = mapped_column(String(500), nullable=False)
    api_key: Mapped[str] = mapped_column(Text, nullable=False)
    chat_model_id: Mapped[str] = mapped_column(String(200), nullable=False)
    embedding_model_id: Mapped[str] = mapped_column(String(200), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<APIProvider(id={self.id}, name='{self.name}', is_active={self.is_active})>"

