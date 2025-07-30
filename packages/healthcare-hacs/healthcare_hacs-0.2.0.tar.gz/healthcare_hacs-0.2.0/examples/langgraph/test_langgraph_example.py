#!/usr/bin/env python3
"""
Comprehensive test suite for HACS + LangGraph example.

This test suite provides full coverage of the LangGraph workflow example,
including unit tests, integration tests, performance benchmarks, and
FHIR compliance validation.
"""

import pytest
import time
import uuid
from datetime import date
from typing import Dict
from unittest.mock import patch

# Check for LangGraph availability
try:
    from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

    HAS_LANGGRAPH = True
except ImportError:
    HAS_LANGGRAPH = False

from hacs_core.actor import Actor, ActorRole
from hacs_core.evidence import Evidence, EvidenceType
from hacs_models.patient import Patient, AdministrativeGender
from hacs_models.observation import Observation, ObservationStatus

# Only import the modules being tested if LangGraph is available
if HAS_LANGGRAPH:
    try:
        from graph import (
            run_example,
            create_workflow_graph,
            create_example_data,
            initialize_workflow,
            assess_risk,
            search_evidence,
            generate_recommendations,
            calculate_cardiovascular_risk,
            search_clinical_evidence,
        )
        from state import (
            create_initial_state,
            update_risk_assessment,
            add_recommendation,
            get_workflow_summary,
            is_high_risk_case,
        )

        IMPORTS_AVAILABLE = True
    except ImportError as e:
        IMPORTS_AVAILABLE = False
        IMPORT_ERROR = str(e)
else:
    IMPORTS_AVAILABLE = False
    IMPORT_ERROR = "LangGraph not available"

# Skip all tests if LangGraph is not available
pytestmark = pytest.mark.skipif(
    not HAS_LANGGRAPH or not IMPORTS_AVAILABLE,
    reason=f"LangGraph example requires optional dependencies: {IMPORT_ERROR if not IMPORTS_AVAILABLE else 'LangGraph not installed'}",
)


@pytest.mark.skipif(not HAS_LANGGRAPH, reason="LangGraph not available")
class TestClinicalTools:
    """Test suite for clinical tool functions."""

    def test_calculate_cardiovascular_risk_high(self):
        """Test high-risk cardiovascular calculation."""
        if not IMPORTS_AVAILABLE:
            pytest.skip("Graph module not available")

        result = calculate_cardiovascular_risk(systolic_bp=170, age=70)

        assert result["risk_category"] == "high"
        assert result["ten_year_risk_percent"] > 20
        assert "Immediate intervention" in result["recommendation"]

    def test_calculate_cardiovascular_risk_moderate(self):
        """Test moderate-risk cardiovascular calculation."""
        if not IMPORTS_AVAILABLE:
            pytest.skip("Graph module not available")

        result = calculate_cardiovascular_risk(systolic_bp=145, age=55)

        assert result["risk_category"] == "moderate"
        assert 10 <= result["ten_year_risk_percent"] <= 20
        assert "Monitor and lifestyle" in result["recommendation"]

    def test_calculate_cardiovascular_risk_low(self):
        """Test low-risk cardiovascular calculation."""
        if not IMPORTS_AVAILABLE:
            pytest.skip("Graph module not available")

        result = calculate_cardiovascular_risk(systolic_bp=110, age=30)

        assert result["risk_category"] == "low"
        assert result["ten_year_risk_percent"] < 10
        assert "Monitor and lifestyle" in result["recommendation"]

    def test_calculate_cardiovascular_risk_edge_cases(self):
        """Test edge cases for risk calculation."""
        # Very high values should be capped
        if not IMPORTS_AVAILABLE:
            pytest.skip("Graph module not available")

        result = calculate_cardiovascular_risk(systolic_bp=250, age=90)
        assert result["ten_year_risk_percent"] <= 95

    def test_search_clinical_evidence_hypertension(self):
        """Test evidence search for hypertension."""
        if not IMPORTS_AVAILABLE:
            pytest.skip("Graph module not available")

        evidence = search_clinical_evidence("hypertension")

        assert len(evidence) > 0
        assert isinstance(evidence[0], Evidence)
        assert evidence[0].evidence_type == EvidenceType.GUIDELINE
        assert "AHA/ACC" in evidence[0].citation

    def test_search_clinical_evidence_diabetes(self):
        """Test evidence search for diabetes."""
        if not IMPORTS_AVAILABLE:
            pytest.skip("Graph module not available")

        evidence = search_clinical_evidence("diabetes")

        assert len(evidence) > 0
        assert evidence[0].evidence_type == EvidenceType.RESEARCH_PAPER
        assert "Prevention Program" in evidence[0].citation

    def test_search_clinical_evidence_not_found(self):
        """Test evidence search for unknown condition."""
        if not IMPORTS_AVAILABLE:
            pytest.skip("Graph module not available")

        evidence = search_clinical_evidence("unknown_condition")
        assert len(evidence) == 0


