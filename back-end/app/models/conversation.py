"""
Conversation model - Stores chat sessions between user and character.
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Conversation(Base):
    """
    Represents a chat session with a character.

    Each conversation:
    - Is linked to a character (who the user is chatting with)
    - Is linked to an API provider (which LLM to use)
    - Contains multiple messages
    - Can optionally have attached knowledge bases (for RAG)
    """

    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Foreign keys
    character_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("characters.id", ondelete="SET NULL"), nullable=True
    )
    api_provider_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("api_providers.id", ondelete="SET NULL"), nullable=True
    )

    # Conversation metadata
    title: Mapped[str | None] = mapped_column(String(200), nullable=True)

    # RAG settings (stored per conversation)
    similarity_threshold: Mapped[float | None] = mapped_column(default=0.5)
    top_k: Mapped[int | None] = mapped_column(default=5)

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

    # Relationships
    character: Mapped["Character | None"] = relationship(
        "Character", back_populates="conversations"
    )
    api_provider: Mapped["APIProvider | None"] = relationship("APIProvider")
    messages: Mapped[list["Message"]] = relationship(
        "Message", back_populates="conversation", cascade="all, delete-orphan",
        order_by="Message.created_at"
    )

    def __repr__(self) -> str:
        return f"<Conversation(id={self.id}, character_id={self.character_id})>"


# Import here to avoid circular imports
from app.models.character import Character  # noqa: E402, F401
from app.models.api_provider import APIProvider  # noqa: E402, F401
from app.models.message import Message  # noqa: E402, F401

