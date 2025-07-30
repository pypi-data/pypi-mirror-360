"""
Tests for HACS models package.

Tests the Patient, AgentMessage, and Encounter models to ensure proper functionality,
validation, business logic, and FHIR compliance.
"""

import pytest
from datetime import date, datetime, timezone, timedelta
from pydantic import ValidationError

from hacs_models import (
    Patient,
    AdministrativeGender,
    AgentMessage,
    MessageRole,
    MessageType,
    MessagePriority,
    Encounter,
    EncounterStatus,
    EncounterClass,
)


def _create_encounter(**kwargs) -> Encounter:
    """Helper function to create Encounter with proper class field handling."""
    encounter_class = kwargs.pop("encounter_class", EncounterClass.AMB)
    encounter_data = {"class": encounter_class, **kwargs}
    return Encounter(**encounter_data)


class TestPatient:
    """Test cases for Patient class."""

    def test_basic_instantiation(self):
        """Test basic patient creation."""
        patient = Patient(
            id="patient-001",
            given=["John", "Michael"],
            family="Smith",
            gender=AdministrativeGender.MALE,
            birth_date=date(1985, 3, 15),
        )

        assert patient.resource_type == "Patient"
        assert patient.id == "patient-001"
        assert patient.given == ["John", "Michael"]
        assert patient.family == "Smith"
        assert patient.gender == AdministrativeGender.MALE
        assert patient.birth_date == date(1985, 3, 15)
        assert patient.active is True
        assert patient.deceased is False

    def test_computed_fields(self):
        """Test computed fields for names and age."""
        patient = Patient(
            id="patient-002",
            given=["Dr.", "Sarah", "Jane"],
            family="Johnson",
            prefix=["Dr."],
            suffix=["MD", "PhD"],
            gender=AdministrativeGender.FEMALE,
            birth_date=date(1990, 6, 20),
        )

        assert patient.full_name == "Dr. Dr. Sarah Jane Johnson MD PhD"
        assert patient.display_name == "Dr. Sarah Jane Johnson"
        assert patient.age_years is not None
        assert patient.age_years >= 30  # Should be around 34 in 2024

    def test_name_validation(self):
        """Test name validation."""
        # Empty given names should fail
        with pytest.raises(
            ValueError, match="At least one given name must be provided"
        ):
            Patient(
                id="patient-invalid",
                given=[],
                family="Smith",
                gender=AdministrativeGender.MALE,
            )

        # Empty family name should fail
        with pytest.raises(ValueError, match="Family name cannot be empty"):
            Patient(
                id="patient-invalid",
                given=["John"],
                family="",
                gender=AdministrativeGender.MALE,
            )

    def test_identifier_management(self):
        """Test identifier management."""
        patient = Patient(
            id="patient-003",
            given=["Alice"],
            family="Brown",
            gender=AdministrativeGender.FEMALE,
        )

        # Add identifier
        patient.add_identifier(
            value="123456789",
            type_code="MR",
            use="usual",
            system="http://hospital.example.com/mrn",
            assigner="Example Hospital",
        )

        assert len(patient.identifiers) == 1
        identifier = patient.identifiers[0]
        assert identifier["value"] == "123456789"
        assert identifier["type"] == "MR"
        assert identifier["use"] == "usual"

        # Get primary identifier
        primary = patient.get_primary_identifier()
        assert primary == identifier

        # Get identifier by type
        mr_identifier = patient.get_identifier_by_type("MR")
        assert mr_identifier == identifier

        # Non-existent type
        ssn_identifier = patient.get_identifier_by_type("SSN")
        assert ssn_identifier is None

    def test_telecom_management(self):
        """Test contact point management."""
        patient = Patient(
            id="patient-004",
            given=["Bob"],
            family="Wilson",
            gender=AdministrativeGender.MALE,
        )

        # Add phone number
        patient.add_telecom("phone", "+1-555-0123", "home")

        # Add email
        patient.add_telecom("email", "bob.wilson@example.com", "home")

        assert len(patient.telecom) == 2

        # Get phone numbers
        phones = patient.get_telecom_by_system("phone")
        assert len(phones) == 1
        assert phones[0]["value"] == "+1-555-0123"

        # Get home contacts
        home_contacts = patient.get_telecom_by_system("email", "home")
        assert len(home_contacts) == 1
        assert home_contacts[0]["value"] == "bob.wilson@example.com"

    def test_care_team_management(self):
        """Test care team management."""
        patient = Patient(
            id="patient-005",
            given=["Carol"],
            family="Davis",
            gender=AdministrativeGender.FEMALE,
        )

        # Add care team members
        patient.add_care_team_member("practitioner-001")
        patient.add_care_team_member("agent-primary-care")

        assert len(patient.care_team) == 2
        assert "practitioner-001" in patient.care_team
        assert "agent-primary-care" in patient.care_team

        # Adding same member should not duplicate
        patient.add_care_team_member("practitioner-001")
        assert len(patient.care_team) == 2

        # Remove care team member
        removed = patient.remove_care_team_member("practitioner-001")
        assert removed is True
        assert len(patient.care_team) == 1
        assert "practitioner-001" not in patient.care_team

        # Removing non-existent member should return False
        removed = patient.remove_care_team_member("non-existent")
        assert removed is False

    def test_agent_context(self):
        """Test agent context management."""
        patient = Patient(
            id="patient-006",
            given=["David"],
            family="Miller",
            gender=AdministrativeGender.MALE,
        )

        # Update agent context
        patient.update_agent_context("last_interaction", "2024-01-15T10:30:00Z")
        patient.update_agent_context("preferred_agent", "primary-care-agent")

        assert patient.agent_context["last_interaction"] == "2024-01-15T10:30:00Z"
        assert patient.agent_context["preferred_agent"] == "primary-care-agent"

    def test_activation_deactivation(self):
        """Test patient activation and deactivation."""
        patient = Patient(
            id="patient-007",
            given=["Eve"],
            family="Taylor",
            gender=AdministrativeGender.FEMALE,
        )

        assert patient.active is True

        # Deactivate patient
        patient.deactivate("moved_to_different_facility")
        assert patient.active is False
        assert (
            patient.agent_context["deactivation_reason"]
            == "moved_to_different_facility"
        )

        # Activate patient
        patient.activate()
        assert patient.active is True
        assert "deactivation_reason" not in patient.agent_context

    def test_age_calculation(self):
        """Test age calculation methods."""
        patient = Patient(
            id="patient-008",
            given=["Frank"],
            family="Anderson",
            gender=AdministrativeGender.MALE,
            birth_date=date(1980, 12, 25),
        )

        # Calculate age as of specific date
        age_2024 = patient.calculate_age(date(2024, 1, 1))
        assert age_2024 == 43  # Not yet birthday in 2024

        age_after_birthday = patient.calculate_age(date(2024, 12, 26))
        assert age_after_birthday == 44  # After birthday in 2024

        # Test with no birth date
        patient_no_birth = Patient(
            id="patient-no-birth",
            given=["Test"],
            family="Patient",
            gender=AdministrativeGender.UNKNOWN,
        )
        assert patient_no_birth.calculate_age() is None

    def test_patient_repr(self):
        """Test Patient __repr__ method."""
        patient = Patient(
            id="patient-repr",
            given=["Test"],
            family="Patient",
            gender=AdministrativeGender.MALE,
            birth_date=date(1990, 1, 1),
        )

        repr_str = repr(patient)
        assert "Patient" in repr_str
        assert "patient-repr" in repr_str
        assert "Test Patient" in repr_str
        assert "male" in repr_str
        assert "active" in repr_str


