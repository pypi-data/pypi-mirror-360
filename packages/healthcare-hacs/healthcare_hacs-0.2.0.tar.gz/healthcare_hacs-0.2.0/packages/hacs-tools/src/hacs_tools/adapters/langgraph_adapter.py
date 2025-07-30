"""
Enhanced LangGraph Adapter

This module provides enhanced adapters for integrating HACS with LangGraph StateGraph
with improved customizability, tool integration, and memory management.
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union, TypedDict, Callable, Type
from enum import Enum

from hacs_core import BaseResource, Actor, MemoryBlock, Evidence
from hacs_models import Patient, AgentMessage, Observation


class LangGraphStateType(str, Enum):
    """LangGraph state types for different workflows."""

    PATIENT_WORKFLOW = "patient_workflow"
    CLINICAL_ASSESSMENT = "clinical_assessment"
    TREATMENT_PLANNING = "treatment_planning"
    EVIDENCE_REVIEW = "evidence_review"
    MEMORY_CONSOLIDATION = "memory_consolidation"
    AGENT_COLLABORATION = "agent_collaboration"
    DECISION_SUPPORT = "decision_support"
    CUSTOM = "custom"


class HACSState(TypedDict, total=False):
    """Base HACS-compatible LangGraph state structure."""

    # Core state
    workflow_id: str
    workflow_type: str
    current_step: str
    actor_context: Dict[str, Any]

    # HACS resources
    patient: Optional[Dict[str, Any]]
    observations: List[Dict[str, Any]]
    memories: List[Dict[str, Any]]
    evidence: List[Dict[str, Any]]
    messages: List[Dict[str, Any]]

    # Workflow context
    clinical_context: Dict[str, Any]
    decision_context: Dict[str, Any]
    memory_context: Dict[str, Any]

    # Tool integration
    available_tools: List[str]
    tool_results: Dict[str, Any]
    tool_history: List[Dict[str, Any]]

    # State metadata
    timestamp: str
    version: int
    metadata: Dict[str, Any]


class CustomStateBuilder:
    """Builder for creating custom HACS state types."""

    def __init__(self, base_state: Any = HACSState):
        self.base_state = base_state
        self.custom_fields = {}
        self.validators = []

    def add_field(
        self, name: str, field_type: Type, default: Any = None
    ) -> "CustomStateBuilder":
        """Add a custom field to the state."""
        self.custom_fields[name] = (field_type, default)
        return self

    def add_validator(
        self, validator: Callable[[Dict[str, Any]], bool]
    ) -> "CustomStateBuilder":
        """Add a state validator function."""
        self.validators.append(validator)
        return self

    def build(self) -> Dict[str, Any]:
        """Build the custom state type."""
        # Create new state dict with custom fields
        base_annotations = getattr(self.base_state, "__annotations__", {})
        custom_annotations = {
            name: field_type for name, (field_type, _) in self.custom_fields.items()
        }
        # Return a dict representation rather than TypedDict
        return {**base_annotations, **custom_annotations}


class HACSToolRegistry:
    """Registry for HACS-compatible tools that can be used in LangGraph workflows."""

    def __init__(self):
        self.tools: Dict[str, Callable] = {}
        self.tool_metadata: Dict[str, Dict[str, Any]] = {}

    def register_tool(
        self,
        name: str,
        func: Callable,
        description: str = "",
        input_schema: Optional[Dict[str, Any]] = None,
        output_schema: Optional[Dict[str, Any]] = None,
        requires_actor: bool = True,
    ) -> None:
        """Register a tool for use in HACS workflows."""
        self.tools[name] = func
        self.tool_metadata[name] = {
            "description": description,
            "input_schema": input_schema,
            "output_schema": output_schema,
            "requires_actor": requires_actor,
            "registered_at": datetime.now(timezone.utc).isoformat(),
        }

    def get_tool(self, name: str) -> Optional[Callable]:
        """Get a registered tool by name."""
        return self.tools.get(name)

    def list_tools(self) -> List[str]:
        """List all registered tool names."""
        return list(self.tools.keys())

    def get_tool_metadata(self, name: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a tool."""
        return self.tool_metadata.get(name)


