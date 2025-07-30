"""
Integration tests for HACS Tools - CRUD Operations.

These tests verify the basic CRUD functionality of the HACS Tools package.
"""

import pytest
from datetime import date
from hacs_core import Actor, ActorRole
from hacs_models import Patient, Observation
from hacs_models import AdministrativeGender, ObservationStatus
from hacs_tools import (
    CreateResource,
    ReadResource,
    UpdateResource,
    DeleteResource,
    ListResources,
    GetAuditLog,
    StorageBackend,
    set_storage_backend,
)


class TestCRUDOperations:
    """Test CRUD operations with Actor permissions."""

    @pytest.fixture
    def physician_actor(self):
        """Create a physician actor with full permissions."""
        return Actor(
            id="physician-test-001",
            name="Dr. Test Physician",
            role=ActorRole.PHYSICIAN,
            permissions=["*:*"],
            is_active=True,
        )

    @pytest.fixture
    def nurse_actor(self):
        """Create a nurse actor with limited permissions."""
        return Actor(
            id="nurse-test-001",
            name="Test Nurse",
            role=ActorRole.NURSE,
            permissions=["patient:read", "observation:read"],
            is_active=True,
        )

    @pytest.fixture
    def test_patient(self):
        """Create a test patient."""
        return Patient(
            id="patient-test-001",
            given=["John"],
            family="Doe",
            gender=AdministrativeGender.MALE,
            birth_date=date(1980, 5, 15),
            active=True,
        )

    @pytest.fixture
    def test_observation(self):
        """Create a test observation."""
        return Observation(
            id="obs-test-001",
            status=ObservationStatus.FINAL,
            code={
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": "8480-6",
                        "display": "Systolic blood pressure",
                    }
                ]
            },
            subject="patient-test-001",
            value_quantity={"value": 120, "unit": "mmHg"},
        )

    def test_create_resource_success(self, physician_actor, test_patient):
        """Test successful resource creation."""
        # Reset storage
        set_storage_backend(StorageBackend.MEMORY)

        resource_id = CreateResource(test_patient, physician_actor)
        assert resource_id == test_patient.id

    def test_create_resource_permission_denied(self, nurse_actor, test_patient):
        """Test resource creation with insufficient permissions."""
        set_storage_backend(StorageBackend.MEMORY)

        with pytest.raises(Exception) as exc_info:
            CreateResource(test_patient, nurse_actor)

        assert "lacks permission" in str(exc_info.value)

    def test_read_resource_success(self, physician_actor, test_patient):
        """Test successful resource reading."""
        set_storage_backend(StorageBackend.MEMORY)

        # Create first
        CreateResource(test_patient, physician_actor)

        # Then read
        retrieved = ReadResource("Patient", test_patient.id, physician_actor)
        assert isinstance(retrieved, Patient)  # Type guard
        assert retrieved.id == test_patient.id
        assert retrieved.family == test_patient.family

    def test_update_resource_success(self, physician_actor, test_patient):
        """Test successful resource update."""
        set_storage_backend(StorageBackend.MEMORY)

        # Create first
        CreateResource(test_patient, physician_actor)

        # Update
        test_patient.family = "Smith"
        updated = UpdateResource(test_patient, physician_actor)
        assert isinstance(updated, Patient)  # Type guard
        assert updated.family == "Smith"

    def test_delete_resource_success(self, physician_actor, test_patient):
        """Test successful resource deletion."""
        set_storage_backend(StorageBackend.MEMORY)

        # Create first
        CreateResource(test_patient, physician_actor)

        # Delete
        result = DeleteResource("Patient", test_patient.id, physician_actor)
        assert result is True

        # Verify deletion
        with pytest.raises(Exception) as exc_info:
            ReadResource("Patient", test_patient.id, physician_actor)
        assert "not found" in str(exc_info.value)

    def test_list_resources(self, physician_actor, test_patient):
        """Test resource listing."""
        set_storage_backend(StorageBackend.MEMORY)

        # Create multiple patients
        CreateResource(test_patient, physician_actor)

        patient2 = Patient(
            id="patient-test-002",
            given=["Jane"],
            family="Smith",
            gender=AdministrativeGender.FEMALE,
            birth_date=date(1990, 8, 20),
            active=True,
        )
        CreateResource(patient2, physician_actor)

        # List patients
        patients = ListResources("Patient", physician_actor, limit=10)
        assert len(patients) == 2
        assert any(p.id == test_patient.id for p in patients)
        assert any(p.id == patient2.id for p in patients)

    def test_audit_logging(self, physician_actor, test_patient):
        """Test audit logging functionality."""
        set_storage_backend(StorageBackend.MEMORY)

        # Perform operations
        CreateResource(test_patient, physician_actor)
        ReadResource("Patient", test_patient.id, physician_actor)

        # Check audit log
        audit_events = GetAuditLog(physician_actor, limit=10)
        assert len(audit_events) >= 2

        # Verify event types
        operations = [event.operation for event in audit_events]
        assert "create" in operations
        assert "read" in operations


