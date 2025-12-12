"""
KBDocument model - Stores document chunks with vector embeddings for RAG.
"""

from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

# Default embedding dimension (OpenAI ada-002 / many other models use 1536)
# Can be adjusted based on the embedding model used
EMBEDDING_DIMENSION = 1536


class KBDocument(Base):
    """
    Stores document chunks with their vector embeddings.

    Each row represents one text chunk from an uploaded document.
    The embedding column stores the vector representation for similarity search.
    """

    __tablename__ = "kb_documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    kb_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("knowledge_bases.id", ondelete="CASCADE"), nullable=False
    )
    source_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    chunk_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)

    # Vector embedding for similarity search (pgvector)
    # Nullable to allow document upload before embedding is generated
    embedding = mapped_column(Vector(EMBEDDING_DIMENSION), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationship to knowledge base
    knowledge_base: Mapped["KnowledgeBase"] = relationship(
        "KnowledgeBase", back_populates="documents"
    )

    def __repr__(self) -> str:
        has_embedding = "✓" if self.embedding is not None else "✗"
        return f"<KBDocument(id={self.id}, kb_id={self.kb_id}, chunk={self.chunk_index}, emb={has_embedding})>"


# Import here to avoid circular imports
from app.models.knowledge_base import KnowledgeBase  # noqa: E402, F401