class TestAgentMessage:
    """Test cases for AgentMessage class."""

    def test_basic_instantiation(self):
        """Test basic agent message creation."""
        message = AgentMessage(
            id="message-001",
            role=MessageRole.ASSISTANT,
            content="Patient presents with chest pain and shortness of breath.",
            message_type=MessageType.CLINICAL_NOTE,
            priority=MessagePriority.HIGH,
        )

        assert message.resource_type == "AgentMessage"
        assert message.id == "message-001"
        assert message.role == MessageRole.ASSISTANT
        assert (
            message.content
            == "Patient presents with chest pain and shortness of breath."
        )
        assert message.message_type == MessageType.CLINICAL_NOTE
        assert message.priority == MessagePriority.HIGH
        assert message.confidence_score == 0.8  # default
        assert message.status == "sent"  # default

    def test_computed_fields(self):
        """Test computed fields for message analysis."""
        clinical_message = AgentMessage(
            id="message-clinical",
            role=MessageRole.PHYSICIAN,
            content="Patient shows elevated blood pressure and requires medication adjustment.",
            priority=MessagePriority.HIGH,
        )

        assert (
            clinical_message.word_count == 9
        )  # Actual count: "Patient shows elevated blood pressure and requires medication adjustment."
        assert clinical_message.has_clinical_content is True
        assert clinical_message.urgency_score >= 0.7  # High priority + clinical content

        non_clinical_message = AgentMessage(
            id="message-non-clinical",
            role=MessageRole.USER,
            content="Hello, how are you today?",
            priority=MessagePriority.LOW,
        )

        assert non_clinical_message.has_clinical_content is False
        assert (
            non_clinical_message.urgency_score <= 0.3
        )  # Low priority + no clinical content

    def test_content_validation(self):
        """Test content validation."""
        # Empty content should fail
        with pytest.raises(ValueError, match="Message content cannot be empty"):
            AgentMessage(id="message-empty", role=MessageRole.ASSISTANT, content="")

    def test_confidence_score_validation(self):
        """Test confidence score validation."""
        # Valid confidence score
        message = AgentMessage(
            id="message-valid",
            role=MessageRole.ASSISTANT,
            content="Test message",
            confidence_score=0.95,
        )
        assert message.confidence_score == 0.95

        # Invalid confidence score should fail
        with pytest.raises(ValueError):
            AgentMessage(
                id="message-invalid",
                role=MessageRole.ASSISTANT,
                content="Test message",
                confidence_score=1.5,
            )

    def test_memory_reference_management(self):
        """Test memory reference management."""
        message = AgentMessage(
            id="message-memory",
            role=MessageRole.AGENT,
            content="Based on previous interactions, recommend cardiology consultation.",
        )

        # Add memory references
        message.add_memory_reference("memory-001")
        message.add_memory_reference("memory-episodic-123")

        assert len(message.memory_handles) == 2
        assert "memory-001" in message.memory_handles
        assert "memory-episodic-123" in message.memory_handles

        # Remove memory reference
        removed = message.remove_memory_reference("memory-001")
        assert removed is True
        assert len(message.memory_handles) == 1
        assert "memory-001" not in message.memory_handles

        # Removing non-existent reference should return False
        removed = message.remove_memory_reference("non-existent")
        assert removed is False

    def test_evidence_linking(self):
        """Test evidence linking."""
        message = AgentMessage(
            id="message-evidence",
            role=MessageRole.PHYSICIAN,
            content="According to recent guidelines, this treatment is recommended.",
        )

        # Link to evidence
        message.link_to_evidence("evidence-guideline-001")
        message.link_to_evidence("evidence-study-002")

        assert len(message.evidence_references) == 2
        assert "evidence-guideline-001" in message.evidence_references
        assert "evidence-study-002" in message.evidence_references

    def test_encounter_linking(self):
        """Test encounter linking."""
        message = AgentMessage(
            id="message-encounter",
            role=MessageRole.NURSE,
            content="Patient vitals recorded during encounter.",
        )

        # Link to encounter
        message.link_to_encounter("encounter-001")

        assert "encounter-001" in message.related_to

    def test_tool_call_tracking(self):
        """Test tool call tracking."""
        message = AgentMessage(
            id="message-tools",
            role=MessageRole.AGENT,
            content="Retrieved patient guidelines and lab results.",
        )

        # Add tool call
        message.add_tool_call(
            tool_name="search_guidelines",
            parameters={"condition": "hypertension", "age_group": "adult"},
            result_summary="Found 3 relevant guidelines",
            execution_time_ms=450,
        )

        assert len(message.tool_calls) == 1
        tool_call = message.tool_calls[0]
        assert tool_call["tool_name"] == "search_guidelines"
        assert tool_call["parameters"]["condition"] == "hypertension"
        assert tool_call["result_summary"] == "Found 3 relevant guidelines"
        assert tool_call["execution_time_ms"] == 450

    def test_reasoning_trace(self):
        """Test reasoning trace functionality."""
        message = AgentMessage(
            id="message-reasoning",
            role=MessageRole.AGENT,
            content="Differential diagnosis suggests cardiac vs. pulmonary causes.",
        )

        # Add reasoning steps
        message.add_reasoning_step(
            step_type="information_gathering",
            description="Retrieved patient history and current symptoms",
            confidence=0.9,
        )

        message.add_reasoning_step(
            step_type="differential_diagnosis",
            description="Considered cardiac vs. pulmonary causes",
            confidence=0.8,
        )

        assert len(message.reasoning_trace) == 2
        assert message.reasoning_trace[0]["step"] == 1
        assert message.reasoning_trace[1]["step"] == 2

        # Test average confidence
        avg_confidence = message.get_average_reasoning_confidence()
        assert (
            abs(avg_confidence - 0.85) < 0.001
        )  # (0.9 + 0.8) / 2, with floating point tolerance

    def test_tag_management(self):
        """Test tag management."""
        message = AgentMessage(
            id="message-tags",
            role=MessageRole.PHYSICIAN,
            content="Cardiology assessment completed.",
        )

        # Add tags
        message.add_tag("Cardiology")
        message.add_tag("ASSESSMENT")  # Should be normalized to lowercase

        assert "cardiology" in message.tags
        assert "assessment" in message.tags

        # Adding same tag should not duplicate
        message.add_tag("cardiology")
        assert message.tags.count("cardiology") == 1

        # Remove tag
        removed = message.remove_tag("cardiology")
        assert removed is True
        assert "cardiology" not in message.tags

    def test_response_deadline(self):
        """Test response deadline functionality."""
        message = AgentMessage(
            id="message-deadline",
            role=MessageRole.PHYSICIAN,
            content="Urgent consultation needed.",
        )

        # Set response deadline
        deadline = datetime.now(timezone.utc) + timedelta(hours=2)
        message.set_response_deadline(deadline)

        assert message.requires_response is True
        assert message.response_deadline == deadline
        assert not message.is_overdue()

        # Set past deadline
        past_deadline = datetime.now(timezone.utc) - timedelta(hours=1)
        message.set_response_deadline(past_deadline)
        assert message.is_overdue()

    def test_message_repr(self):
        """Test AgentMessage __repr__ method."""
        message = AgentMessage(
            id="message-repr",
            role=MessageRole.AGENT,
            content="This is a test message for representation.",
            message_type=MessageType.ASSESSMENT,
            priority=MessagePriority.URGENT,
        )

        repr_str = repr(message)
        assert "AgentMessage" in repr_str
        assert "message-repr" in repr_str
        assert "agent" in repr_str
        assert "assessment" in repr_str
        assert "🔴" in repr_str or "🟡" in repr_str  # Urgency indicator


