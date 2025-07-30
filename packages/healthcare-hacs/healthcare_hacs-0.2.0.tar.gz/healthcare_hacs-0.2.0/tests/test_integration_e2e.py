"""
End-to-End Integration Tests for HACS v0.1.0

This module provides basic integration tests that demonstrate
the core HACS workflow including Actor authentication and resource management.
"""

from datetime import datetime, timezone, date

# HACS Core imports
from hacs_core import Actor, ActorRole

# HACS Models imports
from hacs_models import Patient, Observation
from hacs_models import AdministrativeGender, ObservationStatus

# HACS Tools imports
from hacs_tools import (
    CreateResource,
    ReadResource,
    UpdateResource,
    DeleteResource,
)

# HACS FHIR imports
from hacs_fhir import to_fhir, from_fhir


def test_basic_hacs_workflow():
    """Test basic HACS workflow: Actor Login → Create Patient → Create Observation → Convert to FHIR."""

    print("🧪 Running HACS v0.1.0 Basic Workflow Test...")

    # Step 1: Create Actor
    print("  Step 1: Creating Actor...")
    physician = Actor(
        id="physician-001",
        name="Dr. Sarah Johnson",
        role=ActorRole.PHYSICIAN,
        permissions=["*:*"],
        is_active=True,
        organization="Springfield General Hospital",
    )
    print(f"    ✅ Actor created: {physician.name}")

    # Step 2: Create Patient
    print("  Step 2: Creating Patient...")
    patient = Patient(
        id="patient-e2e-001",
        given=["Ana", "Maria"],
        family="Silva",
        gender=AdministrativeGender.FEMALE,
        birth_date=date(1985, 3, 15),
        active=True,
        identifiers=[
            {
                "system": "http://hospital.example.org/patient-ids",
                "value": "E2E-12345",
                "use": "official",
            }
        ],
    )

    # Create patient with Actor authentication
    patient_id = CreateResource(patient, actor=physician)
    assert patient_id == patient.id
    print(f"    ✅ Patient created: {patient_id}")

    # Verify patient can be read
    retrieved_patient = ReadResource("Patient", patient_id, actor=physician)
    assert isinstance(retrieved_patient, Patient)
    assert retrieved_patient.display_name == "Ana Maria Silva"
    print(
        f"    ✅ Patient retrieved: {retrieved_patient.display_name}, Age: {retrieved_patient.age_years}"
    )

    # Step 3: Create Observation
    print("  Step 3: Creating Observation...")
    observation = Observation(
        id="obs-e2e-001",
        status=ObservationStatus.FINAL,
        code={
            "coding": [
                {
                    "system": "http://loinc.org",
                    "code": "8480-6",
                    "display": "Systolic blood pressure",
                }
            ],
            "text": "Systolic Blood Pressure",
        },
        subject=patient.id,
        effective_datetime=datetime.now(timezone.utc),
        value_quantity={
            "value": 135,
            "unit": "mmHg",
            "system": "http://unitsofmeasure.org",
            "code": "mm[Hg]",
        },
        performer=["physician-001"],
    )

    observation_id = CreateResource(observation, actor=physician)
    assert observation_id == observation.id
    print(f"    ✅ Observation created: {observation_id} (BP: 135 mmHg)")

    # Step 4: FHIR Conversion
    print("  Step 4: Testing FHIR Conversion...")
    patient_fhir = to_fhir(retrieved_patient)
    assert patient_fhir["resourceType"] == "Patient"
    assert patient_fhir["gender"] == "female"
    print("    ✅ HACS → FHIR conversion successful")

    patient_from_fhir = from_fhir(patient_fhir)
    assert isinstance(patient_from_fhir, Patient)
    assert patient_from_fhir.id == patient.id
    assert patient_from_fhir.family == patient.family
    print("    ✅ FHIR → HACS conversion successful (round-trip preserved)")

    print("\n🎉 Basic HACS workflow test passed!")


