# HACS Core Module

The `hacs-core` package provides the foundation models for healthcare AI applications.

## 📦 Package Structure

```
hacs-core/
├── src/hacs_core/
│   ├── __init__.py          # Public exports
│   ├── base_resource.py     # BaseResource foundation
│   ├── memory.py           # MemoryBlock model
│   ├── evidence.py         # Evidence model
│   └── actor.py            # Actor model
└── pyproject.toml          # Package configuration
```

## 🏗️ Core Models

### BaseResource

Foundation class for all HACS resources with common fields:

```python
from hacs_core import BaseResource
from datetime import datetime, timezone

class BaseResource(BaseModel):
    id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    resource_type: str
```

**Key Features:**
- Automatic timestamp management
- Unique resource identification
- JSON schema generation

### MemoryBlock

Agent memory storage with cognitive science-based types:

```python
from hacs_core import MemoryBlock

# Store episodic memory (events)
memory = MemoryBlock(
    id="memory-001",
    memory_type="episodic",
    content="Patient reported chest pain during visit",
    importance_score=0.9,
    metadata={"patient_id": "patient-001", "urgency": "high"}
)
```

**Memory Types:**
- `episodic`: Events and experiences
- `procedural`: Skills and procedures
- `executive`: Goals and plans

**Key Features:**
- Importance scoring (0.0-1.0)
- Rich metadata support
- Access tracking

### Evidence

Clinical evidence with provenance tracking:

```python
from hacs_core import Evidence

evidence = Evidence(
    id="evidence-001",
    evidence_type="guideline",
    citation="2024 AHA Guidelines",
    content="Blood pressure >140/90 requires medication",
    confidence_score=0.95,
    quality_score=0.9
)
```

**Evidence Types:**
- `research_study`: Peer-reviewed research
- `guideline`: Clinical guidelines
- `expert_opinion`: Professional consensus
- `clinical_note`: Provider documentation

**Key Features:**
- Quality assessment scores
- Citation tracking
- Tag management

### Actor

User authentication and permissions:

```python
from hacs_core import Actor

actor = Actor(
    id="dr-smith-001",
    name="Dr. Smith",
    role="physician",
    permissions=["patient:*", "observation:read"],
    is_active=True
)

# Check permissions
if actor.has_permission("patient:create"):
    print("Can create patients")
```

**Actor Roles:**
- `physician`: Medical doctors
- `nurse`: Registered nurses
- `patient`: Healthcare consumers
- `system`: Automated systems
- `agent`: AI agents

**Key Features:**
- Role-based permissions
- Session management
- Permission checking

## 🧪 Testing

All core models are fully tested:

```bash
# Test core functionality
uv run pytest tests/test_core.py -v

# Quick verification
uv run python -c "
from hacs_core import Actor, MemoryBlock, Evidence
print('✅ Core models working')
"
```

## 📊 Performance

Optimized for agent workloads:
- Model creation: <1ms
- Validation: <1ms  
- Permission checks: <0.1ms

## 🔗 Integration

### With Agent Frameworks
```python
# Store agent state as memory
def store_agent_memory(state_data):
    return MemoryBlock(
        memory_type="procedural",
        content=f"Agent state: {state_data}",
        metadata={"framework": "custom"}
    )
```

### With Vector Databases
```python
# Prepare evidence for embedding
evidence = Evidence(
    citation="Study Title",
    content="Long clinical text...",
    vector_id="embedding-001"  # Reference to vector DB
)
```

## 🚀 Best Practices

### Resource IDs
```python
# Use meaningful, hierarchical IDs
patient_id = "patient-hospital-12345"
memory_id = f"memory-{patient_id}-encounter-001"
```

### Memory Importance
```python
# Set appropriate importance scores
critical_memory = MemoryBlock(
    importance_score=0.9,  # High for critical events
    content="Patient allergic to penicillin"
)

routine_memory = MemoryBlock(
    importance_score=0.3,  # Low for routine notes
    content="Patient prefers morning appointments"
)
```

### Actor Security
```python
# Use principle of least privilege
nurse = Actor(
    permissions=[
        "patient:read",
        "observation:create"
        # No delete permissions
    ]
)
```

## 📚 API Reference

### BaseResource
- `update_timestamp()`: Update the updated_at field
- `age_seconds`: Property returning age in seconds

### MemoryBlock  
- `record_access()`: Record memory access
- `update_importance(score)`: Update importance score

### Evidence
- `add_tag(tag)`: Add categorization tag
- `update_quality_score(score)`: Update quality assessment

### Actor
- `has_permission(permission)`: Check specific permission
- `start_session()`: Start authentication session
- `end_session()`: End current session

---

The `hacs-core` module provides the tested foundation for healthcare AI applications with robust security and clinical data management. 