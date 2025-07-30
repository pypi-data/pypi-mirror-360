# Basic Usage Examples

This guide shows practical examples using HACS for healthcare AI applications. All examples are tested and production-ready.

## 🤖 LLM-Friendly Examples

### Example 1: Simple Patient Creation

The easiest way to create patients with natural inputs:

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

print(f"✅ Created patient: {patient.display_name}")
print(f"   ID: {patient.id}")  # Auto-generated: "patient-a1b2c3d4"
print(f"   Age: {patient.age_years} years")
print(f"   Given: {patient.given}")      # ["Maria", "Elena"]
print(f"   Family: {patient.family}")    # "Rodriguez-Smith"
print(f"   Prefix: {patient.prefix}")    # ["Dr."]
print(f"   Suffix: {patient.suffix}")    # ["Jr."]
```

### Example 2: Simple Observations

Create clinical observations with natural language:

```python
from hacs_models import Observation

# Blood pressure - no complex codes needed!
bp_obs = Observation(
    subject=patient.id,
    code_text="blood pressure",  # Auto-converts to LOINC
    value_numeric=120,
    unit="mmHg",
    interpretation_text="normal"
)

# Temperature with simple text
temp_obs = Observation(
    subject=patient.id,
    code_text="body temperature",
    value_numeric=98.6,
    unit="F",
    note_text="Patient feeling well"
)

# Heart rate
hr_obs = Observation(
    subject=patient.id,
    code_text="heart rate",
    value_numeric=72,
    unit="beats/min",
    body_site_text="wrist"
)

print(f"✅ Created {bp_obs.display_name}: {bp_obs.get_numeric_value()} {bp_obs.get_unit()}")
print(f"✅ Created {temp_obs.display_name}: {temp_obs.get_numeric_value()}°{temp_obs.get_unit()}")
print(f"✅ Created {hr_obs.display_name}: {hr_obs.get_numeric_value()} {hr_obs.get_unit()}")
```

### Example 3: Simple Doctor Setup

Create healthcare professionals with auto-generated permissions:

```python
from hacs_core import Actor

# Create a doctor with role-based permissions
doctor = Actor(
    name="Dr. Sarah Johnson",
    role="physician",
    email="sarah.johnson@hospital.com",
    phone="555-0456"
)

# Create a nurse with different permissions
nurse = Actor(
    name="Jennifer Martinez RN",
    role="nurse",
    email="jennifer.martinez@hospital.com"
)

print(f"✅ Doctor {doctor.name} has {len(doctor.permissions)} permissions")
print(f"✅ Nurse {nurse.name} has {len(nurse.permissions)} permissions")
print(f"✅ Doctor permissions: {doctor.permissions[:3]}...")  # First 3
```

### Example 4: Quick Clinical Workflow

Complete patient encounter in just a few lines:

```python
from hacs_models import Patient, Observation
from hacs_core import Actor

# 1. Create doctor
doctor = Actor(
    name="Dr. Michael Chen",
    role="physician"
)

# 2. Create patient
patient = Patient(
    full_name="John Smith",
    age=45,
    phone="555-7890"
)

# 3. Record vitals
vitals = [
    Observation(
        subject=patient.id,
        code_text="blood pressure",
        value_numeric=130,
        unit="mmHg"
    ),
    Observation(
        subject=patient.id,
        code_text="heart rate",
        value_numeric=78,
        unit="beats/min"
    ),
    Observation(
        subject=patient.id,
        code_text="body temperature",
        value_numeric=98.2,
        unit="F"
    )
]

print(f"✅ Complete workflow:")
print(f"   Doctor: {doctor.name}")
print(f"   Patient: {patient.display_name} (Age: {patient.age_years})")
print(f"   Vitals recorded: {len(vitals)}")
for vital in vitals:
    print(f"   • {vital.display_name}: {vital.get_numeric_value()} {vital.get_unit()}")
```

## 🏥 Traditional Examples (Full Control)

### Example 5: Comprehensive Patient Management

Creating and managing patient records with full FHIR compliance:

```python
from hacs_models import Patient
from hacs_core import Actor
from datetime import date