class TestEncounter:
    """Test cases for Encounter class."""

    def test_basic_instantiation(self):
        """Test basic encounter creation."""
        encounter = _create_encounter(
            id="encounter-001",
            status=EncounterStatus.IN_PROGRESS,
            encounter_class=EncounterClass.AMB,
            subject="patient-001",
            period={"start": "2024-01-15T09:00:00Z", "end": "2024-01-15T10:30:00Z"},
        )

        assert encounter.resource_type == "Encounter"
        assert encounter.id == "encounter-001"
        assert encounter.status == EncounterStatus.IN_PROGRESS
        assert encounter.class_fhir == EncounterClass.AMB
        assert encounter.subject == "patient-001"
        assert encounter.period["start"] == "2024-01-15T09:00:00Z"

    def test_computed_fields(self):
        """Test computed fields for encounter status and duration."""
        # Active encounter
        active_encounter = _create_encounter(
            id="encounter-active",
            status=EncounterStatus.IN_PROGRESS,
            encounter_class=EncounterClass.EMER,
            subject="patient-001",
            period={"start": "2024-01-15T09:00:00Z"},
        )

        assert active_encounter.is_active is True
        assert active_encounter.is_completed is False
        assert active_encounter.participant_count == 0

        # Completed encounter with duration
        completed_encounter = _create_encounter(
            id="encounter-completed",
            status=EncounterStatus.FINISHED,
            encounter_class=EncounterClass.AMB,
            subject="patient-001",
            period={"start": "2024-01-15T09:00:00Z", "end": "2024-01-15T10:30:00Z"},
        )

        assert completed_encounter.is_completed is True
        assert completed_encounter.duration_minutes == 90.0

    def test_subject_validation(self):
        """Test subject validation."""
        # Empty subject should fail
        with pytest.raises(ValueError, match="Subject \\(patient\\) cannot be empty"):
            _create_encounter(
                id="encounter-invalid",
                status=EncounterStatus.PLANNED,
                encounter_class=EncounterClass.AMB,
                subject="",
                period={"start": "2024-01-15T09:00:00Z"},
            )

    def test_period_validation(self):
        """Test period validation."""
        # Missing start time should fail
        with pytest.raises(ValueError, match="Period must have a 'start' field"):
            _create_encounter(
                id="encounter-invalid",
                status=EncounterStatus.PLANNED,
                encounter_class=EncounterClass.AMB,
                subject="patient-001",
                period={"end": "2024-01-15T10:30:00Z"},
            )

        # End before start should fail
        with pytest.raises(
            ValidationError, match="Encounter end time must be after start time"
        ):
            _create_encounter(
                id="encounter-invalid",
                status=EncounterStatus.PLANNED,
                encounter_class=EncounterClass.AMB,
                subject="patient-001",
                period={"start": "2024-01-15T10:30:00Z", "end": "2024-01-15T09:00:00Z"},
            )

    def test_participant_management(self):
        """Test participant management."""
        encounter = _create_encounter(
            id="encounter-participants",
            status=EncounterStatus.IN_PROGRESS,
            encounter_class=EncounterClass.AMB,
            subject="patient-001",
            period={"start": "2024-01-15T09:00:00Z"},
        )

        # Add participants
        start_time = datetime(2024, 1, 15, 9, 0, 0, tzinfo=timezone.utc)
        encounter.add_participant("attending", "practitioner-001", start_time)
        encounter.add_participant("agent", "agent-primary-care")

        assert len(encounter.participants) == 2
        assert encounter.participant_count == 2

        # Get participants by type
        agents = encounter.get_participants_by_type("agent")
        assert len(agents) == 1
        assert agents[0]["individual"] == "agent-primary-care"

        # Remove participant
        removed = encounter.remove_participant("practitioner-001")
        assert removed is True
        assert len(encounter.participants) == 1

        # Removing non-existent participant should return False
        removed = encounter.remove_participant("non-existent")
        assert removed is False

    def test_status_updates(self):
        """Test status update functionality."""
        encounter = _create_encounter(
            id="encounter-status",
            status=EncounterStatus.PLANNED,
            encounter_class=EncounterClass.AMB,
            subject="patient-001",
            period={"start": "2024-01-15T09:00:00Z"},
        )

        # Update status
        update_time = datetime(2024, 1, 15, 9, 5, 0, tzinfo=timezone.utc)
        encounter.update_status(EncounterStatus.IN_PROGRESS, update_time)

        assert encounter.status == EncounterStatus.IN_PROGRESS
        assert "status_history" in encounter.agent_context
        assert len(encounter.agent_context["status_history"]) == 1

        status_change = encounter.agent_context["status_history"][0]
        assert status_change["from"] == EncounterStatus.PLANNED
        assert status_change["to"] == EncounterStatus.IN_PROGRESS

        # Finish encounter should set end time
        encounter.update_status(EncounterStatus.FINISHED)
        assert "end" in encounter.period

    def test_agent_session_linking(self):
        """Test agent session linking."""
        encounter = _create_encounter(
            id="encounter-agent",
            status=EncounterStatus.IN_PROGRESS,
            encounter_class=EncounterClass.AMB,
            subject="patient-001",
            period={"start": "2024-01-15T09:00:00Z"},
        )

        # Link to agent session
        session_data = {
            "session_type": "consultation",
            "capabilities": ["diagnosis", "treatment_planning"],
        }
        encounter.link_to_agent_session("agent-cardiology", session_data)

        assert "agent_sessions" in encounter.agent_context
        assert len(encounter.agent_context["agent_sessions"]) == 1

        session = encounter.agent_context["agent_sessions"][0]
        assert session["agent_id"] == "agent-cardiology"
        assert session["session_type"] == "consultation"

    def test_primary_agent_management(self):
        """Test primary agent management."""
        encounter = _create_encounter(
            id="encounter-primary",
            status=EncounterStatus.IN_PROGRESS,
            encounter_class=EncounterClass.AMB,
            subject="patient-001",
            period={"start": "2024-01-15T09:00:00Z"},
        )

        # Set primary agent
        encounter.set_primary_agent("agent-primary-care")

        assert encounter.get_primary_agent() == "agent-primary-care"
        assert encounter.agent_context["primary_agent"] == "agent-primary-care"

    def test_diagnosis_management(self):
        """Test diagnosis management."""
        encounter = _create_encounter(
            id="encounter-diagnosis",
            status=EncounterStatus.IN_PROGRESS,
            encounter_class=EncounterClass.AMB,
            subject="patient-001",
            period={"start": "2024-01-15T09:00:00Z"},
        )

        # Add diagnosis
        encounter.add_diagnosis("condition-001", "AD", 1)

        assert len(encounter.diagnosis) == 1
        diagnosis = encounter.diagnosis[0]
        assert diagnosis["condition"] == "condition-001"
        assert diagnosis["rank"] == 1

    def test_location_management(self):
        """Test location management."""
        encounter = _create_encounter(
            id="encounter-location",
            status=EncounterStatus.IN_PROGRESS,
            encounter_class=EncounterClass.AMB,
            subject="patient-001",
            period={"start": "2024-01-15T09:00:00Z"},
        )

        # Add location
        start_time = datetime(2024, 1, 15, 9, 0, 0, tzinfo=timezone.utc)
        encounter.add_location("location-001", start_time=start_time)

        assert len(encounter.location) == 1
        location = encounter.location[0]
        assert location["location"] == "location-001"
        assert location["status"] == "active"

    def test_encounter_classification(self):
        """Test encounter classification methods."""
        # Emergency encounter
        emergency_encounter = _create_encounter(
            id="encounter-emergency",
            status=EncounterStatus.IN_PROGRESS,
            encounter_class=EncounterClass.EMER,
            subject="patient-001",
            period={"start": "2024-01-15T09:00:00Z"},
        )

        assert emergency_encounter.is_emergency() is True
        assert emergency_encounter.is_inpatient() is False

        # Inpatient encounter
        inpatient_encounter = _create_encounter(
            id="encounter-inpatient",
            status=EncounterStatus.IN_PROGRESS,
            encounter_class=EncounterClass.IMP,
            subject="patient-001",
            period={"start": "2024-01-15T09:00:00Z"},
        )

        assert inpatient_encounter.is_emergency() is False
        assert inpatient_encounter.is_inpatient() is True

    def test_duration_calculation(self):
        """Test duration calculation methods."""
        encounter = _create_encounter(
            id="encounter-duration",
            status=EncounterStatus.IN_PROGRESS,
            encounter_class=EncounterClass.AMB,
            subject="patient-001",
            period={"start": "2024-01-15T09:00:00Z", "end": "2024-01-15T10:30:00Z"},
        )

        # Test get_duration method
        duration = encounter.get_duration()
        assert duration == 90.0

        # Test with as_of_time
        as_of_time = datetime(2024, 1, 15, 10, 0, 0, tzinfo=timezone.utc)
        duration_partial = encounter.get_duration(as_of_time)
        assert duration_partial == 60.0

    def test_encounter_repr(self):
        """Test Encounter __repr__ method."""
        encounter = _create_encounter(
            id="encounter-repr",
            status=EncounterStatus.IN_PROGRESS,
            encounter_class=EncounterClass.EMER,
            subject="patient-001",
            period={"start": "2024-01-15T09:00:00Z", "end": "2024-01-15T10:30:00Z"},
        )

        repr_str = repr(encounter)
        assert "Encounter" in repr_str
        assert "encounter-repr" in repr_str
        assert "patient-001" in repr_str
        assert "EMER" in repr_str
        assert "in-progress" in repr_str
        assert "90min" in repr_str
        assert "🟢" in repr_str  # Active status indicator


