"""
Discover Router - Endpoints for browsing and importing official characters.

Official characters are stored as static JSON files in the 'character cards' directory.
"""

import json
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.character import Character
from app.models.conversation import Conversation
from app.models.message import Message
from app.schemas.character import OfficialCharacter
from app.services.prompt_orchestrator import PromptOrchestrator

router = APIRouter(prefix="/discover", tags=["Discover"])

# Path to official character cards
# Development: relative to project root (.../APAN5560-GenAI-RolePlayChat-AI-Project/character cards)
# Docker: mounted at /app/character_cards
_DEV_PATH = Path(__file__).parent.parent.parent.parent / "character cards"
_DOCKER_PATH = Path("/app/character_cards")


def _get_character_cards_dir() -> Path:
    """Determine the correct path for character cards (Docker vs Dev)."""
    try:
        # Check Docker path first (has files with .json extension)
        if _DOCKER_PATH.exists() and list(_DOCKER_PATH.glob("*.json")):
            return _DOCKER_PATH
    except (PermissionError, OSError):
        pass
    return _DEV_PATH


CHARACTER_CARDS_DIR = _get_character_cards_dir()


def _load_official_characters() -> dict[str, dict]:
    """Load all official character cards from the file system."""
    characters = {}

    if not CHARACTER_CARDS_DIR.exists():
        return characters

    for json_file in CHARACTER_CARDS_DIR.glob("*.json"):
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                card_data = json.load(f)

            char_id = json_file.stem  # filename without extension

            # Parse v2 format
            if "data" in card_data:
                data = card_data["data"]
            else:
                data = card_data

            # Check for matching image
            avatar_url = None
            for ext in [".png", ".jpg", ".jpeg", ".webp"]:
                img_path = CHARACTER_CARDS_DIR / f"{char_id}{ext}"
                if img_path.exists():
                    avatar_url = f"/api/discover/characters/{char_id}/avatar"
                    break

            characters[char_id] = {
                "id": char_id,
                "name": data.get("name", char_id),
                "avatar_url": avatar_url,
                "description": data.get("description"),
                "tags": data.get("tags", []),
                "first_message": data.get("first_mes") or data.get("first_message"),
                "card_data": card_data,  # Full card for import
            }
        except (json.JSONDecodeError, IOError):
            continue

    return characters


@router.get("/characters", response_model=list[OfficialCharacter])
def list_official_characters():
    """
    List all official demo characters.

    Returns a grid-friendly list of characters available for import.
    """
    characters = _load_official_characters()
    return [
        OfficialCharacter(
            id=char["id"],
            name=char["name"],
            avatar_url=char["avatar_url"],
            description=char["description"],
            tags=char["tags"],
            first_message=char["first_message"],
        )
        for char in characters.values()
    ]


@router.get("/characters/{char_id}", response_model=OfficialCharacter)
def get_official_character(char_id: str):
    """Get details for a single official character."""
    characters = _load_official_characters()

    if char_id not in characters:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Official character '{char_id}' not found",
        )

    char = characters[char_id]
    return OfficialCharacter(
        id=char["id"],
        name=char["name"],
        avatar_url=char["avatar_url"],
        description=char["description"],
        tags=char["tags"],
        first_message=char["first_message"],
    )


@router.get("/characters/{char_id}/avatar")
def get_character_avatar(char_id: str):
    """Get the avatar image for an official character."""
    for ext in [".png", ".jpg", ".jpeg", ".webp"]:
        img_path = CHARACTER_CARDS_DIR / f"{char_id}{ext}"
        if img_path.exists():
            media_type = {
                ".png": "image/png",
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".webp": "image/webp",
            }.get(ext, "image/png")
            return FileResponse(img_path, media_type=media_type)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Avatar for character '{char_id}' not found",
    )


@router.post("/characters/{char_id}/import")
def import_official_character(char_id: str, db: Session = Depends(get_db)):
    """
    Import an official character and start a new conversation.

    This endpoint:
    1. Imports the character card into the database
    2. Creates a new conversation with that character
    3. Adds the character's first message (if any)

    Returns the new character_id and conversation_id.
    """
    characters = _load_official_characters()

    if char_id not in characters:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Official character '{char_id}' not found",
        )

    char_data = characters[char_id]
    card_data = char_data["card_data"]

    # Parse card data
    if "data" in card_data:
        data = card_data["data"]
    else:
        data = card_data

    # Create character
    character = Character(
        name=data.get("name", char_id),
        avatar_url=char_data["avatar_url"],
        description=data.get("description"),
        first_message=data.get("first_mes") or data.get("first_message"),
        personality_prompt=data.get("personality"),
        scenario_prompt=data.get("scenario"),
        example_dialogues_prompt=data.get("mes_example") or data.get("example_dialogues"),
        system_prompt=data.get("system_prompt"),
        tags=data.get("tags", []),
        card_json=card_data,
    )
    db.add(character)
    db.commit()
    db.refresh(character)

    # Create conversation
    conversation = Conversation(
        character_id=character.id,
        title=f"Chat with {character.name}",
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    # Add first message if available
    if character.first_message:
        orchestrator = PromptOrchestrator(db, conversation)
        first_msg_content = orchestrator.get_first_message()
        if first_msg_content:
            first_message = Message(
                conversation_id=conversation.id,
                role="assistant",
                content=first_msg_content,
            )
            db.add(first_message)
            db.commit()

    return {
        "character_id": character.id,
        "conversation_id": conversation.id,
        "message": f"Successfully imported '{character.name}' and started a new conversation",
    }


@router.get("/characters/{char_id}/download")
def download_character(char_id: str):
    """
    Download the character card JSON file.

    Note: For a full implementation, this should return a ZIP with JSON + PNG.
    For MVP, we just return the JSON file.
    """
    json_path = CHARACTER_CARDS_DIR / f"{char_id}.json"

    if not json_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character card for '{char_id}' not found",
        )

    return FileResponse(
        json_path,
        media_type="application/json",
        filename=f"{char_id}.json",
    )