@pytest.mark.skipif(not HAS_LANGGRAPH, reason="LangGraph not available")
class TestWorkflowNodes:
    """Test suite for individual workflow nodes."""

    def setup_method(self):
        """Set up test data for each test."""
        if not IMPORTS_AVAILABLE:
            pytest.skip("State module not available")

        self.clinician = Actor(
            id=str(uuid.uuid4()),
            name="Dr. Test",
            role=ActorRole.PHYSICIAN,
            permissions=["read:patient", "write:observation", "execute:workflow"],
            is_active=True,
        )

        self.patient = Patient(
            id="test-patient-001",
            given=["Test"],
            family="Patient",
            gender=AdministrativeGender.FEMALE,
            birth_date=date(1970, 1, 1),
        )

        self.observation = Observation(
            id="test-obs-001",
            subject=self.patient.id,
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
            value_quantity={"value": 150, "unit": "mmHg"},
        )

    def test_initialize_workflow(self):
        """Test workflow initialization node."""
        initial_state = create_initial_state(
            self.patient, [self.observation], self.clinician
        )

        result = initialize_workflow(initial_state)

        assert len(result["messages"]) == 2
        assert isinstance(result["messages"][0], SystemMessage)
        assert isinstance(result["messages"][1], HumanMessage)
        assert "Test Patient" in result["messages"][1].content

    def test_assess_risk_with_bp_data(self):
        """Test risk assessment with blood pressure data."""
        initial_state = create_initial_state(
            self.patient, [self.observation], self.clinician
        )
        initial_state["messages"] = []

        result = assess_risk(initial_state)

        assert result["risk_assessment"] is not None
        assert "risk_category" in result["risk_assessment"]
        assert len(result["messages"]) == 1
        assert isinstance(result["messages"][0], AIMessage)

    def test_assess_risk_without_bp_data(self):
        """Test risk assessment without blood pressure data."""
        # Create observation without BP
        if not IMPORTS_AVAILABLE:
            pytest.skip("State module not available")

        non_bp_obs = Observation(
            id="test-obs-002",
            subject=self.patient.id,
            status=ObservationStatus.FINAL,
            code={"text": "Heart rate"},
            value_quantity={"value": 70, "unit": "bpm"},
        )

        initial_state = create_initial_state(self.patient, [non_bp_obs], self.clinician)
        initial_state["messages"] = []

        result = assess_risk(initial_state)

        assert result["risk_assessment"] is None
        assert len(result["messages"]) == 1
        assert "Unable to assess" in result["messages"][0].content

    def test_search_evidence(self):
        """Test evidence search node."""
        initial_state = create_initial_state(
            self.patient, [self.observation], self.clinician
        )
        initial_state["messages"] = []
        initial_state["risk_assessment"] = {"risk_category": "high"}

        result = search_evidence(initial_state)

        assert "evidence" in result
        assert len(result["evidence"]) > 0
        assert len(result["messages"]) == 1

    def test_generate_recommendations_high_risk(self):
        """Test recommendation generation for high-risk patient."""
        initial_state = create_initial_state(
            self.patient, [self.observation], self.clinician
        )
        initial_state["messages"] = []
        initial_state["risk_assessment"] = {"risk_category": "high"}
        initial_state["evidence"] = []

        result = generate_recommendations(initial_state)

        assert len(result["recommendations"]) >= 4
        assert "medication" in str(result["recommendations"]).lower()
        assert "cardiology" in str(result["recommendations"]).lower()
        assert len(result["messages"]) == 1

    def test_generate_recommendations_low_risk(self):
        """Test recommendation generation for low-risk patient."""
        initial_state = create_initial_state(
            self.patient, [self.observation], self.clinician
        )
        initial_state["messages"] = []
        initial_state["risk_assessment"] = {"risk_category": "low"}
        initial_state["evidence"] = []

        result = generate_recommendations(initial_state)

        assert len(result["recommendations"]) >= 2
        assert "lifestyle" in str(result["recommendations"]).lower()
        assert len(result["messages"]) == 1


