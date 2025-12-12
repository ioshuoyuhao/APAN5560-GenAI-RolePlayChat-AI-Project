"""
Knowledge Bases Router - CRUD endpoints for managing knowledge bases.
"""

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.api_provider import APIProvider
from app.models.kb_document import KBDocument
from app.models.knowledge_base import KnowledgeBase
from app.schemas.knowledge_base import (
    KBDocumentRead,
    KnowledgeBaseCreate,
    KnowledgeBaseRead,
    KnowledgeBaseUpdate,
    KnowledgeBaseWithDocuments,
    UploadResponse,
)
from app.services.chunker import chunk_file_content
from app.services.llm_client import LLMClient, LLMClientError

router = APIRouter(prefix="/knowledge-bases", tags=["Knowledge Bases"])

# Supported file types for upload
SUPPORTED_EXTENSIONS = {".txt", ".md", ".markdown"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def _to_read_schema(kb: KnowledgeBase, doc_count: int = 0) -> KnowledgeBaseRead:
    """Convert ORM object to read schema with document count."""
    return KnowledgeBaseRead(
        id=kb.id,
        name=kb.name,
        description=kb.description,
        document_count=doc_count,
        created_at=kb.created_at,
        updated_at=kb.updated_at,
    )


def _get_active_provider(db: Session) -> APIProvider | None:
    """Get the currently active API provider."""
    return db.execute(
        select(APIProvider).where(APIProvider.is_active == True)
    ).scalar_one_or_none()


@router.get("/", response_model=list[KnowledgeBaseRead])
def list_knowledge_bases(db: Session = Depends(get_db)):
    """List all knowledge bases with document counts."""
    # Query KBs with document counts
    stmt = (
        select(KnowledgeBase, func.count(KBDocument.id).label("doc_count"))
        .outerjoin(KBDocument, KnowledgeBase.id == KBDocument.kb_id)
        .group_by(KnowledgeBase.id)
    )
    results = db.execute(stmt).all()
    return [_to_read_schema(kb, doc_count) for kb, doc_count in results]


@router.post("/", response_model=KnowledgeBaseRead, status_code=status.HTTP_201_CREATED)
def create_knowledge_base(data: KnowledgeBaseCreate, db: Session = Depends(get_db)):
    """Create a new knowledge base."""
    kb = KnowledgeBase(**data.model_dump())
    db.add(kb)
    db.commit()
    db.refresh(kb)
    return _to_read_schema(kb, 0)


@router.get("/{kb_id}", response_model=KnowledgeBaseWithDocuments)
def get_knowledge_base(kb_id: int, db: Session = Depends(get_db)):
    """Get a single knowledge base with its documents."""
    kb = db.get(KnowledgeBase, kb_id)
    if not kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Knowledge base with id {kb_id} not found",
        )

    # Get document count
    doc_count = db.scalar(
        select(func.count(KBDocument.id)).where(KBDocument.kb_id == kb_id)
    )

    return KnowledgeBaseWithDocuments(
        id=kb.id,
        name=kb.name,
        description=kb.description,
        document_count=doc_count or 0,
        created_at=kb.created_at,
        updated_at=kb.updated_at,
        documents=[KBDocumentRead.model_validate(d) for d in kb.documents],
    )


@router.put("/{kb_id}", response_model=KnowledgeBaseRead)
def update_knowledge_base(
    kb_id: int, data: KnowledgeBaseUpdate, db: Session = Depends(get_db)
):
    """Update a knowledge base."""
    kb = db.get(KnowledgeBase, kb_id)
    if not kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Knowledge base with id {kb_id} not found",
        )

    # Update only provided fields
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(kb, key, value)

    db.commit()
    db.refresh(kb)

    doc_count = db.scalar(
        select(func.count(KBDocument.id)).where(KBDocument.kb_id == kb_id)
    )
    return _to_read_schema(kb, doc_count or 0)


@router.delete("/{kb_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_knowledge_base(kb_id: int, db: Session = Depends(get_db)):
    """Delete a knowledge base and all its documents."""
    kb = db.get(KnowledgeBase, kb_id)
    if not kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Knowledge base with id {kb_id} not found",
        )

    db.delete(kb)
    db.commit()


# Document endpoints


@router.get("/{kb_id}/documents", response_model=list[KBDocumentRead])
def list_kb_documents(kb_id: int, db: Session = Depends(get_db)):
    """List all documents in a knowledge base."""
    kb = db.get(KnowledgeBase, kb_id)
    if not kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Knowledge base with id {kb_id} not found",
        )

    return [KBDocumentRead.model_validate(d) for d in kb.documents]