# Create a healthcare provider
physician = Actor(
    name="Dr. Smith",
    role="physician",
    permissions=["read:patient", "write:patient", "read:observation", "write:observation"],
    is_active=True
)

# Create a patient with full demographics
patient = Patient(
    given=["John"],
    family="Doe",
    gender="male",
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
    ]
)

print(f"✅ Created patient: {patient.display_name}")
print(f"   Age: {patient.age_years} years")
print(f"   ID: {patient.id}")
```

### Example 6: Clinical Observations with FHIR Codes

Creating clinical measurements with proper LOINC codes:

```python
from hacs_models import Observation
from datetime import datetime, timezone

# Blood pressure observation with full LOINC coding
bp_observation = Observation(
    status="final",
    code={
        "coding": [{
            "system": "http://loinc.org",
            "code": "8480-6",
            "display": "Systolic blood pressure"
        }]
    },
    subject=patient.id,
    value_quantity={"value": 120, "unit": "mmHg"},
    effective_datetime=datetime.now(timezone.utc),
    performer=[physician.id]
)

print(f"✅ Created observation: {bp_observation.primary_code} = 120 mmHg")
print(f"   LOINC Code: {bp_observation.code['coding'][0]['code']}")
print(f"   Status: {bp_observation.status}")
```

### Example 7: Memory and Evidence

Using memory and evidence for clinical decision support:

```python
from hacs_core import MemoryBlock, Evidence

# Store clinical memory
memory = MemoryBlock(
    memory_type="episodic",
    content="Patient has elevated blood pressure requiring follow-up",
    importance_score=0.8,
    metadata={
        "patient_id": patient.id,
        "condition": "hypertension"
    }
)

# Clinical evidence
evidence = Evidence(
    evidence_type="guideline",
    citation="2024 AHA Guidelines",
    content="BP >140/90 requires lifestyle modification",
    confidence_score=0.95,
    quality_score=0.9
)

print(f"✅ Stored memory with importance: {memory.importance_score}")
print(f"✅ Added evidence: {evidence.citation}")
```

### Example 8: Agent Messages

AI agent communications with clinical context:

```python
from hacs_models import AgentMessage
from datetime import datetime, timezone

# Clinical assessment message
message = AgentMessage(
    role="assistant",
    content="Patient shows elevated BP (120/80). Recommend lifestyle changes.",
    related_to=[patient.id, bp_observation.id],
    confidence_score=0.85,
    reasoning_trace=[
        "Analyzed BP reading: 120/80 mmHg",
        "Compared to normal ranges",
        "Recommended lifestyle modifications"
    ],
    created_at=datetime.now(timezone.utc)
)

print(f"✅ Created assessment with confidence: {message.confidence_score}")
print(f"   Related to: {len(message.related_to)} resources")
```

### Example 9: Healthcare Encounters

Managing healthcare visits:

```python
from hacs_models import Encounter
from datetime import datetime, timezone

encounter = Encounter(
    status="finished",
    class_fhir="ambulatory",
    subject=patient.id,
    period={
        "start": datetime(2024, 1, 20, 9, 0, tzinfo=timezone.utc),
        "end": datetime(2024, 1, 20, 10, 0, tzinfo=timezone.utc)
    },
    participants=[{
        "individual": physician.id,
        "name": physician.name
    }]
)

print(f"✅ Created encounter: {encounter.status}")
print(f"   Duration: {encounter.duration_minutes} minutes")
```

## 🔄 Advanced Features

### Example 10: FHIR Integration

Converting between HACS and FHIR formats:

```python
from hacs_fhir import to_fhir, from_fhir

# Convert HACS patient to FHIR
fhir_patient = to_fhir(patient)
print(f"✅ Converted to FHIR: {fhir_patient['resourceType']}")

# Convert back from FHIR
hacs_patient = from_fhir(fhir_patient)
print(f"✅ Converted from FHIR: {hacs_patient.display_name}")
```

### Example 11: Vector Database Integration

Using HACS with vector databases for RAG:

```python
from hacs_tools.vectorization import VectorMetadata

