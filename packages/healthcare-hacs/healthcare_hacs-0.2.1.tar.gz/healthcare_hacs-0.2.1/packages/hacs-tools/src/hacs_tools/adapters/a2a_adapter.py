"""
A2A (Agent-to-Agent) Adapter

This module provides adapters for wrapping HACS resources in A2A envelopes
with Actor identity and memory handles for agent-to-agent communication.
"""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from hacs_core import Actor, BaseResource, Evidence, MemoryBlock
from hacs_models import AgentMessage
from pydantic import BaseModel, Field


class A2AMessageType(str, Enum):
    """A2A message types for different communication patterns."""

    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    BROADCAST = "broadcast"
    HANDOFF = "handoff"
    COLLABORATION = "collaboration"
    MEMORY_SHARE = "memory_share"
    EVIDENCE_SHARE = "evidence_share"


class A2AEnvelope(BaseModel):
    """A2A Envelope format for agent-to-agent communication."""

    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    message_type: A2AMessageType = Field(description="Type of A2A message")
    sender: dict[str, Any] = Field(description="Sender agent information")
    recipient: dict[str, Any] | None = Field(
        default=None, description="Recipient agent information"
    )
    conversation_id: str | None = Field(
        default=None, description="Conversation thread ID"
    )
    payload: dict[str, Any] = Field(description="Message payload")
    context: dict[str, Any] = Field(default_factory=dict, description="Message context")
    memory_handles: list[str] = Field(
        default_factory=list, description="Related memory references"
    )
    evidence_links: list[str] = Field(
        default_factory=list, description="Related evidence references"
    )
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime | None = Field(
        default=None, description="Message expiration time"
    )
    priority: int = Field(default=5, ge=1, le=10, description="Message priority (1-10)")
    metadata: dict[str, Any] = Field(default_factory=dict)


