"""
State definitions for HACS + LangGraph demo.

This module defines the state structures used in the demo workflow,
leveraging HACS types and the enhanced LangGraph adapter.
"""

from typing import Annotated, List, Dict, Any, Optional

# Optional LangGraph imports with fallbacks
try:
    from langgraph.graph.message import add_messages
    from langchain_core.messages import BaseMessage

    HAS_LANGGRAPH = True
except ImportError:
    # Fallback when LangGraph is not installed
    HAS_LANGGRAPH = False
    # Create mock types for type hints
    BaseMessage = Any

    def add_messages(x):
        return x


from hacs_core.actor import Actor
from hacs_models.patient import Patient
from hacs_models.observation import Observation

# Optional LangGraph adapter import
from hacs_tools.adapters.langgraph_adapter import LangGraphAdapter, HACSState


class ClinicalWorkflowState(HACSState):
    """
    State for clinical workflow demonstration.

    This extends the base HACSState from the LangGraph adapter with
    workflow-specific fields for managing a clinical assessment process.
    """

    # Core LangGraph state (only if LangGraph is available)
    if HAS_LANGGRAPH:
        messages: Annotated[List[BaseMessage], add_messages]
    else:
        messages: List[Any]

    # Assessment-specific fields (extending HACSState)
    risk_assessment: Optional[Dict[str, Any]]
    recommendations: List[str]
    urgency_level: str


def create_initial_state(
    patient: Patient, observations: List[Observation], actor: Actor
) -> ClinicalWorkflowState:
    """
    Create initial state for clinical workflow.

    Args:
        patient: Patient resource
        observations: List of clinical observations
        actor: Actor performing the workflow

    Returns:
        Initialized ClinicalWorkflowState
    """
    if not HAS_LANGGRAPH:
        raise ImportError(
            "LangGraph is required for this example. Install with: uv add langgraph langchain-core"
        )

    # Use enhanced adapter to create base HACS state
    adapter = LangGraphAdapter()

    # Create base state using adapter
    base_state = adapter.create_clinical_workflow_state(
        patient=patient,
        observations=observations,
        actor=actor,
        workflow_type="clinical_assessment",
    )

    # Extend with workflow-specific fields
    clinical_state: ClinicalWorkflowState = {
        **base_state,
        "messages": [],
        "risk_assessment": None,
        "recommendations": [],
        "urgency_level": "normal",
    }

    return clinical_state


def update_risk_assessment(
    state: ClinicalWorkflowState, risk_data: Dict[str, Any]
) -> ClinicalWorkflowState:
    """
    Update the risk assessment in the state.

    Args:
        state: Current workflow state
        risk_data: Risk assessment data

    Returns:
        Updated state
    """
    state["risk_assessment"] = risk_data

    # Update urgency based on risk level
    risk_level = risk_data.get("risk_category", "low")
    if risk_level == "high":
        state["urgency_level"] = "high"
    elif risk_level == "moderate":
        state["urgency_level"] = "moderate"
    else:
        state["urgency_level"] = "normal"

    # Update version and timestamp
    state["version"] = state.get("version", 1) + 1
    state["timestamp"] = state["timestamp"]  # Would be updated with current time

    return state


def add_recommendation(
    state: ClinicalWorkflowState, recommendation: str
) -> ClinicalWorkflowState:
    """
    Add a clinical recommendation to the state.

    Args:
        state: Current workflow state
        recommendation: Clinical recommendation text

    Returns:
        Updated state
    """
    if recommendation not in state["recommendations"]:
        state["recommendations"].append(recommendation)
        state["version"] = state.get("version", 1) + 1

    return state


def get_current_patient(state: ClinicalWorkflowState) -> Optional[Dict[str, Any]]:
    """
    Get the current patient from state.

    Args:
        state: Current workflow state

    Returns:
        Patient data or None
    """
    return state.get("patient")


def get_latest_observation(state: ClinicalWorkflowState) -> Optional[Dict[str, Any]]:
    """
    Get the most recent observation from state.

    Args:
        state: Current workflow state

    Returns:
        Latest observation data or None
    """
    observations = state.get("observations", [])
    return observations[-1] if observations else None


def is_high_risk_case(state: ClinicalWorkflowState) -> bool:
    """
    Determine if this is a high-risk case based on state.

    Args:
        state: Current workflow state

    Returns:
        True if high-risk case
    """
    # Check risk assessment
    risk_assessment = state.get("risk_assessment")
    if risk_assessment and risk_assessment.get("risk_category") == "high":
        return True

    # Check urgency level
    if state.get("urgency_level") == "high":
        return True

    # Check clinical context for risk factors
    clinical_context = state.get("clinical_context", {})
    risk_factors = clinical_context.get("risk_factors", [])
    return len(risk_factors) > 0


def get_workflow_summary(state: ClinicalWorkflowState) -> Dict[str, Any]:
    """
    Generate a summary of the current workflow state.

    Args:
        state: Current workflow state

    Returns:
        Summary dictionary
    """
    patient = get_current_patient(state)
    latest_obs = get_latest_observation(state)

    return {
        "workflow_id": state.get("workflow_id"),
        "patient_name": patient.get("display_name") if patient else "Unknown",
        "current_step": state.get("current_step"),
        "urgency_level": state.get("urgency_level"),
        "observation_count": len(state.get("observations", [])),
        "recommendations_count": len(state.get("recommendations", [])),
        "has_risk_assessment": state.get("risk_assessment") is not None,
        "is_high_risk": is_high_risk_case(state),
        "latest_observation": latest_obs.get("code", {}).get("text")
        if latest_obs
        else None,
        "tools_used": len(state.get("tool_history", [])),
        "version": state.get("version", 1),
    }
