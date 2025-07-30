"""
Tests for HACS FHIR Integration

This module tests bidirectional mapping between HACS models and FHIR resources,
including round-trip preservation, Evidence → Citation mapping, and validation.
"""

import pytest
from datetime import datetime, timezone, date

# Import HACS models
from hacs_core import BaseResource, Evidence, Actor, EvidenceType, ActorRole
from hacs_models import (
    Patient,
    AgentMessage,
    Encounter,
    Observation,
    AdministrativeGender,
    MessageRole,
    MessagePriority,
    EncounterStatus,
    EncounterClass,
    ObservationStatus,
    DataAbsentReason,
)

# Import FHIR integration (gracefully handle missing fhir.resources)
try:
    from hacs_fhir import to_fhir, from_fhir, validate_fhir_compliance, FHIRMappingError

    FHIR_AVAILABLE = True
except ImportError:
    FHIR_AVAILABLE = False
    pytest.skip(
        "fhir.resources not available, skipping FHIR tests", allow_module_level=True
    )


def _create_encounter(**kwargs) -> Encounter:
    """Helper function to create Encounter with proper class field handling."""
    encounter_class = kwargs.pop("encounter_class", EncounterClass.AMB)
    encounter_data = {"class": encounter_class, **kwargs}
    return Encounter(**encounter_data)


class TestPatientFHIRMapping:
    """Test Patient ↔ FHIR Patient mapping."""

    def test_patient_to_fhir_basic(self):
        """Test basic Patient to FHIR mapping."""
        patient = Patient(
            id="patient-001",
            given=["Ana", "Maria"],
            family="Silva",
            gender=AdministrativeGender.FEMALE,
            birth_date=date(1985, 3, 15),
            active=True,
        )

        fhir_dict = to_fhir(patient)

        assert fhir_dict["resourceType"] == "Patient"
        assert fhir_dict["id"] == "patient-001"
        assert fhir_dict["active"] is True
        assert fhir_dict["gender"] == "female"
        assert fhir_dict["birthDate"] == "1985-03-15"

        # Check name structure
        assert len(fhir_dict["name"]) == 1
        name = fhir_dict["name"][0]
        assert name["use"] == "official"
        assert name["family"] == "Silva"
        assert name["given"] == ["Ana", "Maria"]

    def test_fhir_to_patient_basic(self):
        """Test basic FHIR Patient to HACS mapping."""
        fhir_dict = {
            "resourceType": "Patient",
            "id": "patient-002",
            "active": True,
            "gender": "male",
            "birthDate": "1990-07-22",
            "name": [
                {"use": "official", "family": "Santos", "given": ["João", "Carlos"]}
            ],
        }

        patient = from_fhir(fhir_dict)

        assert isinstance(patient, Patient)
        assert patient.id == "patient-002"
        assert patient.active is True
        assert patient.gender == AdministrativeGender.MALE
        assert patient.birth_date == date(1990, 7, 22)
        assert patient.family == "Santos"
        assert patient.given == ["João", "Carlos"]

    def test_patient_round_trip(self):
        """Test Patient → FHIR → Patient round-trip preservation."""
        original_patient = Patient(
            id="patient-round-trip",
            given=["Maria", "José"],
            family="Oliveira",
            gender=AdministrativeGender.FEMALE,
            birth_date=date(1978, 12, 5),
            active=True,
            identifiers=[
                {
                    "use": "usual",
                    "system": "http://hospital.example.org/patients",
                    "value": "12345",
                }
            ],
        )

        # Round trip: HACS → FHIR → HACS
        fhir_dict = to_fhir(original_patient)
        reconstructed_patient = from_fhir(fhir_dict)

        # Verify preservation of key fields
        assert isinstance(reconstructed_patient, Patient)
        assert reconstructed_patient.id == original_patient.id
        assert reconstructed_patient.given == original_patient.given
        assert reconstructed_patient.family == original_patient.family
        assert reconstructed_patient.gender == original_patient.gender
        assert reconstructed_patient.birth_date == original_patient.birth_date
        assert reconstructed_patient.active == original_patient.active