class A2AAdapter:
    """Adapter for wrapping HACS resources in A2A envelopes."""

    def __init__(self):
        """Initialize A2A adapter."""
        self.message_registry: dict[str, A2AEnvelope] = {}
        self.conversation_registry: dict[str, list[str]] = {}

    def create_agent_info(self, actor: Actor) -> dict[str, Any]:
        """Create agent information from Actor.

        Args:
            actor: HACS Actor instance

        Returns:
            Dict containing agent information for A2A
        """
        return {
            "agent_id": actor.id,
            "agent_name": actor.name,
            "agent_role": actor.role.value
            if hasattr(actor.role, "value")
            else str(actor.role),
            "capabilities": actor.permissions,
            "organization": getattr(actor, "organization", None),
            "contact_info": getattr(actor, "contact_info", {}),
            "is_active": actor.is_active,
            "session_id": getattr(actor, "session_id", None),
        }

    def extract_memory_handles(self, resource: BaseResource) -> list[str]:
        """Extract memory handles from resource.

        Args:
            resource: HACS resource instance

        Returns:
            List of memory handle references
        """
        handles = []

        # Check for memory handles in AgentMessage
        if isinstance(resource, AgentMessage):
            handles.extend(resource.memory_handles)

        # Check for memory references in metadata
        metadata = getattr(resource, "metadata", {})
        if metadata:
            memory_refs = metadata.get("memory_references", [])
            if isinstance(memory_refs, list):
                handles.extend(memory_refs)

        # Check for linked memories in MemoryBlock
        if isinstance(resource, MemoryBlock):
            handles.extend(resource.linked_memories)

        return handles

    def extract_evidence_links(self, resource: BaseResource) -> list[str]:
        """Extract evidence links from resource.

        Args:
            resource: HACS resource instance

        Returns:
            List of evidence references
        """
        links = []

        # Check for evidence links in AgentMessage
        if isinstance(resource, AgentMessage):
            evidence_links = getattr(resource, "evidence_links", [])
            if evidence_links:
                links.extend(evidence_links)

        # Check for evidence links in other resources that might have them
        evidence_links = getattr(resource, "evidence_links", [])
        if evidence_links:
            links.extend(evidence_links)

        # Check for linked resources in Evidence
        if isinstance(resource, Evidence):
            links.extend(resource.linked_resources)

        return links

    def create_envelope(
        self,
        message_type: A2AMessageType,
        sender: Actor,
        payload: BaseResource | dict[str, Any],
        recipient: Actor | None = None,
        conversation_id: str | None = None,
        **kwargs,
    ) -> A2AEnvelope:
        """Create A2A envelope for message.

        Args:
            message_type: Type of A2A message
            sender: Sender actor
            payload: Message payload (resource or dict)
            recipient: Optional recipient actor
            conversation_id: Optional conversation thread ID
            **kwargs: Additional envelope parameters

        Returns:
            A2AEnvelope instance
        """
        # Convert payload to dict if it's a BaseResource
        if isinstance(payload, BaseResource):
            payload_data = payload.model_dump()
            memory_handles = self.extract_memory_handles(payload)
            evidence_links = self.extract_evidence_links(payload)
        else:
            payload_data = payload
            memory_handles = kwargs.get("memory_handles", [])
            evidence_links = kwargs.get("evidence_links", [])

        # Create sender info
        sender_info = self.create_agent_info(sender)

        # Create recipient info if provided
        recipient_info = None
        if recipient:
            recipient_info = self.create_agent_info(recipient)

        # Generate conversation ID if not provided
        if conversation_id is None and message_type in [
            A2AMessageType.REQUEST,
            A2AMessageType.COLLABORATION,
        ]:
            conversation_id = str(uuid.uuid4())

        # Create envelope
        envelope = A2AEnvelope(
            message_type=message_type,
            sender=sender_info,
            recipient=recipient_info,
            conversation_id=conversation_id,
            payload=payload_data,
            context=kwargs.get("context", {}),
            memory_handles=memory_handles,
            evidence_links=evidence_links,
            priority=kwargs.get("priority", 5),
            expires_at=kwargs.get("expires_at"),
            metadata=kwargs.get("metadata", {}),
        )

        # Register message
        self.message_registry[envelope.message_id] = envelope

        # Register in conversation if applicable
        if conversation_id:
            if conversation_id not in self.conversation_registry:
                self.conversation_registry[conversation_id] = []
            self.conversation_registry[conversation_id].append(envelope.message_id)

        return envelope

    def create_request(
        self,
        sender: Actor,
        recipient: Actor,
        resource: BaseResource,
        request_type: str = "collaboration",
        **kwargs,
    ) -> A2AEnvelope:
        """Create A2A request message.

        Args:
            sender: Sender actor
            recipient: Recipient actor
            resource: Resource to share/request
            request_type: Type of request
            **kwargs: Additional parameters

        Returns:
            A2AEnvelope instance
        """
        context = {
            "request_type": request_type,
            "resource_type": resource.resource_type,
            "urgency": kwargs.get("urgency", "normal"),
        }

        return self.create_envelope(
            A2AMessageType.REQUEST,
            sender,
            resource,
            recipient,
            context=context,
            **kwargs,
        )

    def create_response(
        self,
        sender: Actor,
        original_message_id: str,
        response_data: BaseResource | dict[str, Any],
        success: bool = True,
        **kwargs,
    ) -> A2AEnvelope:
        """Create A2A response message.

        Args:
            sender: Sender actor
            original_message_id: ID of original request message
            response_data: Response data
            success: Whether request was successful
            **kwargs: Additional parameters

        Returns:
            A2AEnvelope instance
        """
        # Get original message to extract conversation info
        original_message = self.message_registry.get(original_message_id)
        conversation_id = None

        if original_message:
            conversation_id = original_message.conversation_id

        context = {
            "original_message_id": original_message_id,
            "success": success,
            "response_type": "completion" if success else "error",
        }

        return self.create_envelope(
            A2AMessageType.RESPONSE,
            sender,
            response_data,
            conversation_id=conversation_id,
            context=context,
            **kwargs,
        )

    def create_notification(
        self,
        sender: Actor,
        notification_data: BaseResource | dict[str, Any],
        notification_type: str = "update",
        **kwargs,
    ) -> A2AEnvelope:
        """Create A2A notification message.

        Args:
            sender: Sender actor
            notification_data: Notification data
            notification_type: Type of notification
            **kwargs: Additional parameters

        Returns:
            A2AEnvelope instance
        """
        context = {
            "notification_type": notification_type,
            "severity": kwargs.get("severity", "info"),
        }

        return self.create_envelope(
            A2AMessageType.NOTIFICATION,
            sender,
            notification_data,
            context=context,
            **kwargs,
        )

    def create_memory_share(
        self,
        sender: Actor,
        recipient: Actor,
        memory_block: MemoryBlock,
        share_type: str = "reference",
        **kwargs,
    ) -> A2AEnvelope:
        """Create A2A memory sharing message.

        Args:
            sender: Sender actor
            recipient: Recipient actor
            memory_block: Memory block to share
            share_type: Type of sharing (reference, copy, collaborative)
            **kwargs: Additional parameters

        Returns:
            A2AEnvelope instance
        """
        context = {
            "share_type": share_type,
            "memory_type": memory_block.memory_type,
            "importance_score": memory_block.importance_score,
        }

        return self.create_envelope(
            A2AMessageType.MEMORY_SHARE,
            sender,
            memory_block,
            recipient,
            context=context,
            **kwargs,
        )

    def create_evidence_share(
        self,
        sender: Actor,
        recipient: Actor,
        evidence: Evidence,
        share_type: str = "reference",
        **kwargs,
    ) -> A2AEnvelope:
        """Create A2A evidence sharing message.

        Args:
            sender: Sender actor
            recipient: Recipient actor
            evidence: Evidence to share
            share_type: Type of sharing (reference, copy, collaborative)
            **kwargs: Additional parameters

        Returns:
            A2AEnvelope instance
        """
        context = {
            "share_type": share_type,
            "evidence_type": evidence.evidence_type.value,
            "confidence_score": evidence.confidence_score,
            "quality_score": evidence.quality_score,
        }

        return self.create_envelope(
            A2AMessageType.EVIDENCE_SHARE,
            sender,
            evidence,
            recipient,
            context=context,
            **kwargs,
        )

    def get_message(self, message_id: str) -> A2AEnvelope | None:
        """Get message by ID.

        Args:
            message_id: Message ID

        Returns:
            A2AEnvelope instance or None if not found
        """
        return self.message_registry.get(message_id)

    def get_conversation(self, conversation_id: str) -> list[A2AEnvelope]:
        """Get all messages in a conversation.

        Args:
            conversation_id: Conversation ID

        Returns:
            List of A2AEnvelope instances in conversation order
        """
        message_ids = self.conversation_registry.get(conversation_id, [])
        messages = []

        for message_id in message_ids:
            message = self.message_registry.get(message_id)
            if message:
                messages.append(message)

        # Sort by timestamp
        messages.sort(key=lambda m: m.timestamp)
        return messages