class TestJSONSchemaGeneration:
    """Test JSON Schema generation for all models."""

    def test_patient_json_schema(self):
        """Test Patient JSON schema generation."""
        schema = Patient.model_json_schema()

        assert schema["type"] == "object"
        assert "properties" in schema
        assert "resource_type" in schema["properties"]
        assert "given" in schema["properties"]
        assert "family" in schema["properties"]
        assert "gender" in schema["properties"]

        # Check enum definitions
        gender_enum = schema["$defs"]["AdministrativeGender"]["enum"]
        assert "male" in gender_enum
        assert "female" in gender_enum

    def test_agent_message_json_schema(self):
        """Test AgentMessage JSON schema generation."""
        schema = AgentMessage.model_json_schema()

        assert schema["type"] == "object"
        assert "properties" in schema
        assert "role" in schema["properties"]
        assert "content" in schema["properties"]
        assert "confidence_score" in schema["properties"]

        # Check confidence score constraints
        confidence_prop = schema["properties"]["confidence_score"]
        assert confidence_prop["minimum"] == 0.0
        assert confidence_prop["maximum"] == 1.0

    def test_encounter_json_schema(self):
        """Test Encounter JSON schema generation."""
        schema = Encounter.model_json_schema()

        assert schema["type"] == "object"
        assert "properties" in schema
        assert "status" in schema["properties"]
        assert "class" in schema["properties"]  # Note: uses alias
        assert "subject" in schema["properties"]
        assert "period" in schema["properties"]