class TestAgentMessageFHIRMapping:
    """Test AgentMessage ↔ FHIR CommunicationRequest mapping."""

    def test_agent_message_to_fhir(self):
        """Test AgentMessage to FHIR CommunicationRequest mapping."""
        message = AgentMessage(
            id="msg-001",
            role=MessageRole.ASSISTANT,
            content="Patient presents with chest pain, recommend ECG.",
            priority=MessagePriority.HIGH,
            confidence_score=0.95,
            memory_handles=["memory-001", "memory-002"],
        )

        fhir_dict = to_fhir(message)

        assert fhir_dict["resourceType"] == "CommunicationRequest"
        assert fhir_dict["id"] == "msg-001"
        assert fhir_dict["status"] == "active"
        assert fhir_dict["intent"] == "order"
        assert fhir_dict["priority"] == "urgent"

        # Check payload
        assert len(fhir_dict["payload"]) == 1
        assert (
            fhir_dict["payload"][0]["contentString"]
            == "Patient presents with chest pain, recommend ECG."
        )

        # Check extensions
        extensions = fhir_dict["extension"]
        confidence_ext = next(
            ext for ext in extensions if "confidence-score" in ext["url"]
        )
        memory_ext = next(ext for ext in extensions if "memory-handles" in ext["url"])

        assert confidence_ext["valueDecimal"] == 0.95
        assert memory_ext["valueString"] == "memory-001,memory-002"

    def test_fhir_to_agent_message(self):
        """Test FHIR CommunicationRequest to AgentMessage mapping."""
        fhir_dict = {
            "resourceType": "CommunicationRequest",
            "id": "msg-002",
            "status": "active",
            "intent": "order",
            "priority": "stat",
            "payload": [{"contentString": "Blood pressure elevated, monitor closely."}],
            "extension": [
                {
                    "url": "http://hacs.dev/fhir/StructureDefinition/confidence-score",
                    "valueDecimal": 0.87,
                },
                {
                    "url": "http://hacs.dev/fhir/StructureDefinition/memory-handles",
                    "valueString": "memory-003,memory-004",
                },
            ],
        }

        message = from_fhir(fhir_dict)

        assert isinstance(message, AgentMessage)
        assert message.id == "msg-002"
        assert message.role == MessageRole.ASSISTANT
        assert message.content == "Blood pressure elevated, monitor closely."
        assert message.priority == MessagePriority.CRITICAL
        assert message.confidence_score == 0.87
        assert message.memory_handles == ["memory-003", "memory-004"]


class TestEncounterFHIRMapping:
    """Test Encounter ↔ FHIR Encounter mapping."""

    def test_encounter_to_fhir(self):
        """Test Encounter to FHIR mapping."""
        encounter = _create_encounter(
            id="enc-001",
            status=EncounterStatus.FINISHED,
            encounter_class=EncounterClass.AMB,
            subject="patient-001",
            period={"start": "2024-01-15T09:00:00Z", "end": "2024-01-15T10:30:00Z"},
        )

        fhir_dict = to_fhir(encounter)

        assert fhir_dict["resourceType"] == "Encounter"
        assert fhir_dict["id"] == "enc-001"
        assert fhir_dict["status"] == "finished"
        assert fhir_dict["class"]["code"] == "AMB"
        assert fhir_dict["subject"]["reference"] == "Patient/patient-001"
        assert fhir_dict["period"]["start"] == "2024-01-15T09:00:00Z"

    def test_encounter_round_trip(self):
        """Test Encounter round-trip preservation."""
        original_encounter = _create_encounter(
            id="enc-round-trip",
            status=EncounterStatus.IN_PROGRESS,
            encounter_class=EncounterClass.IMP,
            subject="patient-123",
            period={"start": "2024-01-20T08:00:00Z"},
        )

        # Round trip
        fhir_dict = to_fhir(original_encounter)
        reconstructed_encounter = from_fhir(fhir_dict)

        assert isinstance(reconstructed_encounter, Encounter)
        assert reconstructed_encounter.id == original_encounter.id
        assert reconstructed_encounter.status == original_encounter.status
        assert reconstructed_encounter.class_fhir == original_encounter.class_fhir
        assert reconstructed_encounter.subject == original_encounter.subject


