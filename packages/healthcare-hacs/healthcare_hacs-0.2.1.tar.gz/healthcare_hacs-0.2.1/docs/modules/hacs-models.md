# HACS Models Module

The `hacs-models` package provides healthcare-specific data models that extend the core HACS foundation. These models are designed for clinical workflows, agent communication, and healthcare data management with full FHIR compliance.

**🆕 LLM-Friendly Features**: All models now include `create_simple()` methods, auto-generated IDs, and flexible validation to make them perfect for AI structured output generation.

## 📦 Package Overview

```
hacs-models/
├── src/hacs_models/
│   ├── __init__.py          # Public API exports
│   ├── patient.py          # Patient demographics and identifiers (LLM-friendly)
│   ├── agent_message.py    # Agent communication model
│   ├── encounter.py        # Healthcare encounters
│   ├── observation.py      # Clinical observations (LLM-friendly)
│   └── py.typed            # Type hints marker
└── pyproject.toml          # Package configuration
```

## 🤖 LLM-Friendly Quick Start

### Simple Patient Creation
```python
from hacs_models import Patient

# Create a patient with just a name - everything else is optional
patient = Patient(
    full_name="Dr. Maria Elena Rodriguez-Smith Jr.",
    age=42,
    gender="female",
    phone="555-0123",
    email="maria.rodriguez@email.com"
)

print(f"✅ Created: {patient.display_name}")
print(f"   ID: {patient.id}")           # Auto-generated
print(f"   Given: {patient.given}")     # ["Maria", "Elena"]
print(f"   Family: {patient.family}")   # "Rodriguez-Smith"
print(f"   Prefix: {patient.prefix}")   # ["Dr."]
print(f"   Suffix: {patient.suffix}")   # ["Jr."]
```

### Simple Observation Creation
```python
from hacs_models import Observation

# Create observations with natural language
bp_obs = Observation(
    subject=patient.id,
    code_text="blood pressure",  # Auto-converts to LOINC
    value_numeric=120,
    unit="mmHg",
    interpretation_text="normal"
)

print(f"✅ Created: {bp_obs.display_name}")
print(f"   LOINC Code: {bp_obs.primary_code}")  # Auto-generated
print(f"   Value: {bp_obs.get_numeric_value()} {bp_obs.get_unit()}")
```

### Simple Actor Creation
```python
from hacs_core import Actor

# Create healthcare professionals with auto-generated permissions
doctor = Actor(
    name="Dr. Sarah Johnson",
    role="physician",
    email="sarah.johnson@hospital.com"
)

print(f"✅ Created: {doctor.name}")
print(f"   Permissions: {len(doctor.permissions)} auto-generated")
print(f"   Role: {doctor.display_role}")
```

## 🏥 Clinical Models

### Patient

Comprehensive patient demographics with agent-centric features and FHIR compliance.

#### LLM-Friendly Usage
```python
from hacs_models import Patient

# Simple creation with natural inputs
patient = Patient(
    full_name="John Michael Smith",
    age=45,
    gender="male",
    phone="555-0123",
    email="john.smith@email.com",
    address_text="123 Main St, Springfield, IL 62701",
    language="en"
)

print(f"Patient: {patient.display_name}")
print(f"Age: {patient.age_years} years")
print(f"Contact: {patient.phone}, {patient.email}")
```

#### Traditional Usage
```python
from hacs_models import Patient
from datetime import date

# Create a comprehensive patient record
patient = Patient(
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
        }
    ],
    telecom=[
        {
            "system": "phone",
            "value": "+1-555-0123",
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
- **🤖 LLM-Friendly**: `create_simple()` method with natural language inputs
- **🆔 Auto-Generated IDs**: No need to specify unique identifiers
- **👤 Name Parsing**: Full name auto-parsed into given/family/prefix/suffix
- **📅 Age Calculation**: Age field auto-calculates birth_date
- **📞 Simple Contacts**: Direct phone/email/address fields
- **21 comprehensive fields** covering demographics, contact, and clinical context
- **Age calculation** with automatic computation from birth date
- **Identifier management** with primary identifier selection
- **Contact information** with telecom and address validation
- **Care team tracking** with provider relationships
- **Agent context** for AI-specific metadata
- **FHIR compliance** with proper enums and validation

#### Patient Methods
```python
# LLM-friendly helpers
patient = Patient.create_simple(name="Dr. John Smith Jr.", age=45)

# Age calculation
print(f"Age in years: {patient.age_years}")
print(f"Age in days: {patient.age_days}")

# Name components (auto-parsed)
print(f"Given names: {patient.given}")     # ["John"]
print(f"Family name: {patient.family}")    # "Smith"
print(f"Prefix: {patient.prefix}")         # ["Dr."]
print(f"Suffix: {patient.suffix}")         # ["Jr."]

# Simple contact fields
print(f"Phone: {patient.phone}")
print(f"Email: {patient.email}")
print(f"Address: {patient.address_text}")