# Create vector metadata
metadata = VectorMetadata(
    resource_type="Patient",
    resource_id=patient.id,
    content_hash="abc123",
    metadata={
        "name": patient.display_name,
        "age": patient.age_years,
        "conditions": ["hypertension"]
    }
)

print(f"✅ Vector metadata for {metadata.resource_type}")
```

### Example 12: Validation

Validating resources before use:

```python
from hacs_tools import validate_before_create

# Validate patient data
result = validate_before_create(patient, actor=physician)

if len(result.errors) == 0:
    print("✅ Patient data is valid")
else:
    print(f"❌ Validation errors: {result.errors}")
```

## 🔧 CLI Usage

Using the HACS command-line interface:

```bash
# Validate a resource file
hacs validate patient.json

# Convert to FHIR
hacs convert to-fhir patient.json --output patient_fhir.json

# Show resource schema
hacs schema Patient --format table
```

## 🚀 Production Tips

### Error Handling
```python
from pydantic import ValidationError

try:
    patient = Patient(
        given=["John"],
        # Missing required fields will use defaults
    )
    print(f"✅ Patient created with ID: {patient.id}")
except ValidationError as e:
    print(f"❌ Validation error: {e}")
```

### Resource Identification
```python
# LLM-friendly: IDs are auto-generated
patient = Patient(full_name="John Doe")
observation = Observation(
    subject=patient.id,  # Use the auto-generated ID
    code_text="blood pressure",
    value_numeric=120,
    unit="mmHg"
)

print(f"Patient ID: {patient.id}")
print(f"Observation ID: {observation.id}")
```

### Memory Management
```python
# Set appropriate importance scores
critical_memory = MemoryBlock(
    importance_score=0.9,  # High importance
    content="Patient allergic to penicillin",
    memory_type="episodic"
)

routine_memory = MemoryBlock(
    importance_score=0.3,  # Low importance
    content="Patient prefers morning appointments",
    memory_type="procedural"
)
```

## 🧪 Testing Your Implementation

Verify everything works:

```bash
# Run quick verification
uv run python tests/test_quick_start.py

# Test LLM-friendly features
uv run python tests/test_llm_friendly.py

# Run comprehensive tests
uv run pytest tests/ -v
```

## 🔍 Comparison: LLM-Friendly vs Traditional

| Feature | LLM-Friendly | Traditional |
|---------|-------------|-------------|
| **Patient Creation** | `Patient(full_name="John Doe", age=30)` | `Patient(given=["John"], family="Doe", birth_date="1994-01-01")` |
| **Observation** | `Observation(code_text="blood pressure", value_numeric=120)` | `Observation(code={"coding": [{"system": "http://loinc.org", "code": "8480-6"}]}, value_quantity={"value": 120})` |
| **Actor Setup** | `Actor(name="Dr. Smith", role="physician")` | `Actor(name="Dr. Smith", role="physician", permissions=["read:patient", "write:patient", ...])` |
| **ID Management** | Auto-generated | Manual specification |
| **Validation** | Flexible, guides completion | Strict, requires all fields |
| **Learning Curve** | Minimal | Moderate |
| **FHIR Compliance** | Automatic | Manual |

## 🎯 When to Use Which Approach

### Use LLM-Friendly When:
- Building AI agents that generate structured output
- Rapid prototyping and development
- Working with partial or incomplete data
- Simplifying complex healthcare workflows
- Training non-healthcare developers

### Use Traditional When:
- Full control over FHIR compliance is required
- Working with existing healthcare systems
- Regulatory compliance requires specific field validation
- Building enterprise healthcare applications
- Maximum performance is critical

---

Both approaches are production-ready and maintain full FHIR compliance. The LLM-friendly approach simply provides smart defaults and auto-completion to make healthcare AI development more accessible.

For more details, see the [Architecture Guide](../getting-started/architecture.md) and [Models Documentation](../modules/hacs-models.md). 