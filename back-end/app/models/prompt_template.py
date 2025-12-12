"""
PromptTemplate model - Stores global prompt templates for roleplay chat.
"""

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class PromptTemplate(Base):
    """
    Stores global prompt templates used in chat orchestration.

    Each template has:
    - A unique key (e.g., "global_system", "roleplay_meta", "scene")
    - A title and description for UI display
    - A default_prompt (shipped with the app, read-only)
    - A custom_prompt (user-editable override)

    The 8 global templates are:
    1. global_system - Global system prompt
    2. real_time - Real-world time prompt
    3. roleplay_meta - Role-play meta prompt
    4. dialogue_system - Dialogue system prompt
    5. character_config - Character config prompt
    6. character_personality - Character personality prompt
    7. scene - Scene prompt
    8. example_dialogues - Example dialogues prompt
    """

    __tablename__ = "prompt_templates"

    # Use key as primary key (e.g., "global_system", "scene")
    key: Mapped[str] = mapped_column(String(50), primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    default_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    custom_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<PromptTemplate(key='{self.key}', title='{self.title}')>"

    def get_active_prompt(self) -> str:
        """Return custom_prompt if set, otherwise default_prompt."""
        return self.custom_prompt if self.custom_prompt else self.default_prompt

