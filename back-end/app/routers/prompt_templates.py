"""
Prompt Templates Router - CRUD endpoints for managing global prompt templates.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.prompt_template import PromptTemplate
from app.schemas.prompt_template import PromptTemplateRead, PromptTemplateUpdate

router = APIRouter(prefix="/prompt-templates", tags=["Prompt Templates"])


# Default prompt templates shipped with the app
DEFAULT_TEMPLATES = [
    {
        "key": "global_system",
        "title": "Global System Prompt",
        "description": "The main system prompt that sets the overall behavior of the AI.",
        "default_prompt": "You are a creative and immersive roleplay assistant. Respond thoughtfully and stay in character.",
    },
    {
        "key": "real_time",
        "title": "Real-World Time Prompt",
        "description": "Provides current date/time context to the AI.",
        "default_prompt": "Current date and time: {{current_time}}. Use this for temporal awareness in roleplay.",
    },
    {
        "key": "roleplay_meta",
        "title": "Role-Play Meta Prompt",
        "description": "Defines the roleplay style and conventions (tavern RP style).",
        "default_prompt": "This is a tavern-style roleplay. Use *asterisks* for actions and descriptions. Stay immersive and creative. Address the user as {{user}} and play as {{char}}.",
    },
    {
        "key": "dialogue_system",
        "title": "Dialogue System Prompt",
        "description": "Defines how dialogue should be formatted and presented.",
        "default_prompt": "Format dialogue naturally. Use quotation marks for speech. Describe emotions and reactions. Keep responses engaging but concise.",
    },
    {
        "key": "character_config",
        "title": "Character Config Prompt",
        "description": "Template for injecting character metadata.",
        "default_prompt": "Character: {{char_name}}\nDescription: {{char_description}}\nPersonality: {{char_personality}}",
    },
    {
        "key": "character_personality",
        "title": "Character Personality Prompt",
        "description": "Emphasizes the character's personality traits.",
        "default_prompt": "Stay true to {{char}}'s personality. Be consistent with their traits, speech patterns, and mannerisms.",
    },
    {
        "key": "scene",
        "title": "Scene Prompt",
        "description": "Sets the scene and environment for the roleplay.",
        "default_prompt": "Scene: {{scenario}}\n\nMaintain awareness of the environment and use it in your responses.",
    },
    {
        "key": "example_dialogues",
        "title": "Example Dialogues Prompt",
        "description": "Few-shot examples to guide the AI's response style.",
        "default_prompt": "Example interactions:\n{{example_dialogues}}\n\nUse these as a guide for tone and style.",
    },
]


def _to_read_schema(template: PromptTemplate) -> PromptTemplateRead:
    """Convert ORM object to read schema with active_prompt."""
    return PromptTemplateRead(
        key=template.key,
        title=template.title,
        description=template.description,
        default_prompt=template.default_prompt,
        custom_prompt=template.custom_prompt,
        active_prompt=template.get_active_prompt(),
    )


@router.get("/", response_model=list[PromptTemplateRead])
def list_prompt_templates(db: Session = Depends(get_db)):
    """List all prompt templates."""
    templates = db.execute(select(PromptTemplate)).scalars().all()
    return [_to_read_schema(t) for t in templates]


@router.get("/{key}", response_model=PromptTemplateRead)
def get_prompt_template(key: str, db: Session = Depends(get_db)):
    """Get a single prompt template by key."""
    template = db.get(PromptTemplate, key)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prompt template with key '{key}' not found",
        )
    return _to_read_schema(template)


@router.put("/{key}", response_model=PromptTemplateRead)
def update_prompt_template(
    key: str, data: PromptTemplateUpdate, db: Session = Depends(get_db)
):
    """
    Update a prompt template's custom_prompt.

    Set custom_prompt to null to revert to default.
    """
    template = db.get(PromptTemplate, key)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prompt template with key '{key}' not found",
        )

    template.custom_prompt = data.custom_prompt
    db.commit()
    db.refresh(template)
    return _to_read_schema(template)


@router.delete("/{key}", response_model=PromptTemplateRead)
def reset_prompt_template(key: str, db: Session = Depends(get_db)):
    """Reset a prompt template to its default (clears custom_prompt)."""
    template = db.get(PromptTemplate, key)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prompt template with key '{key}' not found",
        )

    template.custom_prompt = None
    db.commit()
    db.refresh(template)
    return _to_read_schema(template)


@router.post("/seed", response_model=list[PromptTemplateRead])
def seed_default_templates(db: Session = Depends(get_db)):
    """
    Seed the database with default prompt templates.

    This endpoint creates the 8 default templates if they don't exist.
    Safe to call multiple times - existing templates are not modified.
    """
    created = []
    for template_data in DEFAULT_TEMPLATES:
        existing = db.get(PromptTemplate, template_data["key"])
        if not existing:
            template = PromptTemplate(**template_data)
            db.add(template)
            created.append(template)

    db.commit()

    # Return all templates (including newly created ones)
    templates = db.execute(select(PromptTemplate)).scalars().all()
    return [_to_read_schema(t) for t in templates]

