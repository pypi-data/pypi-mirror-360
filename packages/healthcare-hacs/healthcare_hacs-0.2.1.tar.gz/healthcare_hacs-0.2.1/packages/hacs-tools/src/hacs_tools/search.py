"""
Hybrid Search Layer for HACS

This module implements hybrid search functionality with FHIR parameter translation,
resource filtering, and preparation for BM25 + cosine similarity hybrid scoring.
"""

import logging
from enum import Enum
from typing import Any

from hacs_core import Actor, BaseResource
from hacs_models import AgentMessage, Observation, Patient
from pydantic import BaseModel, Field

from hacs_tools.crud import CRUDOperation, PermissionManager, get_storage_manager


class SearchMethod(str, Enum):
    """Search methods available."""

    TEXT = "text"
    FHIR_PARAMS = "fhir_params"
    VECTOR = "vector"
    HYBRID = "hybrid"


class SearchResult(BaseModel):
    """Generic search result."""

    resource_id: str
    resource_type: str
    resource: BaseResource
    relevance_score: float = Field(ge=0.0, le=1.0)
    search_metadata: dict[str, Any] = Field(default_factory=dict)


class SearchFilter(BaseModel):
    """Search filter specification."""

    field: str
    operator: str = "eq"  # eq, ne, gt, lt, gte, lte, contains, starts_with
    value: Any
    case_sensitive: bool = False


class SearchEngine:
    """Main search engine with hybrid capabilities."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def search_resources(
        self,
        resource_type: str,
        text_query: str | None = None,
        filters: dict[str, Any] | None = None,
        vector_query: str | None = None,
        actor: Actor | None = None,
        limit: int = 10,
    ) -> list[SearchResult]:
        """
        Main search entry point supporting multiple search methods.
        """
        # Validate permissions
        if actor is not None:
            PermissionManager.validate_permission(
                actor, CRUDOperation.READ, resource_type
            )

        storage = get_storage_manager()
        resources = storage.list_resources(resource_type, limit=1000)

        results = []

        for resource in resources:
            score = 0.0
            metadata: dict[str, Any] = {"method": "text"}

            # Text search scoring
            if text_query:
                text_score = self._calculate_text_score(resource, text_query.lower())
                score += text_score * 0.6
                metadata["text_score"] = text_score

            # Filter matching
            if filters:
                filter_score = self._apply_fhir_filters(resource, filters)
                if filter_score > 0:
                    score += filter_score * 0.4
                    metadata["filter_score"] = filter_score
                else:
                    continue  # Skip if filters don't match

            # Vector search (stub)
            if vector_query:
                vector_score = self._vector_similarity_stub(resource, vector_query)
                score += vector_score * 0.4
                metadata["vector_score"] = vector_score
                metadata["method"] = "hybrid"

            if score > 0:
                results.append(
                    SearchResult(
                        resource_id=resource.id,
                        resource_type=resource.resource_type,
                        resource=resource,
                        relevance_score=min(score, 1.0),
                        search_metadata=metadata,
                    )
                )

        # Sort and limit
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results[:limit]

    def _calculate_text_score(self, resource: BaseResource, query: str) -> float:
        """Calculate text relevance score."""
        score = 0.0

        if isinstance(resource, Patient):
            full_name = f"{' '.join(resource.given)} {resource.family}".lower()
            if query in full_name:
                score += 0.8
            if query in str(resource.gender).lower():
                score += 0.3

        elif isinstance(resource, Observation):
            if resource.code and query in str(resource.code).lower():
                score += 0.7
            if resource.value_string and query in resource.value_string.lower():
                score += 0.6

        elif isinstance(resource, AgentMessage):
            if query in resource.content.lower():
                score += 0.8
            if query in str(resource.role).lower():
                score += 0.3

        return score

    def _apply_fhir_filters(
        self, resource: BaseResource, filters: dict[str, Any]
    ) -> float:
        """Apply FHIR-style filters and return match score."""
        score = 0.0
        matches = 0
        total_filters = len(filters)

        for param, value in filters.items():
            if self._matches_fhir_param(resource, param, value):
                matches += 1

        if matches > 0:
            score = matches / total_filters

        return score

    def _matches_fhir_param(
        self, resource: BaseResource, param: str, value: Any
    ) -> bool:
        """Check if resource matches FHIR parameter."""
        if isinstance(resource, Patient):
            if param == "given" and any(
                value.lower() in name.lower() for name in resource.given
            ):
                return True
            if param == "family" and value.lower() in resource.family.lower():
                return True
            if param == "gender" and str(resource.gender).lower() == str(value).lower():
                return True

        elif isinstance(resource, Observation):
            if param == "code" and resource.code and value in str(resource.code):
                return True
            if param == "subject" and value in resource.subject:
                return True
            if param == "status" and str(resource.status).lower() == str(value).lower():
                return True

        return False

    def _vector_similarity_stub(self, resource: BaseResource, query: str) -> float:
        """Stub for vector similarity search."""
        # In production, this would:
        # 1. Generate embedding for query
        # 2. Compare with stored resource embeddings
        # 3. Return cosine similarity score

        # For now, return a mock score based on text similarity
        text_score = self._calculate_text_score(resource, query.lower())
        return text_score * 0.8  # Simulate vector similarity


# Global search engine
_search_engine = SearchEngine()


def search_resources(
    resource_type: str,
    filters: dict[str, Any],
    vector_query: str | None = None,
    actor: Actor | None = None,
    limit: int = 10,
) -> list[SearchResult]:
    """
    Main search function with FHIR parameter translation.

    Example:
        results = search_resources(
            "Observation",
            {"code": "55284-4", "date": "2025-05"},
            vector_query="tachycardia",
            actor=physician
        )
    """
    engine = _search_engine
    return engine.search_resources(
        resource_type=resource_type,
        filters=filters,
        vector_query=vector_query,
        actor=actor,
        limit=limit,
    )


def search_patients(query: str, actor: Actor, limit: int = 10) -> list[SearchResult]:
    """Search patients by name."""
    engine = _search_engine
    return engine.search_resources(
        "Patient", text_query=query, actor=actor, limit=limit
    )


def search_observations(
    code: str | None = None,
    subject: str | None = None,
    actor: Actor | None = None,
    limit: int = 10,
) -> list[SearchResult]:
    """Search observations with FHIR parameters."""
    filters = {}
    if code:
        filters["code"] = code
    if subject:
        filters["subject"] = subject

    return search_resources("Observation", filters, actor=actor, limit=limit)