class TestObservationFHIRMapping:
    """Test Observation ↔ FHIR Observation mapping."""

    def test_observation_to_fhir_vital_sign(self):
        """Test Observation (vital sign) to FHIR mapping."""
        observation = Observation(
            id="obs-001",
            status=ObservationStatus.FINAL,
            category=[
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                            "code": "vital-signs",
                            "display": "Vital Signs",
                        }
                    ]
                }
            ],
            code={
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": "8480-6",
                        "display": "Systolic blood pressure",
                    }
                ]
            },
            subject="patient-001",
            effective_datetime=datetime(2024, 1, 15, 9, 15, 0, tzinfo=timezone.utc),
            value_quantity={
                "value": 140,
                "unit": "mmHg",
                "system": "http://unitsofmeasure.org",
                "code": "mm[Hg]",
            },
        )

        fhir_dict = to_fhir(observation)

        assert fhir_dict["resourceType"] == "Observation"
        assert fhir_dict["id"] == "obs-001"
        assert fhir_dict["status"] == "final"
        assert fhir_dict["subject"]["reference"] == "Patient/patient-001"
        assert fhir_dict["effectiveDateTime"] == "2024-01-15T09:15:00+00:00"

        # Check code
        assert fhir_dict["code"]["coding"][0]["code"] == "8480-6"
        assert fhir_dict["code"]["coding"][0]["system"] == "http://loinc.org"

        # Check value
        assert fhir_dict["valueQuantity"]["value"] == 140
        assert fhir_dict["valueQuantity"]["unit"] == "mmHg"

    def test_observation_with_components(self):
        """Test Observation with components mapping."""
        observation = Observation(
            id="obs-bp-001",
            status=ObservationStatus.FINAL,
            code={
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": "85354-9",
                        "display": "Blood pressure panel",
                    }
                ]
            },
            subject="patient-001",
            effective_datetime=datetime(2024, 1, 15, 9, 15, 0, tzinfo=timezone.utc),
            data_absent_reason=DataAbsentReason.NOT_APPLICABLE,
            component=[
                {
                    "code": {
                        "coding": [
                            {
                                "system": "http://loinc.org",
                                "code": "8480-6",
                                "display": "Systolic blood pressure",
                            }
                        ]
                    },
                    "valueQuantity": {
                        "value": 140,
                        "unit": "mmHg",
                        "system": "http://unitsofmeasure.org",
                        "code": "mm[Hg]",
                    },
                },
                {
                    "code": {
                        "coding": [
                            {
                                "system": "http://loinc.org",
                                "code": "8462-4",
                                "display": "Diastolic blood pressure",
                            }
                        ]
                    },
                    "valueQuantity": {
                        "value": 90,
                        "unit": "mmHg",
                        "system": "http://unitsofmeasure.org",
                        "code": "mm[Hg]",
                    },
                },
            ],
        )

        fhir_dict = to_fhir(observation)

        assert len(fhir_dict["component"]) == 2
        assert fhir_dict["component"][0]["valueQuantity"]["value"] == 140
        assert fhir_dict["component"][1]["valueQuantity"]["value"] == 90

    def test_observation_round_trip(self):
        """Test Observation round-trip preservation."""
        original_obs = Observation(
            id="obs-round-trip",
            status=ObservationStatus.FINAL,
            code={
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": "33747-0",
                        "display": "General appearance",
                    }
                ]
            },
            subject="patient-001",
            effective_datetime=datetime(2024, 1, 15, 10, 0, 0, tzinfo=timezone.utc),
            value_string="Patient appears well",
        )

        # Round trip
        fhir_dict = to_fhir(original_obs)
        reconstructed_obs = from_fhir(fhir_dict)

        assert isinstance(reconstructed_obs, Observation)
        assert reconstructed_obs.id == original_obs.id
        assert reconstructed_obs.status == original_obs.status
        assert reconstructed_obs.subject == original_obs.subject
        assert reconstructed_obs.value_string == original_obs.value_string
        assert reconstructed_obs.effective_datetime == original_obs.effective_datetime


