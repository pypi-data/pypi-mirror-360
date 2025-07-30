"""
AG-UI (Agent-UI) Adapter

This module provides adapters for formatting HACS resources as AG-UI event payloads
with clinical context for frontend integration and user interface updates.
"""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from hacs_core import Actor, BaseResource, Evidence, MemoryBlock
from hacs_models import AgentMessage, Observation, Patient
from pydantic import BaseModel, Field


class AGUIEventType(str, Enum):
    """AG-UI event types for different UI interactions."""

    RESOURCE_CREATED = "resource_created"
    RESOURCE_UPDATED = "resource_updated"
    RESOURCE_DELETED = "resource_deleted"
    MEMORY_STORED = "memory_stored"
    MEMORY_RECALLED = "memory_recalled"
    EVIDENCE_CREATED = "evidence_created"
    EVIDENCE_FOUND = "evidence_found"
    PATIENT_STATUS_CHANGE = "patient_status_change"
    OBSERVATION_ALERT = "observation_alert"
    AGENT_MESSAGE = "agent_message"
    WORKFLOW_UPDATE = "workflow_update"
    NOTIFICATION = "notification"
    ERROR = "error"


class AGUIComponent(str, Enum):
    """AG-UI component types for UI targeting."""

    PATIENT_DASHBOARD = "patient_dashboard"
    OBSERVATION_PANEL = "observation_panel"
    MEMORY_VIEWER = "memory_viewer"
    EVIDENCE_BROWSER = "evidence_browser"
    CHAT_INTERFACE = "chat_interface"
    WORKFLOW_TRACKER = "workflow_tracker"
    ALERT_SYSTEM = "alert_system"
    NAVIGATION = "navigation"
    SIDEBAR = "sidebar"
    MODAL = "modal"
    TOAST = "toast"


class AGUIEvent(BaseModel):
    """AG-UI Event format for frontend updates."""

    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: AGUIEventType = Field(description="Type of UI event")
    component: AGUIComponent = Field(description="Target UI component")
    payload: dict[str, Any] = Field(description="Event payload data")
    ui_context: dict[str, Any] = Field(
        default_factory=dict, description="UI-specific context"
    )
    actor_context: dict[str, Any] = Field(
        default_factory=dict, description="Actor context"
    )
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    priority: int = Field(default=5, ge=1, le=10, description="Event priority (1-10)")
    auto_dismiss: bool = Field(
        default=False, description="Whether event should auto-dismiss"
    )
    dismiss_after_ms: int | None = Field(
        default=None, description="Auto-dismiss timeout"
    )
    metadata: dict[str, Any] = Field(default_factory=dict)


