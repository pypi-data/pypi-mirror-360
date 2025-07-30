# HACS Models Module

The `hacs-models` package provides healthcare-specific data models that extend the core HACS foundation. These models are designed for clinical workflows, agent communication, and healthcare data management with full FHIR compliance.

## 📦 Package Overview

```
hacs-models/
├── src/hacs_models/
│   ├── __init__.py          # Public API exports
│   ├── patient.py          # Patient demographics and identifiers
│   ├── agent_message.py    # Agent communication model
│   ├── encounter.py        # Healthcare encounters
│   ├── observation.py      # Clinical observations
│   └── py.typed            # Type hints marker
└── pyproject.toml          # Package configuration
```

## 🏥 Clinical Models

### Patient

Comprehensive patient demographics with agent-centric features and FHIR compliance.

```python
from hacs_models import Patient
from datetime import date

# Create a comprehensive patient record
patient = Patient(
    id="patient-001",
    given=["Ana", "Maria"],
    family="Silva",
    gender="female",
    birth_date=date(1985, 3, 15),
    active=True,
    identifiers=[
        {
            "system": "http://hospital.org/mrn",
            "value": "MRN12345",
            "type": "MR"
        },
        {
            "system": "http://hl7.org/fhir/sid/us-ssn",
            "value": "123-45-6789",
            "type": "SS"
        }
    ],
    telecom=[
        {
            "system": "phone",
            "value": "+1-555-0123",
            "use": "home"
        },
        {
            "system": "email",
            "value": "ana.silva@email.com",
            "use": "home"
        }
    ],
    address=[
        {
            "use": "home",
            "line": ["123 Main Street", "Apt 4B"],
            "city": "Springfield",
            "state": "IL",
            "postal_code": "62701",
            "country": "US"
        }
    ],
    marital_status="married",
    language="en-US",
    care_team=[
        {
            "role": "primary_care_physician",
            "provider_id": "dr-smith-001",
            "provider_name": "Dr. Emily Smith"
        }
    ],
    agent_context={
        "preferred_communication": "email",
        "health_concerns": ["hypertension", "diabetes_risk"],
        "care_preferences": {
            "appointment_time": "morning",
            "communication_frequency": "weekly"
        }
    }
)

print(f"Patient: {patient.display_name}")
print(f"Age: {patient.age_years} years")
print(f"Primary ID: {patient.primary_identifier}")
print(f"Active: {patient.active}")
```

#### Key Features
- **21 comprehensive fields** covering demographics, contact, and clinical context
- **Age calculation** with automatic computation from birth date
- **Identifier management** with primary identifier selection
- **Contact information** with telecom and address validation
- **Care team tracking** with provider relationships
- **Agent context** for AI-specific metadata
- **FHIR compliance** with proper enums and validation

#### Patient Methods
```python
# Age calculation
print(f"Age in years: {patient.age_years}")
print(f"Age in days: {patient.age_days}")

# Identifier management
patient.add_identifier("http://hospital.org/account", "ACC789", "AN")
primary_id = patient.get_primary_identifier()

# Contact methods
patient.add_telecom("phone", "+1-555-9876", "work")
patient.add_address("work", ["456 Business Ave"], "Springfield", "IL", "62702")

# Care team management
patient.add_care_team_member("cardiologist", "dr-jones-002", "Dr. Michael Jones")

# Display utilities
print(f"Full name: {patient.display_name}")
print(f"Contact summary: {patient.contact_summary}")
```

### AgentMessage

Sophisticated agent communication model with memory integration and clinical context.

```python
from hacs_models import AgentMessage
from datetime import datetime

# Create an agent message with comprehensive metadata
message = AgentMessage(
    id="msg-001",
    role="assistant",
    content="Based on the patient's blood pressure readings (145/90 mmHg), I recommend lifestyle modifications including the DASH diet and regular exercise. Schedule follow-up in 3 months.",
    related_to=["patient-001", "obs-bp-001"],
    confidence_score=0.85,
    urgency_score=0.6,
    memory_handles=[
        "memory-bp-guidelines",
        "memory-patient-history-001"
    ],
    evidence_links=[
        "evidence-aha-bp-2024",
        "evidence-dash-study"
    ],
    reasoning_trace=[
        "Analyzed patient BP readings over 3 visits",
        "Consulted AHA guidelines for stage 1 hypertension",
        "Considered patient's lifestyle factors and preferences",
        "Recommended evidence-based interventions"
    ],
    tool_calls=[
        {
            "tool": "calculate_cardiovascular_risk",
            "parameters": {"age": 39, "bp_systolic": 145, "bp_diastolic": 90},
            "result": {"risk_score": 0.12, "risk_category": "low-moderate"}
        }
    ],
    clinical_context={
        "encounter_id": "encounter-001",
        "provider_id": "dr-smith-001",
        "clinical_domain": "cardiology",
        "intervention_type": "lifestyle_modification"
    },
    agent_metadata={
        "model": "gpt-4",
        "temperature": 0.3,
        "tokens_used": 1250,
        "processing_time_ms": 850
    }
)

print(f"Message: {message.content[:100]}...")
print(f"Confidence: {message.confidence_score}")
print(f"Urgency: {message.urgency_level}")
print(f"Memory handles: {len(message.memory_handles)}")
print(f"Evidence links: {len(message.evidence_links)}")
```

