# 🔗 HACS LangGraph Adapter

[![PyPI version](https://badge.fury.io/py/hacs-langgraph.svg)](https://badge.fury.io/py/hacs-langgraph)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

**LangGraph integration for HACS (Healthcare Agent Communication Standard)**

Seamlessly integrate HACS clinical data models with LangGraph workflows for advanced healthcare AI applications.

## 🚀 Quick Start

### Installation

```bash
pip install hacs-langgraph
```

### Basic Usage

```python
from hacs_langgraph import LangGraphAdapter, LangGraphStateType
from hacs_core import Actor
from hacs_models import Patient, Observation

# Create adapter
adapter = LangGraphAdapter()

# Create actor
actor = Actor(name="Dr. Smith", role="physician")

# Create clinical workflow state
patient = Patient(full_name="John Doe", age=45)
observations = [
    Observation(code_text="blood pressure", value_numeric=140, unit="mmHg")
]

state = adapter.create_clinical_workflow_state(
    patient=patient,
    observations=observations,
    actor=actor,
    workflow_type=LangGraphStateType.CLINICAL_ASSESSMENT
)

print(f"Workflow ID: {state['workflow_id']}")
print(f"Patient: {state['patient']['display_name']}")
print(f"Observations: {len(state['observations'])}")
```

## 🎯 Key Features

### 🔄 State Management
- **HACS-Compatible States**: Native integration with HACS data models
- **Type Safety**: Full TypeScript-style type hints for Python
- **State Transitions**: Configurable workflow transitions
- **Custom State Builders**: Extend states with custom fields

### 🛠️ Tool Integration
- **Tool Registry**: Register and manage clinical tools
- **Actor-Based Security**: Role-based tool access control
- **Tool History**: Complete audit trail of tool executions
- **Error Handling**: Robust error recovery and logging

### 🧠 Memory Management
- **Workflow Memory**: Persistent memory across workflow steps
- **Memory Consolidation**: Configurable memory consolidation rules
- **Memory Types**: Support for different memory categories
- **Memory Querying**: Efficient memory retrieval and filtering

### 🏥 Clinical Workflows
- **Clinical Assessment**: Structured clinical evaluation workflows
- **Treatment Planning**: Evidence-based treatment recommendations
- **Evidence Review**: Integration with clinical evidence databases
- **Decision Support**: AI-powered clinical decision assistance

## 📚 Core Components

### LangGraphAdapter

The main adapter class for integrating HACS with LangGraph:

```python
from hacs_langgraph import LangGraphAdapter, LangGraphStateType
from hacs_core import Actor

adapter = LangGraphAdapter()

# Create HACS-compatible state
state = adapter.create_hacs_state(
    workflow_type=LangGraphStateType.CLINICAL_ASSESSMENT,
    actor=actor,
    initial_step="assessment"
)

# Add resources to state
adapter.add_resource_to_state(state, patient)
adapter.add_resource_to_state(state, observation)

# Execute tools
state = adapter.execute_tool(state, "risk_calculator", patient_id=patient.id)
```

### Custom State Builder

Create custom state types for specialized workflows:

```python
from hacs_langgraph import CustomStateBuilder

# Create custom state builder
builder = adapter.create_custom_state_builder("cardiology")

# Add custom fields
builder.add_field("ejection_fraction", float, 0.0)
builder.add_field("nyha_class", int, 1)
builder.add_field("medications", list, [])

# Add validation
builder.add_validator(lambda state: state.get("ejection_fraction", 0) > 0)

# Use in workflow
state = adapter.create_hacs_state(
    workflow_type="cardiology_assessment",
    actor=actor,
    custom_state_type="cardiology",
    ejection_fraction=0.45,
    nyha_class=2
)
```

### Tool Registry

Register and manage clinical tools:

```python
from hacs_langgraph import HACSToolRegistry

# Create registry
registry = HACSToolRegistry()

# Register a clinical tool
def calculate_cardiovascular_risk(age: int, systolic_bp: int, **kwargs) -> dict:
    """Calculate 10-year cardiovascular risk."""
    base_risk = 0.05
    age_factor = max(0, (age - 40) * 0.01)
    bp_factor = max(0, (systolic_bp - 120) * 0.002)
    
    risk = base_risk + age_factor + bp_factor
    return {
        "risk_percentage": min(risk * 100, 100),
        "risk_category": "high" if risk > 0.2 else "moderate" if risk > 0.1 else "low"
    }

registry.register_tool(
    "cardiovascular_risk",
    calculate_cardiovascular_risk,
    description="Calculate 10-year cardiovascular risk",
    requires_actor=True
)

# Use in adapter
adapter.tool_registry = registry
```

### Memory Management

Manage workflow memory and consolidation:

```python
from hacs_langgraph import MemoryManager
from hacs_core import MemoryBlock

memory_manager = MemoryManager()

# Add memory to workflow
memory = MemoryBlock(
    content="Patient shows signs of hypertension",
    memory_type="clinical_observation",
    confidence=0.85
)

memory_manager.add_memory("workflow-123", memory)

# Get memories
memories = memory_manager.get_memories("workflow-123", "clinical_observation")

# Add consolidation rule
def consolidate_clinical_observations(memories):
    """Consolidate clinical observations by confidence."""
    return sorted(memories, key=lambda m: m.confidence, reverse=True)[:5]

memory_manager.add_consolidation_rule(consolidate_clinical_observations)
```

## 🏥 Clinical Workflow Examples

### Clinical Assessment Workflow

```python
from hacs_langgraph import LangGraphAdapter, LangGraphStateType
from hacs_core import Actor
from hacs_models import Patient, Observation

# Setup
adapter = LangGraphAdapter()
actor = Actor(name="Dr. Johnson", role="physician")

# Create patient and observations
patient = Patient(full_name="Maria Rodriguez", age=59)
observations = [
    Observation(code_text="systolic blood pressure", value_numeric=165, unit="mmHg"),
    Observation(code_text="heart rate", value_numeric=88, unit="bpm"),
    Observation(code_text="body mass index", value_numeric=28.5, unit="kg/m2")
]

# Create clinical workflow state
state = adapter.create_clinical_workflow_state(
    patient=patient,
    observations=observations,
    actor=actor,
    workflow_type=LangGraphStateType.CLINICAL_ASSESSMENT
)

# The state now contains:
# - Patient information
# - All observations
# - Clinical context with risk factors
# - Actor context with permissions
# - Workflow metadata
```

### State Bridging

Bridge between different workflow types:

```python
from hacs_langgraph import create_state_bridge

# Bridge from assessment to treatment planning
treatment_state = create_state_bridge(
    source_state=assessment_state,
    target_workflow_type="treatment_planning",
    actor=actor,
    preserve_data=True
)

# The new state preserves:
# - Patient data
# - Observations
# - Clinical context
# - Previous workflow metadata
```

## 🔧 Advanced Usage

### Custom Workflow States

```python
from hacs_langgraph import create_custom_workflow_state

# Create specialized workflow state
state = create_custom_workflow_state(
    workflow_type="emergency_assessment",
    actor=emergency_physician,
    custom_fields={
        "triage_level": "urgent",
        "arrival_time": datetime.now(),
        "chief_complaint": "chest pain"
    }
)
```

### State Transitions

```python
from hacs_langgraph import StateTransition

# Define transition conditions
def high_risk_condition(state):
    """Check if patient is high risk."""
    clinical_context = state.get("clinical_context", {})
    return len(clinical_context.get("risk_factors", [])) > 2

# Create transition
transition = StateTransition(
    from_step="assessment",
    to_step="urgent_intervention",
    condition=high_risk_condition,
    action=lambda state: {**state, "priority": "urgent"}
)

# Add to adapter
adapter.add_state_transition(transition)
```

## 🧪 Testing

The package includes comprehensive tests:

```bash
# Run tests
pytest tests/

# Run with coverage
pytest tests/ --cov=hacs_langgraph --cov-report=html

# Run specific test
pytest tests/test_adapter.py::test_create_clinical_workflow_state -v
```

## 📖 Documentation

- **[HACS Documentation](https://github.com/solanovisitor/hacs/tree/main/docs)**: Complete HACS documentation
- **[LangGraph Documentation](https://langchain-ai.github.io/langgraph/)**: Official LangGraph documentation
- **[Examples](./examples/)**: Comprehensive usage examples
- **[API Reference](./docs/api.md)**: Detailed API documentation

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guidelines](https://github.com/solanovisitor/hacs/blob/main/CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](https://github.com/solanovisitor/hacs/blob/main/LICENSE) file for details.

## 🔗 Related Packages

- **[hacs-core](https://pypi.org/project/hacs-core/)**: Core HACS data models and utilities
- **[hacs-models](https://pypi.org/project/hacs-models/)**: Clinical data models (Patient, Observation, etc.)
- **[hacs-tools](https://pypi.org/project/hacs-tools/)**: Core tools and utilities
- **[hacs-crewai](https://pypi.org/project/hacs-crewai/)**: CrewAI integration
- **[hacs-autogen](https://pypi.org/project/hacs-autogen/)**: AutoGen integration

---

**Built with ❤️ for healthcare AI developers** 