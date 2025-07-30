"""
LangGraph workflow definition for HACS clinical example.

This module demonstrates the LangGraph Functional API integrated with HACS,
showing a clean, simple clinical assessment workflow.
"""

import uuid
from datetime import date

# Optional LangGraph imports with fallbacks
try:
    from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

    HAS_LANGCHAIN = True
except ImportError:
    HAS_LANGCHAIN = False

    # Create mock types
    class HumanMessage:
        def __init__(self, content):
            self.content = content

    class AIMessage:
        def __init__(self, content):
            self.content = content

    class SystemMessage:
        def __init__(self, content):
            self.content = content


from hacs_core.actor import Actor, ActorRole
from hacs_core.evidence import Evidence, EvidenceType
from hacs_models.patient import Patient, AdministrativeGender
from hacs_models.observation import Observation, ObservationStatus

# Handle both direct execution and module import with optional LangGraph
try:
    from .state import (
        ClinicalWorkflowState,
        create_initial_state,
        update_risk_assessment,
        add_recommendation,
        get_workflow_summary,
        HAS_LANGGRAPH,
    )
except ImportError:
    try:
        from state import (
            ClinicalWorkflowState,
            create_initial_state,
            update_risk_assessment,
            add_recommendation,
            get_workflow_summary,
            HAS_LANGGRAPH,
        )
    except ImportError:
        # Fallback when state module can't be imported
        HAS_LANGGRAPH = False
        ClinicalWorkflowState = dict

        def create_initial_state(*args, **kwargs):
            raise ImportError("LangGraph dependencies not available")

        def update_risk_assessment(state, data):
            return state

        def add_recommendation(state, rec):
            return state

        def get_workflow_summary(state):
            return {}


# --- Mock Clinical Tools ---


def calculate_cardiovascular_risk(systolic_bp: int, age: int, **kwargs) -> dict:
    """
    Mock cardiovascular risk calculator.

    Args:
        systolic_bp: Systolic blood pressure
        age: Patient age

    Returns:
        Risk assessment data
    """
    # Simple risk calculation logic
    base_risk = 0.05  # 5% base risk

    # Age factor
    if age > 65:
        base_risk += 0.10
    elif age > 50:
        base_risk += 0.05

    # BP factor
    if systolic_bp > 160:
        base_risk += 0.15
    elif systolic_bp > 140:
        base_risk += 0.08

    risk_percentage = min(base_risk * 100, 95)  # Cap at 95%

    if risk_percentage > 20:
        category = "high"
    elif risk_percentage > 10:
        category = "moderate"
    else:
        category = "low"

    return {
        "ten_year_risk_percent": risk_percentage,
        "risk_category": category,
        "recommendation": f"Risk is {category}. {'Immediate intervention recommended.' if category == 'high' else 'Monitor and lifestyle changes recommended.'}",
    }


def search_clinical_evidence(condition: str, **kwargs) -> list:
    """
    Mock clinical evidence search.

    Args:
        condition: Medical condition to search for

    Returns:
        List of evidence items
    """
    # Mock evidence database
    evidence_db = {
        "hypertension": [
            Evidence(
                id="htn-guideline-001",
                citation="2024 AHA/ACC Hypertension Guidelines",
                content="For stage 2 hypertension (≥140/90), initiate antihypertensive medication alongside lifestyle modifications.",
                evidence_type=EvidenceType.GUIDELINE,
                confidence_score=0.95,
                tags=["hypertension", "guidelines", "medication"],
            )
        ],
        "diabetes": [
            Evidence(
                id="dm-prevention-001",
                citation="Diabetes Prevention Program (2002)",
                content="Lifestyle intervention reduces diabetes incidence by 58% in high-risk individuals.",
                evidence_type=EvidenceType.RESEARCH_PAPER,
                confidence_score=0.90,
                tags=["diabetes", "prevention", "lifestyle"],
            )
        ],
    }

    return evidence_db.get(condition.lower(), [])


# --- Workflow Nodes (Functional API) ---