#### Key Features
- **24 comprehensive fields** for agent communication
- **Memory integration** with handles to episodic/procedural/executive memory
- **Evidence linking** to clinical guidelines and research
- **Reasoning traces** for explainable AI
- **Tool call tracking** with parameters and results
- **Clinical context** for healthcare-specific metadata
- **Urgency scoring** with automatic level classification
- **Agent metadata** for model performance tracking

#### AgentMessage Methods
```python
# Memory and evidence management
message.add_memory_reference("memory-treatment-plan-001")
message.link_to_evidence("evidence-lifestyle-rct-2023")

# Clinical context
message.link_to_encounter("encounter-001")
message.update_clinical_context({"specialty": "cardiology"})

# Status and workflow
message.mark_as_reviewed()
message.set_deadline(datetime(2024, 2, 1))
message.add_tag("treatment_recommendation")

# Urgency and priority
print(f"Urgency level: {message.urgency_level}")  # low, medium, high, critical
print(f"Is overdue: {message.is_overdue}")
print(f"Priority score: {message.priority_score}")
```

### Encounter

Healthcare encounter model with FHIR workflow and agent integration.

```python
from hacs_models import Encounter
from datetime import datetime

# Create a comprehensive healthcare encounter
encounter = Encounter(
    id="encounter-001",
    status="in-progress",
    class_fhir="ambulatory",
    subject="patient-001",
    period={
        "start": datetime(2024, 1, 15, 9, 0),
        "end": None  # Still in progress
    },
    participants=[
        {
            "type": "PPRF",  # Primary performer
            "individual": "dr-smith-001",
            "name": "Dr. Emily Smith",
            "role": "attending_physician"
        },
        {
            "type": "PART",  # Participant
            "individual": "nurse-johnson-001",
            "name": "Sarah Johnson, RN",
            "role": "nurse"
        }
    ],
    reason_code=[
        {
            "coding": [{
                "system": "http://snomed.info/sct",
                "code": "38341003",
                "display": "Hypertensive disorder"
            }]
        }
    ],
    diagnosis=[
        {
            "condition": "condition-hypertension-001",
            "rank": 1,
            "use": "billing"
        }
    ],
    location=[
        {
            "location": "location-clinic-room-3",
            "status": "active",
            "period": {
                "start": datetime(2024, 1, 15, 9, 0)
            }
        }
    ],
    agent_context={
        "session_id": "agent-session-001",
        "workflow_state": "assessment_complete",
        "ai_assistance_used": True,
        "decision_support_tools": ["bp_calculator", "risk_assessor"]
    }
)

print(f"Encounter: {encounter.id}")
print(f"Status: {encounter.status}")
print(f"Duration: {encounter.duration_minutes} minutes")
print(f"Participants: {len(encounter.participants)}")
```

#### Key Features
- **23 comprehensive fields** for encounter management
- **FHIR-compliant workflow** with proper status transitions
- **Participant management** with roles and relationships
- **Location tracking** with status and time periods
- **Diagnosis coding** with ranking and billing context
- **Agent integration** with session and workflow tracking
- **Duration calculation** for encounter metrics

#### Encounter Methods
```python
# Participant management
encounter.add_participant("SPRF", "dr-jones-002", "Dr. Michael Jones", "consultant")

# Status workflow
encounter.update_status("finished")
encounter.finish_encounter(datetime(2024, 1, 15, 10, 30))

# Agent integration
encounter.link_to_agent_session("agent-session-001")
encounter.update_workflow_state("treatment_planning")

# Classification and metrics
encounter.classify_encounter_type()  # Determines encounter complexity
print(f"Encounter type: {encounter.encounter_type}")
print(f"Duration: {encounter.duration_minutes} minutes")
```

### Observation

Clinical observation model with FHIR compliance and agent-centric features.

