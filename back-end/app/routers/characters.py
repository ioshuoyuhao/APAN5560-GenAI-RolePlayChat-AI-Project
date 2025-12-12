"""
Characters Router - CRUD endpoints for managing imported characters.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.character import Character
from app.schemas.character import (
    CharacterCreate,
    CharacterImport,
    CharacterRead,
    CharacterSummary,
    CharacterUpdate,
)

router = APIRouter(prefix="/characters", tags=["Characters"])


def _parse_card_json(card_json: dict) -> dict:
    """
    Parse a SillyTavern-style character card JSON.

    Supports both v1 (flat) and v2 (nested 'data' field) formats.
    """
    # Check if it's v2 format with nested 'data' field
    if "data" in card_json and isinstance(card_json["data"], dict):
        data = card_json["data"]
    else:
        # v1 format - fields at top level
        data = card_json

    return {
        "name": data.get("name", "Unknown"),
        "description": data.get("description"),
        "first_message": data.get("first_mes") or data.get("first_message"),
        "personality_prompt": data.get("personality"),
        "scenario_prompt": data.get("scenario"),
        "example_dialogues_prompt": data.get("mes_example") or data.get("example_dialogues"),
        "system_prompt": data.get("system_prompt"),
        "tags": data.get("tags", []),
    }


@router.get("/", response_model=list[CharacterSummary])
def list_characters(
    favorite_only: bool = False,
    db: Session = Depends(get_db),
):
    """List all imported characters."""
    query = select(Character).order_by(Character.is_favorite.desc(), Character.created_at.desc())
    if favorite_only:
        query = query.filter(Character.is_favorite == True)

    characters = db.execute(query).scalars().all()
    return characters


@router.post("/", response_model=CharacterRead, status_code=status.HTTP_201_CREATED)
def create_character(data: CharacterCreate, db: Session = Depends(get_db)):
    """Create a new character manually."""
    character = Character(**data.model_dump())
    db.add(character)
    db.commit()
    db.refresh(character)
    return character


@router.post("/import", response_model=CharacterRead, status_code=status.HTTP_201_CREATED)
def import_character(data: CharacterImport, db: Session = Depends(get_db)):
    """
    Import a character from a JSON card.

    Supports SillyTavern v1 and v2 card formats.
    """
    parsed = _parse_card_json(data.card_json)

    character = Character(
        name=parsed["name"],
        avatar_url=data.avatar_url,
        description=parsed["description"],
        first_message=parsed["first_message"],
        personality_prompt=parsed["personality_prompt"],
        scenario_prompt=parsed["scenario_prompt"],
        example_dialogues_prompt=parsed["example_dialogues_prompt"],
        system_prompt=parsed["system_prompt"],
        tags=parsed["tags"],
        card_json=data.card_json,
    )

    db.add(character)
    db.commit()
    db.refresh(character)
    return character


@router.get("/{character_id}", response_model=CharacterRead)
def get_character(character_id: int, db: Session = Depends(get_db)):
    """Get a single character by ID."""
    character = db.get(Character, character_id)
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character with id {character_id} not found",
        )
    return character


@router.put("/{character_id}", response_model=CharacterRead)
def update_character(
    character_id: int,
    data: CharacterUpdate,
    db: Session = Depends(get_db),
):
    """Update a character."""
    character = db.get(Character, character_id)
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character with id {character_id} not found",
        )

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(character, key, value)

    db.commit()
    db.refresh(character)
    return character


@router.delete("/{character_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_character(character_id: int, db: Session = Depends(get_db)):
    """Delete a character and all associated conversations."""
    character = db.get(Character, character_id)
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character with id {character_id} not found",
        )

    db.delete(character)
    db.commit()


@router.post("/{character_id}/favorite", response_model=CharacterRead)
def toggle_favorite(character_id: int, db: Session = Depends(get_db)):
    """Toggle the favorite status of a character."""
    character = db.get(Character, character_id)
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character with id {character_id} not found",
        )

    character.is_favorite = not character.is_favorite
    db.commit()
    db.refresh(character)
    return character

