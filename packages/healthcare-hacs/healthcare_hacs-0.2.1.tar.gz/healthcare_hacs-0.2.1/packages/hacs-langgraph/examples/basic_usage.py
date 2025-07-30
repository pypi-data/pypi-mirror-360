"""
Basic Usage Example for HACS LangGraph Integration

This example demonstrates the basic usage of the HACS LangGraph adapter
for creating clinical workflows.
"""

from hacs_core import Actor
from hacs_langgraph import LangGraphAdapter, LangGraphStateType
from hacs_models import Observation, Patient


def main():
    """Demonstrate basic HACS LangGraph integration."""
    print("🔗 HACS LangGraph Basic Usage Example")
    print("=" * 50)

    # Create adapter
    adapter = LangGraphAdapter()

    # Create actor (clinician)
    actor = Actor(name="Dr. Sarah Chen", role="physician")
    print(f"👩‍⚕️ Created actor: {actor.name} ({actor.role})")

    # Create patient
    patient = Patient(full_name="Maria Rodriguez", age=59)
    print(f"👤 Created patient: {patient.display_name}, age {patient.age_years}")

    # Create observations
    observations = [
        Observation(
            code_text="systolic blood pressure", value_numeric=165, unit="mmHg"
        ),
        Observation(code_text="heart rate", value_numeric=88, unit="bpm"),
        Observation(code_text="body mass index", value_numeric=28.5, unit="kg/m2"),
    ]
    print(f"📊 Created {len(observations)} observations")

    # Create clinical workflow state
    state = adapter.create_clinical_workflow_state(
        patient=patient,
        observations=observations,
        actor=actor,
        workflow_type=LangGraphStateType.CLINICAL_ASSESSMENT,
    )

    print("\n🔄 Created clinical workflow state:")
    print(f"   Workflow ID: {state['workflow_id']}")
    print(f"   Workflow Type: {state['workflow_type']}")
    print(f"   Current Step: {state['current_step']}")
    print(f"   Patient: {state['patient']['display_name']}")
    print(f"   Observations: {len(state['observations'])}")
    print(f"   Version: {state['version']}")

    # Register a simple clinical tool
    def calculate_cardiovascular_risk(age: int, systolic_bp: int, **kwargs) -> dict:
        """Calculate simple cardiovascular risk."""
        base_risk = 0.05
        age_factor = max(0, (age - 40) * 0.01)
        bp_factor = max(0, (systolic_bp - 120) * 0.002)

        risk = base_risk + age_factor + bp_factor
        risk_percentage = min(risk * 100, 100)

        if risk_percentage > 20:
            category = "high"
        elif risk_percentage > 10:
            category = "moderate"
        else:
            category = "low"

        return {
            "risk_percentage": risk_percentage,
            "risk_category": category,
            "factors": {"age_factor": age_factor, "bp_factor": bp_factor},
        }

    adapter.register_tool(
        "cardiovascular_risk",
        calculate_cardiovascular_risk,
        description="Calculate 10-year cardiovascular risk",
    )

    print("\n🛠️ Registered clinical tool: cardiovascular_risk")

    # Execute the tool
    bp_obs = next(obs for obs in observations if "blood pressure" in obs.code_text)
    state = adapter.execute_tool(
        state,
        "cardiovascular_risk",
        age=patient.age_years,
        systolic_bp=int(bp_obs.value_numeric),
    )

    risk_result = state["tool_results"]["cardiovascular_risk"]
    print("\n📈 Risk Assessment Results:")
    print(f"   Risk Percentage: {risk_result['risk_percentage']:.1f}%")
    print(f"   Risk Category: {risk_result['risk_category']}")
    print(f"   Age Factor: {risk_result['factors']['age_factor']:.3f}")
    print(f"   BP Factor: {risk_result['factors']['bp_factor']:.3f}")

    # Show clinical context
    clinical_context = state["clinical_context"]
    print("\n🏥 Clinical Context:")
    print(f"   Patient ID: {clinical_context['patient_id']}")
    print(f"   Patient Age: {clinical_context['patient_age']}")
    print(f"   Observation Count: {clinical_context['observation_count']}")
    print(f"   Initiated By: {clinical_context['workflow_initiated_by']}")

    # Show tool history
    print("\n📋 Tool Execution History:")
    for i, execution in enumerate(state["tool_history"], 1):
        print(
            f"   {i}. {execution['tool_name']} - {'✅ Success' if execution['success'] else '❌ Failed'}"
        )
        if execution["success"]:
            print(f"      Result: {execution['result']}")

    print("\n✅ Workflow completed successfully!")
    print(f"   Final state version: {state['version']}")
    print(f"   Total tools executed: {len(state['tool_history'])}")


if __name__ == "__main__":
    main()
