"""
Custom state factories for HACS-LangGraph integration.

This module provides custom state factories that can be used to create
specialized state structures for different types of workflows.
"""

from datetime import datetime, timezone
from typing import Any

from hacs_core import Actor


class CustomStateFactory:
    """Base factory for creating custom states."""

    def __init__(self, default_fields: dict[str, Any] | None = None):
        self.default_fields = default_fields or {}

    def create_state(
        self, workflow_type: str, actor: Actor, **kwargs
    ) -> dict[str, Any]:
        """Create a custom state with default fields."""
        # Create base actor context
        actor_context = {
            "actor_id": actor.id,
            "actor_name": actor.name,
            "actor_role": actor.role.value
            if hasattr(actor.role, "value")
            else str(actor.role),
            "permissions": actor.permissions,
            "is_active": actor.is_active,
        }

        # Create base state
        state: dict[str, Any] = {
            "workflow_id": kwargs.get("workflow_id", ""),
            "workflow_type": workflow_type,
            "current_step": kwargs.get("initial_step", "start"),
            "actor_context": actor_context,
            "patient": kwargs.get("patient"),
            "observations": kwargs.get("observations", []),
            "memories": kwargs.get("memories", []),
            "evidence": kwargs.get("evidence", []),
            "messages": kwargs.get("messages", []),
            "clinical_context": kwargs.get("clinical_context", {}),
            "decision_context": kwargs.get("decision_context", {}),
            "memory_context": kwargs.get("memory_context", {}),
            "state_history": [],
            "tool_results": [],
            "custom_data": kwargs.get("custom_data", {}),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": 1,
            "metadata": kwargs.get("metadata", {}),
        }

        # Apply default fields
        for key, value in self.default_fields.items():
            if key in state:
                if isinstance(state[key], dict) and isinstance(value, dict):
                    state[key].update(value)
                else:
                    state[key] = value
            else:
                state["custom_data"][key] = value

        return state


class ClinicalStateFactory(CustomStateFactory):
    """Factory for creating clinical workflow states."""

    def __init__(self):
        super().__init__(
            {
                "clinical_context": {
                    "assessment_type": "comprehensive",
                    "priority_level": "routine",
                    "clinical_protocols": [],
                    "risk_assessment": {},
                    "care_plan": {},
                    "follow_up_required": False,
                },
                "decision_context": {
                    "decision_points": [],
                    "clinical_reasoning": [],
                    "differential_diagnoses": [],
                    "treatment_options": [],
                    "contraindications": [],
                },
            }
        )

    def create_state(
        self, workflow_type: str, actor: Actor, **kwargs
    ) -> dict[str, Any]:
        """Create a clinical workflow state with enhanced clinical context."""
        state = super().create_state(workflow_type, actor, **kwargs)

        # Add clinical-specific enhancements
        if kwargs.get("patient"):
            patient_data = kwargs["patient"]
            if isinstance(patient_data, dict):
                state["clinical_context"]["patient_id"] = patient_data.get("id")
                state["clinical_context"]["patient_age"] = patient_data.get("age_years")
                state["clinical_context"]["patient_gender"] = patient_data.get("gender")

        if kwargs.get("observations"):
            observations = kwargs["observations"]
            state["clinical_context"]["observation_count"] = len(observations)

            # Analyze observation types
            obs_types = {}
            for obs in observations:
                if isinstance(obs, dict):
                    obs_code = obs.get("code", {})
                    obs_text = (
                        obs_code.get("text", "Unknown") if obs_code else "Unknown"
                    )
                    obs_types[obs_text] = obs_types.get(obs_text, 0) + 1

            state["clinical_context"]["observation_types"] = obs_types

        return state


class EmergencyStateFactory(CustomStateFactory):
    """Factory for creating emergency workflow states."""

    def __init__(self):
        super().__init__(
            {
                "clinical_context": {
                    "triage_level": "unknown",
                    "emergency_protocols": [],
                    "time_sensitive": True,
                    "critical_alerts": [],
                    "response_team": [],
                },
                "decision_context": {
                    "urgency_score": 0.0,
                    "time_constraints": {},
                    "emergency_procedures": [],
                    "escalation_triggers": [],
                },
            }
        )

    def create_state(
        self, workflow_type: str, actor: Actor, **kwargs
    ) -> dict[str, Any]:
        """Create an emergency workflow state with urgency tracking."""
        state = super().create_state(workflow_type, actor, **kwargs)

        # Set emergency-specific defaults
        state["clinical_context"]["priority_level"] = "urgent"
        state["clinical_context"]["assessment_type"] = "emergency"

        # Calculate initial urgency score based on observations
        urgency_score = 0.0
        observations = kwargs.get("observations", [])

        for obs in observations:
            if isinstance(obs, dict):
                # Check for high-urgency indicators
                interpretation = obs.get("interpretation", [])
                for interp in interpretation:
                    if isinstance(interp, dict):
                        coding = interp.get("coding", [])
                        for code in coding:
                            if isinstance(code, dict) and code.get("code") == "H":
                                urgency_score += 0.3

                # Check for critical values
                value_qty = obs.get("value_quantity", {})
                if isinstance(value_qty, dict):
                    value = value_qty.get("value", 0)
                    obs_code = obs.get("code", {}).get("text", "").lower()

                    if "blood pressure" in obs_code and value >= 180:
                        urgency_score += 0.4
                    elif "heart rate" in obs_code and (value >= 120 or value <= 50):
                        urgency_score += 0.3
                    elif "temperature" in obs_code and (value >= 39 or value <= 35):
                        urgency_score += 0.3

        state["decision_context"]["urgency_score"] = min(urgency_score, 1.0)

        # Set triage level based on urgency
        if urgency_score >= 0.8:
            state["clinical_context"]["triage_level"] = "critical"
        elif urgency_score >= 0.6:
            state["clinical_context"]["triage_level"] = "urgent"
        elif urgency_score >= 0.4:
            state["clinical_context"]["triage_level"] = "semi-urgent"
        else:
            state["clinical_context"]["triage_level"] = "non-urgent"

        return state


class ResearchStateFactory(CustomStateFactory):
    """Factory for creating research workflow states."""

    def __init__(self):
        super().__init__(
            {
                "research_context": {
                    "study_type": "observational",
                    "data_collection_phase": "active",
                    "research_protocols": [],
                    "ethical_approvals": [],
                    "data_quality_checks": [],
                },
                "analysis_context": {
                    "statistical_methods": [],
                    "hypothesis": "",
                    "variables": {},
                    "confounders": [],
                    "results": {},
                },
            }
        )

    def create_state(
        self, workflow_type: str, actor: Actor, **kwargs
    ) -> dict[str, Any]:
        """Create a research workflow state with data analysis context."""
        state = super().create_state(workflow_type, actor, **kwargs)

        # Add research-specific metadata
        state["metadata"]["research_study"] = True
        state["metadata"]["data_anonymized"] = kwargs.get("anonymized", True)
        state["metadata"]["consent_obtained"] = kwargs.get("consent", False)

        return state