class MemoryManager:
    """Enhanced memory management for HACS workflows."""

    def __init__(self):
        self.memory_store: Dict[str, List[MemoryBlock]] = {}
        self.consolidation_rules: List[Callable] = []

    def add_memory(self, workflow_id: str, memory: MemoryBlock) -> None:
        """Add a memory to a workflow."""
        if workflow_id not in self.memory_store:
            self.memory_store[workflow_id] = []
        self.memory_store[workflow_id].append(memory)

    def get_memories(
        self, workflow_id: str, memory_type: Optional[str] = None
    ) -> List[MemoryBlock]:
        """Get memories for a workflow, optionally filtered by type."""
        memories = self.memory_store.get(workflow_id, [])
        if memory_type:
            memories = [m for m in memories if m.memory_type == memory_type]
        return memories

    def consolidate_memories(self, workflow_id: str) -> List[MemoryBlock]:
        """Consolidate memories using registered rules."""
        memories = self.get_memories(workflow_id)
        for rule in self.consolidation_rules:
            memories = rule(memories)
        return memories

    def add_consolidation_rule(
        self, rule: Callable[[List[MemoryBlock]], List[MemoryBlock]]
    ) -> None:
        """Add a memory consolidation rule."""
        self.consolidation_rules.append(rule)


class StateTransition:
    """Represents a state transition with conditions and actions."""

    def __init__(
        self,
        from_step: str,
        to_step: str,
        condition: Optional[Callable[[Dict[str, Any]], bool]] = None,
        action: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None,
    ):
        self.from_step = from_step
        self.to_step = to_step
        self.condition = condition or (lambda state: True)
        self.action = action or (lambda state: state)

    def can_transition(self, state: Dict[str, Any]) -> bool:
        """Check if transition is possible."""
        return state.get("current_step") == self.from_step and self.condition(state)

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the transition."""
        updated_state = self.action(state)
        updated_state["current_step"] = self.to_step
        return updated_state


class LangGraphAdapter:
    """Enhanced adapter for integrating HACS with LangGraph workflows."""

    def __init__(self):
        """Initialize enhanced LangGraph adapter."""
        self.state_registry: Dict[str, Dict[str, Any]] = {}
        self.workflow_registry: Dict[str, Dict[str, Any]] = {}
        self.tool_registry = HACSToolRegistry()
        self.memory_manager = MemoryManager()
        self.state_transitions: List[StateTransition] = []
        self.custom_state_builders: Dict[str, CustomStateBuilder] = {}

    def create_custom_state_builder(self, name: str) -> CustomStateBuilder:
        """Create a custom state builder."""
        builder = CustomStateBuilder()
        self.custom_state_builders[name] = builder
        return builder

    def register_tool(self, name: str, func: Callable, **kwargs) -> None:
        """Register a tool with the adapter."""
        self.tool_registry.register_tool(name, func, **kwargs)

    def add_state_transition(self, transition: StateTransition) -> None:
        """Add a state transition rule."""
        self.state_transitions.append(transition)

    def create_hacs_state(
        self,
        workflow_type: Union[LangGraphStateType, str],
        actor: Actor,
        workflow_id: Optional[str] = None,
        custom_state_type: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Create HACS-compatible LangGraph state with enhanced customization.

        Args:
            workflow_type: Type of LangGraph workflow
            actor: Actor initiating the workflow
            workflow_id: Optional workflow ID
            custom_state_type: Name of custom state type to use
            **kwargs: Additional state parameters

        Returns:
            HACSState instance
        """
        if workflow_id is None:
            workflow_id = str(uuid.uuid4())

        # Handle string workflow types
        if isinstance(workflow_type, str):
            try:
                workflow_type = LangGraphStateType(workflow_type.lower())
            except ValueError:
                workflow_type = LangGraphStateType.CUSTOM

        # Create actor context
        actor_context = {
            "actor_id": actor.id,
            "actor_name": actor.name,
            "actor_role": actor.role.value
            if hasattr(actor.role, "value")
            else str(actor.role),
            "permissions": actor.permissions,
            "is_active": actor.is_active,
        }

        # Initialize base state
        state: Dict[str, Any] = {
            "workflow_id": workflow_id,
            "workflow_type": workflow_type.value,
            "current_step": kwargs.get("initial_step", "start"),
            "actor_context": actor_context,
            "patient": None,
            "observations": [],
            "memories": [],
            "evidence": [],
            "messages": [],
            "clinical_context": kwargs.get("clinical_context", {}),
            "decision_context": kwargs.get("decision_context", {}),
            "memory_context": kwargs.get("memory_context", {}),
            "available_tools": self.tool_registry.list_tools(),
            "tool_results": {},
            "tool_history": [],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": 1,
            "metadata": kwargs.get("metadata", {}),
        }

        # Apply custom state fields if specified
        if custom_state_type and custom_state_type in self.custom_state_builders:
            builder = self.custom_state_builders[custom_state_type]
            for name, (_, default) in builder.custom_fields.items():
                state[name] = kwargs.get(name, default)

        # Register state
        self.state_registry[workflow_id] = state

        return state

    def execute_tool(
        self, state: Dict[str, Any], tool_name: str, **tool_kwargs
    ) -> Dict[str, Any]:
        """Execute a registered tool and update state."""
        tool = self.tool_registry.get_tool(tool_name)
        if not tool:
            raise ValueError(f"Tool '{tool_name}' not found in registry")

        # Get tool metadata
        metadata = self.tool_registry.get_tool_metadata(tool_name)

        # Add actor if required
        if metadata and metadata.get("requires_actor", True):
            actor_id = state["actor_context"]["actor_id"]
            # In a real implementation, you'd retrieve the Actor object
            tool_kwargs["actor_id"] = actor_id

        # Execute tool
        try:
            result = tool(**tool_kwargs)

            # Record tool execution
            tool_execution = {
                "tool_name": tool_name,
                "parameters": tool_kwargs,
                "result": result,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "success": True,
            }

            # Update state
            state["tool_results"][tool_name] = result
            state["tool_history"].append(tool_execution)

        except Exception as e:
            # Record failed execution
            tool_execution = {
                "tool_name": tool_name,
                "parameters": tool_kwargs,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "success": False,
            }
            state["tool_history"].append(tool_execution)
            raise

        # Update state metadata
        state["timestamp"] = datetime.now(timezone.utc).isoformat()
        state["version"] = state.get("version", 1) + 1

        return state

    def transition_state(
        self, state: Dict[str, Any], target_step: Optional[str] = None
    ) -> Dict[str, Any]:
        """Transition state based on registered rules or explicit target."""
        if target_step:
            # Explicit transition
            state["current_step"] = target_step
        else:
            # Check transition rules
            for transition in self.state_transitions:
                if transition.can_transition(state):
                    state = transition.execute(state)
                    break

        state["timestamp"] = datetime.now(timezone.utc).isoformat()
        state["version"] = state.get("version", 1) + 1

        return state

    def add_memory_to_workflow(self, workflow_id: str, memory: MemoryBlock) -> None:
        """Add memory to a workflow."""
        self.memory_manager.add_memory(workflow_id, memory)

        # Update state if it exists
        if workflow_id in self.state_registry:
            state = self.state_registry[workflow_id]
            state["memories"].append(memory.model_dump())
            state["timestamp"] = datetime.now(timezone.utc).isoformat()
            state["version"] = state.get("version", 1) + 1

    def get_workflow_memories(
        self, workflow_id: str, memory_type: Optional[str] = None
    ) -> List[MemoryBlock]:
        """Get memories for a workflow."""
        return self.memory_manager.get_memories(workflow_id, memory_type)

    # Keep existing methods for backward compatibility
    def add_resource_to_state(
        self, state: Dict[str, Any], resource: BaseResource
    ) -> Dict[str, Any]:
        """Add HACS resource to LangGraph state."""
        resource_data = resource.model_dump()

        if isinstance(resource, Patient):
            state["patient"] = resource_data
        elif isinstance(resource, Observation):
            state["observations"].append(resource_data)
        elif isinstance(resource, MemoryBlock):
            state["memories"].append(resource_data)
            self.memory_manager.add_memory(state["workflow_id"], resource)
        elif isinstance(resource, Evidence):
            state["evidence"].append(resource_data)
        elif isinstance(resource, AgentMessage):
            state["messages"].append(resource_data)

        state["timestamp"] = datetime.now(timezone.utc).isoformat()
        state["version"] = state.get("version", 1) + 1

        return state

    def create_clinical_workflow_state(
        self,
        patient: Patient,
        observations: List[Observation],
        actor: Actor,
        workflow_type: LangGraphStateType = LangGraphStateType.CLINICAL_ASSESSMENT,
        **kwargs,
    ) -> Dict[str, Any]:
        """Create clinical workflow state with patient and observations."""
        state = self.create_hacs_state(workflow_type, actor, **kwargs)

        # Add patient and observations
        state["patient"] = patient.model_dump()
        state["observations"] = [obs.model_dump() for obs in observations]

        # Create enhanced clinical context
        clinical_context = {
            "patient_id": patient.id,
            "patient_name": patient.display_name,
            "patient_age": patient.age_years,
            "observation_count": len(observations),
            "latest_observation": observations[-1].model_dump()
            if observations
            else None,
            "workflow_initiated_by": actor.name,
            "workflow_timestamp": datetime.now(timezone.utc).isoformat(),
            "risk_factors": [],
            "alerts": [],
            "recommendations": [],
        }

        # Analyze observations for risk factors
        for obs in observations:
            if obs.interpretation:
                for interp in obs.interpretation:
                    if interp.get("coding", [{}])[0].get("code") == "H":
                        clinical_context["risk_factors"].append(
                            {
                                "type": "high_value",
                                "observation_id": obs.id,
                                "description": f"High {obs.code.get('text', 'value')}",
                            }
                        )

        state["clinical_context"] = clinical_context
        return state


