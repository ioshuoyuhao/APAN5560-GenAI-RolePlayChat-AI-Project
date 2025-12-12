"""
Pydantic schemas for Character endpoints.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CharacterBase(BaseModel):
    """Base schema with common character fields."""

    name: str = Field(..., min_length=1, max_length=200, description="Character name")
    avatar_url: str | None = Field(None, max_length=500, description="Avatar image URL")
    description: str | None = Field(None, description="Character description")
    first_message: str | None = Field(None, description="Opening message from character")
    personality_prompt: str | None = Field(None, description="Personality description")
    scenario_prompt: str | None = Field(None, description="Scene/world setting")
    example_dialogues_prompt: str | None = Field(None, description="Example dialogues")
    system_prompt: str | None = Field(None, description="Character-specific system prompt")
    tags: list[str] | None = Field(None, description="Tags for categorization")


class CharacterCreate(CharacterBase):
    """Schema for creating a character manually."""

    pass


class CharacterImport(BaseModel):
    """Schema for importing a character from JSON card."""

    card_json: dict[str, Any] = Field(..., description="Raw character card JSON")
    avatar_url: str | None = Field(None, description="Avatar image URL")


class CharacterUpdate(BaseModel):
    """Schema for updating a character (all fields optional)."""

    name: str | None = Field(None, min_length=1, max_length=200)
    avatar_url: str | None = Field(None, max_length=500)
    description: str | None = None
    first_message: str | None = None
    personality_prompt: str | None = None
    scenario_prompt: str | None = None
    example_dialogues_prompt: str | None = None
    system_prompt: str | None = None
    tags: list[str] | None = None
    is_favorite: bool | None = None


class CharacterRead(BaseModel):
    """Schema for reading a character (response)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    avatar_url: str | None
    description: str | None
    first_message: str | None
    personality_prompt: str | None
    scenario_prompt: str | None
    example_dialogues_prompt: str | None
    system_prompt: str | None
    tags: list[str] | None
    is_favorite: bool
    created_at: datetime


class CharacterSummary(BaseModel):
    """Lightweight schema for character lists."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    avatar_url: str | None
    description: str | None
    tags: list[str] | None
    is_favorite: bool


class OfficialCharacter(BaseModel):
    """Schema for official characters in Discover."""

    id: str = Field(..., description="Unique identifier (filename without extension)")
    name: str
    avatar_url: str | None
    description: str | None
    tags: list[str] | None
    first_message: str | None

