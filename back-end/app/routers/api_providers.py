"""
API Providers Router - CRUD endpoints for managing LLM API providers.
"""

import asyncio

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.api_provider import APIProvider
from app.schemas.api_provider import (
    APIProviderCreate,
    APIProviderRead,
    APIProviderUpdate,
    APIProviderTestResult,
)
from app.services.llm_client import LLMClient, get_llm_client

router = APIRouter(prefix="/api-providers", tags=["API Providers"])


@router.get("/", response_model=list[APIProviderRead])
def list_api_providers(db: Session = Depends(get_db)):
    """List all API providers."""
    providers = db.execute(select(APIProvider)).scalars().all()
    return [APIProviderRead.from_orm_with_masked_key(p) for p in providers]


@router.post("/", response_model=APIProviderRead, status_code=status.HTTP_201_CREATED)
def create_api_provider(data: APIProviderCreate, db: Session = Depends(get_db)):
    """Create a new API provider."""
    provider = APIProvider(**data.model_dump())
    db.add(provider)
    db.commit()
    db.refresh(provider)
    return APIProviderRead.from_orm_with_masked_key(provider)


@router.get("/{provider_id}", response_model=APIProviderRead)
def get_api_provider(provider_id: int, db: Session = Depends(get_db)):
    """Get a single API provider by ID."""
    provider = db.get(APIProvider, provider_id)
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"API Provider with id {provider_id} not found",
        )
    return APIProviderRead.from_orm_with_masked_key(provider)


@router.put("/{provider_id}", response_model=APIProviderRead)
def update_api_provider(
    provider_id: int, data: APIProviderUpdate, db: Session = Depends(get_db)
):
    """Update an API provider."""
    provider = db.get(APIProvider, provider_id)
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"API Provider with id {provider_id} not found",
        )

    # Update only provided fields
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(provider, key, value)

    db.commit()
    db.refresh(provider)
    return APIProviderRead.from_orm_with_masked_key(provider)


@router.delete("/{provider_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_api_provider(provider_id: int, db: Session = Depends(get_db)):
    """Delete an API provider."""
    provider = db.get(APIProvider, provider_id)
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"API Provider with id {provider_id} not found",
        )

    db.delete(provider)
    db.commit()


@router.post("/{provider_id}/activate", response_model=APIProviderRead)
def activate_api_provider(provider_id: int, db: Session = Depends(get_db)):
    """Set this provider as the active provider (deactivates others)."""
    provider = db.get(APIProvider, provider_id)
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"API Provider with id {provider_id} not found",
        )

    # Deactivate all other providers
    db.execute(APIProvider.__table__.update().values(is_active=False))

    # Activate this provider
    provider.is_active = True
    db.commit()
    db.refresh(provider)
    return APIProviderRead.from_orm_with_masked_key(provider)


@router.post("/{provider_id}/test", response_model=APIProviderTestResult)
async def test_api_provider(provider_id: int, db: Session = Depends(get_db)):
    """
    Test API provider connection.

    Makes a simple chat API call to verify connectivity and measure latency.
    Returns success status, latency in milliseconds, and the model's response.
    """
    provider = db.get(APIProvider, provider_id)
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"API Provider with id {provider_id} not found",
        )

    # Create appropriate LLM client based on provider type and test connection
    client = get_llm_client(provider)
    result = await client.test_connection()

    return APIProviderTestResult(**result)


@router.post("/{provider_id}/test-embedding", response_model=APIProviderTestResult)
async def test_api_provider_embedding(provider_id: int, db: Session = Depends(get_db)):
    """
    Test API provider's embedding endpoint.

    Makes a simple embedding API call to verify connectivity and check embedding dimension.
    """
    provider = db.get(APIProvider, provider_id)
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"API Provider with id {provider_id} not found",
        )

    # Create appropriate LLM client based on provider type and test embedding
    client = get_llm_client(provider)
    result = await client.test_embedding()

    return APIProviderTestResult(
        success=result["success"],
        message=result["message"],
        latency_ms=result["latency_ms"],
        model_response=f"dimension={result.get('embedding_dimension')}" if result["success"] else None,
    )