```python
from hacs_models import Observation
from datetime import datetime

# Create a comprehensive clinical observation
observation = Observation(
    id="obs-bp-001",
    status="final",
    category=[
        {
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                "code": "vital-signs",
                "display": "Vital Signs"
            }]
        }
    ],
    code={
        "coding": [{
            "system": "http://loinc.org",
            "code": "85354-9",
            "display": "Blood pressure panel with all children optional"
        }]
    },
    subject="patient-001",
    encounter="encounter-001",
    effective_datetime=datetime(2024, 1, 15, 9, 15),
    performer=["dr-smith-001", "nurse-johnson-001"],
    value_quantity=None,  # Complex BP measurement uses components
    component=[
        {
            "code": {
                "coding": [{
                    "system": "http://loinc.org",
                    "code": "8480-6",
                    "display": "Systolic blood pressure"
                }]
            },
            "value_quantity": {
                "value": 145,
                "unit": "mmHg",
                "system": "http://unitsofmeasure.org"
            }
        },
        {
            "code": {
                "coding": [{
                    "system": "http://loinc.org",
                    "code": "8462-4",
                    "display": "Diastolic blood pressure"
                }]
            },
            "value_quantity": {
                "value": 90,
                "unit": "mmHg",
                "system": "http://unitsofmeasure.org"
            }
        }
    ],
    reference_range=[
        {
            "low": {"value": 90, "unit": "mmHg"},
            "high": {"value": 140, "unit": "mmHg"},
            "type": "normal",
            "text": "Normal blood pressure range"
        }
    ],
    interpretation=[
        {
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
                "code": "H",
                "display": "High"
            }]
        }
    ],
    agent_context={
        "measurement_method": "automated_cuff",
        "patient_position": "seated",
        "cuff_size": "adult_regular",
        "measurement_sequence": 2,
        "ai_flagged": True,
        "alert_level": "moderate"
    }
)

print(f"Observation: {observation.display_name}")
print(f"Status: {observation.status}")
print(f"Components: {len(observation.component)}")
print(f"Interpretation: {observation.interpretation_summary}")
```

#### Key Features
- **25+ comprehensive fields** for clinical observations
- **FHIR compliance** with proper coding systems (LOINC, SNOMED CT, UCUM)
- **Component support** for complex measurements
- **Reference ranges** with normal/abnormal flagging
- **Interpretation codes** for clinical significance
- **Agent context** for AI-specific metadata
- **Validation methods** for code systems and units

#### Observation Methods
```python
# Component management
observation.add_component(
    loinc_code="8867-4",
    display="Heart rate",
    value=72,
    unit="beats/min"
)

# Reference range management
observation.set_reference_range(60, 100, "normal", "Normal heart rate")

# Evidence linking
observation.link_to_evidence("evidence-vital-signs-guidelines")

# Validation
if observation.is_loinc_code("8480-6"):
    print("✅ Valid LOINC code")

if observation.is_ucum_unit("mmHg"):
    print("✅ Valid UCUM unit")

# Clinical significance
print(f"Is abnormal: {observation.is_abnormal}")
print(f"Clinical significance: {observation.clinical_significance}")
```

## 🔧 Model Utilities

### JSON Schema Export
```python
from hacs_models import Patient, AgentMessage, Encounter, Observation

# Export schemas for LLM function specifications
patient_schema = Patient.model_json_schema()
message_schema = AgentMessage.model_json_schema()
encounter_schema = Encounter.model_json_schema()
observation_schema = Observation.model_json_schema()

print(f"Patient fields: {len(patient_schema['properties'])}")
print(f"Message fields: {len(message_schema['properties'])}")
print(f"Encounter fields: {len(encounter_schema['properties'])}")
print(f"Observation fields: {len(observation_schema['properties'])}")
```

### Validation Helpers
```python
from pydantic import ValidationError

# Validate model data
try:
    patient = Patient(
        given=["John"],
        family="Doe",
        gender="invalid_gender"  # Will trigger validation error
    )
except ValidationError as e:
    print(f"Validation errors: {e.error_count()}")
    for error in e.errors():
        print(f"Field: {error['loc']}, Error: {error['msg']}")
```

## 🧪 Testing

The models module includes comprehensive validation and testing:

```bash
# Run models module tests
uv run --package hacs-models pytest

# Run with coverage
uv run --package hacs-models pytest --cov=hacs_models

# Run specific model tests
uv run --package hacs-models pytest -k "test_patient"
uv run --package hacs-models pytest -k "test_agent_message"
uv run --package hacs-models pytest -k "test_encounter"
uv run --package hacs-models pytest -k "test_observation"
```

## 📊 Performance Characteristics

The models module is optimized for healthcare workflows:

- **Model Creation**: <2ms for complex models with 25+ fields
- **Validation**: <3ms for comprehensive field validation
- **JSON Schema Generation**: <10ms for all models
- **FHIR Compliance Checking**: <5ms per model
- **Memory Usage**: <1KB per model instance

## 🔗 Integration Patterns

