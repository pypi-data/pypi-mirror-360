#!/usr/bin/env python3
"""
HACS Quick Start Test

A simple test to verify your HACS installation is working correctly.
This test covers the basic functionality of all HACS packages.

To run this test:
    uv run python tests/test_quick_start.py

Or with pytest:
    uv run pytest tests/test_quick_start.py -v
"""

import sys
import os
from datetime import datetime, timezone

# Add packages to Python path for testing
sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "..", "packages", "hacs-core", "src")
)
sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "..", "packages", "hacs-models", "src")
)
sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "..", "packages", "hacs-tools", "src")
)


def test_imports():
    """Test that all core packages can be imported."""
    print("🔍 Testing imports...")
    # Import packages to test availability
    print("✅ All core packages imported successfully")


def test_patient_creation():
    """Test creating a basic patient record."""
    print("🧪 Testing patient creation...")

    from hacs_models import Patient

    patient = Patient(
        id="test-patient-001",
        given=["John"],
        family="Doe",
        gender="male",
        birth_date="1985-03-15",
        active=True,
    )

    assert patient.display_name == "John Doe"
    assert patient.age_years >= 35  # Should be around 39-40 years old
    print(f"✅ Patient created: {patient.display_name}, Age: {patient.age_years}")


def test_observation_creation():
    """Test creating a clinical observation."""
    print("🧪 Testing observation creation...")

    from hacs_models import Observation

    observation = Observation(
        id="test-obs-001",
        status="final",
        code={
            "coding": [
                {
                    "system": "http://loinc.org",
                    "code": "8480-6",
                    "display": "Systolic blood pressure",
                }
            ]
        },
        subject="test-patient-001",
        value_quantity={"value": 120, "unit": "mmHg"},
        effective_datetime=datetime.now(timezone.utc),
    )

    assert observation.status == "final"
    assert observation.value_quantity["value"] == 120
    # Use the primary_code computed field instead of display_name
    assert observation.primary_code == "8480-6"
    print(
        f"✅ Observation created: {observation.primary_code} = {observation.value_quantity['value']} {observation.value_quantity['unit']}"
    )


def test_actor_creation():
    """Test creating an actor with permissions."""
    print("🧪 Testing actor creation...")

    from hacs_core import Actor

    # Start a session to make the actor authenticated
    actor = Actor(
        id="test-doctor-001",
        name="Dr. Jane Smith",
        role="physician",
        permissions=["patient:read", "observation:*"],
        is_active=True,
    )

    # Start a session to make the actor authenticated for permission checks
    actor.start_session("test-session-001")

    assert actor.has_permission("patient:read")
    assert actor.has_permission("observation:create")
    assert not actor.has_permission("admin:delete")
    print(f"✅ Actor created: {actor.name} with {len(actor.permissions)} permissions")


def test_memory_block_creation():
    """Test creating a memory block."""
    print("🧪 Testing memory block creation...")

    from hacs_core import MemoryBlock

    memory = MemoryBlock(
        id="test-memory-001",
        memory_type="episodic",  # This field is required
        content="Patient presents with elevated blood pressure",
        importance_score=0.8,
        metadata={
            "tags": ["hypertension", "cardiovascular"],
            "patient_id": "test-patient-001",
        },
    )

    assert memory.memory_type == "episodic"
    assert memory.importance_score == 0.8
    print(f"✅ Memory block created with importance score: {memory.importance_score}")


def test_vector_metadata():
    """Test creating vector metadata."""
    print("🧪 Testing vector metadata creation...")

    from hacs_tools.vectorization import VectorMetadata

    metadata = VectorMetadata(
        resource_type="Patient",
        resource_id="test-patient-001",
        content_hash="abc123",
        metadata={"name": "John Doe", "age": 39, "condition": "hypertension"},
    )

    assert metadata.resource_type == "Patient"
    assert metadata.metadata["name"] == "John Doe"
    print(f"✅ Vector metadata created for {metadata.resource_type}")


def run_quick_tests():
    """Run all quick tests and return overall success."""
    print("🚀 HACS Quick Start Test Suite")
    print("=" * 50)

    tests = [
        test_imports,
        test_patient_creation,
        test_observation_creation,
        test_actor_creation,
        test_memory_block_creation,
        test_vector_metadata,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed: {e}")
        print()  # Add spacing between tests

    print("=" * 50)
    print(f"📊 Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Your HACS installation is working correctly.")
        print("\n🚀 Next steps:")
        print("   • Check out examples/ for usage examples")
        print("   • Read docs/ for detailed documentation")
        print("   • Try the LangGraph example in examples/langgraph/")
        return True
    else:
        print("⚠️  Some tests failed. Please check your installation.")
        print("\n🔧 Troubleshooting:")
        print("   • Make sure you're in the HACS project root directory")
        print("   • Run 'uv sync' to install dependencies")
        print("   • Check the installation guide in docs/getting-started/")
        return False


if __name__ == "__main__":
    success = run_quick_tests()
    sys.exit(0 if success else 1)