class TestIntegrationWorkflows:
    """Test end-to-end integration workflows."""

    def test_complete_patient_workflow(self):
        """Test complete patient management workflow."""
        set_storage_backend(StorageBackend.MEMORY)

        # Create physician
        physician = Actor(
            id="workflow-physician-001",
            name="Dr. Workflow",
            role=ActorRole.PHYSICIAN,
            permissions=["*:*"],
            is_active=True,
        )

        # 1. Create patient
        patient = Patient(
            id="workflow-patient-001",
            given=["Workflow"],
            family="Test",
            gender=AdministrativeGender.FEMALE,
            birth_date=date(1985, 6, 10),
            active=True,
        )

        # Create patient
        patient_id = CreateResource(patient, physician)
        assert patient_id == patient.id

        # 2. Create observation for patient
        observation = Observation(
            id="workflow-obs-001",
            status=ObservationStatus.FINAL,
            code={
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": "8867-4",
                        "display": "Heart rate",
                    }
                ]
            },
            subject=patient.id,
            value_quantity={"value": 72, "unit": "/min"},
        )

        obs_id = CreateResource(observation, physician)
        assert obs_id == observation.id

        # 3. Read resources
        retrieved_patient = ReadResource("Patient", patient.id, physician)
        retrieved_obs = ReadResource("Observation", observation.id, physician)

        assert isinstance(retrieved_patient, Patient)  # Type guard
        assert isinstance(retrieved_obs, Observation)  # Type guard
        assert retrieved_patient.family == "Test"
        assert retrieved_obs.get_numeric_value() == 72

        # 4. Update patient
        patient.family = "Updated"
        updated_patient = UpdateResource(patient, physician)
        assert isinstance(updated_patient, Patient)  # Type guard
        assert updated_patient.family == "Updated"

        # 5. Check audit trail
        audit_events = GetAuditLog(physician, limit=10)
        assert len(audit_events) >= 4  # create, create, read, read, update

        operations = [event.operation for event in audit_events]
        assert "create" in operations
        assert "read" in operations
        assert "update" in operations


if __name__ == "__main__":
    # Run basic tests
    print("Running HACS Tools Integration Tests...")

    # Test basic CRUD
    physician = Actor(
        id="test-physician",
        name="Test Doctor",
        role=ActorRole.PHYSICIAN,
        permissions=["*:*"],
        is_active=True,
    )

    patient = Patient(
        id="test-patient",
        given=["Test"],
        family="Patient",
        gender=AdministrativeGender.MALE,
        active=True,
    )

    set_storage_backend(StorageBackend.MEMORY)

    # Test CRUD operations
    patient_id = CreateResource(patient, physician)
    print(f"✅ Created patient: {patient_id}")

    retrieved = ReadResource("Patient", patient_id, physician)
    print(f"✅ Retrieved patient: {retrieved.display_name}")

    print("✅ All basic tests passed!")