### With HACS Core
```python
from hacs_core import Actor, MemoryBlock, Evidence
from hacs_models import Patient, AgentMessage

# Create clinical workflow
physician = Actor(id="dr-001", name="Dr. Smith", role="physician")
patient = Patient(id="patient-001", given=["John"], family="Doe")

# Link agent message to memory and evidence
message = AgentMessage(
    content="Patient assessment complete",
    memory_handles=["memory-assessment-001"],
    evidence_links=["evidence-guidelines-001"]
)
```

### With HACS FHIR
```python
from hacs_fhir import to_fhir, from_fhir
from hacs_models import Patient

# FHIR round-trip conversion
patient = Patient(given=["Jane"], family="Smith", gender="female")
fhir_patient = to_fhir(patient)
back_to_hacs = from_fhir(fhir_patient)

print(f"Round-trip successful: {patient.id == back_to_hacs.id}")
```

### With Agent Frameworks
```python
# LangGraph state integration
def create_patient_state(patient: Patient) -> dict:
    return {
        "patient_id": patient.id,
        "patient_name": patient.display_name,
        "age": patient.age_years,
        "active": patient.active
    }

# CrewAI task integration
def create_assessment_task(message: AgentMessage) -> dict:
    return {
        "task_id": message.id,
        "content": message.content,
        "confidence": message.confidence_score,
        "urgency": message.urgency_level
    }
```

## 🚀 Best Practices

### Patient Data Management
```python
# Use comprehensive identifiers
patient = Patient(
    identifiers=[
        {"system": "http://hospital.org/mrn", "value": "MRN12345", "type": "MR"},
        {"system": "http://hl7.org/fhir/sid/us-ssn", "value": "123-45-6789", "type": "SS"}
    ]
)

# Include contact information
patient.add_telecom("email", "patient@email.com", "home")
patient.add_address("home", ["123 Main St"], "Springfield", "IL", "62701")
```

### Agent Message Best Practices
```python
# Include comprehensive metadata
message = AgentMessage(
    content="Clinical recommendation",
    confidence_score=0.85,  # Include confidence
    memory_handles=["memory-001"],  # Link to relevant memories
    evidence_links=["evidence-001"],  # Link to supporting evidence
    reasoning_trace=["Step 1", "Step 2"],  # Include reasoning
    clinical_context={"domain": "cardiology"}  # Add clinical context
)
```

### Clinical Observation Standards
```python
# Use proper coding systems
observation = Observation(
    code={
        "coding": [{
            "system": "http://loinc.org",  # Use LOINC for lab/vital signs
            "code": "8480-6",
            "display": "Systolic blood pressure"
        }]
    },
    value_quantity={
        "value": 120,
        "unit": "mmHg",  # Use UCUM units
        "system": "http://unitsofmeasure.org"
    }
)
```

### Encounter Management
```python
# Track encounter lifecycle
encounter = Encounter(
    status="planned",  # Start with planned
    participants=[...],  # Include all participants
    agent_context={
        "workflow_state": "scheduling",
        "ai_assistance": True
    }
)

# Update status as encounter progresses
encounter.update_status("in-progress")
encounter.update_status("finished")
```

## 📚 API Reference

### Patient
- `display_name`: Full name property
- `age_years`: Age in years
- `age_days`: Age in days
- `primary_identifier`: Primary identifier
- `add_identifier()`: Add new identifier
- `add_telecom()`: Add contact information
- `add_care_team_member()`: Add care team member

### AgentMessage
- `urgency_level`: Computed urgency level
- `priority_score`: Combined urgency/confidence score
- `is_overdue`: Check if past deadline
- `add_memory_reference()`: Link to memory
- `link_to_evidence()`: Link to evidence
- `mark_as_reviewed()`: Update review status

### Encounter
- `duration_minutes`: Encounter duration
- `encounter_type`: Computed encounter type
- `add_participant()`: Add participant
- `update_status()`: Update encounter status
- `finish_encounter()`: Complete encounter
- `link_to_agent_session()`: Link to AI session

### Observation
- `display_name`: Observation display name
- `is_abnormal`: Check if outside reference range
- `clinical_significance`: Computed significance
- `add_component()`: Add measurement component
- `link_to_evidence()`: Link to supporting evidence
- `is_loinc_code()`: Validate LOINC code
- `is_ucum_unit()`: Validate UCUM unit

## 🔄 Version History

- **v0.1.0**: Initial release with 4 core clinical models
- **v0.1.1**: Enhanced validation and FHIR compliance
- **v0.1.2**: Added agent-centric features and metadata

## 🤝 Contributing

See the [Contributing Guidelines](../contributing/guidelines.md) for information on how to contribute to the hacs-models module.

---

The `hacs-models` module provides comprehensive healthcare data models that bridge clinical workflows with AI agent capabilities. These models ensure FHIR compliance while enabling sophisticated agent communication and memory integration. 