@router.delete(
    "/{kb_id}/documents/{doc_id}", status_code=status.HTTP_204_NO_CONTENT
)
def delete_kb_document(kb_id: int, doc_id: int, db: Session = Depends(get_db)):
    """Delete a document from a knowledge base."""
    doc = db.get(KBDocument, doc_id)
    if not doc or doc.kb_id != kb_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with id {doc_id} not found in KB {kb_id}",
        )

    db.delete(doc)
    db.commit()


@router.post("/{kb_id}/upload", response_model=UploadResponse)
async def upload_document(
    kb_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Upload and process a document for RAG.

    Process:
    1. Validate file type and size
    2. Read file content
    3. Split into chunks
    4. Generate embeddings using active API provider
    5. Store chunks with embeddings in database

    Supported file types: .txt, .md
    Max file size: 10 MB
    """
    # Verify KB exists
    kb = db.get(KnowledgeBase, kb_id)
    if not kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Knowledge base with id {kb_id} not found",
        )

    # Validate file extension
    filename = file.filename or "unknown.txt"
    extension = "." + filename.split(".")[-1].lower() if "." in filename else ""
    if extension not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '{extension}'. Supported: {', '.join(SUPPORTED_EXTENSIONS)}",
        )

    # Read file content
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Max size: {MAX_FILE_SIZE // (1024*1024)} MB",
        )

    # Decode content
    try:
        text_content = content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File encoding not supported. Please use UTF-8 encoded text files.",
        )

    if not text_content.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is empty or contains only whitespace.",
        )

    # Chunk the content
    chunks = chunk_file_content(text_content, filename)

    if not chunks:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No content to process after chunking.",
        )

    # Get active provider for embeddings
    provider = _get_active_provider(db)
    embeddings = None
    embedding_error = None

    if provider:
        try:
            client = LLMClient(provider)
            # Get embeddings for all chunks in one batch
            chunk_texts = [c["chunk_text"] for c in chunks]
            embeddings = await client.create_embedding(chunk_texts)
        except LLMClientError as e:
            embedding_error = str(e)
    else:
        embedding_error = "No active API provider configured. Documents stored without embeddings."

    # Create document records
    created_docs = []
    for i, chunk_data in enumerate(chunks):
        doc = KBDocument(
            kb_id=kb_id,
            source_filename=chunk_data["source_filename"],
            chunk_index=chunk_data["chunk_index"],
            chunk_text=chunk_data["chunk_text"],
            embedding=embeddings[i] if embeddings and i < len(embeddings) else None,
        )
        db.add(doc)
        created_docs.append(doc)

    db.commit()

    # Refresh to get IDs
    for doc in created_docs:
        db.refresh(doc)

    # Build response
    embedded_count = len(embeddings) if embeddings else 0

    return UploadResponse(
        success=True,
        message=f"Uploaded {filename}: {len(chunks)} chunks created, {embedded_count} embedded",
        filename=filename,
        chunks_created=len(chunks),
        chunks_embedded=embedded_count,
        warning=embedding_error if embedding_error else None,
    )


@router.post("/{kb_id}/embed-all", response_model=UploadResponse)
async def embed_all_documents(kb_id: int, db: Session = Depends(get_db)):
    """
    Generate embeddings for all documents in a KB that don't have embeddings yet.

    Useful if documents were uploaded without an active provider.
    """
    kb = db.get(KnowledgeBase, kb_id)
    if not kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Knowledge base with id {kb_id} not found",
        )

    # Get active provider
    provider = _get_active_provider(db)
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active API provider configured. Please activate a provider first.",
        )

    # Get documents without embeddings
    docs_without_embeddings = (
        db.execute(
            select(KBDocument)
            .where(KBDocument.kb_id == kb_id)
            .where(KBDocument.embedding.is_(None))
        )
        .scalars()
        .all()
    )

    if not docs_without_embeddings:
        return UploadResponse(
            success=True,
            message="All documents already have embeddings.",
            filename=None,
            chunks_created=0,
            chunks_embedded=0,
        )

    # Generate embeddings
    try:
        client = LLMClient(provider)
        chunk_texts = [doc.chunk_text for doc in docs_without_embeddings]
        embeddings = await client.create_embedding(chunk_texts)

        # Update documents with embeddings
        for i, doc in enumerate(docs_without_embeddings):
            if i < len(embeddings):
                doc.embedding = embeddings[i]

        db.commit()

        return UploadResponse(
            success=True,
            message=f"Generated embeddings for {len(embeddings)} documents",
            filename=None,
            chunks_created=0,
            chunks_embedded=len(embeddings),
        )

    except LLMClientError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Embedding generation failed: {str(e)}",
        )