# Convenience functions for direct usage
def create_a2a_envelope(
    message_type: str,
    sender: Actor,
    payload: BaseResource | dict[str, Any],
    recipient: Actor | None = None,
    **kwargs,
) -> A2AEnvelope:
    """Create A2A envelope for agent communication.

    Args:
        message_type: Type of A2A message
        sender: Sender actor
        payload: Message payload
        recipient: Optional recipient actor
        **kwargs: Additional parameters

    Returns:
        A2AEnvelope instance
    """
    adapter = A2AAdapter()
    return adapter.create_envelope(
        A2AMessageType(message_type.lower()), sender, payload, recipient, **kwargs
    )


def extract_from_a2a_envelope(envelope: A2AEnvelope) -> dict[str, Any]:
    """Extract data from A2A envelope.

    Args:
        envelope: A2A envelope instance

    Returns:
        Dict containing extracted envelope data
    """
    return {
        "message_id": envelope.message_id,
        "message_type": envelope.message_type.value,
        "sender": envelope.sender,
        "recipient": envelope.recipient,
        "conversation_id": envelope.conversation_id,
        "payload": envelope.payload,
        "context": envelope.context,
        "memory_handles": envelope.memory_handles,
        "evidence_links": envelope.evidence_links,
        "timestamp": envelope.timestamp.isoformat(),
        "priority": envelope.priority,
        "metadata": envelope.metadata,
    }