def initialize_workflow(state: ClinicalWorkflowState) -> ClinicalWorkflowState:
    """
    Initialize the clinical workflow.

    This node sets up the initial state and adds a system message.
    """
    # Add system message
    system_msg = SystemMessage(
        content="You are a clinical assessment AI. Analyze patient data and provide evidence-based recommendations."
    )

    # Add initial human message
    patient_name = (
        state["patient"]["display_name"] if state.get("patient") else "Unknown Patient"
    )
    human_msg = HumanMessage(
        content=f"Please assess {patient_name} based on the available clinical data."
    )

    return {**state, "messages": [system_msg, human_msg]}


def assess_risk(state: ClinicalWorkflowState) -> ClinicalWorkflowState:
    """
    Assess cardiovascular risk based on observations.

    This node analyzes the patient's observations and calculates risk.
    """
    patient = state.get("patient", {})
    observations = state.get("observations", [])

    # Find blood pressure observation
    bp_obs = None
    for obs in observations:
        if "blood pressure" in obs.get("code", {}).get("text", "").lower():
            bp_obs = obs
            break

    if bp_obs and patient:
        # Extract values
        systolic_bp = bp_obs.get("value_quantity", {}).get("value", 120)
        age = patient.get("age_years", 50)

        # Calculate risk using mock tool
        risk_data = calculate_cardiovascular_risk(systolic_bp, age)

        # Update state
        state = update_risk_assessment(state, risk_data)

        # Add AI message about risk
        ai_msg = AIMessage(
            content=f"Risk assessment completed. {risk_data['risk_category'].title()} risk detected ({risk_data['ten_year_risk_percent']:.1f}% 10-year risk)."
        )

        return {**state, "messages": state["messages"] + [ai_msg]}

    # No BP data found
    ai_msg = AIMessage(
        content="Unable to assess cardiovascular risk - no blood pressure data available."
    )
    return {**state, "messages": state["messages"] + [ai_msg]}


def search_evidence(state: ClinicalWorkflowState) -> ClinicalWorkflowState:
    """
    Search for relevant clinical evidence.

    This node searches for evidence based on identified conditions.
    """
    # Determine search terms based on risk assessment
    search_terms = ["hypertension"]  # Default search

    risk_assessment = state.get("risk_assessment")
    if risk_assessment and risk_assessment.get("risk_category") == "high":
        search_terms.append("cardiovascular")

    # Search for evidence
    all_evidence = []
    for term in search_terms:
        evidence = search_clinical_evidence(term)
        all_evidence.extend(evidence)

    # Add evidence to state
    evidence_data = [e.model_dump() for e in all_evidence]

    # Create summary message
    if evidence_data:
        ai_msg = AIMessage(
            content=f"Found {len(evidence_data)} relevant evidence sources. Proceeding to generate recommendations."
        )
    else:
        ai_msg = AIMessage(
            content="No specific evidence found. Using general clinical guidelines."
        )

    return {
        **state,
        "evidence": evidence_data,
        "messages": state["messages"] + [ai_msg],
    }


def generate_recommendations(state: ClinicalWorkflowState) -> ClinicalWorkflowState:
    """
    Generate clinical recommendations based on assessment.

    This node synthesizes all information to create actionable recommendations.
    """
    recommendations = []

    # Base recommendations on risk level
    risk_assessment = state.get("risk_assessment")
    if risk_assessment:
        risk_category = risk_assessment.get("risk_category", "low")

        if risk_category == "high":
            recommendations.extend(
                [
                    "Initiate antihypertensive medication immediately",
                    "Schedule cardiology consultation within 48 hours",
                    "Implement DASH diet and lifestyle modifications",
                    "Follow-up in 1 week for medication adjustment",
                ]
            )
        elif risk_category == "moderate":
            recommendations.extend(
                [
                    "Consider antihypertensive medication",
                    "Lifestyle modifications (diet, exercise, weight management)",
                    "Follow-up in 2-4 weeks",
                    "Monitor blood pressure at home",
                ]
            )
        else:
            recommendations.extend(
                [
                    "Continue lifestyle modifications",
                    "Regular blood pressure monitoring",
                    "Annual cardiovascular risk assessment",
                ]
            )

    # Add evidence-based recommendations
    evidence = state.get("evidence", [])
    if evidence:
        recommendations.append(
            "Recommendations are based on current clinical guidelines and evidence"
        )

    # Update state with recommendations
    updated_state = state.copy()
    for rec in recommendations:
        updated_state = add_recommendation(updated_state, rec)

    # Create final summary message
    summary = get_workflow_summary(updated_state)

    final_msg = AIMessage(
        content=f"""Clinical Assessment Complete:

Patient: {summary["patient_name"]}
Risk Level: {updated_state.get("urgency_level", "normal").title()}
Recommendations ({len(recommendations)}):
{chr(10).join(f"• {rec}" for rec in recommendations)}

Assessment based on {summary["observation_count"]} observation(s) and {len(evidence)} evidence source(s)."""
    )

    return {**updated_state, "messages": updated_state["messages"] + [final_msg]}


