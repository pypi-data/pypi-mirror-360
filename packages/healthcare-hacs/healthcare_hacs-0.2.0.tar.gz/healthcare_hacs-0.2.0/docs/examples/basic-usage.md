# Basic Usage Examples

This guide shows practical examples using HACS for healthcare AI applications. All examples are tested and production-ready.

## 🏥 Example 1: Patient Management

Creating and managing patient records:

```python
from hacs_models import Patient
from hacs_core import Actor
from datetime import date

# Create a healthcare provider
physician = Actor(
    id="dr-smith-001",
    name="Dr. Smith",
    role="physician",
    permissions=["patient:*", "observation:*"],
    is_active=True
)

# Create a patient
patient = Patient(
    id="patient-001",
    given=["John"],
    family="Doe",
    gender="male",
    birth_date=date(1985, 3, 15),
    active=True
)

print(f"✅ Created patient: {patient.display_name}")
print(f"   Age: {patient.age_years} years")
```

## 🩺 Example 2: Clinical Observations

Creating clinical measurements with FHIR codes:

```python
from hacs_models import Observation
from datetime import datetime, timezone

# Blood pressure observation
bp_observation = Observation(
    id="obs-bp-001",
    status="final",
    code={
        "coding": [{
            "system": "http://loinc.org",
            "code": "8480-6",
            "display": "Systolic blood pressure"
        }]
    },
    subject="patient-001",
    value_quantity={"value": 120, "unit": "mmHg"},
    effective_datetime=datetime.now(timezone.utc)
)

print(f"✅ Created observation: {bp_observation.primary_code} = 120 mmHg")
```

## 🧠 Example 3: Memory and Evidence

Using memory and evidence for clinical decision support:

```python
from hacs_core import MemoryBlock, Evidence

# Store clinical memory
memory = MemoryBlock(
    id="memory-001",
    memory_type="episodic",
    content="Patient has elevated blood pressure requiring follow-up",
    importance_score=0.8,
    metadata={
        "patient_id": "patient-001",
        "condition": "hypertension"
    }
)

# Clinical evidence
evidence = Evidence(
    id="evidence-001",
    evidence_type="guideline",
    citation="2024 AHA Guidelines",
    content="BP >140/90 requires lifestyle modification",
    confidence_score=0.95,
    quality_score=0.9
)

print(f"✅ Stored memory with importance: {memory.importance_score}")
print(f"✅ Added evidence: {evidence.citation}")
```

## 🤖 Example 4: Agent Messages

AI agent communications with clinical context:

```python
from hacs_models import AgentMessage
from datetime import datetime, timezone

# Clinical assessment message
message = AgentMessage(
    id="msg-001",
    role="assistant",
    content="Patient shows elevated BP (120/80). Recommend lifestyle changes.",
    related_to=["patient-001", "obs-bp-001"],
    confidence_score=0.85,
    reasoning_trace=[
        "Analyzed BP reading: 120/80 mmHg",
        "Compared to normal ranges",
        "Recommended lifestyle modifications"
    ],
    created_at=datetime.now(timezone.utc)
)

print(f"✅ Created assessment with confidence: {message.confidence_score}")
```

## 🏥 Example 5: Healthcare Encounters

Managing healthcare visits:

```python
from hacs_models import Encounter
from datetime import datetime, timezone

encounter = Encounter(
    id="encounter-001",
    status="finished",
    class_fhir="ambulatory",
    subject="patient-001",
    period={
        "start": datetime(2024, 1, 20, 9, 0, tzinfo=timezone.utc),
        "end": datetime(2024, 1, 20, 10, 0, tzinfo=timezone.utc)
    },
    participants=[{
        "individual": "dr-smith-001",
        "name": "Dr. Smith"
    }]
)

print(f"✅ Created encounter: {encounter.status}")
```

## 🔄 Example 6: FHIR Integration

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

## 🗃️ Example 7: Vector Database Integration

Using HACS with vector databases for RAG:

```python
from hacs_tools.vectorization import VectorMetadata

# Create vector metadata
metadata = VectorMetadata(
    resource_type="Patient",
    resource_id="patient-001",
    content_hash="abc123",
    metadata={
        "name": "John Doe",
        "age": 39,
        "conditions": ["hypertension"]
    }
)

print(f"✅ Vector metadata for {metadata.resource_type}")
```

## 🧪 Example 8: Validation

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

## 🔧 Example 9: CLI Usage

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
        id="invalid",
        # Missing required fields
    )
except ValidationError as e:
    print(f"Validation error: {e}")
```

### Resource Identification
```python
# Use meaningful IDs
patient_id = "patient-hospital-12345"
observation_id = f"obs-{patient_id}-bp-001"
```

### Memory Management
```python
# Set appropriate importance scores
critical_memory = MemoryBlock(
    importance_score=0.9,  # High importance
    content="Patient allergic to penicillin"
)
```

## 🧪 Testing Your Implementation

Verify everything works:

```bash
# Run quick verification
uv run python tests/test_quick_start.py

# Run comprehensive tests
uv run pytest tests/ -v
```

---

These examples cover all implemented and tested HACS functionality. For more details, see the [Architecture Guide](../getting-started/architecture.md). 