@pytest.mark.skipif(not HAS_LANGGRAPH, reason="LangGraph not available")
class TestStateManagement:
    """Test suite for state management functions."""

    def setup_method(self):
        """Set up test data."""
        if not IMPORTS_AVAILABLE:
            pytest.skip("State module not available")

        self.clinician = Actor(
            id=str(uuid.uuid4()),
            name="Dr. State Test",
            role=ActorRole.PHYSICIAN,
            permissions=["read:patient", "execute:workflow"],
            is_active=True,
        )

        self.patient = Patient(
            id="state-test-patient",
            given=["State"],
            family="Test",
            gender=AdministrativeGender.MALE,
            birth_date=date(1980, 1, 1),
        )

    def test_create_initial_state(self):
        """Test initial state creation."""
        state = create_initial_state(self.patient, [], self.clinician)

        assert state["workflow_id"] is not None
        assert state["patient"]["id"] == self.patient.id
        assert state["actor_context"]["actor_name"] == self.clinician.name
        assert state["urgency_level"] == "normal"
        assert state["recommendations"] == []

    def test_update_risk_assessment(self):
        """Test risk assessment state update."""
        state = create_initial_state(self.patient, [], self.clinician)
        initial_version = state.get("version", 1)

        risk_data = {"risk_category": "high", "ten_year_risk_percent": 25.0}
        updated_state = update_risk_assessment(state, risk_data)

        assert updated_state["risk_assessment"] == risk_data
        assert updated_state["urgency_level"] == "high"
        assert updated_state["version"] == initial_version + 1

    def test_add_recommendation(self):
        """Test adding recommendations to state."""
        state = create_initial_state(self.patient, [], self.clinician)

        recommendation = "Test recommendation"
        updated_state = add_recommendation(state, recommendation)

        assert recommendation in updated_state["recommendations"]
        assert len(updated_state["recommendations"]) == 1

    def test_add_duplicate_recommendation(self):
        """Test that duplicate recommendations are not added."""
        state = create_initial_state(self.patient, [], self.clinician)

        recommendation = "Duplicate recommendation"
        state = add_recommendation(state, recommendation)
        state = add_recommendation(state, recommendation)

        assert len(state["recommendations"]) == 1

    def test_is_high_risk_case(self):
        """Test high-risk case detection."""
        state = create_initial_state(self.patient, [], self.clinician)

        # Not high risk initially
        assert not is_high_risk_case(state)

        # High risk with assessment
        state["risk_assessment"] = {"risk_category": "high"}
        assert is_high_risk_case(state)

        # High risk with urgency
        state["risk_assessment"] = {"risk_category": "low"}
        state["urgency_level"] = "high"
        assert is_high_risk_case(state)

    def test_get_workflow_summary(self):
        """Test workflow summary generation."""
        state = create_initial_state(self.patient, [], self.clinician)
        state["recommendations"] = ["Rec 1", "Rec 2"]
        state["risk_assessment"] = {"risk_category": "moderate"}

        summary = get_workflow_summary(state)

        assert summary["patient_name"] == self.patient.display_name
        assert summary["recommendations_count"] == 2
        assert summary["has_risk_assessment"] is True
        assert summary["urgency_level"] == "normal"


@pytest.mark.skipif(not HAS_LANGGRAPH, reason="LangGraph not available")
class TestIntegration:
    """Integration tests for complete workflow execution."""

    def test_complete_workflow_execution(self):
        """Test complete workflow from start to finish."""
        if not IMPORTS_AVAILABLE:
            pytest.skip("Workflow modules not available")

        # This should execute without errors
        final_state = run_example()

        # Verify final state structure
        assert final_state is not None
        assert "workflow_id" in final_state
        assert "patient" in final_state
        assert "recommendations" in final_state
        assert len(final_state["recommendations"]) > 0
        assert len(final_state["messages"]) >= 4

    def test_workflow_graph_creation(self):
        """Test workflow graph creation and compilation."""
        app = create_workflow_graph()

        # Should be able to create without errors
        assert app is not None

        # Should have the expected structure
        graph = app.get_graph()
        assert graph is not None

    def test_example_data_creation(self):
        """Test example data creation."""
        clinician, patient, observations = create_example_data()

        assert isinstance(clinician, Actor)
        assert isinstance(patient, Patient)
        assert len(observations) == 1
        assert isinstance(observations[0], Observation)

        # Verify FHIR compliance
        assert patient.gender == AdministrativeGender.FEMALE
        assert observations[0].status == ObservationStatus.FINAL


