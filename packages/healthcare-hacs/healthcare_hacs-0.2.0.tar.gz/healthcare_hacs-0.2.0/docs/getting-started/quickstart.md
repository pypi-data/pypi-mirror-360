# HACS Quick Start

Get started with HACS in 5 minutes. This guide covers the essential features that are implemented and tested.

## 🚀 Installation

```bash
# Clone and install
git clone https://github.com/voa-health/hacs.git
cd hacs && uv sync

# Verify installation
uv run python tests/test_quick_start.py
```

**Expected output:**
```
🚀 HACS Quick Start Test Suite
==================================================
🧪 Testing core imports...
✅ All core packages imported successfully
...
📊 Results: 6/6 tests passed
🎉 All tests passed! Your HACS installation is working correctly.
```

## 🏥 Core Concepts

HACS provides healthcare data models for AI applications:

- **Patient**: Demographics and identifiers
- **Observation**: Clinical measurements  
- **Actor**: User roles and permissions
- **MemoryBlock**: Agent memory storage
- **Evidence**: Clinical evidence with citations

## 💡 Your First Healthcare AI Workflow

### Step 1: Create a Healthcare Provider

```python
from hacs_core import Actor

physician = Actor(
    id="dr-smith-001",
    name="Dr. Smith",
    role="physician",
    permissions=["patient:*", "observation:*"],
    is_active=True
)

print(f"✅ Created physician: {physician.name}")
```

### Step 2: Create a Patient

```python
from hacs_models import Patient
from datetime import date

patient = Patient(
    id="patient-001",
    given=["John"],
    family="Doe", 
    gender="male",
    birth_date=date(1985, 3, 15),
    active=True
)

print(f"✅ Created patient: {patient.display_name}, Age: {patient.age_years}")
```

### Step 3: Record Clinical Observations

```python
from hacs_models import Observation
from datetime import datetime, timezone

observation = Observation(
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

print(f"✅ Recorded: {observation.primary_code} = 120 mmHg")
```

### Step 4: Store Agent Memory

```python
from hacs_core import MemoryBlock

memory = MemoryBlock(
    id="memory-001",
    memory_type="episodic",
    content="Patient has normal blood pressure reading",
    importance_score=0.7,
    metadata={
        "patient_id": "patient-001",
        "observation_id": "obs-bp-001"
    }
)

print(f"✅ Stored memory with importance: {memory.importance_score}")
```

### Step 5: Add Clinical Evidence

```python
from hacs_core import Evidence

evidence = Evidence(
    id="evidence-001",
    evidence_type="guideline",
    citation="2024 AHA Guidelines",
    content="Normal BP is <120/80 mmHg",
    confidence_score=0.95,
    quality_score=0.9
)

print(f"✅ Added evidence: {evidence.citation}")
```

## 🤖 AI Agent Integration

Create agent messages with clinical context:

```python
from hacs_models import AgentMessage

message = AgentMessage(
    id="msg-001",
    role="assistant",
    content="Patient blood pressure is within normal range. Continue routine monitoring.",
    related_to=["patient-001", "obs-bp-001"],
    confidence_score=0.9,
    reasoning_trace=[
        "Analyzed BP reading: 120 mmHg systolic",
        "Compared to AHA guidelines",
        "Determined normal range"
    ]
)

print(f"✅ Agent assessment complete (confidence: {message.confidence_score})")
```

## 🔄 FHIR Integration

Convert between HACS and FHIR formats:

```python
from hacs_fhir import to_fhir, from_fhir

# Convert to FHIR
fhir_patient = to_fhir(patient)
print(f"✅ FHIR conversion: {fhir_patient['resourceType']}")

# Convert back
hacs_patient = from_fhir(fhir_patient)
print(f"✅ Round-trip successful: {hacs_patient.display_name}")
```

## 🧪 Validation

Validate resources before use:

```python
from hacs_tools import validate_before_create

result = validate_before_create(patient, actor=physician)

if len(result.errors) == 0:
    print("✅ Patient data is valid")
else:
    print(f"❌ Validation errors: {result.errors}")
```

## 🗃️ Vector Database Support

Prepare data for vector storage:

```python
from hacs_tools.vectorization import VectorMetadata

metadata = VectorMetadata(
    resource_type="Patient",
    resource_id="patient-001", 
    content_hash="abc123",
    metadata={"name": "John Doe", "age": 39}
)

print(f"✅ Vector metadata ready for {metadata.resource_type}")
```

## 🔧 Command Line Interface

Use HACS from the command line:

```bash
# Validate resources
hacs validate patient.json

# Convert to FHIR  
hacs convert to-fhir patient.json --output patient_fhir.json

# Show schema
hacs schema Patient --format table
```

## 📊 Testing

Verify your setup:

```bash
# Quick test
uv run python tests/test_quick_start.py

# Full test suite
uv run pytest tests/ -v

# Specific tests
uv run pytest tests/test_models.py -v
```

## 🚀 What's Next?

Now that you have the basics working:

1. **[Learn Core Concepts](concepts.md)** - Understand HACS architecture
2. **[Explore Examples](../examples/basic-usage.md)** - See real-world patterns  
3. **[Read Architecture Guide](architecture.md)** - Understand the design
4. **[Vector Store Integration](../examples/basic-usage.md#example-7-vector-database-integration)** - Add RAG capabilities

## 🎯 Key Features Demonstrated

✅ **Healthcare Data Models** - Patient, Observation, Encounter  
✅ **Actor Security** - Role-based permissions  
✅ **Agent Memory** - Episodic, procedural, executive memory types  
✅ **Clinical Evidence** - Citation tracking and quality scores  
✅ **FHIR Integration** - Bidirectional conversion  
✅ **Validation** - Resource validation and error checking  
✅ **Vector Support** - Metadata for RAG applications  
✅ **CLI Tools** - Command-line operations  

---

You now have a working healthcare AI foundation. All examples above are tested and production-ready! 