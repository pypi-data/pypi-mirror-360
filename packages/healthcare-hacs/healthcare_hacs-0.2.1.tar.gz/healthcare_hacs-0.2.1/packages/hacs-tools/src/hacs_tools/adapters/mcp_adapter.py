"""
MCP (Model Context Protocol) Adapter

This module provides adapters for converting HACS CRUD operations to MCP task format
with Actor permission mapping and context preservation.
"""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from hacs_core import Actor, BaseResource, Evidence, MemoryBlock
from pydantic import BaseModel, Field


class MCPTaskType(str, Enum):
    """MCP task types for different operations."""

    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    SEARCH = "search"
    VALIDATE = "validate"
    MEMORY_STORE = "memory_store"
    MEMORY_RECALL = "memory_recall"
    EVIDENCE_CREATE = "evidence_create"
    EVIDENCE_SEARCH = "evidence_search"


class MCPTask(BaseModel):
    """MCP Task format for agent communication."""

    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    task_type: MCPTaskType = Field(description="Type of MCP task")
    resource_type: str = Field(description="HACS resource type")
    payload: dict[str, Any] = Field(description="Task payload")
    context: dict[str, Any] = Field(default_factory=dict, description="Task context")
    actor_context: dict[str, Any] = Field(description="Actor permissions and context")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    priority: int = Field(default=5, ge=1, le=10, description="Task priority (1-10)")
    timeout_seconds: int = Field(default=30, description="Task timeout in seconds")
    metadata: dict[str, Any] = Field(default_factory=dict)


class MCPResult(BaseModel):
    """MCP Result format for task responses."""

    task_id: str = Field(description="Original task ID")
    success: bool = Field(description="Whether task completed successfully")
    result: dict[str, Any] | None = Field(default=None, description="Task result data")
    error: str | None = Field(default=None, description="Error message if failed")
    execution_time_ms: float = Field(description="Task execution time in milliseconds")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = Field(default_factory=dict)