# Removed route_next_step function - using direct edges for sequential workflow


# --- Example Data Creation ---


def create_example_data():
    """Create example patient and observation data."""

    # Create clinician actor
    clinician = Actor(
        id=str(uuid.uuid4()),
        name="Dr. Sarah Chen",
        role=ActorRole.PHYSICIAN,
        permissions=["read:patient", "write:observation", "execute:workflow"],
        is_active=True,
    )

    # Create patient
    patient = Patient(
        id="patient-demo-001",
        given=["Maria"],
        family="Rodriguez",
        gender=AdministrativeGender.FEMALE,
        birth_date=date(1965, 3, 15),
    )

    # Create high-risk observation
    observation = Observation(
        id="obs-bp-demo-001",
        subject=patient.id,
        status=ObservationStatus.FINAL,
        code={
            "coding": [
                {
                    "system": "http://loinc.org",
                    "code": "8480-6",
                    "display": "Systolic blood pressure",
                }
            ],
            "text": "Systolic blood pressure",
        },
        value_quantity={"value": 165, "unit": "mmHg"},
        interpretation=[{"coding": [{"code": "H", "display": "High"}]}],
    )

    return clinician, patient, [observation]


def create_workflow_graph():
    """
    Create the LangGraph workflow using Functional API.

    Returns:
        Compiled LangGraph application
    """
    if not HAS_LANGGRAPH:
        raise ImportError(
            "LangGraph is required for this example. Install with: uv add langgraph langchain-core"
        )

    from langgraph.graph import StateGraph, END

    # Create the graph
    workflow = StateGraph(ClinicalWorkflowState)

    # Add nodes
    workflow.add_node("initialize", initialize_workflow)
    workflow.add_node("assess_risk", assess_risk)
    workflow.add_node("search_evidence", search_evidence)
    workflow.add_node("generate_recommendations", generate_recommendations)

    # Set entry point
    workflow.set_entry_point("initialize")

    # Add sequential edges (no conditional routing needed)
    workflow.add_edge("initialize", "assess_risk")
    workflow.add_edge("assess_risk", "search_evidence")
    workflow.add_edge("search_evidence", "generate_recommendations")
    workflow.add_edge("generate_recommendations", END)

    return workflow.compile()


# --- Main Example Function ---


def run_example():
    """Run the complete clinical workflow example."""
    if not HAS_LANGGRAPH:
        raise ImportError(
            "LangGraph is required for this example. Install with: uv add langgraph langchain-core"
        )

    print("🏥 HACS + LangGraph Clinical Workflow Example")
    print("=" * 50)

    # Create example data
    clinician, patient, observations = create_example_data()
    print(f"Created example data for patient: {patient.display_name}")

    # Create initial state
    initial_state = create_initial_state(patient, observations, clinician)
    print(f"Initialized workflow: {initial_state['workflow_id']}")

    # Create and run workflow
    app = create_workflow_graph()
    print("Running clinical assessment workflow...\n")

    # Execute workflow
    final_state = app.invoke(initial_state)

    # Display results
    print("\n" + "=" * 50)
    print("🎯 Workflow Complete!")

    summary = get_workflow_summary(final_state)
    print(f"Patient: {summary['patient_name']}")
    print(f"Risk Level: {summary['urgency_level'].title()}")
    print(f"Recommendations: {summary['recommendations_count']}")
    print(f"High Risk Case: {'Yes' if summary['is_high_risk'] else 'No'}")

    # Show final message
    if final_state.get("messages"):
        final_message = final_state["messages"][-1]
        print(f"\nFinal Assessment:\n{final_message.content}")

    return final_state


if __name__ == "__main__":
    run_example()