# Convenience functions for direct usage
def create_custom_workflow_state(
    workflow_type: str,
    actor: Actor,
    custom_fields: Optional[Dict[str, Any]] = None,
    **kwargs,
) -> Dict[str, Any]:
    """Create a custom workflow state with additional fields."""
    adapter = LangGraphAdapter()

    if custom_fields:
        builder = adapter.create_custom_state_builder("custom")
        for name, value in custom_fields.items():
            builder.add_field(name, type(value), value)
        kwargs.update(custom_fields)

    return adapter.create_hacs_state(workflow_type, actor, **kwargs)


def create_state_bridge(
    source_state: Dict[str, Any],
    target_workflow_type: str,
    actor: Actor,
    preserve_data: bool = True,
    **kwargs,
) -> Dict[str, Any]:
    """
    Create a state bridge between different workflow types.

    This function transforms a source state from one workflow type to another,
    preserving relevant data and adapting the structure as needed.

    Args:
        source_state: Source workflow state
        target_workflow_type: Target workflow type to bridge to
        actor: Actor performing the state bridge
        preserve_data: Whether to preserve data from source state
        **kwargs: Additional parameters for the target state

    Returns:
        New state dict for the target workflow type
    """
    adapter = LangGraphAdapter()

    # Create new state for target workflow
    target_state = adapter.create_hacs_state(target_workflow_type, actor, **kwargs)

    if preserve_data:
        # Preserve common data fields from source state
        preserve_fields = [
            "patient",
            "observations",
            "memories",
            "evidence",
            "messages",
            "clinical_context",
            "decision_context",
            "memory_context",
        ]

        for field in preserve_fields:
            if field in source_state:
                target_state[field] = source_state[field]

        # Preserve metadata with bridge information
        source_metadata = source_state.get("metadata", {})
        target_state["metadata"].update(source_metadata)
        target_state["metadata"]["bridged_from"] = source_state.get(
            "workflow_type", "unknown"
        )
        target_state["metadata"]["bridge_timestamp"] = datetime.now(
            timezone.utc
        ).isoformat()

    return target_state