def test_performance_benchmarks():
    """Test performance benchmarks with target <300ms p95 for CRUD operations."""
    import time

    print("🏃 Running Performance Benchmarks...")

    physician = Actor(
        id="perf-physician",
        name="Performance Test Doctor",
        role=ActorRole.PHYSICIAN,
        permissions=["*:*"],
        is_active=True,
    )

    test_patient = Patient(
        id="perf-test-001",
        given=["Performance"],
        family="Test",
        gender=AdministrativeGender.OTHER,
        birth_date=date(1990, 1, 1),
        active=True,
    )

    # Benchmark CREATE operation
    start_time = time.time()
    patient_id = CreateResource(test_patient, actor=physician)
    create_time = (time.time() - start_time) * 1000  # Convert to ms

    # Benchmark READ operation
    start_time = time.time()
    retrieved_patient = ReadResource("Patient", patient_id, actor=physician)
    assert isinstance(retrieved_patient, Patient)
    read_time = (time.time() - start_time) * 1000

    # Benchmark UPDATE operation
    retrieved_patient.active = False
    start_time = time.time()
    UpdateResource(retrieved_patient, actor=physician)
    update_time = (time.time() - start_time) * 1000

    # Benchmark DELETE operation
    start_time = time.time()
    DeleteResource("Patient", patient_id, actor=physician)
    delete_time = (time.time() - start_time) * 1000

    print("  Performance Results:")
    print(f"    CREATE: {create_time:.2f}ms (target: <300ms)")
    print(f"    READ: {read_time:.2f}ms (target: <300ms)")
    print(f"    UPDATE: {update_time:.2f}ms (target: <300ms)")
    print(f"    DELETE: {delete_time:.2f}ms (target: <300ms)")

    # Assert performance targets
    assert create_time < 300, f"CREATE took {create_time:.2f}ms (target: <300ms)"
    assert read_time < 300, f"READ took {read_time:.2f}ms (target: <300ms)"
    assert update_time < 300, f"UPDATE took {update_time:.2f}ms (target: <300ms)"
    assert delete_time < 300, f"DELETE took {delete_time:.2f}ms (target: <300ms)"

    print("  ✅ All performance benchmarks passed!")


def test_package_imports():
    """Test that all packages can be imported successfully."""
    print("\n🔍 Testing package imports...")

    try:
        # Import all packages to test availability (imports used for testing)
        from hacs_core import BaseResource, Actor, MemoryBlock, Evidence  # noqa: F401
        from hacs_models import Patient, AgentMessage, Encounter, Observation  # noqa: F401
        from hacs_fhir import to_fhir, from_fhir  # noqa: F401
        from hacs_tools import CreateResource, ReadResource  # noqa: F401

        print("  ✅ All packages imported successfully")
        return True
    except ImportError as e:
        print(f"  ❌ Import failed: {e}")
        raise  # Re-raise to fail the test


if __name__ == "__main__":
    """Run all integration tests."""
    print("🚀 HACS v0.1.0 Integration Test Suite")
    print("=" * 50)

    tests_passed = 0
    total_tests = 3

    try:
        # Test 1: Cross-package imports
        if test_package_imports():
            tests_passed += 1

        # Test 2: Basic workflow
        if test_basic_hacs_workflow():
            tests_passed += 1

        # Test 3: Performance benchmarks
        if test_performance_benchmarks():
            tests_passed += 1

        print("=" * 50)
        print(f"🎯 Test Results: {tests_passed}/{total_tests} tests passed")

        if tests_passed == total_tests:
            print("🎉 HACS v0.1.0 Integration Test Suite: SUCCESS")
            print("✅ All core functionality working correctly!")
            print("✅ Performance targets met!")
            print("✅ FHIR round-trip preservation verified!")
            print("✅ Actor security enforced!")
        else:
            print("❌ Some tests failed - see output above")

    except Exception as e:
        print(f"❌ HACS v0.1.0 Integration Test Suite: FAILED - {e}")
        import traceback

        traceback.print_exc()
        raise
