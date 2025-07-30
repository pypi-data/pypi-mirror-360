# HACS – Healthcare Agent Communication Standard

[![Version](https://img.shields.io/badge/version-0.2.0-blue)](https://github.com/solanovisitor/hacs)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://python.org)
[![Tests](https://img.shields.io/badge/tests-passing-green)](https://github.com/solanovisitor/hacs/actions)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue)](LICENSE)

HACS provides standardized data models and tools for healthcare AI applications, with full FHIR compatibility and optimized interfaces for LLM integration.

## Installation

```bash
pip install healthcare-hacs
```

For development:
```bash
git clone https://github.com/solanovisitor/hacs.git
cd hacs && uv sync
```

## Quick Start

### Basic Usage

```python
from hacs_models import Patient, Observation
from hacs_core import Actor

# Create healthcare provider
doctor = Actor(name="Dr. Smith", role="physician")

# Create patient
patient = Patient(full_name="John Doe", age=45, gender="male")

# Record observation
bp = Observation(
    subject=patient.id,
    code_text="blood pressure",
    value_numeric=120,
    unit="mmHg"
)

print(f"Patient: {patient.display_name}")
print(f"Observation: {bp.display_name} = {bp.get_numeric_value()} {bp.get_unit()}")
```

### FHIR-Compatible Usage

```python
from hacs_models import Patient, Observation
from datetime import date

# Create patient with FHIR fields
patient = Patient(
    given=["John"],
    family="Doe",
    gender="male",
    birth_date=date(1979, 1, 1)
)

# Create observation with LOINC code
bp = Observation(
    status="final",
    code={
        "coding": [{
            "system": "http://loinc.org",
            "code": "8480-6",
            "display": "Systolic blood pressure"
        }]
    },
    subject=patient.id,
    value_quantity={"value": 120, "unit": "mmHg"}
)
```

## Core Features

### Data Models
- **Patient**: Demographics, identifiers, contact information
- **Observation**: Clinical measurements with LOINC codes
- **Encounter**: Healthcare visits and interactions
- **Actor**: Healthcare providers with role-based permissions
- **Evidence**: Clinical evidence with confidence scoring
- **MemoryBlock**: Structured memory for AI agents

### Tools
- **CRUD Operations**: Create, read, update, delete resources
- **FHIR Conversion**: Bidirectional FHIR R4/R5 conversion
- **Validation**: Resource validation and error checking
- **Vector Support**: Metadata for vector databases
- **CLI Interface**: Command-line operations

### AI Integration
- **LangGraph**: Workflow adapter for clinical decision support
- **CrewAI**: Multi-agent healthcare workflows
- **Vector Stores**: Pinecone and Qdrant integration
- **Memory Management**: Episodic, procedural, and executive memory

## Documentation

| Guide | Description |
|-------|-------------|
| [Installation](docs/getting-started/installation.md) | Setup and dependencies |
| [Quick Start](docs/getting-started/quickstart.md) | 5-minute tutorial |
| [Core Concepts](docs/getting-started/concepts.md) | Understanding HACS |
| [Architecture](docs/getting-started/architecture.md) | System design |
| [Basic Usage](docs/examples/basic-usage.md) | Code examples |
| [API Reference](docs/reference/api.md) | Complete API documentation |

## Examples

### Simple Patient Workflow
```python
from hacs_models import Patient, Observation
from hacs_core import Actor, MemoryBlock

# Setup
doctor = Actor(name="Dr. Johnson", role="physician")
patient = Patient(full_name="Maria Rodriguez", age=32, gender="female")

# Clinical data
vitals = [
    Observation(subject=patient.id, code_text="blood pressure", value_numeric=118, unit="mmHg"),
    Observation(subject=patient.id, code_text="heart rate", value_numeric=72, unit="bpm"),
    Observation(subject=patient.id, code_text="temperature", value_numeric=98.6, unit="F")
]

# Store clinical memory
memory = MemoryBlock(
    content="Patient has normal vital signs",
    memory_type="episodic",
    importance_score=0.7
)
```

### Vector Database Integration
```python
from hacs_tools.vectorization import VectorMetadata

metadata = VectorMetadata(
    resource_type="Patient",
    resource_id=patient.id,
    content_hash="abc123",
    metadata={"name": patient.display_name, "age": patient.age_years}
)
```

### FHIR Conversion
```python
from hacs_fhir import to_fhir, from_fhir

# Convert to FHIR
fhir_patient = to_fhir(patient)

# Convert back
hacs_patient = from_fhir(fhir_patient)
```

## Testing

```bash
# Quick verification
uv run python tests/test_quick_start.py

# Full test suite
uv run pytest tests/ -v

# LLM-friendly features
uv run python tests/test_llm_friendly.py
```

## Packages

| Package | Purpose | Status |
|---------|---------|--------|
| `hacs-core` | Base models, Actor, Memory, Evidence | Stable |
| `hacs-models` | Patient, Observation, Encounter, AgentMessage | Stable |
| `hacs-tools` | CRUD operations, adapters, validation | Stable |
| `hacs-fhir` | FHIR R4/R5 conversion | Stable |
| `hacs-api` | FastAPI service | Basic |
| `hacs-cli` | Command-line interface | Stable |
| `hacs-qdrant` | Qdrant vector store | Stable |
| `hacs-openai` | OpenAI embeddings | Stable |
| `hacs-pinecone` | Pinecone vector store | Stable |

## Requirements

- Python 3.10+
- Pydantic 2.0+
- Optional: Vector database (Pinecone, Qdrant)
- Optional: LLM providers (OpenAI, Anthropic)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Run `uv run pytest tests/`
5. Submit a pull request

See [Contributing Guidelines](docs/contributing/guidelines.md) for details.

## License

Apache 2.0 - see [LICENSE](LICENSE) for details.

## Support

- [Documentation](docs/README.md)
- [GitHub Issues](https://github.com/solanovisitor/hacs/issues)
- [GitHub Discussions](https://github.com/solanovisitor/hacs/discussions)
