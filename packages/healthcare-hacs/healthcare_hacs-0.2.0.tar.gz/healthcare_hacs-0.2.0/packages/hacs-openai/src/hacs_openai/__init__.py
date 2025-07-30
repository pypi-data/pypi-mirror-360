"""
HACS OpenAI Integration

This package provides OpenAI embedding and generation integration for HACS vectorization.
"""

from hacs_tools.vectorization import EmbeddingModel


class OpenAIEmbedding(EmbeddingModel):
    """OpenAI embedding model wrapper."""

    def __init__(self, model: str = "text-embedding-3-small", api_key: str | None = None):
        try:
            import openai
        except ImportError:
            raise ImportError("openai not available. Install with: pip install openai")

        self.model = model
        self.client = openai.OpenAI(api_key=api_key)

        # Model dimensions mapping
        self._dimensions_map = {
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
            "text-embedding-ada-002": 1536,
        }

        if model not in self._dimensions_map:
            raise ValueError(f"Unknown OpenAI model: {model}")

    def embed(self, text: str) -> list[float]:
        """Generate embedding for text."""
        response = self.client.embeddings.create(input=text, model=self.model)
        return response.data[0].embedding

    @property
    def dimensions(self) -> int:
        """Number of dimensions in the embedding."""
        return self._dimensions_map[self.model]


# Convenience functions
def create_openai_embedding(
    model: str = "text-embedding-3-small", api_key: str | None = None
) -> OpenAIEmbedding:
    """Create an OpenAI embedding model."""
    return OpenAIEmbedding(model=model, api_key=api_key)


def create_openai_vectorizer(
    model: str = "text-embedding-3-small", api_key: str | None = None, vector_store=None
):
    """Create a complete vectorizer with OpenAI embeddings."""
    from hacs_tools.vectorization import HACSVectorizer

    if vector_store is None:
        raise ValueError(
            "vector_store is required. Install a vector store package like hacs-qdrant"
        )

    embedding_model = create_openai_embedding(model, api_key)
    return HACSVectorizer(embedding_model, vector_store)


__all__ = ["OpenAIEmbedding", "create_openai_embedding", "create_openai_vectorizer"]
