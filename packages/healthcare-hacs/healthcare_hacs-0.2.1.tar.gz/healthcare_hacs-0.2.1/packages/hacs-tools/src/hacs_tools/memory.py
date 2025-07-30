"""
Memory Operations for HACS

This module implements memory operations following conceptual guide patterns
with Actor permissions, automatic indexing, and adapter interfaces for
Mem0, LangMem, and vector DB integration.
"""

import json
import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from hacs_core import Actor, MemoryBlock
from pydantic import BaseModel, Field

from hacs_tools.crud import CRUDOperation, PermissionManager


class MemorySearchResult(BaseModel):
    """Result of memory search operation."""

    memory_id: str
    memory: MemoryBlock
    relevance_score: float = Field(ge=0.0, le=1.0)
    search_metadata: dict[str, Any] = Field(default_factory=dict)


class MemoryLinkType(str, Enum):
    """Types of memory links."""

    CAUSAL = "causal"
    TEMPORAL = "temporal"
    SEMANTIC = "semantic"
    EPISODIC = "episodic"
    PROCEDURAL = "procedural"


class MemoryLink(BaseModel):
    """Represents a link between memories."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_memory_id: str
    target_memory_id: str
    link_type: MemoryLinkType
    strength: float = Field(ge=0.0, le=1.0, default=0.5)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: str  # Actor ID
    metadata: dict[str, Any] = Field(default_factory=dict)


class InMemoryAdapter:
    """In-memory storage adapter for development and testing."""

    def __init__(self):
        self._memories: dict[str, MemoryBlock] = {}
        self._links: dict[str, MemoryLink] = {}
        self.logger = logging.getLogger(__name__)

    def store(self, memory: MemoryBlock, actor: Actor) -> str:
        """Store a memory block."""
        self._memories[memory.id] = memory
        self.logger.info(f"Stored memory {memory.id} by {actor.id}")
        return memory.id

    def retrieve(self, memory_id: str, actor: Actor) -> MemoryBlock | None:
        """Retrieve a memory block by ID."""
        return self._memories.get(memory_id)

    def search(
        self,
        query: str,
        memory_type: str | None = None,
        actor: Actor | None = None,
        limit: int = 10,
    ) -> list[MemorySearchResult]:
        """Search for memories using simple text matching."""
        results = []

        for memory in self._memories.values():
            # Filter by memory type if specified
            if memory_type and memory.memory_type != memory_type:
                continue

            # Simple text search in content and metadata
            score = 0.0
            query_lower = query.lower()

            if query_lower in memory.content.lower():
                score += 0.8

            # Search in metadata
            metadata_text = json.dumps(memory.metadata).lower()
            if query_lower in metadata_text:
                score += 0.4

            # Boost score based on importance and access count
            score += memory.importance_score * 0.2
            score += min(memory.access_count / 10.0, 0.1)

            if score > 0:
                results.append(
                    MemorySearchResult(
                        memory_id=memory.id,
                        memory=memory,
                        relevance_score=min(score, 1.0),
                        search_metadata={"query": query, "method": "text_search"},
                    )
                )

        # Sort by relevance score and limit results
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results[:limit]

    def delete(self, memory_id: str, actor: Actor) -> bool:
        """Delete a memory block."""
        if memory_id in self._memories:
            del self._memories[memory_id]
            self.logger.info(f"Deleted memory {memory_id} by {actor.id}")
            return True
        return False

    def add_link(self, link: MemoryLink) -> str:
        """Add a memory link."""
        self._links[link.id] = link
        return link.id

    def get_links(
        self, memory_id: str, link_type: MemoryLinkType | None = None
    ) -> list[MemoryLink]:
        """Get links for a memory."""
        links = []
        for link in self._links.values():
            if link.source_memory_id == memory_id or link.target_memory_id == memory_id:
                if not link_type or link.link_type == link_type:
                    links.append(link)
        return links


class MemoryManager:
    """Manages memory operations with pluggable adapters."""

    def __init__(self, adapter=None):
        self.adapter = adapter or InMemoryAdapter()
        self.logger = logging.getLogger(__name__)

    def get_adapter_type(self) -> str:
        """Get the type of current adapter."""
        return type(self.adapter).__name__


# Global memory manager instance
_memory_manager = MemoryManager()


def get_memory_manager() -> MemoryManager:
    """Get the global memory manager."""
    return _memory_manager


def store_memory(memory: MemoryBlock, actor: Actor) -> str:
    """
    Store a memory block with automatic indexing and Actor permissions.
    """
    # Validate permissions
    PermissionManager.validate_permission(actor, CRUDOperation.CREATE, "MemoryBlock")

    # Automatic indexing - update metadata
    memory.metadata.update(
        {
            "stored_by": actor.id,
            "stored_at": datetime.now(timezone.utc).isoformat(),
            "indexed": True,
        }
    )

    # Store using current adapter
    manager = get_memory_manager()
    memory_id = manager.adapter.store(memory, actor)

    # Record access for importance scoring
    memory.increment_access()

    return memory_id


def recall_memory(
    memory_type: str, query: str, actor: Actor, limit: int = 10
) -> list[MemorySearchResult]:
    """
    Search and recall memories with simple text search and ACL.
    """
    # Validate permissions
    PermissionManager.validate_permission(actor, CRUDOperation.READ, "MemoryBlock")

    # Use memory type string directly
    mem_type = memory_type

    # Search using current adapter
    manager = get_memory_manager()
    results = manager.adapter.search(query, mem_type, actor, limit)

    # Update access count for retrieved memories
    for result in results:
        result.memory.increment_access()

    return results


def link_memories(
    memory_ids: list[str],
    actor: Actor,
    link_type: MemoryLinkType = MemoryLinkType.SEMANTIC,
) -> bool:
    """
    Create bidirectional links between memories with validation.
    """
    # Validate permissions
    PermissionManager.validate_permission(actor, CRUDOperation.UPDATE, "MemoryBlock")

    if len(memory_ids) < 2:
        raise ValueError("At least 2 memory IDs required for linking")

    manager = get_memory_manager()

    # Validate all memories exist
    for memory_id in memory_ids:
        memory = manager.adapter.retrieve(memory_id, actor)
        if not memory:
            raise ValueError(f"Memory {memory_id} not found")

    # Create bidirectional links between all pairs
    links_created = 0
    for i, source_id in enumerate(memory_ids):
        for target_id in memory_ids[i + 1 :]:
            # Create forward link
            forward_link = MemoryLink(
                source_memory_id=source_id,
                target_memory_id=target_id,
                link_type=link_type,
                created_by=actor.id,
                metadata={"bidirectional": True},
            )

            # Create backward link
            backward_link = MemoryLink(
                source_memory_id=target_id,
                target_memory_id=source_id,
                link_type=link_type,
                created_by=actor.id,
                metadata={"bidirectional": True},
            )

            # Store links if adapter supports it
            if hasattr(manager.adapter, "add_link"):
                manager.adapter.add_link(forward_link)
                manager.adapter.add_link(backward_link)
                links_created += 2

    return links_created > 0


# Convenience functions for specific memory types
def store_episodic_memory(
    content: str, actor: Actor, importance: float = 0.5, metadata: dict | None = None
) -> str:
    """Store an episodic memory."""
    memory = MemoryBlock(
        id=str(uuid.uuid4()),
        memory_type="episodic",
        content=content,
        importance_score=importance,
        metadata=metadata or {},
    )
    return store_memory(memory, actor)


def store_procedural_memory(
    content: str, actor: Actor, importance: float = 0.7, metadata: dict | None = None
) -> str:
    """Store a procedural memory."""
    memory = MemoryBlock(
        id=str(uuid.uuid4()),
        memory_type="procedural",
        content=content,
        importance_score=importance,
        metadata=metadata or {},
    )
    return store_memory(memory, actor)


def recall_episodic_memories(
    query: str, actor: Actor, limit: int = 10
) -> list[MemorySearchResult]:
    """Recall episodic memories."""
    return recall_memory("episodic", query, actor, limit)
