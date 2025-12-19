"""
HuggingFace Inference API Client - Wraps HF Inference API to OpenAI-compatible format.

Supports HuggingFace models hosted on the Inference API, particularly for
text generation models like GPT-2 fine-tuned variants.
"""

import re
import time
from typing import Any

import httpx


class HFInferenceClientError(Exception):
    """Base exception for HuggingFace Inference client errors."""

    pass


class HFInferenceClient:
    """
    HuggingFace Inference API client with OpenAI-compatible interface.

    Transforms OpenAI-style chat completion requests to HuggingFace format
    and wraps responses back to OpenAI format.

    Usage:
        client = HFInferenceClient(provider)
        response = await client.create_chat_completion([
            {"role": "user", "content": "Hello!"}
        ])
    """

    def __init__(self, provider, timeout: float = 120.0):
        """
        Initialize the HuggingFace Inference client.

        Args:
            provider: APIProvider instance with api_key and chat_model_id
            timeout: Request timeout in seconds (longer for model cold starts)
        """
        self.provider = provider
        self.api_key = provider.api_key
        self.model_id = provider.chat_model_id
        self.timeout = timeout

        # Build endpoint URL
        # For HuggingFace provider, always use the provided base_url directly
        # Supports both:
        # - Inference Endpoints: https://xxx.us-east-1.aws.endpoints.huggingface.cloud
        # - Legacy API (deprecated): https://api-inference.huggingface.co/models/xxx
        self.endpoint = provider.base_url.rstrip("/")

    def _get_headers(self) -> dict[str, str]:
        """Get headers for HuggingFace API requests."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    # GPT-2 has 1024 max position embeddings, leave room for generation
    MAX_PROMPT_CHARS = 800

    def _messages_to_prompt(self, messages: list[dict[str, str]]) -> str:
        """
        Convert OpenAI-style messages array to a single prompt string.

        For GPT-2 style models with custom handler.py, we send ONLY the
        last user message content (not formatted with User:/Assistant:).
        The handler.py on HuggingFace adds the User:/Assistant: formatting.

        This avoids double-formatting and keeps prompts short for GPT-2's
        1024 token limit.
        """
        # Extract the last user message only (ignore system/assistant for HF)
        last_user_content = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                last_user_content = msg.get("content", "")
                break

        # Truncate to avoid exceeding GPT-2's position embedding limit
        if len(last_user_content) > self.MAX_PROMPT_CHARS:
            last_user_content = last_user_content[:self.MAX_PROMPT_CHARS] + "..."

        return last_user_content

    def _extract_assistant_response(self, generated_text: str, prompt: str) -> str:
        """
        Extract the assistant's response from the generated text.

        With custom handler.py on HuggingFace Inference Endpoint, the response
        is already cleaned and extracted. We just need minimal post-processing.
        """
        # The handler.py already extracts and cleans the response
        response = generated_text.strip()

        # Additional cleanup if needed
        response = self._clean_response(response)
        return response

    @staticmethod
    def _clean_response(text: str) -> str:
        """Clean up generated response text."""
        # Remove common special tokens
        bad_tokens = [
            "<s>", "</s>", "<|endoftext|>", "<|user|>", "<|assistant|>",
            "<user>", "</user>", "<assistant>", "</assistant>",
            "<pad>", "</pad>", "<unk>",
        ]
        for token in bad_tokens:
            text = text.replace(token, "")

        # Stop at "User:" if the model generates a new turn
        if "User:" in text:
            text = text.split("User:")[0]

        # Clean up whitespace
        text = text.strip()
        text = re.sub(r"\s+", " ", text)

        # Remove surrounding quotes if present
        text = text.strip('"').strip("'")

        return text

    async def create_chat_completion(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.8,
        max_tokens: int | None = None,
        stream: bool = False,
    ) -> dict[str, Any]:
        """
        Create a chat completion using HuggingFace Inference API.

        Transforms the OpenAI-style request to HuggingFace format and
        wraps the response back to OpenAI format.

        Args:
            messages: List of message dicts with 'role' and 'content' keys
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum tokens in response (default: 100)
            stream: Whether to stream (not supported, ignored)

        Returns:
            OpenAI-style response dict with 'choices' containing the assistant message

        Raises:
            HFInferenceClientError: If the API call fails
        """
        # Convert messages to prompt
        prompt = self._messages_to_prompt(messages)

        # Build HuggingFace Inference Endpoint payload
        # The custom handler.py on HuggingFace will:
        # 1. Wrap input with "User: {input}\nAssistant:" format
        # 2. Generate response with appropriate parameters
        # 3. Clean and extract the assistant's response
        payload: dict[str, Any] = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": max_tokens or 40,  # GPT-2 works better with shorter outputs
                "temperature": temperature,
                "top_p": 0.9,
                "repetition_penalty": 1.1,
            },
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    self.endpoint,
                    headers=self._get_headers(),
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()

                # Parse HuggingFace response
                if isinstance(data, list) and len(data) > 0:
                    generated_text = data[0].get("generated_text", "")
                elif isinstance(data, dict):
                    generated_text = data.get("generated_text", "")
                else:
                    generated_text = ""

                # Extract assistant response
                assistant_content = self._extract_assistant_response(
                    generated_text, prompt
                )

                if not assistant_content:
                    assistant_content = "I apologize, I couldn't generate a response."

                # Return in OpenAI format
                return {
                    "id": f"hf-{int(time.time())}",
                    "object": "chat.completion",
                    "created": int(time.time()),
                    "model": self.model_id,
                    "choices": [
                        {
                            "index": 0,
                            "message": {
                                "role": "assistant",
                                "content": assistant_content,
                            },
                            "finish_reason": "stop",
                        }
                    ],
                    "usage": {
                        "prompt_tokens": len(prompt.split()),
                        "completion_tokens": len(assistant_content.split()),
                        "total_tokens": len(prompt.split()) + len(assistant_content.split()),
                    },
                }

            except httpx.HTTPStatusError as e:
                error_detail = e.response.text if e.response else str(e)

                # Handle specific HuggingFace errors
                if e.response.status_code == 503:
                    raise HFInferenceClientError(
                        f"Model is loading. Please try again in a few seconds. ({error_detail})"
                    ) from e
                elif e.response.status_code == 401:
                    raise HFInferenceClientError(
                        "Invalid HuggingFace API token. Please check your credentials."
                    ) from e

                raise HFInferenceClientError(
                    f"HuggingFace API error ({e.response.status_code}): {error_detail}"
                ) from e

            except httpx.RequestError as e:
                raise HFInferenceClientError(f"Request failed: {str(e)}") from e

    async def test_connection(self) -> dict[str, Any]:
        """
        Test the HuggingFace API connection with a simple request.

        Returns:
            Dict with 'success', 'message', 'latency_ms', and optionally 'model_response'
        """
        test_messages = [
            {"role": "user", "content": "Say hello in one sentence."}
        ]

        start_time = time.perf_counter()
        try:
            response = await self.create_chat_completion(
                messages=test_messages,
                temperature=0.5,
                max_tokens=30,
            )
            end_time = time.perf_counter()
            latency_ms = (end_time - start_time) * 1000

            model_response = (
                response.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
            )

            return {
                "success": True,
                "message": f"Connected to HuggingFace model {self.model_id}",
                "latency_ms": round(latency_ms, 2),
                "model_response": model_response.strip(),
            }

        except HFInferenceClientError as e:
            end_time = time.perf_counter()
            latency_ms = (end_time - start_time) * 1000
            return {
                "success": False,
                "message": str(e),
                "latency_ms": round(latency_ms, 2),
                "model_response": None,
            }

    async def create_embedding(self, text: str | list[str]) -> list[list[float]]:
        """
        Create embeddings (not supported for this GPT-2 model).

        Raises:
            HFInferenceClientError: Always, as GPT-2 doesn't support embeddings
        """
        raise HFInferenceClientError(
            "Embedding is not supported for this HuggingFace model. "
            "Please configure a separate embedding model or use an OpenAI-compatible provider."
        )

    async def test_embedding(self) -> dict[str, Any]:
        """Test embedding API (not supported for GPT-2 models)."""
        return {
            "success": False,
            "message": "Embedding not supported for HuggingFace GPT-2 models",
            "latency_ms": 0,
            "embedding_dimension": None,
        }
