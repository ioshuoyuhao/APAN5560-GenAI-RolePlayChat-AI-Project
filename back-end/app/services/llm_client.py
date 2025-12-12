"""
LLM Client - OpenAI-compatible API client for chat and embeddings.

Supports any provider implementing the OpenAI API format:
- OpenAI
- DeepSeek (via SiliconFlow)
- Doubao
- Custom HuggingFace models with OpenAI-style gateway
"""

import time
from typing import Any

import httpx

from app.models.api_provider import APIProvider


class LLMClientError(Exception):
    """Base exception for LLM client errors."""

    pass


class LLMClient:
    """
    OpenAI-compatible LLM client.

    Usage:
        client = LLMClient(provider)
        response = await client.create_chat_completion([
            {"role": "user", "content": "Hello!"}
        ])
        embedding = await client.create_embedding("Some text to embed")
    """

    def __init__(self, provider: APIProvider, timeout: float = 60.0):
        """
        Initialize the LLM client.

        Args:
            provider: APIProvider instance with base_url, api_key, and model IDs
            timeout: Request timeout in seconds
        """
        self.provider = provider
        self.base_url = provider.base_url.rstrip("/")
        self.api_key = provider.api_key
        self.chat_model_id = provider.chat_model_id
        self.embedding_model_id = provider.embedding_model_id
        self.timeout = timeout

    def _get_headers(self) -> dict[str, str]:
        """Get common headers for API requests."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def create_chat_completion(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int | None = None,
        stream: bool = False,
    ) -> dict[str, Any]:
        """
        Create a chat completion.

        Args:
            messages: List of message dicts with 'role' and 'content' keys
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum tokens in response (None = model default)
            stream: Whether to stream the response (not implemented yet)

        Returns:
            OpenAI-style response dict with 'choices' containing the assistant message

        Raises:
            LLMClientError: If the API call fails
        """
        if stream:
            raise NotImplementedError("Streaming is not yet implemented")

        url = f"{self.base_url}/chat/completions"
        payload: dict[str, Any] = {
            "model": self.chat_model_id,
            "messages": messages,
            "temperature": temperature,
        }
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    url, headers=self._get_headers(), json=payload
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                error_detail = e.response.text if e.response else str(e)
                raise LLMClientError(
                    f"Chat completion failed ({e.response.status_code}): {error_detail}"
                ) from e
            except httpx.RequestError as e:
                raise LLMClientError(f"Request failed: {str(e)}") from e

    async def create_embedding(
        self, text: str | list[str]
    ) -> list[list[float]]:
        """
        Create embeddings for text.

        Args:
            text: Single string or list of strings to embed

        Returns:
            List of embedding vectors (each is a list of floats)

        Raises:
            LLMClientError: If the API call fails
        """
        url = f"{self.base_url}/embeddings"
        payload = {
            "model": self.embedding_model_id,
            "input": text if isinstance(text, list) else [text],
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    url, headers=self._get_headers(), json=payload
                )
                response.raise_for_status()
                data = response.json()

                # Extract embeddings from response
                embeddings = [item["embedding"] for item in data["data"]]
                return embeddings

            except httpx.HTTPStatusError as e:
                error_detail = e.response.text if e.response else str(e)
                raise LLMClientError(
                    f"Embedding failed ({e.response.status_code}): {error_detail}"
                ) from e
            except httpx.RequestError as e:
                raise LLMClientError(f"Request failed: {str(e)}") from e

    async def test_connection(self) -> dict[str, Any]:
        """
        Test the API connection with a simple chat request.

        Returns:
            Dict with 'success', 'message', 'latency_ms', and optionally 'model_response'
        """
        test_messages = [
            {"role": "user", "content": "Say 'API connection successful' in 5 words or less."}
        ]

        start_time = time.perf_counter()
        try:
            response = await self.create_chat_completion(
                messages=test_messages,
                temperature=0.1,
                max_tokens=20,
            )
            end_time = time.perf_counter()
            latency_ms = (end_time - start_time) * 1000

            # Extract the assistant's response
            model_response = response.get("choices", [{}])[0].get("message", {}).get("content", "")

            return {
                "success": True,
                "message": f"Connected to {self.provider.name} successfully",
                "latency_ms": round(latency_ms, 2),
                "model_response": model_response.strip(),
            }

        except LLMClientError as e:
            end_time = time.perf_counter()
            latency_ms = (end_time - start_time) * 1000
            return {
                "success": False,
                "message": str(e),
                "latency_ms": round(latency_ms, 2),
                "model_response": None,
            }

    async def test_embedding(self) -> dict[str, Any]:
        """
        Test the embedding API with a simple request.

        Returns:
            Dict with 'success', 'message', 'latency_ms', and 'embedding_dimension'
        """
        test_text = "Test embedding"

        start_time = time.perf_counter()
        try:
            embeddings = await self.create_embedding(test_text)
            end_time = time.perf_counter()
            latency_ms = (end_time - start_time) * 1000

            embedding_dim = len(embeddings[0]) if embeddings else 0

            return {
                "success": True,
                "message": f"Embedding API working (dimension: {embedding_dim})",
                "latency_ms": round(latency_ms, 2),
                "embedding_dimension": embedding_dim,
            }

        except LLMClientError as e:
            end_time = time.perf_counter()
            latency_ms = (end_time - start_time) * 1000
            return {
                "success": False,
                "message": str(e),
                "latency_ms": round(latency_ms, 2),
                "embedding_dimension": None,
            }