class AGUIAdapter:
    """Adapter for formatting HACS resources as AG-UI events."""

    def __init__(self):
        """Initialize AG-UI adapter."""
        self.event_registry: dict[str, AGUIEvent] = {}

    def create_ui_context(
        self, resource: BaseResource, action: str = "view"
    ) -> dict[str, Any]:
        """Create UI context from resource.

        Args:
            resource: HACS resource instance
            action: UI action (view, edit, create, delete)

        Returns:
            Dict containing UI context
        """
        context = {
            "resource_type": resource.resource_type,
            "resource_id": resource.id,
            "action": action,
            "created_at": resource.created_at.isoformat(),
            "updated_at": resource.updated_at.isoformat(),
        }

        # Add resource-specific UI context
        if isinstance(resource, Patient):
            context.update(
                {
                    "patient_name": resource.display_name,
                    "patient_age": resource.age_years,
                    "patient_gender": resource.gender.value
                    if resource.gender
                    else None,
                    "is_active": resource.active,
                }
            )
        elif isinstance(resource, Observation):
            context.update(
                {
                    "observation_status": resource.status,
                    "observation_code": resource.code.get("text", "Unknown")
                    if resource.code
                    else "Unknown",
                    "has_value": bool(resource.value_quantity),
                    "subject": resource.subject,
                }
            )
        elif isinstance(resource, AgentMessage):
            context.update(
                {
                    "message_role": resource.role.value,
                    "confidence_score": resource.confidence_score,
                    "urgency_score": resource.urgency_score,
                    "has_memory_handles": bool(resource.memory_handles),
                    "has_evidence_links": bool(resource.evidence_links),
                }
            )
        elif isinstance(resource, MemoryBlock):
            context.update(
                {
                    "memory_type": resource.memory_type,
                    "importance_score": resource.importance_score,
                    "access_count": resource.access_count,
                    "has_linked_memories": bool(resource.linked_memories),
                }
            )
        elif isinstance(resource, Evidence):
            context.update(
                {
                    "evidence_type": resource.evidence_type.value,
                    "confidence_score": resource.confidence_score,
                    "quality_score": resource.quality_score,
                    "review_status": resource.review_status,
                }
            )

        return context

    def create_actor_ui_context(self, actor: Actor) -> dict[str, Any]:
        """Create UI context from actor.

        Args:
            actor: HACS Actor instance

        Returns:
            Dict containing actor UI context
        """
        return {
            "actor_id": actor.id,
            "actor_name": actor.name,
            "actor_role": actor.role.value
            if hasattr(actor.role, "value")
            else str(actor.role),
            "is_active": actor.is_active,
            "permissions_count": len(actor.permissions),
            "organization": getattr(actor, "organization", None),
        }

    def format_resource_for_ui(self, resource: BaseResource) -> dict[str, Any]:
        """Format resource data for UI display.

        Args:
            resource: HACS resource instance

        Returns:
            Dict containing UI-formatted resource data
        """
        base_data = {
            "id": resource.id,
            "resource_type": resource.resource_type,
            "created_at": resource.created_at.isoformat(),
            "updated_at": resource.updated_at.isoformat(),
            "age_seconds": getattr(resource, "age_seconds", 0),
        }

        # Add resource-specific UI formatting
        if isinstance(resource, Patient):
            base_data.update(
                {
                    "display_name": resource.display_name,
                    "age_years": resource.age_years,
                    "gender": resource.gender.value if resource.gender else None,
                    "birth_date": resource.birth_date.isoformat()
                    if resource.birth_date
                    else None,
                    "active": resource.active,
                    "identifier_count": len(resource.identifiers),
                    "telecom_count": len(resource.telecom),
                    "address_count": len(resource.address),
                    "care_team_count": len(resource.care_team),
                    "emergency_contact_count": len(resource.emergency_contact),
                }
            )
        elif isinstance(resource, Observation):
            base_data.update(
                {
                    "status": resource.status,
                    "code_text": resource.code.get("text", "Unknown")
                    if resource.code
                    else "Unknown",
                    "subject": resource.subject,
                    "effective_datetime": resource.effective_datetime.isoformat()
                    if resource.effective_datetime
                    else None,
                    "value_display": self._format_observation_value(resource),
                    "performer_count": len(resource.performer),
                    "component_count": len(resource.component),
                    "has_reference_range": bool(resource.reference_range),
                }
            )
        elif isinstance(resource, AgentMessage):
            base_data.update(
                {
                    "role": resource.role.value,
                    "content_preview": resource.content[:100] + "..."
                    if len(resource.content) > 100
                    else resource.content,
                    "confidence_score": resource.confidence_score,
                    "urgency_score": resource.urgency_score,
                    "memory_handles_count": len(resource.memory_handles),
                    "evidence_links_count": len(resource.evidence_links),
                    "tool_calls_count": len(resource.tool_calls),
                    "reasoning_steps_count": len(resource.reasoning_trace),
                }
            )
        elif isinstance(resource, MemoryBlock):
            base_data.update(
                {
                    "memory_type": resource.memory_type,
                    "content_preview": resource.content[:100] + "..."
                    if len(resource.content) > 100
                    else resource.content,
                    "importance_score": resource.importance_score,
                    "access_count": resource.access_count,
                    "last_accessed": resource.last_accessed.isoformat()
                    if resource.last_accessed
                    else None,
                    "linked_memories_count": len(resource.linked_memories),
                    "has_vector_id": bool(resource.vector_id),
                }
            )
        elif isinstance(resource, Evidence):
            base_data.update(
                {
                    "evidence_type": resource.evidence_type.value,
                    "citation_preview": resource.citation[:100] + "..."
                    if len(resource.citation) > 100
                    else resource.citation,
                    "content_preview": resource.content[:100] + "..."
                    if len(resource.content) > 100
                    else resource.content,
                    "confidence_score": resource.confidence_score,
                    "quality_score": resource.quality_score,
                    "review_status": resource.review_status,
                    "tags_count": len(resource.tags),
                    "linked_resources_count": len(resource.linked_resources),
                }
            )

        return base_data

    def _format_observation_value(self, observation: Observation) -> str:
        """Format observation value for display.

        Args:
            observation: Observation instance

        Returns:
            Formatted value string
        """
        if observation.value_quantity:
            value = observation.value_quantity.get("value", "")
            unit = observation.value_quantity.get("unit", "")
            return f"{value} {unit}".strip()
        elif observation.value_string:
            return observation.value_string
        elif observation.value_boolean is not None:
            return str(observation.value_boolean)
        else:
            return "No value"

    def create_event(
        self,
        event_type: AGUIEventType,
        component: AGUIComponent,
        resource: BaseResource | None = None,
        actor: Actor | None = None,
        custom_payload: dict[str, Any] | None = None,
        **kwargs,
    ) -> AGUIEvent:
        """Create AG-UI event.

        Args:
            event_type: Type of UI event
            component: Target UI component
            resource: Optional HACS resource
            actor: Optional actor context
            custom_payload: Optional custom payload data
            **kwargs: Additional event parameters

        Returns:
            AGUIEvent instance
        """
        # Build payload
        payload = custom_payload or {}

        if resource:
            payload["resource"] = self.format_resource_for_ui(resource)

        # Create UI context
        ui_context = {}
        if resource:
            ui_context = self.create_ui_context(resource, kwargs.get("action", "view"))

        # Create actor context
        actor_context = {}
        if actor:
            actor_context = self.create_actor_ui_context(actor)

        # Create event
        event = AGUIEvent(
            event_type=event_type,
            component=component,
            payload=payload,
            ui_context=ui_context,
            actor_context=actor_context,
            priority=kwargs.get("priority", 5),
            auto_dismiss=kwargs.get("auto_dismiss", False),
            dismiss_after_ms=kwargs.get("dismiss_after_ms"),
            metadata=kwargs.get("metadata", {}),
        )

        # Register event
        self.event_registry[event.event_id] = event

        return event

    def create_resource_event(
        self,
        action: str,
        resource: BaseResource,
        actor: Actor | None = None,
        **kwargs,
    ) -> AGUIEvent:
        """Create resource-related UI event.

        Args:
            action: Action performed (created, updated, deleted)
            resource: HACS resource
            actor: Optional actor context
            **kwargs: Additional parameters

        Returns:
            AGUIEvent instance
        """
        # Map action to event type
        event_type_map = {
            "created": AGUIEventType.RESOURCE_CREATED,
            "updated": AGUIEventType.RESOURCE_UPDATED,
            "deleted": AGUIEventType.RESOURCE_DELETED,
        }
        event_type = event_type_map.get(action, AGUIEventType.RESOURCE_UPDATED)

        # Map resource type to component
        component_map = {
            "Patient": AGUIComponent.PATIENT_DASHBOARD,
            "Observation": AGUIComponent.OBSERVATION_PANEL,
            "MemoryBlock": AGUIComponent.MEMORY_VIEWER,
            "Evidence": AGUIComponent.EVIDENCE_BROWSER,
            "AgentMessage": AGUIComponent.CHAT_INTERFACE,
            "Encounter": AGUIComponent.WORKFLOW_TRACKER,
        }
        component = component_map.get(resource.resource_type, AGUIComponent.SIDEBAR)

        return self.create_event(
            event_type,
            component,
            resource=resource,
            actor=actor,
            action=action,
            **kwargs,
        )

    def create_notification_event(
        self,
        message: str,
        notification_type: str = "info",
        component: AGUIComponent = AGUIComponent.TOAST,
        actor: Actor | None = None,
        **kwargs,
    ) -> AGUIEvent:
        """Create notification UI event.

        Args:
            message: Notification message
            notification_type: Type of notification (info, warning, error, success)
            component: Target UI component
            actor: Optional actor context
            **kwargs: Additional parameters

        Returns:
            AGUIEvent instance
        """
        payload = {
            "message": message,
            "notification_type": notification_type,
            "icon": self._get_notification_icon(notification_type),
            "color": self._get_notification_color(notification_type),
        }

        # Auto-dismiss for non-error notifications
        auto_dismiss = notification_type != "error"
        dismiss_after_ms = kwargs.get(
            "dismiss_after_ms", 5000 if auto_dismiss else None
        )

        return self.create_event(
            AGUIEventType.NOTIFICATION,
            component,
            custom_payload=payload,
            actor=actor,
            auto_dismiss=auto_dismiss,
            dismiss_after_ms=dismiss_after_ms,
            **kwargs,
        )

    def create_alert_event(
        self,
        alert_message: str,
        alert_type: str = "warning",
        resource: BaseResource | None = None,
        actor: Actor | None = None,
        **kwargs,
    ) -> AGUIEvent:
        """Create alert UI event.

        Args:
            alert_message: Alert message
            alert_type: Type of alert (info, warning, error, critical)
            resource: Optional related resource
            actor: Optional actor context
            **kwargs: Additional parameters

        Returns:
            AGUIEvent instance
        """
        payload = {
            "alert_message": alert_message,
            "alert_type": alert_type,
            "severity": self._get_alert_severity(alert_type),
            "requires_action": alert_type in ["error", "critical"],
        }

        # Determine component based on resource type
        component = AGUIComponent.ALERT_SYSTEM
        if resource and isinstance(resource, Observation):
            component = AGUIComponent.OBSERVATION_PANEL
        elif resource and isinstance(resource, Patient):
            component = AGUIComponent.PATIENT_DASHBOARD

        # High priority for critical alerts
        priority = 9 if alert_type == "critical" else 7 if alert_type == "error" else 5

        return self.create_event(
            AGUIEventType.OBSERVATION_ALERT
            if isinstance(resource, Observation)
            else AGUIEventType.NOTIFICATION,
            component,
            resource=resource,
            custom_payload=payload,
            actor=actor,
            priority=priority,
            **kwargs,
        )

    def _get_notification_icon(self, notification_type: str) -> str:
        """Get icon for notification type."""
        icons = {
            "info": "info-circle",
            "success": "check-circle",
            "warning": "exclamation-triangle",
            "error": "times-circle",
        }
        return icons.get(notification_type, "info-circle")

    def _get_notification_color(self, notification_type: str) -> str:
        """Get color for notification type."""
        colors = {
            "info": "blue",
            "success": "green",
            "warning": "yellow",
            "error": "red",
        }
        return colors.get(notification_type, "blue")

    def _get_alert_severity(self, alert_type: str) -> int:
        """Get numeric severity for alert type."""
        severities = {"info": 1, "warning": 3, "error": 7, "critical": 10}
        return severities.get(alert_type, 5)

    def get_event(self, event_id: str) -> AGUIEvent | None:
        """Get event by ID.

        Args:
            event_id: Event ID

        Returns:
            AGUIEvent instance or None if not found
        """
        return self.event_registry.get(event_id)

    def list_events(
        self,
        component: AGUIComponent | None = None,
        event_type: AGUIEventType | None = None,
    ) -> list[AGUIEvent]:
        """List events, optionally filtered.

        Args:
            component: Optional component filter
            event_type: Optional event type filter

        Returns:
            List of AGUIEvent instances
        """
        events = list(self.event_registry.values())

        if component:
            events = [e for e in events if e.component == component]

        if event_type:
            events = [e for e in events if e.event_type == event_type]

        # Sort by timestamp (newest first)
        events.sort(key=lambda e: e.timestamp, reverse=True)
        return events


