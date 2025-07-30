"""
CRUD Operations for HACS Resources

This module provides comprehensive Create, Read, Update, Delete operations
with Actor permission validation, audit logging, and storage backend support.
"""

import logging
import os
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from hacs_core import Actor, ActorRole, BaseResource
from hacs_models import Observation, Patient
from pydantic import BaseModel, Field


class StorageBackend(str, Enum):
    """Available storage backends."""

    MEMORY = "memory"
    MCP = "mcp"
    FILE = "file"
    DATABASE = "database"


class CRUDOperation(str, Enum):
    """CRUD operation types."""

    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"


class CRUDError(Exception):
    """Base exception for CRUD operations."""

    pass


class PermissionError(CRUDError):
    """Exception raised for permission violations."""

    pass


class ResourceNotFoundError(CRUDError):
    """Exception raised when resource is not found."""

    pass


class ConflictError(CRUDError):
    """Exception raised for resource conflicts."""

    pass


class AuditEvent(BaseModel):
    """Audit event for CRUD operations."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    operation: CRUDOperation
    resource_type: str
    resource_id: str
    actor_id: str
    success: bool
    error_message: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class StorageManager:
    """Manages different storage backends."""

    def __init__(self, backend: StorageBackend = StorageBackend.MEMORY):
        self.backend = backend
        self._memory_store: dict[str, dict[str, BaseResource]] = {}
        self._audit_log: list[AuditEvent] = []
        self.logger = logging.getLogger(__name__)

        # MCP routing preparation
        self.mcp_url = os.getenv("HACS_MCP_URL")
        if self.mcp_url:
            self.logger.info(f"MCP routing enabled: {self.mcp_url}")

    def _get_collection(self, resource_type: str) -> dict[str, BaseResource]:
        """Get or create collection for resource type."""
        if resource_type not in self._memory_store:
            self._memory_store[resource_type] = {}
        return self._memory_store[resource_type]

    def store(self, resource: BaseResource) -> str:
        """Store a resource and return its ID."""
        if self.backend == StorageBackend.MEMORY:
            collection = self._get_collection(resource.resource_type)
            collection[resource.id] = resource
            return resource.id
        elif self.backend == StorageBackend.MCP and self.mcp_url:
            # MCP routing would be implemented here
            self.logger.info(f"Would route to MCP: {self.mcp_url}")
            # Fallback to memory for now
            return self.store_in_memory(resource)
        else:
            raise CRUDError(f"Storage backend {self.backend} not implemented")

    def store_in_memory(self, resource: BaseResource) -> str:
        """Store resource in memory (fallback method)."""
        collection = self._get_collection(resource.resource_type)
        collection[resource.id] = resource
        return resource.id

    def retrieve(self, resource_type: str, resource_id: str) -> BaseResource | None:
        """Retrieve a resource by type and ID."""
        if self.backend == StorageBackend.MEMORY:
            collection = self._get_collection(resource_type)
            return collection.get(resource_id)
        else:
            raise CRUDError(f"Storage backend {self.backend} not implemented")

    def update(self, resource: BaseResource) -> bool:
        """Update an existing resource."""
        if self.backend == StorageBackend.MEMORY:
            collection = self._get_collection(resource.resource_type)
            if resource.id in collection:
                resource.update_timestamp()
                collection[resource.id] = resource
                return True
            return False
        else:
            raise CRUDError(f"Storage backend {self.backend} not implemented")

    def delete(self, resource_type: str, resource_id: str) -> bool:
        """Delete a resource by type and ID."""
        if self.backend == StorageBackend.MEMORY:
            collection = self._get_collection(resource_type)
            if resource_id in collection:
                del collection[resource_id]
                return True
            return False
        else:
            raise CRUDError(f"Storage backend {self.backend} not implemented")

    def list_resources(
        self, resource_type: str, limit: int = 100, offset: int = 0
    ) -> list[BaseResource]:
        """List resources of a given type with pagination."""
        if self.backend == StorageBackend.MEMORY:
            collection = self._get_collection(resource_type)
            resources = list(collection.values())
            return resources[offset : offset + limit]
        else:
            raise CRUDError(f"Storage backend {self.backend} not implemented")

    def add_audit_event(self, event: AuditEvent) -> None:
        """Add an audit event to the log."""
        self._audit_log.append(event)
        self.logger.info(
            f"Audit: {event.operation} {event.resource_type}/{event.resource_id} by {event.actor_id} - {'SUCCESS' if event.success else 'FAILED'}"
        )

    def get_audit_log(
        self,
        resource_type: str | None = None,
        actor_id: str | None = None,
        limit: int = 100,
    ) -> list[AuditEvent]:
        """Get audit log with optional filtering."""
        events = self._audit_log

        if resource_type:
            events = [e for e in events if e.resource_type == resource_type]

        if actor_id:
            events = [e for e in events if e.actor_id == actor_id]

        return events[-limit:]


class PermissionManager:
    """Manages Actor permissions for CRUD operations."""

    @staticmethod
    def check_permission(
        actor: Actor,
        operation: CRUDOperation,
        resource_type: str,
        resource_id: str | None = None,
    ) -> bool:
        """Check if actor has permission for the operation."""
        if not actor.is_active:
            return False

        # System actors have all permissions
        if actor.role == ActorRole.SYSTEM:
            return True

        # Check specific permissions
        required_permission = f"{resource_type.lower()}:{operation.value}"
        wildcard_permission = f"{resource_type.lower()}:*"
        global_permission = "*:*"

        return any(
            perm in [required_permission, wildcard_permission, global_permission]
            for perm in actor.permissions
        )

    @staticmethod
    def validate_permission(
        actor: Actor,
        operation: CRUDOperation,
        resource_type: str,
        resource_id: str | None = None,
    ) -> None:
        """Validate permission and raise exception if denied."""
        if not PermissionManager.check_permission(
            actor, operation, resource_type, resource_id
        ):
            raise PermissionError(
                f"Actor {actor.id} ({actor.role}) lacks permission for {operation.value} on {resource_type}"
            )


# Global storage manager instance
_storage_manager = StorageManager()


def set_storage_backend(backend: StorageBackend) -> None:
    """Set the global storage backend."""
    global _storage_manager
    _storage_manager = StorageManager(backend)


def get_storage_manager() -> StorageManager:
    """Get the global storage manager."""
    return _storage_manager


def CreateResource(
    resource: BaseResource, actor: Actor, storage_backend: str = "memory"
) -> str:
    """
    Create a new resource with Actor permission validation.

    Args:
        resource: Resource to create
        actor: Actor performing the operation
        storage_backend: Storage backend to use

    Returns:
        Resource ID

    Raises:
        PermissionError: If actor lacks permission
        CRUDError: If creation fails
    """
    storage = get_storage_manager()

    # Validate permissions
    PermissionManager.validate_permission(
        actor, CRUDOperation.CREATE, resource.resource_type
    )

    # Create audit event
    audit_event = AuditEvent(
        operation=CRUDOperation.CREATE,
        resource_type=resource.resource_type,
        resource_id=resource.id,
        actor_id=actor.id,
        success=False,
    )

    try:
        # Check if resource already exists
        existing = storage.retrieve(resource.resource_type, resource.id)
        if existing:
            raise ConflictError(
                f"Resource {resource.resource_type}/{resource.id} already exists"
            )

        # Store the resource
        resource_id = storage.store(resource)

        # Update audit event
        audit_event.success = True
        audit_event.metadata = {
            "resource_fields": len(resource.__class__.model_fields),
            "storage_backend": storage_backend,
        }

        return resource_id

    except Exception as e:
        audit_event.error_message = str(e)
        raise
    finally:
        storage.add_audit_event(audit_event)


def ReadResource(resource_type: str, resource_id: str, actor: Actor) -> BaseResource:
    """
    Read a resource with Actor permission validation.

    Args:
        resource_type: Type of resource to read
        resource_id: ID of resource to read
        actor: Actor performing the operation

    Returns:
        The requested resource

    Raises:
        PermissionError: If actor lacks permission
        ResourceNotFoundError: If resource not found
    """
    storage = get_storage_manager()

    # Validate permissions
    PermissionManager.validate_permission(
        actor, CRUDOperation.READ, resource_type, resource_id
    )

    # Create audit event
    audit_event = AuditEvent(
        operation=CRUDOperation.READ,
        resource_type=resource_type,
        resource_id=resource_id,
        actor_id=actor.id,
        success=False,
    )

    try:
        # Retrieve the resource
        resource = storage.retrieve(resource_type, resource_id)
        if not resource:
            raise ResourceNotFoundError(
                f"Resource {resource_type}/{resource_id} not found"
            )

        # Update audit event
        audit_event.success = True
        audit_event.metadata = {"resource_age_seconds": resource.get_age_seconds()}

        return resource

    except Exception as e:
        audit_event.error_message = str(e)
        raise
    finally:
        storage.add_audit_event(audit_event)


def UpdateResource(resource: BaseResource, actor: Actor) -> BaseResource:
    """
    Update an existing resource with Actor permission validation.

    Args:
        resource: Updated resource
        actor: Actor performing the operation

    Returns:
        The updated resource

    Raises:
        PermissionError: If actor lacks permission
        ResourceNotFoundError: If resource not found
        ConflictError: If resource has been modified
    """
    storage = get_storage_manager()

    # Validate permissions
    PermissionManager.validate_permission(
        actor, CRUDOperation.UPDATE, resource.resource_type, resource.id
    )

    # Create audit event
    audit_event = AuditEvent(
        operation=CRUDOperation.UPDATE,
        resource_type=resource.resource_type,
        resource_id=resource.id,
        actor_id=actor.id,
        success=False,
    )

    try:
        # Check if resource exists
        existing = storage.retrieve(resource.resource_type, resource.id)
        if not existing:
            raise ResourceNotFoundError(
                f"Resource {resource.resource_type}/{resource.id} not found"
            )

        # Conflict detection (basic version)
        if hasattr(existing, "updated_at") and hasattr(resource, "updated_at"):
            if existing.updated_at > resource.updated_at:
                raise ConflictError(
                    f"Resource {resource.resource_type}/{resource.id} has been modified by another actor"
                )

        # Update the resource
        success = storage.update(resource)
        if not success:
            raise CRUDError(
                f"Failed to update resource {resource.resource_type}/{resource.id}"
            )

        # Update audit event
        audit_event.success = True
        audit_event.metadata = {
            "previous_update": existing.updated_at.isoformat()
            if hasattr(existing, "updated_at")
            else None,
            "new_update": resource.updated_at.isoformat()
            if hasattr(resource, "updated_at")
            else None,
        }

        return resource

    except Exception as e:
        audit_event.error_message = str(e)
        raise
    finally:
        storage.add_audit_event(audit_event)


def DeleteResource(
    resource_type: str, resource_id: str, actor: Actor, cascade: bool = False
) -> bool:
    """
    Delete a resource with Actor permission validation.

    Args:
        resource_type: Type of resource to delete
        resource_id: ID of resource to delete
        actor: Actor performing the operation
        cascade: Whether to cascade delete related resources

    Returns:
        True if deleted successfully

    Raises:
        PermissionError: If actor lacks permission
        ResourceNotFoundError: If resource not found
    """
    storage = get_storage_manager()

    # Validate permissions
    PermissionManager.validate_permission(
        actor, CRUDOperation.DELETE, resource_type, resource_id
    )

    # Create audit event
    audit_event = AuditEvent(
        operation=CRUDOperation.DELETE,
        resource_type=resource_type,
        resource_id=resource_id,
        actor_id=actor.id,
        success=False,
    )

    try:
        # Check if resource exists
        existing = storage.retrieve(resource_type, resource_id)
        if not existing:
            raise ResourceNotFoundError(
                f"Resource {resource_type}/{resource_id} not found"
            )

        # Delete the resource
        success = storage.delete(resource_type, resource_id)
        if not success:
            raise CRUDError(f"Failed to delete resource {resource_type}/{resource_id}")

        # Update audit event
        audit_event.success = True
        audit_event.metadata = {
            "cascade": cascade,
            "resource_age_seconds": existing.get_age_seconds(),
        }

        return True

    except Exception as e:
        audit_event.error_message = str(e)
        raise
    finally:
        storage.add_audit_event(audit_event)


def ListResources(
    resource_type: str, actor: Actor, limit: int = 100, offset: int = 0
) -> list[BaseResource]:
    """
    List resources with Actor permission validation.

    Args:
        resource_type: Type of resources to list
        actor: Actor performing the operation
        limit: Maximum number of resources to return
        offset: Number of resources to skip

    Returns:
        List of resources

    Raises:
        PermissionError: If actor lacks permission
    """
    storage = get_storage_manager()

    # Validate permissions
    PermissionManager.validate_permission(actor, CRUDOperation.READ, resource_type)

    # Create audit event
    audit_event = AuditEvent(
        operation=CRUDOperation.READ,
        resource_type=resource_type,
        resource_id="*",
        actor_id=actor.id,
        success=False,
    )

    try:
        # List resources
        resources = storage.list_resources(resource_type, limit, offset)

        # Update audit event
        audit_event.success = True
        audit_event.metadata = {
            "count": len(resources),
            "limit": limit,
            "offset": offset,
        }

        return resources

    except Exception as e:
        audit_event.error_message = str(e)
        raise
    finally:
        storage.add_audit_event(audit_event)


def GetAuditLog(
    actor: Actor,
    resource_type: str | None = None,
    target_actor_id: str | None = None,
    limit: int = 100,
) -> list[AuditEvent]:
    """
    Get audit log with Actor permission validation.

    Args:
        actor: Actor requesting the audit log
        resource_type: Optional filter by resource type
        target_actor_id: Optional filter by target actor ID
        limit: Maximum number of events to return

    Returns:
        List of audit events

    Raises:
        PermissionError: If actor lacks permission
    """
    # System actors, auditors, and physicians can access audit logs
    if actor.role not in [ActorRole.SYSTEM, ActorRole.AUDITOR, ActorRole.PHYSICIAN]:
        raise PermissionError(
            f"Actor {actor.id} ({actor.role}) cannot access audit logs"
        )

    storage = get_storage_manager()
    return storage.get_audit_log(resource_type, target_actor_id, limit)


# Helper functions for common resource types
def CreatePatient(patient: Patient, actor: Actor) -> str:
    """Create a Patient resource."""
    return CreateResource(patient, actor)


def ReadPatient(patient_id: str, actor: Actor) -> Patient:
    """Read a Patient resource."""
    resource = ReadResource("Patient", patient_id, actor)
    if not isinstance(resource, Patient):
        raise CRUDError(f"Resource {patient_id} is not a Patient")
    return resource


def CreateObservation(observation: Observation, actor: Actor) -> str:
    """Create an Observation resource."""
    return CreateResource(observation, actor)


def ReadObservation(observation_id: str, actor: Actor) -> Observation:
    """Read an Observation resource."""
    resource = ReadResource("Observation", observation_id, actor)
    if not isinstance(resource, Observation):
        raise CRUDError(f"Resource {observation_id} is not an Observation")
    return resource
