"""
HACS Tools Package

This package provides tools and utilities for working with HACS resources,
including CRUD operations, search functionality, validation, and vectorization.
"""

# CRUD Operations
from .crud import (
    CreateResource,
    ReadResource,
    UpdateResource,
    DeleteResource,
    ListResources,
    GetAuditLog,
    CreatePatient,
    ReadPatient,
    CreateObservation,
    ReadObservation,
    StorageBackend,
    CRUDOperation,
    CRUDError,
    PermissionError,
    ResourceNotFoundError,
    ConflictError,
    AuditEvent,
    StorageManager,
    PermissionManager,
    set_storage_backend,
    get_storage_manager,
)

# Base vectorization classes and protocols
from .vectorization import (
    EmbeddingModel,
    VectorStore,
    VectorMetadata,
    HACSVectorizer,
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
