"""
Text Chunker - Splits documents into overlapping chunks for RAG.

Simple implementation using character-based chunking with overlap.
For production, consider using tiktoken for token-accurate chunking.
"""


class TextChunker:
    """
    Splits text into overlapping chunks for embedding and retrieval.

    Uses a simple character-based approach with approximate token estimation.
    Average English word is ~5 characters, so we estimate tokens as chars/4.
    """

    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 100,
        chars_per_token: float = 4.0,
    ):
        """
        Initialize the chunker.

        Args:
            chunk_size: Target chunk size in tokens (approximate)
            chunk_overlap: Overlap between chunks in tokens
            chars_per_token: Estimated characters per token (default 4.0)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.chars_per_token = chars_per_token

        # Convert to characters for processing
        self._chunk_chars = int(chunk_size * chars_per_token)
        self._overlap_chars = int(chunk_overlap * chars_per_token)

    def chunk_text(self, text: str) -> list[str]:
        """
        Split text into overlapping chunks.

        Args:
            text: The text to split

        Returns:
            List of text chunks
        """
        if not text or not text.strip():
            return []

        # Normalize whitespace
        text = " ".join(text.split())

        # If text is shorter than chunk size, return as single chunk
        if len(text) <= self._chunk_chars:
            return [text]

        chunks = []
        start = 0

        while start < len(text):
            # Calculate end position
            end = start + self._chunk_chars

            # If this is the last chunk, take the rest
            if end >= len(text):
                chunks.append(text[start:].strip())
                break

            # Try to find a good break point (sentence or word boundary)
            chunk_text = text[start:end]
            break_point = self._find_break_point(chunk_text)

            if break_point > 0:
                end = start + break_point

            chunks.append(text[start:end].strip())

            # Move start position, accounting for overlap
            start = end - self._overlap_chars

            # Prevent infinite loop if overlap is too large
            if start <= chunks[-1] if isinstance(chunks[-1], int) else 0:
                start = end

        return [c for c in chunks if c]  # Filter empty chunks

    def _find_break_point(self, text: str) -> int:
        """
        Find a good break point in text (sentence or word boundary).

        Prefers sentence boundaries, then word boundaries.

        Args:
            text: Text to find break point in

        Returns:
            Index of break point, or 0 if none found
        """
        # Look for sentence boundaries in the last 20% of the chunk
        search_start = int(len(text) * 0.8)
        search_text = text[search_start:]

        # Sentence boundaries (prefer these)
        for sep in [". ", "! ", "? ", ".\n", "!\n", "?\n"]:
            idx = search_text.rfind(sep)
            if idx != -1:
                return search_start + idx + len(sep)

        # Word boundaries (fallback)
        for sep in [" ", "\n", "\t"]:
            idx = search_text.rfind(sep)
            if idx != -1:
                return search_start + idx + 1

        # No good break point found
        return 0

    def chunk_file_content(
        self, content: str, filename: str | None = None
    ) -> list[dict[str, any]]:
        """
        Chunk file content and return structured chunks.

        Args:
            content: File content as string
            filename: Optional source filename

        Returns:
            List of dicts with 'chunk_index', 'chunk_text', and 'source_filename'
        """
        chunks = self.chunk_text(content)

        return [
            {
                "chunk_index": i,
                "chunk_text": chunk,
                "source_filename": filename,
            }
            for i, chunk in enumerate(chunks)
        ]


# Default chunker instance
default_chunker = TextChunker(chunk_size=500, chunk_overlap=100)


def chunk_text(text: str) -> list[str]:
    """Convenience function using default chunker."""
    return default_chunker.chunk_text(text)


def chunk_file_content(content: str, filename: str | None = None) -> list[dict]:
    """Convenience function using default chunker."""
    return default_chunker.chunk_file_content(content, filename)