class TestEvidenceCitationMapping:
    """Test Evidence ↔ FHIR Citation mapping."""

    def test_evidence_to_citation(self):
        """Test Evidence to FHIR Citation mapping."""
        evidence = Evidence(
            id="evidence-001",
            evidence_type=EvidenceType.RESEARCH_PAPER,
            citation="Smith J, et al. Hypertension Guidelines. NEJM. 2024.",
            content="ACE inhibitors recommended as first-line therapy.",
            confidence_score=0.95,
            quality_score=0.9,
            vector_id="vec_abc123",
        )

        fhir_dict = to_fhir(evidence)

        assert fhir_dict["resourceType"] == "Citation"
        assert fhir_dict["id"] == "evidence-001"
        assert fhir_dict["status"] == "active"

        # Check cited artifact
        cited_artifact = fhir_dict["citedArtifact"]
        assert (
            cited_artifact["title"]
            == "Smith J, et al. Hypertension Guidelines. NEJM. 2024."
        )

        # Check summary
        assert len(fhir_dict["summary"]) == 1
        assert (
            fhir_dict["summary"][0]["text"]
            == "ACE inhibitors recommended as first-line therapy."
        )

    def test_citation_to_evidence(self):
        """Test FHIR Citation to Evidence mapping."""
        fhir_dict = {
            "resourceType": "Citation",
            "id": "citation-001",
            "status": "active",
            "citedArtifact": {
                "title": "Jones A, et al. Diabetes Treatment Protocol. Diabetes Care. 2024;47(2):234-245.",
                "type": {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/citation-artifact-classifier",
                            "code": "clinical-note",
                        }
                    ]
                },
            },
            "summary": [
                {
                    "type": {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/citation-summary-style",
                                "code": "narrative",
                            }
                        ]
                    },
                    "text": "Metformin remains first-line therapy for type 2 diabetes mellitus.",
                }
            ],
            "extension": [
                {
                    "url": "http://hacs.dev/fhir/StructureDefinition/confidence-score",
                    "valueDecimal": 0.88,
                },
                {
                    "url": "http://hacs.dev/fhir/StructureDefinition/vector-id",
                    "valueString": "vec_def456",
                },
            ],
        }

        evidence = from_fhir(fhir_dict)

        assert isinstance(evidence, Evidence)
        assert evidence.id == "citation-001"
        assert evidence.evidence_type == EvidenceType.CLINICAL_NOTE
        assert (
            evidence.citation
            == "Jones A, et al. Diabetes Treatment Protocol. Diabetes Care. 2024;47(2):234-245."
        )
        assert (
            evidence.content
            == "Metformin remains first-line therapy for type 2 diabetes mellitus."
        )
        assert evidence.confidence_score == 0.88
        assert evidence.vector_id == "vec_def456"

    def test_evidence_citation_round_trip(self):
        """Test Evidence → Citation → Evidence round-trip preservation."""
        original_evidence = Evidence(
            id="evidence-round-trip",
            evidence_type=EvidenceType.GUIDELINE,
            citation="WHO Guidelines on CVD Prevention. 2024.",
            content="Regular exercise reduces CVD risk by 30-50%.",
            confidence_score=0.92,
        )

        # Round trip
        fhir_dict = to_fhir(original_evidence)
        reconstructed_evidence = from_fhir(fhir_dict)

        assert isinstance(reconstructed_evidence, Evidence)
        assert reconstructed_evidence.id == original_evidence.id
        assert reconstructed_evidence.citation == original_evidence.citation
        assert reconstructed_evidence.content == original_evidence.content
        assert (
            reconstructed_evidence.confidence_score
            == original_evidence.confidence_score
        )


