"""
Conversations Router - Endpoints for managing chat sessions and messages.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.api_provider import APIProvider
from app.models.character import Character
from app.models.conversation import Conversation
from app.models.message import Message
from app.schemas.conversation import (
    ConversationCreate,
    ConversationRead,
    ConversationSummary,
    ConversationUpdate,
)
from app.schemas.message import ChatRequest, ChatResponse, MessageRead
from app.services.llm_client import LLMClient, LLMClientError, get_llm_client
from app.services.prompt_orchestrator import PromptOrchestrator

router = APIRouter(prefix="/conversations", tags=["Conversations"])


def _get_active_provider(db: Session) -> APIProvider | None:
    """Get the active API provider."""
    return db.execute(
        select(APIProvider).filter(APIProvider.is_active == True)
    ).scalar_one_or_none()


def _conversation_to_summary(conv: Conversation) -> ConversationSummary:
    """Convert a Conversation to ConversationSummary with nested data."""
    # Get last message preview
    last_message = (
        conv.messages[-1].content[:100] + "..."
        if conv.messages and len(conv.messages[-1].content) > 100
        else conv.messages[-1].content if conv.messages else None
    )

    return ConversationSummary(
        id=conv.id,
        character_id=conv.character_id,
        title=conv.title,
        updated_at=conv.updated_at,
        character_name=conv.character.name if conv.character else None,
        character_avatar=conv.character.avatar_url if conv.character else None,
        last_message_preview=last_message,
    )


def _conversation_to_read(conv: Conversation) -> ConversationRead:
    """Convert a Conversation to ConversationRead with nested data."""
    return ConversationRead(
        id=conv.id,
        character_id=conv.character_id,
        api_provider_id=conv.api_provider_id,
        title=conv.title,
        similarity_threshold=conv.similarity_threshold,
        top_k=conv.top_k,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        character_name=conv.character.name if conv.character else None,
        character_avatar=conv.character.avatar_url if conv.character else None,
    )


@router.get("/", response_model=list[ConversationSummary])
def list_conversations(db: Session = Depends(get_db)):
    """List all conversations, most recent first."""
    conversations = (
        db.execute(
            select(Conversation)
            .order_by(Conversation.updated_at.desc())
        )
        .scalars()
        .all()
    )
    return [_conversation_to_summary(c) for c in conversations]


@router.post("/", response_model=ConversationRead, status_code=status.HTTP_201_CREATED)
def create_conversation(data: ConversationCreate, db: Session = Depends(get_db)):
    """
    Create a new conversation.

    If api_provider_id is not specified, uses the active provider.
    Also creates the character's first message if available.
    """
    # Verify character exists
    character = db.get(Character, data.character_id)
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character with id {data.character_id} not found",
        )

    # Get API provider (specified or active)
    api_provider_id = data.api_provider_id
    if not api_provider_id:
        active_provider = _get_active_provider(db)
        if active_provider:
            api_provider_id = active_provider.id

    # Create conversation
    conversation = Conversation(
        character_id=data.character_id,
        api_provider_id=api_provider_id,
        title=data.title or f"Chat with {character.name}",
        similarity_threshold=data.similarity_threshold,
        top_k=data.top_k,
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    # Add character's first message if available
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

    return _conversation_to_read(conversation)


@router.get("/{conversation_id}", response_model=ConversationRead)
def get_conversation(conversation_id: int, db: Session = Depends(get_db)):
    """Get a conversation by ID."""
    conversation = db.get(Conversation, conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with id {conversation_id} not found",
        )
    return _conversation_to_read(conversation)


@router.put("/{conversation_id}", response_model=ConversationRead)
def update_conversation(
    conversation_id: int,
    data: ConversationUpdate,
    db: Session = Depends(get_db),
):
    """Update conversation settings."""
    conversation = db.get(Conversation, conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with id {conversation_id} not found",
        )

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(conversation, key, value)

    db.commit()
    db.refresh(conversation)
    return _conversation_to_read(conversation)


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(conversation_id: int, db: Session = Depends(get_db)):
    """Delete a conversation and all its messages."""
    conversation = db.get(Conversation, conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with id {conversation_id} not found",
        )

    db.delete(conversation)
    db.commit()


@router.get("/{conversation_id}/messages", response_model=list[MessageRead])
def get_messages(conversation_id: int, db: Session = Depends(get_db)):
    """Get all messages in a conversation."""
    conversation = db.get(Conversation, conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with id {conversation_id} not found",
        )

    messages = (
        db.execute(
            select(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
        )
        .scalars()
        .all()
    )
    return messages


@router.post("/{conversation_id}/messages", response_model=ChatResponse)
async def send_message(
    conversation_id: int,
    data: ChatRequest,
    db: Session = Depends(get_db),
):
    """
    Send a message and get an AI response.

    This endpoint:
    1. Saves the user's message
    2. Builds the prompt using PromptOrchestrator
    3. Calls the LLM API
    4. Saves and returns the assistant's response
    """
    # Get conversation with related data
    conversation = db.get(Conversation, conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with id {conversation_id} not found",
        )

    # Get API provider
    provider = conversation.api_provider
    if not provider:
        provider = _get_active_provider(db)
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No API provider configured. Please add and activate a provider in Settings.",
        )

    # 1. Save user message
    user_message = Message(
        conversation_id=conversation_id,
        role="user",
        content=data.content,
    )
    db.add(user_message)
    db.commit()
    db.refresh(user_message)

    # 2. Build prompt with orchestrator
    orchestrator = PromptOrchestrator(db, conversation)

    # Get query embedding for RAG if knowledge bases specified
    query_embedding = None
    if data.kb_ids:
        try:
            # Use OpenAI-compatible client for embeddings (HF doesn't support embeddings)
            llm_client = LLMClient(provider)
            embeddings = await llm_client.create_embedding(data.content)
            query_embedding = embeddings[0] if embeddings else None
        except LLMClientError:
            # Continue without RAG if embedding fails
            pass

    messages, rag_snippets_count = orchestrator.build_messages(
        user_input=data.content,
        kb_ids=data.kb_ids,
        query_embedding=query_embedding,
    )

    # 3. Call LLM API (uses factory to get appropriate client for provider type)
    try:
        llm_client = get_llm_client(provider)
        response = await llm_client.create_chat_completion(messages)
        assistant_content = (
            response.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "I apologize, but I couldn't generate a response.")
        )
    except LLMClientError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"LLM API error: {str(e)}",
        )

    # 4. Save assistant message
    assistant_message = Message(
        conversation_id=conversation_id,
        role="assistant",
        content=assistant_content,
    )
    db.add(assistant_message)
    db.commit()
    db.refresh(assistant_message)

    # Update conversation timestamp
    conversation.updated_at = assistant_message.created_at
    db.commit()

    return ChatResponse(
        user_message=MessageRead.model_validate(user_message),
        assistant_message=MessageRead.model_validate(assistant_message),
        rag_snippets_used=rag_snippets_count,
    )

