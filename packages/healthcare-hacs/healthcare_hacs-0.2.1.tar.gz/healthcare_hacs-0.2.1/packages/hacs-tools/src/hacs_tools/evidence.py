"""
Evidence Operations for HACS

This module implements evidence operations with vector-RAG preparation,
including evidence creation, search, linking, and vector embedding support.
"""

import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from hacs_core import Actor, Evidence, EvidenceType
from pydantic import BaseModel, Field

from hacs_tools.crud import CRUDOperation, PermissionManager


class EvidenceSearchResult(BaseModel):
    """Result of evidence search operation."""

    evidence_id: str
    evidence: Evidence
    relevance_score: float = Field(ge=0.0, le=1.0)
    search_metadata: dict[str, Any] = Field(default_factory=dict)


class EvidenceLevel(str, Enum):
    """Evidence levels for filtering."""

    SYSTEMATIC_REVIEW = "systematic_review"
    META_ANALYSIS = "meta_analysis"
    RCT = "rct"
    COHORT_STUDY = "cohort_study"
    CASE_CONTROL = "case_control"
    CASE_SERIES = "case_series"
    EXPERT_OPINION = "expert_opinion"
    CLINICAL_GUIDELINE = "clinical_guideline"


class EvidenceLink(BaseModel):
    """Link between evidence and resources."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    evidence_id: str
    resource_type: str
    resource_id: str
    link_strength: float = Field(ge=0.0, le=1.0, default=0.5)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: str  # Actor ID
    metadata: dict[str, Any] = Field(default_factory=dict)


class VectorEmbedding(BaseModel):
    """Vector embedding for evidence (RAG preparation)."""

    evidence_id: str
    embedding: list[float] = Field(default_factory=list)
    embedding_model: str = "text-embedding-ada-002"  # Default OpenAI model
    chunk_index: int = 0  # For chunked content
    chunk_text: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EvidenceAdapter:
    """Base adapter for evidence storage and search."""

    def __init__(self):
        self._evidence: dict[str, Evidence] = {}
        self._links: dict[str, EvidenceLink] = {}
        self._embeddings: dict[str, list[VectorEmbedding]] = {}
        self.logger = logging.getLogger(__name__)

    def store(self, evidence: Evidence, actor: Actor) -> str:
        """Store evidence."""
        self._evidence[evidence.id] = evidence
        self.logger.info(f"Stored evidence {evidence.id} by {actor.id}")
        return evidence.id

    def retrieve(self, evidence_id: str, actor: Actor) -> Evidence | None:
        """Retrieve evidence by ID."""
        return self._evidence.get(evidence_id)

    def search(
        self,
        query: str,
        level: EvidenceLevel | None = None,
        actor: Actor | None = None,
        limit: int = 10,
    ) -> list[EvidenceSearchResult]:
        """Search evidence using text matching."""
        results = []

        for evidence in self._evidence.values():
            # Filter by evidence level if specified
            if level and not self._matches_evidence_level(evidence, level):
                continue

            # Calculate relevance score
            score = self._calculate_text_relevance(evidence, query)

            if score > 0:
                results.append(
                    EvidenceSearchResult(
                        evidence_id=evidence.id,
                        evidence=evidence,
                        relevance_score=score,
                        search_metadata={"query": query, "method": "text_search"},
                    )
                )

        # Sort by relevance and limit
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results[:limit]

    def _matches_evidence_level(self, evidence: Evidence, level: EvidenceLevel) -> bool:
        """Check if evidence matches the specified level."""
        evidence_type_to_level = {
            EvidenceType.RESEARCH_PAPER: EvidenceLevel.SYSTEMATIC_REVIEW,
            EvidenceType.RESEARCH_PAPER: EvidenceLevel.META_ANALYSIS,
            EvidenceType.RESEARCH_PAPER: EvidenceLevel.RCT,
            EvidenceType.RESEARCH_PAPER: EvidenceLevel.COHORT_STUDY,
            EvidenceType.RESEARCH_PAPER: EvidenceLevel.CASE_CONTROL,
            EvidenceType.RESEARCH_PAPER: EvidenceLevel.CASE_SERIES,
            EvidenceType.CLINICAL_NOTE: EvidenceLevel.EXPERT_OPINION,
            EvidenceType.GUIDELINE: EvidenceLevel.CLINICAL_GUIDELINE,
        }

        return evidence_type_to_level.get(evidence.evidence_type) == level

    def _calculate_text_relevance(self, evidence: Evidence, query: str) -> float:
        """Calculate text-based relevance score."""
        query_lower = query.lower()
        score = 0.0

        # Search in citation
        if query_lower in evidence.citation.lower():
            score += 0.6

        # Search in content
        if query_lower in evidence.content.lower():
            score += 0.8

        # Search in tags
        for tag in evidence.tags:
            if query_lower in tag.lower():
                score += 0.4

        # Boost based on confidence and quality
        score += evidence.confidence_score * 0.3
        score += evidence.quality_score * 0.2

        # Boost based on evidence type (higher for research papers, guidelines, etc.)
        type_boost = {
            EvidenceType.RESEARCH_PAPER: 0.3,
            EvidenceType.GUIDELINE: 0.25,
            EvidenceType.LAB_RESULT: 0.2,
            EvidenceType.IMAGING: 0.15,
            EvidenceType.CLINICAL_NOTE: 0.1,
            EvidenceType.PATIENT_REPORTED: 0.05,
            EvidenceType.OBSERVATION: 0.1,
        }
        score += type_boost.get(evidence.evidence_type, 0.0)

        return min(score, 1.0)

    def add_link(self, link: EvidenceLink) -> str:
        """Add evidence-resource link."""
        self._links[link.id] = link
        return link.id

    def get_links(self, evidence_id: str) -> list[EvidenceLink]:
        """Get links for evidence."""
        return [
            link for link in self._links.values() if link.evidence_id == evidence_id
        ]

    def get_resource_links(
        self, resource_type: str, resource_id: str
    ) -> list[EvidenceLink]:
        """Get evidence links for a resource."""
        return [
            link
            for link in self._links.values()
            if link.resource_type == resource_type and link.resource_id == resource_id
        ]

    def upsert_embedding(self, embedding: VectorEmbedding) -> str:
        """Store vector embedding (preparation for vector DB)."""
        if embedding.evidence_id not in self._embeddings:
            self._embeddings[embedding.evidence_id] = []

        self._embeddings[embedding.evidence_id].append(embedding)
        self.logger.info(f"Stored embedding for evidence {embedding.evidence_id}")
        return embedding.evidence_id

    def get_embeddings(self, evidence_id: str) -> list[VectorEmbedding]:
        """Get embeddings for evidence."""
        return self._embeddings.get(evidence_id, [])


class EvidenceManager:
    """Manages evidence operations."""

    def __init__(self, adapter: EvidenceAdapter | None = None):
        self.adapter = adapter or EvidenceAdapter()
        self.logger = logging.getLogger(__name__)

    def get_adapter_type(self) -> str:
        """Get adapter type."""
        return type(self.adapter).__name__


# Global evidence manager
_evidence_manager = EvidenceManager()


def get_evidence_manager() -> EvidenceManager:
    """Get the global evidence manager."""
    return _evidence_manager


def create_evidence(
    citation: str,
    content: str,
    actor: Actor,
    evidence_type: EvidenceType = EvidenceType.CLINICAL_NOTE,
    confidence_score: float = 0.5,
    quality_score: float = 0.5,
    tags: list[str] | None = None,
    metadata: dict[str, Any] | None = None,
) -> Evidence:
    """
    Create evidence with provenance tracking.

    Args:
        citation: Citation or reference
        content: Evidence content
        actor: Actor creating the evidence
        evidence_type: Type of evidence
        confidence_score: Confidence in evidence (0-1)
        quality_score: Quality of evidence (0-1)
        tags: Optional tags
        metadata: Optional metadata

    Returns:
        Created Evidence object

    Raises:
        PermissionError: If actor lacks permission
    """
    # Validate permissions
    PermissionManager.validate_permission(actor, CRUDOperation.CREATE, "Evidence")

    # Create evidence with provenance
    evidence = Evidence(
        id=str(uuid.uuid4()),
        evidence_type=evidence_type,
        citation=citation,
        content=content,
        confidence_score=confidence_score,
        quality_score=quality_score,
        tags=tags or [],
        provenance={
            "created_by": actor.id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "source": "hacs_tools",
            "method": "create_evidence",
        },
    )

    # Add metadata if provided
    if metadata:
        evidence.provenance.update(metadata)

    # Store evidence
    manager = get_evidence_manager()
    manager.adapter.store(evidence, actor)

    return evidence


def search_evidence(
    query: str,
    level: str | None = None,
    actor: Actor | None = None,
    limit: int = 10,
) -> list[EvidenceSearchResult]:
    """
    Search evidence with text-based search and filtering.

    Args:
        query: Search query
        level: Evidence level filter (e.g., "RCT", "meta_analysis")
        actor: Actor performing search
        limit: Maximum results

    Returns:
        List of evidence search results

    Raises:
        PermissionError: If actor lacks permission
    """
    if actor:
        # Validate permissions
        PermissionManager.validate_permission(actor, CRUDOperation.READ, "Evidence")

    # Convert level string to enum
    evidence_level = None
    if level:
        try:
            evidence_level = EvidenceLevel(level.lower())
        except ValueError:
            pass

    # Search using manager
    manager = get_evidence_manager()
    results = manager.adapter.search(query, evidence_level, actor, limit)

    return results


def link_evidence_to_resource(
    evidence_id: str,
    resource_type: str,
    resource_id: str,
    actor: Actor,
    link_strength: float = 0.5,
    metadata: dict[str, Any] | None = None,
) -> bool:
    """
    Link evidence to a resource with permission checks.

    Args:
        evidence_id: ID of evidence to link
        resource_type: Type of resource (e.g., "Patient", "Observation")
        resource_id: ID of resource
        actor: Actor performing the operation
        link_strength: Strength of the link (0-1)
        metadata: Optional metadata

    Returns:
        True if link created successfully

    Raises:
        PermissionError: If actor lacks permission
        ValueError: If evidence not found
    """
    # Validate permissions
    PermissionManager.validate_permission(actor, CRUDOperation.UPDATE, "Evidence")
    PermissionManager.validate_permission(actor, CRUDOperation.READ, resource_type)

    manager = get_evidence_manager()

    # Verify evidence exists
    evidence = manager.adapter.retrieve(evidence_id, actor)
    if not evidence:
        raise ValueError(f"Evidence {evidence_id} not found")

    # Create link
    link = EvidenceLink(
        evidence_id=evidence_id,
        resource_type=resource_type,
        resource_id=resource_id,
        link_strength=link_strength,
        created_by=actor.id,
        metadata=metadata or {},
    )

    # Store link
    link_id = manager.adapter.add_link(link)

    return bool(link_id)


def get_evidence_links(evidence_id: str, actor: Actor) -> list[EvidenceLink]:
    """
    Get links for evidence.

    Args:
        evidence_id: Evidence ID
        actor: Actor requesting links

    Returns:
        List of evidence links
    """
    # Validate permissions
    PermissionManager.validate_permission(actor, CRUDOperation.READ, "Evidence")

    manager = get_evidence_manager()
    return manager.adapter.get_links(evidence_id)


def get_resource_evidence(
    resource_type: str, resource_id: str, actor: Actor
) -> list[tuple[Evidence, EvidenceLink]]:
    """
    Get evidence linked to a resource.

    Args:
        resource_type: Type of resource
        resource_id: Resource ID
        actor: Actor requesting evidence

    Returns:
        List of (Evidence, EvidenceLink) tuples
    """
    # Validate permissions
    PermissionManager.validate_permission(actor, CRUDOperation.READ, resource_type)
    PermissionManager.validate_permission(actor, CRUDOperation.READ, "Evidence")

    manager = get_evidence_manager()

    # Get links for resource
    links = manager.adapter.get_resource_links(resource_type, resource_id)

    # Get evidence for each link
    evidence_links = []
    for link in links:
        evidence = manager.adapter.retrieve(link.evidence_id, actor)
        if evidence:
            evidence_links.append((evidence, link))

    return evidence_links


def upsert_evidence_embedding(
    evidence_id: str,
    content_chunks: list[str],
    actor: Actor,
    embedding_model: str = "text-embedding-ada-002",
) -> list[str]:
    """
    Upsert evidence embeddings for vector-RAG (stub for future vector DB integration).

    Args:
        evidence_id: Evidence ID
        content_chunks: List of text chunks to embed
        actor: Actor performing operation
        embedding_model: Model to use for embeddings

    Returns:
        List of embedding IDs

    Note:
        This is a stub implementation. In production, this would:
        1. Generate actual embeddings using OpenAI/Cohere/etc.
        2. Store in vector database (Pinecone, Chroma, etc.)
        3. Enable semantic search
    """
    # Validate permissions
    PermissionManager.validate_permission(actor, CRUDOperation.UPDATE, "Evidence")

    manager = get_evidence_manager()

    # Verify evidence exists
    evidence = manager.adapter.retrieve(evidence_id, actor)
    if not evidence:
        raise ValueError(f"Evidence {evidence_id} not found")

    embedding_ids = []

    # Create stub embeddings for each chunk
    for i, chunk in enumerate(content_chunks):
        # In production, this would call embedding API
        # embedding_vector = openai.Embedding.create(input=chunk, model=embedding_model)

        # Stub: create fake embedding
        fake_embedding = [0.1] * 1536  # OpenAI ada-002 dimension

        embedding = VectorEmbedding(
            evidence_id=evidence_id,
            embedding=fake_embedding,
            embedding_model=embedding_model,
            chunk_index=i,
            chunk_text=chunk,
        )

        embedding_id = manager.adapter.upsert_embedding(embedding)
        embedding_ids.append(embedding_id)

    return embedding_ids


def get_evidence_embeddings(evidence_id: str, actor: Actor) -> list[VectorEmbedding]:
    """
    Get embeddings for evidence.

    Args:
        evidence_id: Evidence ID
        actor: Actor requesting embeddings

    Returns:
        List of vector embeddings
    """
    # Validate permissions
    PermissionManager.validate_permission(actor, CRUDOperation.READ, "Evidence")

    manager = get_evidence_manager()
    return manager.adapter.get_embeddings(evidence_id)


def get_evidence_stats(actor: Actor) -> dict[str, Any]:
    """
    Get evidence statistics.

    Args:
        actor: Actor requesting statistics

    Returns:
        Dictionary with evidence statistics
    """
    # Validate permissions
    PermissionManager.validate_permission(actor, CRUDOperation.READ, "Evidence")

    manager = get_evidence_manager()

    stats = {
        "adapter_type": manager.get_adapter_type(),
        "total_evidence": 0,
        "evidence_types": {},
        "average_confidence": 0.0,
        "average_quality": 0.0,
        "total_links": 0,
        "total_embeddings": 0,
    }

    # Get actual stats if using default adapter
    if hasattr(manager.adapter, "_evidence"):
        evidence_list = list(manager.adapter._evidence.values())
        stats["total_evidence"] = len(evidence_list)

        if evidence_list:
            # Type distribution
            for evidence in evidence_list:
                evidence_type = (
                    evidence.evidence_type
                    if isinstance(evidence.evidence_type, str)
                    else evidence.evidence_type.value
                )
                stats["evidence_types"][evidence_type] = (
                    stats["evidence_types"].get(evidence_type, 0) + 1
                )

            # Average scores
            total_confidence = sum(e.confidence_score for e in evidence_list)
            total_quality = sum(e.quality_score for e in evidence_list)
            stats["average_confidence"] = total_confidence / len(evidence_list)
            stats["average_quality"] = total_quality / len(evidence_list)

    if hasattr(manager.adapter, "_links"):
        stats["total_links"] = len(manager.adapter._links)

    if hasattr(manager.adapter, "_embeddings"):
        total_embeddings = sum(
            len(emb_list) for emb_list in manager.adapter._embeddings.values()
        )
        stats["total_embeddings"] = total_embeddings

    return stats


# Convenience functions for common evidence types
def create_clinical_guideline(
    citation: str, content: str, actor: Actor, **kwargs
) -> Evidence:
    """Create clinical guideline evidence."""
    return create_evidence(citation, content, actor, EvidenceType.GUIDELINE, **kwargs)


def create_rct_evidence(
    citation: str, content: str, actor: Actor, **kwargs
) -> Evidence:
    """Create RCT evidence."""
    return create_evidence(
        citation, content, actor, EvidenceType.RESEARCH_PAPER, **kwargs
    )


def create_expert_opinion(
    citation: str, content: str, actor: Actor, **kwargs
) -> Evidence:
    """Create expert opinion evidence."""
    return create_evidence(
        citation, content, actor, EvidenceType.CLINICAL_NOTE, **kwargs
    )


def search_high_quality_evidence(
    query: str, actor: Actor, min_quality: float = 0.7, limit: int = 10
) -> list[EvidenceSearchResult]:
    """Search for high-quality evidence."""
    results = search_evidence(query, None, actor, limit * 2)  # Get more to filter

    # Filter by quality score
    high_quality = [r for r in results if r.evidence.quality_score >= min_quality]

    return high_quality[:limit]