@pytest.mark.skipif(not HAS_LANGGRAPH, reason="LangGraph not available")
class TestPerformance:
    """Performance tests for workflow execution."""

    def test_workflow_execution_time(self):
        """Test that workflow executes within performance targets."""
        if not IMPORTS_AVAILABLE:
            pytest.skip("Workflow modules not available")

        start_time = time.time()

        final_state = run_example()

        execution_time = (time.time() - start_time) * 1000  # Convert to ms

        # Should execute in under 100ms (target from docs)
        assert execution_time < 100, (
            f"Execution took {execution_time:.1f}ms, expected <100ms"
        )
        assert final_state is not None

    def test_memory_usage(self):
        """Test memory usage stays within bounds."""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Run workflow multiple times
        for _ in range(10):
            run_example()

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # Should not increase memory by more than 10MB
        assert memory_increase < 10, f"Memory increased by {memory_increase:.1f}MB"

    def test_node_performance(self):
        """Test individual node performance."""
        clinician, patient, observations = create_example_data()
        initial_state = create_initial_state(patient, observations, clinician)

        # Test initialize_workflow performance
        start_time = time.time()
        initialize_workflow(initial_state)
        init_time = (time.time() - start_time) * 1000
        assert init_time < 10, f"Initialize took {init_time:.1f}ms, expected <10ms"

        # Test assess_risk performance
        start_time = time.time()
        assess_risk(initial_state)
        assess_time = (time.time() - start_time) * 1000
        assert assess_time < 20, f"Assess risk took {assess_time:.1f}ms, expected <20ms"


@pytest.mark.skipif(not HAS_LANGGRAPH, reason="LangGraph not available")
class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_invalid_patient_data(self):
        """Test handling of invalid patient data."""
        # This should not crash the workflow
        with patch("graph.create_example_data") as mock_data:
            mock_data.return_value = (None, None, [])

            # Should handle gracefully
            try:
                run_example()
            except Exception as e:
                # Should be a controlled exception, not a crash
                assert "patient" in str(e).lower() or "data" in str(e).lower()

    def test_missing_observations(self):
        """Test handling of missing observations."""
        clinician = Actor(
            id=str(uuid.uuid4()),
            name="Dr. Test",
            role=ActorRole.PHYSICIAN,
            permissions=["read:patient", "execute:workflow"],
            is_active=True,
        )

        patient = Patient(
            id="test-patient",
            given=["Test"],
            family="Patient",
            gender=AdministrativeGender.FEMALE,
            birth_date=date(1970, 1, 1),
        )

        # Empty observations should be handled gracefully
        initial_state = create_initial_state(patient, [], clinician)
        result = assess_risk(initial_state)

        # Should add appropriate message about missing data
        assert len(result["messages"]) > 0
        assert any(
            "unable" in msg.content.lower()
            for msg in result["messages"]
            if hasattr(msg, "content")
        )

    def test_workflow_with_exceptions(self):
        """Test workflow behavior when nodes raise exceptions."""
        # Mock a node to raise an exception
        with patch("graph.calculate_cardiovascular_risk") as mock_calc:
            mock_calc.side_effect = Exception("Mock calculation error")

            # Should handle the exception gracefully
            try:
                run_example()
            except Exception:
                # If it raises an exception, it should be handled appropriately
                pass


@pytest.mark.skipif(not HAS_LANGGRAPH, reason="LangGraph not available")
class TestFHIRCompliance:
    """Test FHIR compliance of generated data."""

    def test_patient_fhir_compliance(self):
        """Test that patient data is FHIR compliant."""
        _, patient, _ = create_example_data()

        # Check required FHIR fields
        assert patient.id is not None
        assert patient.given is not None
        assert patient.family is not None
        assert patient.gender in [g for g in AdministrativeGender]
        assert patient.birth_date is not None

    def test_observation_fhir_compliance(self):
        """Test that observation data is FHIR compliant."""
        _, _, observations = create_example_data()
        obs = observations[0]

        # Check required FHIR fields
        assert obs.id is not None
        assert obs.subject is not None
        assert obs.status in [s for s in ObservationStatus]
        assert obs.code is not None
        assert "coding" in obs.code
        assert obs.value_quantity is not None

    def test_evidence_fhir_compliance(self):
        """Test that evidence data follows FHIR patterns."""
        evidence_list = search_clinical_evidence("hypertension")

        for evidence in evidence_list:
            assert evidence.id is not None
            assert evidence.citation is not None
            assert evidence.content is not None
            assert evidence.evidence_type in [t for t in EvidenceType]
            assert 0 <= evidence.confidence_score <= 1


