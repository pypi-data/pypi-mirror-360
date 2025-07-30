"""
HACS Tools Package

This package provides tools and utilities for working with HACS resources,
including CRUD operations, search functionality, validation, and vectorization.
"""

# CRUD Operations
from .crud import (
    AuditEvent,
    ConflictError,
    CreateObservation,
    CreatePatient,
    CreateResource,
    CRUDError,
    CRUDOperation,
    DeleteResource,
    GetAuditLog,
    ListResources,
    PermissionError,
    PermissionManager,
    ReadObservation,
    ReadPatient,
    ReadResource,
    ResourceNotFoundError,
    StorageBackend,
    StorageManager,
    UpdateResource,
    get_storage_manager,
    set_storage_backend,
)

# Base vectorization classes and protocols
from .vectorization import (
    EmbeddingModel,
    HACSVectorizer,
    VectorMetadata,
    VectorStore,
)

__all__ = [
    # CRUD operations
    "CreateResource",
    "ReadResource",
    "UpdateResource",
    "DeleteResource",
    "ListResources",
    "GetAuditLog",
    "CreatePatient",
    "ReadPatient",
    "CreateObservation",
    "ReadObservation",
    "StorageBackend",
    "CRUDOperation",
    "CRUDError",
    "PermissionError",
    "ResourceNotFoundError",
    "ConflictError",
    "AuditEvent",
    "StorageManager",
    "PermissionManager",
    "set_storage_backend",
    "get_storage_manager",
    # Base vectorization
    "EmbeddingModel",
    "VectorStore",
    "VectorMetadata",
    "HACSVectorizer",
]


def hello() -> str:
    return "Hello from hacs-tools!"
