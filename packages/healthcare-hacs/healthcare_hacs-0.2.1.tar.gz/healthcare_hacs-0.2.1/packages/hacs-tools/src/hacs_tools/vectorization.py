"""
HACS Vectorization - Base Interfaces

This module provides the base interfaces for HACS vectorization functionality.
Individual vector stores and embedding providers are implemented in separate packages.
"""

import hashlib
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Protocol

from hacs_core import Actor, Evidence, MemoryBlock
from pydantic import BaseModel, ConfigDict, Field


class VectorMetadata(BaseModel):
    """Metadata for vectors stored in vector databases."""

    model_config = ConfigDict(extra="allow")

    # Core metadata
    resource_type: str = Field(
        ..., description="Type of resource (memory, evidence, etc.)"
    )
    resource_id: str = Field(..., description="ID of the source resource")
    content_hash: str = Field(..., description="Hash of the content for deduplication")

    # Actor and timing info
    actor_id: str | None = Field(None, description="ID of the actor who created this")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Content metadata
    content_length: int | None = Field(None, description="Length of original content")
    importance_score: float | None = Field(None, description="Importance score (0-1)")

    # Search and categorization
    tags: list[str] = Field(default_factory=list, description="Tags for categorization")
    category: str | None = Field(None, description="Primary category")


class EmbeddingModel(Protocol):
    """Protocol for embedding models."""

    def embed(self, text: str) -> list[float]:
        """Generate embedding for text."""
        ...

    @property
    def dimensions(self) -> int:
        """Number of dimensions in the embedding."""
        ...


class VectorStore(ABC):
    """Abstract base class for vector stores."""

    @abstractmethod
    def store_vector(
        self, vector_id: str, embedding: list[float], metadata: VectorMetadata
    ) -> bool:
        """Store a vector with metadata."""
        pass

    @abstractmethod
    def search_similar(
        self,
        query_embedding: list[float],
        limit: int = 10,
        filters: dict[str, Any] | None = None,
    ) -> list[tuple[str, float, VectorMetadata]]:
        """Search for similar vectors."""
        pass

    @abstractmethod
    def get_vector(self, vector_id: str) -> tuple[list[float], VectorMetadata] | None:
        """Retrieve a specific vector."""
        pass

    @abstractmethod
    def delete_vector(self, vector_id: str) -> bool:
        """Delete a vector."""
        pass


class HACSVectorizer:
    """Main vectorization interface for HACS."""

    def __init__(self, embedding_model: EmbeddingModel, vector_store: VectorStore):
        self.embedding_model = embedding_model
        self.vector_store = vector_store

    def vectorize_memory(self, memory: MemoryBlock, actor: Actor) -> str:
        """Vectorize a memory block and store it."""
        # Generate embedding
        embedding = self.embedding_model.embed(memory.content)

        # Create metadata
        metadata = VectorMetadata(
            resource_type="memory",
            resource_id=memory.id,
            content_hash=hashlib.sha256(memory.content.encode()).hexdigest(),
            actor_id=actor.id,
            content_length=len(memory.content),
            importance_score=memory.importance_score,
            category=memory.memory_type,
        )

        # Store vector
        vector_id = f"memory_{memory.id}"
        success = self.vector_store.store_vector(vector_id, embedding, metadata)

        if success:
            return vector_id
        else:
            raise RuntimeError(f"Failed to store vector for memory {memory.id}")

    def vectorize_evidence(self, evidence: Evidence, actor: Actor) -> str:
        """Vectorize evidence and store it."""
        # Combine citation and content for embedding
        text_to_embed = f"{evidence.citation}\n\n{evidence.content}"
        embedding = self.embedding_model.embed(text_to_embed)

        # Create metadata
        metadata = VectorMetadata(
            resource_type="evidence",
            resource_id=evidence.id,
            content_hash=hashlib.sha256(text_to_embed.encode()).hexdigest(),
            actor_id=actor.id,
            content_length=len(text_to_embed),
            importance_score=evidence.confidence_score,
            category=evidence.evidence_type.value if evidence.evidence_type else None,
            tags=[evidence.evidence_type.value] if evidence.evidence_type else [],
        )

        # Store vector
        vector_id = f"evidence_{evidence.id}"
        success = self.vector_store.store_vector(vector_id, embedding, metadata)

        if success:
            return vector_id
        else:
            raise RuntimeError(f"Failed to store vector for evidence {evidence.id}")

    def search_memories(
        self, query: str, limit: int = 10, actor: Actor | None = None
    ) -> list[tuple[str, float, VectorMetadata]]:
        """Search for similar memories."""
        query_embedding = self.embedding_model.embed(query)

        filters = {"resource_type": "memory"}
        if actor:
            filters["actor_id"] = actor.id

        return self.vector_store.search_similar(query_embedding, limit, filters)

    def search_evidence(
        self, query: str, limit: int = 10, actor: Actor | None = None
    ) -> list[tuple[str, float, VectorMetadata]]:
        """Search for similar evidence."""
        query_embedding = self.embedding_model.embed(query)

        filters = {"resource_type": "evidence"}
        if actor:
            filters["actor_id"] = actor.id

        return self.vector_store.search_similar(query_embedding, limit, filters)

    def search_all(
        self, query: str, limit: int = 10, actor: Actor | None = None
    ) -> list[tuple[str, float, VectorMetadata]]:
        """Search across all vectorized content."""
        query_embedding = self.embedding_model.embed(query)

        filters = {}
        if actor:
            filters["actor_id"] = actor.id

        return self.vector_store.search_similar(query_embedding, limit, filters)


# Export main classes
__all__ = ["VectorMetadata", "EmbeddingModel", "VectorStore", "HACSVectorizer"]
