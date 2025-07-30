"""
Actor models for authentication, authorization, and audit trails.

This module provides actor-related models that enable secure agent interactions
with proper permission management, authentication context, and audit logging.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Literal, Optional
from pydantic import Field, field_validator, computed_field

from .base_resource import BaseResource


class ActorRole(str, Enum):
    """Standard actor roles in healthcare systems."""

    PHYSICIAN = "physician"
    NURSE = "nurse"
    PHARMACIST = "pharmacist"
    THERAPIST = "therapist"
    TECHNICIAN = "technician"
    ADMINISTRATOR = "administrator"
    PATIENT = "patient"
    CAREGIVER = "caregiver"
    AGENT = "agent"
    SYSTEM = "system"
    RESEARCHER = "researcher"
    AUDITOR = "auditor"


class PermissionLevel(str, Enum):
    """Permission levels for resource access."""

    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"
    AUDIT = "audit"


class SessionStatus(str, Enum):
    """Session status values."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"
    LOCKED = "locked"
    TERMINATED = "terminated"


class Actor(BaseResource):
    """
    Represents an actor (human or agent) in the healthcare system.

    Actors have roles, permissions, and authentication context for secure
    interactions with healthcare data and other agents.
    """

    resource_type: Literal["Actor"] = Field(
        default="Actor", description="Resource type identifier"
    )

    name: str = Field(
        description="Display name of the actor",
        examples=["Dr. Sarah Johnson", "Nursing Agent v2.1", "John Doe (Patient)"],
    )

    role: ActorRole = Field(
        description="Primary role of this actor",
        examples=["physician", "agent", "patient"],
    )

    permissions: List[str] = Field(
        default_factory=list,
        description="List of permissions granted to this actor",
        examples=[
            ["read:patient", "write:observation", "read:encounter"],
            ["admin:system", "audit:all"],
            ["read:own_data", "write:own_data"],
        ],
    )

    auth_context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Authentication and authorization context",
        examples=[
            {
                "auth_provider": "oauth2",
                "token_type": "bearer",
                "scope": ["patient:read", "observation:write"],
                "issued_at": "2024-01-15T10:30:00Z",
                "expires_at": "2024-01-15T18:30:00Z",
            }
        ],
    )

    session_id: Optional[str] = Field(
        default=None,
        description="Current session identifier",
        examples=["sess_abc123", "session_456def", None],
    )

    session_status: SessionStatus = Field(
        default=SessionStatus.INACTIVE, description="Current session status"
    )

    last_activity: Optional[datetime] = Field(
        default=None, description="Timestamp of last activity"
    )

    organization: Optional[str] = Field(
        default=None,
        description="Organization this actor belongs to",
        examples=["Mayo Clinic", "Johns Hopkins", "AI Health Systems Inc."],
    )

    department: Optional[str] = Field(
        default=None,
        description="Department within the organization",
        examples=["Cardiology", "Emergency Medicine", "AI Operations"],
    )

    contact_info: Dict[str, str] = Field(
        default_factory=dict,
        description="Contact information for this actor",
        examples=[
            {
                "email": "sarah.johnson@hospital.com",
                "phone": "+1-555-0123",
                "pager": "12345",
            }
        ],
    )

    audit_trail: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Audit trail of significant actions",
        examples=[
            [
                {
                    "action": "login",
                    "timestamp": "2024-01-15T10:30:00Z",
                    "ip_address": "192.168.1.100",
                    "user_agent": "Mozilla/5.0...",
                }
            ]
        ],
    )

    is_active: bool = Field(
        default=True, description="Whether this actor is currently active"
    )

    security_level: Literal["low", "medium", "high", "critical"] = Field(
        default="medium", description="Security clearance level"
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Ensure name is not empty."""
        if not v.strip():
            raise ValueError("Actor name cannot be empty")
        return v.strip()

    @field_validator("permissions")
    @classmethod
    def validate_permissions(cls, v: List[str]) -> List[str]:
        """Validate permission format."""
        validated_permissions = []
        for perm in v:
            if not isinstance(perm, str) or not perm.strip():
                continue
            # Basic format validation: should be like "action:resource"
            perm = perm.strip().lower()
            if ":" not in perm:
                raise ValueError(
                    f"Permission '{perm}' must be in format 'action:resource'"
                )
            validated_permissions.append(perm)
        return validated_permissions

    @field_validator("auth_context")
    @classmethod
    def validate_auth_context(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure auth_context is a valid dictionary."""
        if not isinstance(v, dict):
            raise ValueError("Auth context must be a dictionary")
        return v

    @computed_field
    @property
    def is_authenticated(self) -> bool:
        """Check if actor has valid authentication."""
        if not self.auth_context:
            return False

        # Check if token is expired
        expires_at = self.auth_context.get("expires_at")
        if expires_at:
            try:
                expiry = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
                if datetime.now(timezone.utc) > expiry:
                    return False
            except (ValueError, TypeError):
                return False

        return self.session_status == SessionStatus.ACTIVE

    @computed_field
    @property
    def permission_summary(self) -> Dict[str, List[str]]:
        """Group permissions by action type."""
        summary = {}
        for perm in self.permissions:
            if ":" in perm:
                action, resource = perm.split(":", 1)
                if action not in summary:
                    summary[action] = []
                summary[action].append(resource)
        return summary

    def has_permission(self, permission: str) -> bool:
        """
        Check if actor has a specific permission.

        Args:
            permission: Permission to check (format: "action:resource")

        Returns:
            True if actor has the permission
        """
        if not self.is_active or not self.is_authenticated:
            return False

        permission = permission.lower().strip()

        # Check exact permission
        if permission in self.permissions:
            return True

        # Check for wildcard permissions
        if ":" in permission:
            action, resource = permission.split(":", 1)

            # Check for action:* (all resources for this action)
            if f"{action}:*" in self.permissions:
                return True

            # Check for admin permissions
            if "admin:*" in self.permissions or "admin:all" in self.permissions:
                return True

        return False

    def add_permission(self, permission: str) -> None:
        """
        Add a permission to this actor.

        Args:
            permission: Permission to add (format: "action:resource")
        """
        permission = permission.lower().strip()
        if ":" not in permission:
            raise ValueError("Permission must be in format 'action:resource'")

        if permission not in self.permissions:
            self.permissions.append(permission)
            self.update_timestamp()
            self._log_audit_event("permission_added", {"permission": permission})

    def remove_permission(self, permission: str) -> bool:
        """
        Remove a permission from this actor.

        Args:
            permission: Permission to remove

        Returns:
            True if permission was removed, False if not found
        """
        permission = permission.lower().strip()
        if permission in self.permissions:
            self.permissions.remove(permission)
            self.update_timestamp()
            self._log_audit_event("permission_removed", {"permission": permission})
            return True
        return False

    def update_auth_context(self, key: str, value: Any) -> None:
        """
        Update authentication context.

        Args:
            key: Context key
            value: Context value
        """
        self.auth_context[key] = value
        self.update_timestamp()

    def start_session(self, session_id: str, **context) -> None:
        """
        Start a new session for this actor.

        Args:
            session_id: Unique session identifier
            **context: Additional session context
        """
        self.session_id = session_id
        self.session_status = SessionStatus.ACTIVE
        self.last_activity = datetime.now(timezone.utc)

        # Update auth context with session info - ensure at least session_id is in context
        self.auth_context["session_id"] = session_id
        self.auth_context["session_started"] = datetime.now(timezone.utc).isoformat()

        for key, value in context.items():
            self.auth_context[key] = value

        self.update_timestamp()
        self._log_audit_event("session_started", {"session_id": session_id, **context})

    def end_session(self, reason: str = "user_logout") -> None:
        """
        End the current session.

        Args:
            reason: Reason for ending the session
        """
        old_session_id = self.session_id
        self.session_id = None
        self.session_status = SessionStatus.TERMINATED
        self.update_timestamp()

        self._log_audit_event(
            "session_ended", {"session_id": old_session_id, "reason": reason}
        )

    def update_activity(self) -> None:
        """Update the last activity timestamp."""
        self.last_activity = datetime.now(timezone.utc)
        self.update_timestamp()

    def deactivate(self, reason: str = "administrative") -> None:
        """
        Deactivate this actor.

        Args:
            reason: Reason for deactivation
        """
        self.is_active = False
        if self.session_id:
            self.end_session(f"deactivated: {reason}")
        self.update_timestamp()

        self._log_audit_event("actor_deactivated", {"reason": reason})

    def activate(self, reason: str = "administrative") -> None:
        """
        Activate this actor.

        Args:
            reason: Reason for activation
        """
        self.is_active = True
        self.update_timestamp()

        self._log_audit_event("actor_activated", {"reason": reason})

    def _log_audit_event(self, action: str, details: Dict[str, Any]) -> None:
        """
        Log an audit event.

        Args:
            action: Action that occurred
            details: Additional details about the action
        """
        audit_entry = {
            "action": action,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "actor_id": self.id,
            "details": details,
        }
        self.audit_trail.append(audit_entry)

    def get_audit_events(
        self, action_filter: Optional[str] = None, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get audit events for this actor.

        Args:
            action_filter: Filter by specific action type
            limit: Maximum number of events to return

        Returns:
            List of audit events
        """
        events = self.audit_trail

        if action_filter:
            events = [e for e in events if e.get("action") == action_filter]

        # Return most recent events first
        return sorted(events, key=lambda x: x.get("timestamp", ""), reverse=True)[
            :limit
        ]

    def is_session_expired(self, timeout_minutes: int = 480) -> bool:
        """
        Check if the current session has expired.

        Args:
            timeout_minutes: Session timeout in minutes (default 8 hours)

        Returns:
            True if session is expired
        """
        if not self.last_activity or self.session_status != SessionStatus.ACTIVE:
            return True

        timeout_threshold = datetime.now(timezone.utc).timestamp() - (
            timeout_minutes * 60
        )
        last_activity_timestamp = self.last_activity.timestamp()

        return last_activity_timestamp < timeout_threshold

    def __repr__(self) -> str:
        """Enhanced representation including role and status."""
        status = "active" if self.is_active else "inactive"
        auth_status = "authenticated" if self.is_authenticated else "unauthenticated"
        return f"Actor(id='{self.id}', name='{self.name}', role='{self.role}', status='{status}', auth='{auth_status}')"