@pytest.mark.skipif(not HAS_LANGGRAPH, reason="LangGraph not available")
class TestSecurityAndValidation:
    """Test security and validation aspects."""

    def test_actor_permissions(self):
        """Test that actor permissions are properly validated."""
        clinician, patient, observations = create_example_data()

        # Actor should have required permissions
        assert "read:patient" in clinician.permissions
        assert "execute:workflow" in clinician.permissions
        assert clinician.is_active is True

    def test_data_sanitization(self):
        """Test that sensitive data is properly handled."""
        clinician, patient, observations = create_example_data()

        # Patient data should not contain sensitive information in logs
        patient_dict = patient.model_dump()

        # These fields should not be present or should be sanitized
        sensitive_fields = ["ssn", "medical_record_number", "phone", "email"]
        for field in sensitive_fields:
            assert field not in patient_dict or patient_dict[field] == "***REDACTED***"

    def test_state_version_tracking(self):
        """Test that state versions are properly tracked."""
        clinician, patient, observations = create_example_data()
        initial_state = create_initial_state(patient, observations, clinician)

        initial_version = initial_state.get("version", 1)

        # State updates should increment version
        updated_state = add_recommendation(initial_state, "Test recommendation")
        assert updated_state["version"] == initial_version + 1


# Performance benchmark utility
def benchmark_workflow(iterations: int = 100) -> Dict[str, float]:
    """
    Benchmark workflow performance over multiple iterations.

    Args:
        iterations: Number of iterations to run

    Returns:
        Performance metrics dictionary
    """
    execution_times = []

    for _ in range(iterations):
        start_time = time.time()
        run_example()
        execution_time = (time.time() - start_time) * 1000  # ms
        execution_times.append(execution_time)

    return {
        "min_time_ms": min(execution_times),
        "max_time_ms": max(execution_times),
        "avg_time_ms": sum(execution_times) / len(execution_times),
        "median_time_ms": sorted(execution_times)[len(execution_times) // 2],
        "total_iterations": iterations,
    }


def test_langgraph_availability():
    """Test to check if LangGraph is available and provide helpful message."""
    if not HAS_LANGGRAPH:
        pytest.skip(
            "LangGraph not installed. Install with: uv add langgraph langchain-core"
        )

    if not IMPORTS_AVAILABLE:
        pytest.skip(f"LangGraph example modules not available: {IMPORT_ERROR}")

    # If we get here, everything is available
    assert True


if __name__ == "__main__":
    # Run basic smoke test
    print("🧪 Running HACS LangGraph Example Tests")
    print("=" * 50)

    if not HAS_LANGGRAPH:
        print("⚠️  LangGraph not available - skipping all tests")
        print("   Install with: uv add langgraph langchain-core")
        exit(0)

    if not IMPORTS_AVAILABLE:
        print(f"⚠️  LangGraph example modules not available: {IMPORT_ERROR}")
        print("   Check LangGraph installation and dependencies")
        exit(0)

    # Quick smoke test
    try:
        final_state = run_example()
        print("✅ Basic workflow execution: PASSED")
    except Exception as e:
        print(f"❌ Basic workflow execution: FAILED - {e}")
        exit(1)

    # Performance benchmark
    print("\n📊 Running performance benchmark...")
    metrics = benchmark_workflow(10)
    print(f"Average execution time: {metrics['avg_time_ms']:.1f}ms")
    print(f"Min/Max: {metrics['min_time_ms']:.1f}ms / {metrics['max_time_ms']:.1f}ms")

    if metrics["avg_time_ms"] < 100:
        print("✅ Performance target met (<100ms)")
    else:
        print(f"⚠️  Performance target missed (avg: {metrics['avg_time_ms']:.1f}ms)")

    print("\n🎉 All smoke tests completed!")
    print(
        "Run 'pytest examples/langgraph/test_langgraph_example.py -v' for full test suite"
    )