# Traditional methods
patient.add_identifier("http://hospital.org/account", "ACC789", "AN")
primary_id = patient.get_primary_identifier()
patient.add_telecom("phone", "+1-555-9876", "work")
patient.add_address("work", ["456 Business Ave"], "Springfield", "IL", "62702")
patient.add_care_team_member("cardiologist", "dr-jones-002", "Dr. Michael Jones")

# Display utilities
print(f"Full name: {patient.display_name}")
print(f"Contact summary: {patient.contact_summary}")
```

### Observation

Clinical observation model with FHIR compliance and LLM-friendly features.

#### LLM-Friendly Usage
```python
from hacs_models import Observation

# Create observations with natural language
bp_obs = Observation.create_simple(
    subject="patient-001",
    observation_type="blood pressure",  # Auto-converts to LOINC
    value=120,
    unit="mmHg",
    interpretation="high",
    note="Patient was sitting during measurement"
)

# Temperature observation
temp_obs = Observation.create_simple(
    subject="patient-001",
    observation_type="body temperature",
    value=98.6,
    unit="F",
    body_site="oral"
)

# Heart rate with simple inputs
hr_obs = Observation.create_simple(
    subject="patient-001",
    observation_type="heart rate",
    value=72,
    unit="beats/min",
    interpretation="normal"
)

print(f"✅ {bp_obs.display_name}: {bp_obs.get_numeric_value()} {bp_obs.get_unit()}")
print(f"✅ {temp_obs.display_name}: {temp_obs.get_numeric_value()}°{temp_obs.get_unit()}")
print(f"✅ {hr_obs.display_name}: {hr_obs.get_numeric_value()} {hr_obs.get_unit()}")
```

#### Traditional Usage
```python
from hacs_models import Observation
from datetime import datetime