# Convenience functions for direct usage
def format_for_ag_ui(
    event_type: str,
    component: str,
    resource: BaseResource | None = None,
    actor: Actor | None = None,
    **kwargs,
) -> AGUIEvent:
    """Format HACS data for AG-UI event.

    Args:
        event_type: Type of UI event
        component: Target UI component
        resource: Optional HACS resource
        actor: Optional actor context
        **kwargs: Additional parameters

    Returns:
        AGUIEvent instance
    """
    adapter = AGUIAdapter()
    return adapter.create_event(
        AGUIEventType(event_type.lower()),
        AGUIComponent(component.lower()),
        resource=resource,
        actor=actor,
        **kwargs,
    )


def parse_ag_ui_event(event: AGUIEvent) -> dict[str, Any]:
    """Parse AG-UI event to extract data.

    Args:
        event: AG-UI event instance

    Returns:
        Dict containing parsed event data
    """
    return {
        "event_id": event.event_id,
        "event_type": event.event_type.value,
        "component": event.component.value,
        "payload": event.payload,
        "ui_context": event.ui_context,
        "actor_context": event.actor_context,
        "timestamp": event.timestamp.isoformat(),
        "priority": event.priority,
        "auto_dismiss": event.auto_dismiss,
        "dismiss_after_ms": event.dismiss_after_ms,
        "metadata": event.metadata,
    }
