"""
Pydantic schemas for Prompt Template endpoints.
"""

from pydantic import BaseModel, ConfigDict, Field


class PromptTemplateRead(BaseModel):
    """Schema for reading a prompt template (response)."""

    model_config = ConfigDict(from_attributes=True)

    key: str = Field(..., description="Unique template key (e.g., 'global_system')")
    title: str = Field(..., description="Display title for UI")
    description: str = Field(..., description="Description of what this template does")
    default_prompt: str = Field(..., description="Default prompt (read-only)")
    custom_prompt: str | None = Field(None, description="User-customized prompt")
    active_prompt: str = Field(..., description="Currently active prompt (custom or default)")


class PromptTemplateUpdate(BaseModel):
    """Schema for updating a prompt template (only custom_prompt is editable)."""

    custom_prompt: str | None = Field(
        None,
        description="Set custom prompt (null to use default)",
    )