class MCPAdapter:
    """Adapter for converting HACS operations to MCP format."""

    def __init__(self, server_url: str | None = None):
        """Initialize MCP adapter.

        Args:
            server_url: Optional MCP server URL for routing
        """
        self.server_url = server_url
        self.task_registry: dict[str, MCPTask] = {}

    def create_actor_context(self, actor: Actor) -> dict[str, Any]:
        """Create MCP-compatible actor context.

        Args:
            actor: HACS Actor instance

        Returns:
            Dict containing actor context for MCP
        """
        return {
            "actor_id": actor.id,
            "actor_name": actor.name,
            "actor_role": actor.role.value
            if hasattr(actor.role, "value")
            else str(actor.role),
            "permissions": actor.permissions,
            "is_active": actor.is_active,
            "session_id": getattr(actor, "session_id", None),
            "organization": getattr(actor, "organization", None),
            "auth_context": getattr(actor, "auth_context", {}),
        }

    def convert_resource_to_payload(self, resource: BaseResource) -> dict[str, Any]:
        """Convert HACS resource to MCP payload format.

        Args:
            resource: HACS resource instance

        Returns:
            Dict containing resource data for MCP
        """
        payload = resource.model_dump()

        # Add MCP-specific metadata
        payload["_mcp_metadata"] = {
            "resource_type": resource.resource_type,
            "created_at": resource.created_at.isoformat(),
            "updated_at": resource.updated_at.isoformat(),
            "age_seconds": getattr(resource, "age_seconds", 0),
        }

        return payload

    def create_crud_task(
        self,
        operation: str,
        resource: BaseResource | None = None,
        resource_type: str | None = None,
        resource_id: str | None = None,
        actor: Actor | None = None,
        **kwargs,
    ) -> MCPTask:
        """Create MCP task for CRUD operations.

        Args:
            operation: CRUD operation (create, read, update, delete)
            resource: Resource for create/update operations
            resource_type: Resource type for read/delete operations
            resource_id: Resource ID for read/update/delete operations
            actor: Actor performing the operation
            **kwargs: Additional task parameters

        Returns:
            MCPTask instance
        """
        task_type = MCPTaskType(operation.lower())

        # Build payload based on operation
        payload = {}
        if resource:
            payload = self.convert_resource_to_payload(resource)
        elif resource_type and resource_id:
            payload = {"resource_type": resource_type, "resource_id": resource_id}

        # Add additional parameters
        payload.update(kwargs)

        # Create actor context
        actor_context = {}
        if actor:
            actor_context = self.create_actor_context(actor)

        # Create task
        task = MCPTask(
            task_type=task_type,
            resource_type=resource_type
            or (resource.resource_type if resource else "unknown"),
            payload=payload,
            actor_context=actor_context,
            priority=kwargs.get("priority", 5),
            timeout_seconds=kwargs.get("timeout_seconds", 30),
        )

        # Register task
        self.task_registry[task.task_id] = task

        return task

    def create_memory_task(
        self,
        operation: str,
        memory_block: MemoryBlock | None = None,
        query: str | None = None,
        memory_type: str | None = None,
        actor: Actor | None = None,
        **kwargs,
    ) -> MCPTask:
        """Create MCP task for memory operations.

        Args:
            operation: Memory operation (store, recall)
            memory_block: Memory block for store operations
            query: Search query for recall operations
            memory_type: Memory type filter
            actor: Actor performing the operation
            **kwargs: Additional task parameters

        Returns:
            MCPTask instance
        """
        task_type = (
            MCPTaskType.MEMORY_STORE
            if operation == "store"
            else MCPTaskType.MEMORY_RECALL
        )

        # Build payload
        payload = {}
        if memory_block:
            payload = self.convert_resource_to_payload(memory_block)
        elif query:
            payload = {
                "query": query,
                "memory_type": memory_type,
                "limit": kwargs.get("limit", 10),
                "min_importance": kwargs.get("min_importance", 0.0),
            }

        # Create actor context
        actor_context = {}
        if actor:
            actor_context = self.create_actor_context(actor)

        # Create task
        task = MCPTask(
            task_type=task_type,
            resource_type="MemoryBlock",
            payload=payload,
            actor_context=actor_context,
            priority=kwargs.get(
                "priority", 6
            ),  # Memory operations slightly higher priority
            timeout_seconds=kwargs.get("timeout_seconds", 45),
        )

        # Register task
        self.task_registry[task.task_id] = task

        return task

    def create_evidence_task(
        self,
        operation: str,
        evidence: Evidence | None = None,
        query: str | None = None,
        evidence_level: str | None = None,
        actor: Actor | None = None,
        **kwargs,
    ) -> MCPTask:
        """Create MCP task for evidence operations.

        Args:
            operation: Evidence operation (create, search)
            evidence: Evidence for create operations
            query: Search query for search operations
            evidence_level: Evidence level filter
            actor: Actor performing the operation
            **kwargs: Additional task parameters

        Returns:
            MCPTask instance
        """
        task_type = (
            MCPTaskType.EVIDENCE_CREATE
            if operation == "create"
            else MCPTaskType.EVIDENCE_SEARCH
        )

        # Build payload
        payload = {}
        if evidence:
            payload = self.convert_resource_to_payload(evidence)
        elif query:
            payload = {
                "query": query,
                "evidence_level": evidence_level,
                "min_confidence": kwargs.get("min_confidence", 0.0),
                "min_quality": kwargs.get("min_quality", 0.0),
                "limit": kwargs.get("limit", 10),
            }

        # Create actor context
        actor_context = {}
        if actor:
            actor_context = self.create_actor_context(actor)

        # Create task
        task = MCPTask(
            task_type=task_type,
            resource_type="Evidence",
            payload=payload,
            actor_context=actor_context,
            priority=kwargs.get("priority", 7),  # Evidence operations high priority
            timeout_seconds=kwargs.get("timeout_seconds", 60),
        )

        # Register task
        self.task_registry[task.task_id] = task

        return task

    def create_result(
        self,
        task_id: str,
        success: bool,
        result: Any | None = None,
        error: str | None = None,
        execution_time_ms: float = 0.0,
        **kwargs,
    ) -> MCPResult:
        """Create MCP result for task completion.

        Args:
            task_id: Original task ID
            success: Whether task completed successfully
            result: Task result data
            error: Error message if failed
            execution_time_ms: Task execution time in milliseconds
            **kwargs: Additional metadata

        Returns:
            MCPResult instance
        """
        # Convert result to dict if it's a BaseResource
        result_data: dict[str, Any] | None = None
        if result is not None:
            if isinstance(result, BaseResource):
                result_data = result.model_dump()
            elif (
                isinstance(result, list)
                and result
                and isinstance(result[0], BaseResource)
            ):
                result_data = {"items": [item.model_dump() for item in result]}
            else:
                result_data = {"value": result}

        return MCPResult(
            task_id=task_id,
            success=success,
            result=result_data,
            error=error,
            execution_time_ms=execution_time_ms,
            metadata=kwargs,
        )

    def get_task(self, task_id: str) -> MCPTask | None:
        """Get task by ID.

        Args:
            task_id: Task ID

        Returns:
            MCPTask instance or None if not found
        """
        return self.task_registry.get(task_id)

    def list_tasks(self, task_type: MCPTaskType | None = None) -> list[MCPTask]:
        """List tasks, optionally filtered by type.

        Args:
            task_type: Optional task type filter

        Returns:
            List of MCPTask instances
        """
        tasks = list(self.task_registry.values())

        if task_type:
            tasks = [task for task in tasks if task.task_type == task_type]

        return tasks


# Convenience functions for direct usage
def convert_to_mcp_task(
    operation: str,
    resource: BaseResource | None = None,
    actor: Actor | None = None,
    **kwargs,
) -> MCPTask:
    """Convert HACS operation to MCP task format.

    Args:
        operation: Operation type (create, read, update, delete, etc.)
        resource: HACS resource
        actor: Actor performing operation
        **kwargs: Additional parameters

    Returns:
        MCPTask instance
    """
    adapter = MCPAdapter()

    if operation in ["memory_store", "memory_recall"]:
        return adapter.create_memory_task(
            operation.replace("memory_", ""),
            memory_block=resource if isinstance(resource, MemoryBlock) else None,
            actor=actor,
            **kwargs,
        )
    elif operation in ["evidence_create", "evidence_search"]:
        return adapter.create_evidence_task(
            operation.replace("evidence_", ""),
            evidence=resource if isinstance(resource, Evidence) else None,
            actor=actor,
            **kwargs,
        )
    else:
        return adapter.create_crud_task(
            operation, resource=resource, actor=actor, **kwargs
        )


def convert_from_mcp_result(mcp_result: MCPResult) -> dict[str, Any]:
    """Convert MCP result back to standard format.

    Args:
        mcp_result: MCP result instance

    Returns:
        Dict containing result data
    """
    return {
        "task_id": mcp_result.task_id,
        "success": mcp_result.success,
        "data": mcp_result.result,
        "error": mcp_result.error,
        "execution_time_ms": mcp_result.execution_time_ms,
        "timestamp": mcp_result.timestamp.isoformat(),
        "metadata": mcp_result.metadata,
    }