# Create a comprehensive clinical observation
observation = Observation(
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
- **🤖 LLM-Friendly**: `create_simple()` method with natural language observation types
- **🆔 Auto-Generated IDs**: No need to specify unique identifiers
- **🏥 Auto-LOINC Mapping**: Common observations auto-convert to LOINC codes
- **📊 Simple Values**: Use `value_numeric + unit` instead of complex `value_quantity`
- **📝 Simple Text Fields**: `code_text`, `interpretation_text`, `note_text`, `body_site_text`
- **25+ comprehensive fields** for clinical observations
- **FHIR compliance** with proper coding systems (LOINC, SNOMED CT, UCUM)
- **Component support** for complex measurements
- **Reference ranges** with normal/abnormal flagging
- **Interpretation codes** for clinical significance
- **Agent context** for AI-specific metadata
- **Validation methods** for code systems and units

#### Observation Methods
```python
# LLM-friendly creation
obs = Observation.create_simple(
    subject="patient-001",
    observation_type="blood pressure",
    value=120,
    unit="mmHg"
)

# Simple value access
print(f"Value: {obs.get_numeric_value()}")
print(f"Unit: {obs.get_unit()}")
print(f"Display: {obs.display_name}")

# Auto-generated LOINC code
print(f"LOINC Code: {obs.primary_code}")

# Traditional component management
obs.add_component(
    loinc_code="8867-4",
    display="Heart rate",
    value=72,
    unit="beats/min"
)

# Reference range management
obs.set_reference_range(60, 100, "normal", "Normal heart rate")

# Evidence linking
obs.link_to_evidence("evidence-vital-signs-guidelines")

# Validation
if obs.is_loinc_code("8480-6"):
    print("✅ Valid LOINC code")

if obs.is_ucum_unit("mmHg"):
    print("✅ Valid UCUM unit")

# Clinical significance
print(f"Is abnormal: {obs.is_abnormal}")
print(f"Clinical significance: {obs.clinical_significance}")
```

### Actor (from hacs-core)

Healthcare professional model with role-based permissions and LLM-friendly features.

#### LLM-Friendly Usage
```python
from hacs_core import Actor

# Create healthcare professionals with auto-generated permissions
doctor = Actor.create_simple(
    name="Dr. Sarah Johnson",
    role="physician",
    email="sarah.johnson@hospital.com",
    phone="555-0456"
)

nurse = Actor.create_simple(
    name="Jennifer Martinez RN",
    role="nurse",
    email="jennifer.martinez@hospital.com"
)

admin = Actor.create_simple(
    name="Michael Chen",
    role="admin",
    email="michael.chen@hospital.com"
)

print(f"✅ Doctor: {doctor.name} ({doctor.display_role})")
print(f"   Permissions: {len(doctor.permissions)} auto-generated")
print(f"   Contact: {doctor.email}, {doctor.phone}")

print(f"✅ Nurse: {nurse.name} ({nurse.display_role})")
print(f"   Permissions: {len(nurse.permissions)} auto-generated")

print(f"✅ Admin: {admin.name} ({admin.display_role})")
print(f"   Permissions: {len(admin.permissions)} auto-generated")
```

#### Traditional Usage
```python
from hacs_core import Actor

# Create with explicit permissions
doctor = Actor(
    name="Dr. Emily Smith",
    role="physician",
    permissions=[
        "read:patient", "write:patient", "delete:patient",
        "read:observation", "write:observation", "delete:observation",
        "read:encounter", "write:encounter", "delete:encounter",
        "read:evidence", "write:evidence",
        "read:memory", "write:memory",
        "execute:clinical_tools"
    ],
    is_active=True,
    contact_info={
        "email": "emily.smith@hospital.com",
        "phone": "+1-555-0123"
    }
)

print(f"Doctor: {doctor.name}")
print(f"Permissions: {len(doctor.permissions)}")
print(f"Active: {doctor.is_active}")
```

#### Key Features
- **🤖 LLM-Friendly**: `create_simple()` method with role-based auto-permissions
- **🆔 Auto-Generated IDs**: No need to specify unique identifiers
- **👔 Role-Based Permissions**: Auto-generates appropriate permissions for role
- **📞 Simple Contacts**: Direct email/phone fields
- **🏥 Display Roles**: Human-readable role names
- **🔐 Permission Levels**: Simple read/write/admin levels
- **Actor-based security** with role validation
- **Session management** for authentication
- **Permission validation** with flexible formats
- **Contact information** management
- **Activity tracking** and audit trails

#### Actor Methods
```python
# LLM-friendly creation
actor = Actor.create_simple(
    name="Dr. John Smith",
    role="physician",
    email="john.smith@hospital.com"
)

# Auto-generated features
print(f"Display role: {actor.display_role}")
print(f"Permission level: {actor.permission_level}")
print(f"Contact: {actor.email}, {actor.phone}")

# Permission checking
if actor.has_permission("read:patient"):
    print("✅ Can read patient data")

if actor.can_write("observation"):
    print("✅ Can write observations")

# Session management
session_id = actor.start_session("session-001")
print(f"Started session: {session_id}")

# Traditional methods
actor.add_permission("execute:special_procedure")
actor.update_contact_info({"phone": "+1-555-9999"})
actor.deactivate()
```

### AgentMessage

Sophisticated agent communication model with memory integration and clinical context.

```python
from hacs_models import AgentMessage
from datetime import datetime

# Create an agent message with comprehensive metadata
message = AgentMessage(
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

### Encounter

Healthcare encounter model with FHIR workflow and agent integration.

```python
from hacs_models import Encounter
from datetime import datetime

# Create a comprehensive healthcare encounter
encounter = Encounter(
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

# LLM-friendly validation - flexible and guides completion
try:
    patient = Patient.create_simple(
        name="John Doe",
        age=30
        # Missing fields will be auto-completed or use defaults
    )
    print(f"✅ Patient created: {patient.display_name}")
except ValidationError as e:
    print(f"❌ Validation errors: {e.error_count()}")
    for error in e.errors():
        print(f"Field: {error['loc']}, Error: {error['msg']}")

# Traditional validation - strict requirements
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

# Test LLM-friendly features specifically
uv run python tests/test_llm_friendly.py

# Run with coverage
uv run --package hacs-models pytest --cov=hacs_models

# Run specific model tests
uv run --package hacs-models pytest -k "test_patient"
uv run --package hacs-models pytest -k "test_agent_message"
uv run --package hacs-models pytest -k "test_encounter"
uv run --package hacs-models pytest -k "test_observation"
```

## 🔍 LLM-Friendly vs Traditional Comparison

| Feature | LLM-Friendly | Traditional |
|---------|-------------|-------------|
| **Patient Creation** | `Patient.create_simple(name="John Doe", age=30)` | `Patient(given=["John"], family="Doe", birth_date="1994-01-01")` |
| **Observation** | `Observation.create_simple(observation_type="blood pressure", value=120)` | `Observation(code={"coding": [{"system": "http://loinc.org", "code": "8480-6"}]}, value_quantity={"value": 120})` |
| **Actor Setup** | `Actor.create_simple(name="Dr. Smith", role="physician")` | `Actor(name="Dr. Smith", role="physician", permissions=["read:patient", "write:patient", ...])` |
| **ID Management** | Auto-generated UUIDs | Manual specification required |
| **Validation** | Flexible, guides completion | Strict, requires all fields |
| **Learning Curve** | Minimal - natural language | Moderate - requires FHIR knowledge |
| **FHIR Compliance** | Automatic conversion | Manual coding required |
| **Error Handling** | Graceful defaults | Strict validation errors |

## 🎯 When to Use Which Approach

### Use LLM-Friendly When:
- Building AI agents that generate structured output
- Rapid prototyping and development
- Working with partial or incomplete data
- Simplifying complex healthcare workflows
- Training non-healthcare developers
- Need automatic LOINC/SNOMED code generation

### Use Traditional When:
- Full control over FHIR compliance is required
- Working with existing healthcare systems
- Regulatory compliance requires specific field validation
- Building enterprise healthcare applications
- Maximum performance is critical
- Need precise control over medical coding

---

Both approaches are production-ready and maintain full FHIR compliance. The LLM-friendly approach provides smart defaults and auto-completion to make healthcare AI development more accessible while preserving all the power and flexibility of the traditional approach. 