class TestActorPractitionerMapping:
    """Test Actor ↔ FHIR Practitioner mapping."""

    def test_actor_to_practitioner(self):
        """Test Actor to FHIR Practitioner mapping."""
        actor = Actor(
            id="actor-001",
            name="Dr. Sarah Johnson",
            role=ActorRole.PHYSICIAN,
            is_active=True,
        )

        fhir_dict = to_fhir(actor)

        assert fhir_dict["resourceType"] == "Practitioner"
        assert fhir_dict["id"] == "actor-001"
        assert fhir_dict["active"] is True
        assert fhir_dict["name"][0]["text"] == "Dr. Sarah Johnson"
        assert fhir_dict["qualification"][0]["code"]["coding"][0]["code"] == "physician"

    def test_practitioner_to_actor(self):
        """Test FHIR Practitioner to Actor mapping."""
        fhir_dict = {
            "resourceType": "Practitioner",
            "id": "pract-001",
            "active": True,
            "name": [
                {"use": "official", "family": "Smith", "given": ["John", "Michael"]}
            ],
            "qualification": [
                {
                    "code": {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/v2-0360",
                                "code": "nurse",
                            }
                        ]
                    }
                }
            ],
        }

        actor = from_fhir(fhir_dict)

        assert isinstance(actor, Actor)
        assert actor.id == "pract-001"
        assert actor.is_active is True
        assert actor.name == "John Michael Smith"
        assert actor.role == ActorRole.NURSE


class TestFHIRValidation:
    """Test FHIR compliance validation."""

    def test_validate_patient_compliance(self):
        """Test Patient FHIR compliance validation."""
        patient = Patient(
            id="patient-valid",
            given=["Test"],
            family="Patient",
            gender=AdministrativeGender.FEMALE,
            active=True,
        )

        errors = validate_fhir_compliance(patient)
        # Note: May have errors due to missing fhir.resources, but should not crash
        assert isinstance(errors, list)

    def test_validate_observation_compliance(self):
        """Test Observation FHIR compliance validation."""
        observation = Observation(
            id="obs-valid",
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
            subject="patient-001",
            value_quantity={
                "value": 120,
                "unit": "mmHg",
                "system": "http://unitsofmeasure.org",
                "code": "mm[Hg]",
            },
        )

        errors = validate_fhir_compliance(observation)
        assert len(errors) == 0  # Should be valid

    def test_unsupported_resource_type(self):
        """Test error handling for unsupported resource types."""

        # Create a mock resource with unsupported type
        class UnsupportedResource(BaseResource):
            resource_type: str = "UnsupportedType"

        unsupported = UnsupportedResource(id="unsupported-001")

        with pytest.raises(FHIRMappingError) as exc_info:
            to_fhir(unsupported)

        assert "No FHIR mapping available" in str(exc_info.value)


class TestFHIRCodeValidation:
    """Test FHIR code system validation."""

    def test_observation_loinc_validation(self):
        """Test LOINC code validation in observations."""
        observation = Observation(
            id="obs-loinc",
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
            subject="patient-001",
            value_quantity={"value": 120, "unit": "mmHg"},
        )

        assert observation.is_loinc_code() is True
        assert observation.is_snomed_code() is False
        assert observation.validate_code_system("http://loinc.org") is True

    def test_observation_snomed_validation(self):
        """Test SNOMED CT code validation in observations."""
        observation = Observation(
            id="obs-snomed",
            status=ObservationStatus.FINAL,
            code={
                "coding": [
                    {
                        "system": "http://snomed.info/sct",
                        "code": "271649006",
                        "display": "Systolic blood pressure",
                    }
                ]
            },
            subject="patient-001",
            value_quantity={"value": 120, "unit": "mmHg"},
        )

        assert observation.is_snomed_code() is True
        assert observation.is_loinc_code() is False
        assert observation.validate_code_system("http://snomed.info/sct") is True


if __name__ == "__main__":
    pytest.main([__file__])
