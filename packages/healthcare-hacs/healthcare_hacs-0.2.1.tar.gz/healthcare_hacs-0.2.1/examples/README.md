# HACS + LangGraph Examples

This directory contains working examples demonstrating the integration of HACS (Healthcare Agent Communication Standard) with LangGraph for building sophisticated healthcare AI workflows.

## Examples

### `langgraph/` - Clean Functional API Demo ⭐ **NEW**

A clean, production-ready demonstration using LangGraph's **Functional API** for maximum simplicity and readability.

**Files:**
- `state.py` - Clean state definitions with HACS integration
- `graph.py` - Functional workflow using simple node functions  
- `run_demo.py` - Simple execution script
- `README.md` - Comprehensive documentation

**Features:**
- **Functional API**: Simple node functions instead of complex classes
- **Clean State Management**: Custom state types using HACS models
- **Clinical Tools**: Mock cardiovascular risk calculator and evidence search
- **HACS Integration**: Proper use of Patient, Observation, Evidence, and Actor models
- **Conditional Routing**: Dynamic workflow based on clinical data

**Running:**
```bash
cd examples/langgraph
uv run graph.py
```

### `advanced_langgraph_agent.py` - Comprehensive Example

A comprehensive example showcasing a clinical assessment agent workflow that demonstrates:

**Key Features:**
- **Conditional Routing**: Uses LangGraph conditional edges to make decisions based on observation data
- **Tool Integration**: Simulates calling clinical risk calculators
- **Evidence Search**: Searches through evidence databases for relevant guidelines
- **State Management**: Uses HACS state objects throughout the workflow
- **Structured Output**: Generates comprehensive HACS `AgentMessage` with reasoning traces

**Workflow Steps:**
1. **Initialize**: Creates patient, observation, and evidence data using HACS models
2. **Route**: Conditionally routes based on risk level (high-risk observations trigger tool calls)
3. **Calculate Risk**: Simulates cardiovascular risk calculation tool
4. **Search Evidence**: Finds relevant clinical guidelines and research
5. **Synthesize**: Creates a structured clinical assessment with full provenance

**Running the Example:**
```bash
uv run examples/advanced_langgraph_agent.py
```

**Expected Output:**
- Step-by-step workflow execution with rich console output
- Final structured `AgentMessage` in JSON format
- Workflow visualization saved as `advanced_workflow.png`

## Enhanced LangGraph Adapter

Both examples use the enhanced `LangGraphAdapter` from `hacs-tools` which provides:

### New Features
- **Custom State Builders**: Create domain-specific state types
- **Tool Registry**: Register and manage clinical tools
- **Memory Management**: Enhanced memory consolidation and retrieval
- **State Transitions**: Rule-based state transitions
- **Enhanced Clinical Context**: Automatic risk factor detection

### Usage Example
```python
from hacs_tools.adapters.langgraph_adapter import LangGraphAdapter

# Create enhanced adapter
adapter = LangGraphAdapter()

# Register a clinical tool
def calculate_risk(bp: int, age: int) -> dict:
    return {"risk": "high" if bp > 140 else "low"}

adapter.register_tool("risk_calculator", calculate_risk)

# Create clinical workflow state
state = adapter.create_clinical_workflow_state(
    patient=patient,
    observations=[observation],
    actor=clinician
)
```

## Key Integration Points

### HACS Models Used
- `Patient`: Demographics and patient information
- `Observation`: Clinical measurements with FHIR-compliant coding
- `Evidence`: Clinical guidelines and research references
- `AgentMessage`: Structured communication with reasoning traces
- `Actor`: Healthcare provider or AI agent identity

### LangGraph Features Demonstrated
- `StateGraph`: Stateful workflow management
- Conditional edges for dynamic routing
- Node-based processing with state updates
- Workflow compilation and execution

### State Management
The examples use the `LangGraphAdapter` from `hacs-tools` to:
- Convert HACS resources to LangGraph state format
- Maintain clinical context throughout the workflow
- Bridge between different workflow types
- Preserve provenance and audit trails

## Dependencies

The examples require:
- `langgraph`: Graph-based workflow orchestration
- `langchain-core`: Core LangChain functionality
- `rich`: Enhanced console output
- All HACS packages (`hacs-core`, `hacs-models`, `hacs-tools`)

## Comparison: Functional vs Object-Oriented API

| Aspect | Functional API (`langgraph/`) | Object-Oriented (`advanced_*`) |
|--------|-------------------------|--------------------------------|
| **Complexity** | Simple, clean functions | More complex, feature-rich |
| **Readability** | High - pure functions | Medium - class-based |
| **Testability** | Excellent - isolated functions | Good - mocked dependencies |
| **Customization** | Easy to extend | Highly configurable |
| **Best For** | Simple workflows, learning | Complex enterprise workflows |

## Running the Examples

### LangGraph Functional API Demo
```bash
# Option 1: Direct execution
cd examples/langgraph
uv run graph.py

# Option 2: Using run script
uv run examples/langgraph/run_demo.py
```

### Advanced Object-Oriented Example
```bash
uv run examples/advanced_langgraph_agent.py
```

## Next Steps

These examples provide a foundation for building more complex healthcare AI workflows. Consider extending them with:
- Real LLM integration (OpenAI, Anthropic, etc.)
- Actual clinical tools and APIs
- Database persistence for evidence and memories
- Multi-agent collaboration patterns
- Human-in-the-loop approvals

## Architecture

The integration follows this pattern:

```
HACS Resources → LangGraphAdapter → StateGraph → Workflow Execution → HACS AgentMessage
```

This ensures that all clinical data maintains FHIR compliance and audit trails while benefiting from LangGraph's powerful workflow orchestration capabilities. 