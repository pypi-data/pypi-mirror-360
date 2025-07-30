#!/usr/bin/env python3
"""
Test LLM-friendly features in HACS models.

This test validates that the models can be easily used by LLMs for structured output generation,
with flexible validation and smart defaults.
"""

from hacs_core import Actor
from hacs_models import Observation, Patient


def test_patient_llm_friendly():
    """Test Patient model with LLM-friendly inputs."""
    # Test with natural language name parsing
    patient = Patient(
        full_name="Dr. Maria Elena Rodriguez-Smith Jr.",
        age=42,
        gender="female",
        phone="555-0123",
        email="maria.rodriguez@email.com",
    )

    # Verify auto-parsing worked
    assert patient.given == ["Maria", "Elena"]
    assert patient.family == "Rodriguez-Smith"
    assert patient.prefix == ["Dr."]
    assert patient.suffix == ["Jr."]
    assert patient.age_years == 42
    assert patient.phone == "555-0123"
    assert patient.email == "maria.rodriguez@email.com"

    # Verify ID was auto-generated
    assert patient.id.startswith("patient-")

    # Verify simple contact info was added to structured format
    assert any(t.get("system") == "phone" for t in patient.telecom)
    assert any(t.get("system") == "email" for t in patient.telecom)

    print(f"✅ Patient LLM-friendly features working: {patient.display_name}")


def test_observation_llm_friendly():
    """Test Observation model with LLM-friendly inputs."""
    # Create a patient first
    patient = Patient(full_name="John Smith", age=45)

    # Test with natural language observation type
    observation = Observation(
        subject=patient.id,
        code_text="blood pressure",  # Auto-converts to LOINC
        value_numeric=120,
        unit="mmHg",
        interpretation_text="normal",
    )

    # Verify auto-conversion worked
    assert observation.code is not None
    assert "coding" in observation.code
    assert observation.code["coding"][0]["system"] == "http://loinc.org"
    assert observation.display_name == "blood pressure"
    assert observation.get_numeric_value() == 120
    assert observation.get_unit() == "mmHg"

    # Verify ID was auto-generated
    assert observation.id.startswith("observation-")

    # Verify interpretation was converted
    assert len(observation.interpretation) > 0

    print(f"✅ Observation LLM-friendly features working: {observation.display_name}")


def test_actor_llm_friendly():
    """Test Actor model with LLM-friendly inputs."""
    # Test with role-based auto-permissions
    actor = Actor(
        name="Dr. Sarah Johnson",
        role="physician",
        email="sarah.johnson@hospital.com",
        phone="555-0456",
    )

    # Verify auto-generation worked
    assert len(actor.permissions) > 0
    assert "read:patient" in actor.permissions
    assert "write:patient" in actor.permissions
    assert actor.display_role == "Physician"
    assert actor.email == "sarah.johnson@hospital.com"
    assert actor.phone == "555-0456"

    # Verify ID was auto-generated
    assert actor.id.startswith("actor-")

    # Verify contact info was added to structured format
    assert "email" in actor.contact_info
    assert "phone" in actor.contact_info

    print(
        f"✅ Actor LLM-friendly features working: {actor.name} ({actor.display_role})"
    )


def test_complete_workflow():
    """Test a complete clinical workflow with LLM-friendly inputs."""
    # Create doctor
    doctor = Actor(name="Dr. Michael Chen", role="physician")

    # Create patient
    patient = Patient(
        full_name="John Michael Smith", age=45, gender="male", phone="555-7890"
    )

    # Create multiple observations
    observations = [
        Observation(
            subject=patient.id,
            code_text="blood pressure",
            value_numeric=130,
            unit="mmHg",
        ),
        Observation(
            subject=patient.id,
            code_text="heart rate",
            value_numeric=78,
            unit="beats/min",
        ),
        Observation(
            subject=patient.id,
            code_text="body temperature",
            value_numeric=98.2,
            unit="F",
        ),
    ]

    # Verify everything works together
    assert doctor.name == "Dr. Michael Chen"
    assert patient.display_name == "John Michael Smith"
    assert len(observations) == 3

    # All should have auto-generated IDs
    assert all(
        obj.id.startswith(f"{obj.resource_type.lower()}-")
        for obj in [doctor, patient] + observations
    )

    # All observations should have proper LOINC codes
    assert all(obs.code is not None for obs in observations)
    assert all(obs.get_numeric_value() is not None for obs in observations)

    print("✅ Complete workflow working:")
    print(f"   Doctor: {doctor.name}")
    print(f"   Patient: {patient.display_name} (Age: {patient.age_years})")
    print(f"   Observations: {len(observations)}")
    for obs in observations:
        print(f"   • {obs.display_name}: {obs.get_numeric_value()} {obs.get_unit()}")


if __name__ == "__main__":
    print("🧪 Testing LLM-friendly features...")

    test_patient_llm_friendly()
    test_observation_llm_friendly()
    test_actor_llm_friendly()
    test_complete_workflow()

    print("\n✅ All LLM-friendly features are working correctly!")
    print("\n🎯 Key LLM-friendly improvements:")
    print("   • Auto-generated IDs - no need to specify unique identifiers")
    print("   • Natural language inputs - use simple text instead of complex codes")
    print("   • Smart defaults - flexible validation that guides rather than blocks")
    print(
        "   • Auto-parsing - full names, ages, and contact info are automatically structured"
    )
    print(
        "   • LOINC mapping - common observations auto-convert to proper medical codes"
    )
