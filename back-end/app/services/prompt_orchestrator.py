"""
Prompt Orchestrator - Builds the full message array for LLM chat completions.

This service orchestrates all prompts for a conversation:
1. Global system prompt
2. Real-world time prompt
3. Role-play meta prompt
4. Dialogue system prompt
5. Character config prompt
6. Character personality prompt
7. Scene prompt
8. Example dialogues prompt
9. RAG snippets (if knowledge base attached)
10. Conversation history
11. Latest user message
"""

from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.character import Character
from app.models.conversation import Conversation
from app.models.kb_document import KBDocument
from app.models.message import Message
from app.models.prompt_template import PromptTemplate


class PromptOrchestrator:
    """
    Builds the complete prompt array for LLM API calls.

    Usage:
        orchestrator = PromptOrchestrator(db, conversation)
        messages = await orchestrator.build_messages(
            user_input="Hello!",
            kb_ids=[1, 2],
            query_embedding=[0.1, 0.2, ...]
        )
    """

    # Template keys in order of appearance
    TEMPLATE_KEYS = [
        "global_system",
        "real_time",
        "roleplay_meta",
        "dialogue_system",
        "character_config",
        "character_personality",
        "scene",
        "example_dialogues",
    ]

    def __init__(
        self,
        db: Session,
        conversation: Conversation,
        max_history_messages: int = 20,
    ):
        """
        Initialize the prompt orchestrator.

        Args:
            db: Database session
            conversation: The conversation to build prompts for
            max_history_messages: Maximum number of history messages to include
        """
        self.db = db
        self.conversation = conversation
        self.character = conversation.character
        self.max_history_messages = max_history_messages

    def _load_templates(self) -> dict[str, str]:
        """Load all prompt templates from database."""
        templates = {}
        result = self.db.execute(select(PromptTemplate)).scalars().all()
        for template in result:
            templates[template.key] = template.get_active_prompt()
        return templates

    def _render_template(self, template: str, variables: dict[str, str]) -> str:
        """
        Render a template with variables.

        Supports placeholders like {{char}}, {{user}}, {{date}}, etc.
        """
        rendered = template
        for key, value in variables.items():
            placeholder = "{{" + key + "}}"
            rendered = rendered.replace(placeholder, value or "")
        return rendered

    def _get_template_variables(self) -> dict[str, str]:
        """Get variables for template rendering."""
        char_name = self.character.name if self.character else "Assistant"
        return {
            "char": char_name,
            "user": "User",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.now().strftime("%H:%M"),
            "day": datetime.now().strftime("%A"),
        }

    def _build_character_prompts(self, variables: dict[str, str]) -> list[dict[str, str]]:
        """Build character-specific prompts."""
        prompts = []
        if not self.character:
            return prompts

        # Character description/config
        if self.character.description:
            prompts.append({
                "role": "system",
                "content": f"Character Description: {self.character.description}"
            })

        # Character personality
        if self.character.personality_prompt:
            prompts.append({
                "role": "system",
                "content": f"Character Personality: {self.character.personality_prompt}"
            })

        # Scenario/scene
        if self.character.scenario_prompt:
            prompts.append({
                "role": "system",
                "content": f"Scene: {self.character.scenario_prompt}"
            })

        # Example dialogues
        if self.character.example_dialogues_prompt:
            rendered = self._render_template(
                self.character.example_dialogues_prompt, variables
            )
            prompts.append({
                "role": "system",
                "content": f"Example Dialogue:\n{rendered}"
            })

        # Character system prompt
        if self.character.system_prompt:
            prompts.append({
                "role": "system",
                "content": self.character.system_prompt
            })

        return prompts

    def _build_rag_prompt(
        self,
        kb_ids: list[int],
        query_embedding: list[float],
    ) -> str | None:
        """
        Build RAG context by querying similar documents.

        Uses pgvector similarity search to find relevant snippets.
        """
        if not kb_ids or not query_embedding:
            return None

        # Get RAG settings from conversation
        threshold = self.conversation.similarity_threshold or 0.5
        top_k = self.conversation.top_k or 5

        # Query similar documents using pgvector
        # Note: Using L2 distance, smaller is better
        # For cosine similarity, we use <=> operator
        from pgvector.sqlalchemy import Vector

        results = (
            self.db.query(KBDocument)
            .filter(KBDocument.kb_id.in_(kb_ids))
            .filter(KBDocument.embedding.isnot(None))
            .order_by(KBDocument.embedding.cosine_distance(query_embedding))
            .limit(top_k)
            .all()
        )

        if not results:
            return None

        # Build RAG context
        snippets = []
        for i, doc in enumerate(results, 1):
            source = doc.source_filename or "Unknown"
            snippets.append(f"[{i}] (Source: {source})\n{doc.chunk_text}")

        return "Relevant Knowledge:\n" + "\n\n".join(snippets)

    def _get_conversation_history(self) -> list[dict[str, str]]:
        """Get recent conversation history as message dicts."""
        messages = (
            self.db.query(Message)
            .filter(Message.conversation_id == self.conversation.id)
            .order_by(Message.created_at.desc())
            .limit(self.max_history_messages)
            .all()
        )

        # Reverse to get chronological order
        messages = list(reversed(messages))

        return [msg.to_dict() for msg in messages]

    def build_messages(
        self,
        user_input: str,
        kb_ids: list[int] | None = None,
        query_embedding: list[float] | None = None,
    ) -> tuple[list[dict[str, str]], int]:
        """
        Build the complete message array for LLM API call.

        Args:
            user_input: The user's latest message
            kb_ids: Optional list of knowledge base IDs for RAG
            query_embedding: Optional embedding of user query for RAG search

        Returns:
            Tuple of (messages list, number of RAG snippets used)
        """
        messages: list[dict[str, str]] = []
        variables = self._get_template_variables()
        templates = self._load_templates()
        rag_snippets_count = 0

        # 1-4. Global templates (if they exist)
        for key in ["global_system", "real_time", "roleplay_meta", "dialogue_system"]:
            if key in templates and templates[key]:
                rendered = self._render_template(templates[key], variables)
                messages.append({"role": "system", "content": rendered})

        # 5-8. Character-specific prompts
        char_prompts = self._build_character_prompts(variables)
        messages.extend(char_prompts)

        # 9. RAG snippets (if knowledge bases attached)
        if kb_ids and query_embedding:
            rag_context = self._build_rag_prompt(kb_ids, query_embedding)
            if rag_context:
                messages.append({"role": "system", "content": rag_context})
                rag_snippets_count = rag_context.count("[")  # Count snippets

        # 10. Conversation history
        history = self._get_conversation_history()
        messages.extend(history)

        # 11. Latest user message
        messages.append({"role": "user", "content": user_input})

        return messages, rag_snippets_count

    def get_first_message(self) -> str | None:
        """Get the character's first message for new conversations."""
        if self.character and self.character.first_message:
            variables = self._get_template_variables()
            return self._render_template(self.character.first_message, variables)
        return None

