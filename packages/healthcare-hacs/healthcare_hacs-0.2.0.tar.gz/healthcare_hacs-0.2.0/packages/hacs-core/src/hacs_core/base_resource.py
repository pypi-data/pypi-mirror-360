"""
Base resource model for all HACS resources.

This module provides the foundational BaseResource class that all HACS models inherit from.
It includes core fields, validation, and serialization capabilities.
"""

from datetime import datetime, timezone
from typing import Any, Dict, Union
from pydantic import BaseModel, Field, ConfigDict


class BaseResource(BaseModel):
    """
    Base class for all HACS resources.

    Provides core functionality including:
    - Resource type identification
    - Unique ID management
    - Timestamp tracking
    - JSON Schema generation
    - Pretty printing
    """

    model_config = ConfigDict(
        # Enable validation on assignment
        validate_assignment=True,
        # Use enum values in serialization
        use_enum_values=True,
        # Allow extra fields for extensibility
        extra="allow",
        # Generate JSON schema with examples
        json_schema_extra={
            "examples": [
                {
                    "id": "resource-001",
                    "resource_type": "BaseResource",
                    "created_at": "2024-01-15T10:30:00Z",
                    "updated_at": "2024-01-15T10:30:00Z",
                }
            ]
        },
    )

    id: str = Field(
        description="Unique identifier for this resource",
        examples=["patient-001", "obs-bp-123", "mem-episode-456"],
    )

    resource_type: Union[str, Any] = Field(
        description="The type of this resource (e.g., Patient, Observation)",
        examples=["Patient", "Encounter", "Observation", "MemoryBlock"],
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When this resource was created (UTC)",
        examples=["2025-01-15T10:30:00Z"],
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When this resource was last updated (UTC)",
        examples=["2025-01-15T10:30:00Z"],
    )

    def __repr__(self) -> str:
        """
        Pretty-print representation of the resource.

        Returns:
            Human-readable string representation
        """
        return f"{self.resource_type}(id='{self.id}', created={self.created_at.isoformat()})"

    def __str__(self) -> str:
        """String representation using __repr__."""
        return self.__repr__()

    def model_dump_json_schema(self) -> Dict[str, Any]:
        """
        Generate JSON Schema for this resource type.

        Returns:
            JSON Schema dictionary
        """
        return self.model_json_schema()

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current UTC time."""
        self.updated_at = datetime.now(timezone.utc)

    def is_newer_than(self, other: "BaseResource") -> bool:
        """
        Check if this resource is newer than another resource.

        Args:
            other: Another BaseResource to compare against

        Returns:
            True if this resource is newer
        """
        return self.updated_at > other.updated_at

    def get_age_seconds(self) -> float:
        """
        Get the age of this resource in seconds.

        Returns:
            Number of seconds since creation
        """
        return (datetime.now(timezone.utc) - self.created_at).total_seconds()
