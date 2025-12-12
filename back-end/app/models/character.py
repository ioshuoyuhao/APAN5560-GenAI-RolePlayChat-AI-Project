"""
Character model - Stores imported character cards for roleplay chat.
"""

from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Character(Base):
    """
    Stores character cards imported from Discover or local uploads.

    Compatible with SillyTavern v2 card format:
    - name, description, personality, scenario, first_message
    - example_dialogues, system_prompt, tags
    - card_json stores the raw imported JSON for future compatibility
    """

    __tablename__ = "characters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    first_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    personality_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    scenario_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    example_dialogues_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    system_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Store raw JSON from card for future compatibility
    card_json: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    # Tags for filtering/search
    tags: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)

    # User preferences
    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    conversations: Mapped[list["Conversation"]] = relationship(
        "Conversation", back_populates="character", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Character(id={self.id}, name='{self.name}')>"


# Import here to avoid circular imports
from app.models.conversation import Conversation  # noqa: E402, F401

