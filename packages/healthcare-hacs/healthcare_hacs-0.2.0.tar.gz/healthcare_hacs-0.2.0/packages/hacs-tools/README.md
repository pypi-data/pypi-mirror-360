# HACS Tools

CRUD tools and protocol adapters for Healthcare Agent Communication Standard (HACS).

## Overview

`hacs-tools` provides essential tools for working with HACS data, including CRUD operations, protocol adapters, and integration utilities for various agent frameworks and healthcare systems.

## Key Components

### CRUD Operations
- Create, Read, Update, Delete operations for all HACS models
- Bulk operations for efficient data processing
- Transaction support and rollback capabilities
- Data validation and integrity checks

### Protocol Adapters
- **MCP Adapter**: Model Context Protocol integration
- **A2A Adapter**: Agent-to-Agent communication
- **AG-UI Adapter**: Agent-UI interface integration
- **LangGraph Adapter**: LangGraph workflow integration
- **CrewAI Adapter**: CrewAI framework integration

### Search and Retrieval
- Semantic search capabilities
- Structured query interface
- Full-text search with medical terminology
- Faceted search and filtering

### Memory Management
- Persistent memory storage
- Memory retrieval and querying
- Cross-agent memory sharing
- Memory lifecycle management

## Installation

```bash
pip install hacs-tools
```

## Quick Start

```python
from hacs_tools import HACScrud, MCPAdapter, SemanticSearch
from hacs_models import Patient, Observation

# CRUD operations
crud = HACScrud()

# Create a patient
patient = Patient(display_name="Alice Johnson")
patient_id = crud.create_patient(patient)

# Read patient
retrieved_patient = crud.get_patient(patient_id)

# Update patient
retrieved_patient.display_name = "Alice Johnson-Smith"
crud.update_patient(retrieved_patient)

# Search functionality
search = SemanticSearch()
results = search.find_patients(query="hypertension", limit=10)

# Protocol adapter usage
mcp_adapter = MCPAdapter()
mcp_adapter.register_tool("get_patient", crud.get_patient)
mcp_adapter.start_server()
```

## Protocol Adapters

### MCP Adapter
```python
from hacs_tools.adapters import MCPAdapter

adapter = MCPAdapter()
adapter.register_tool("search_patients", search.find_patients)
adapter.register_tool("get_observations", crud.get_observations)
adapter.start_server(port=8080)
```

### LangGraph Adapter
```python
from hacs_tools.adapters import LangGraphAdapter

adapter = LangGraphAdapter()
workflow = adapter.create_clinical_workflow()
result = workflow.run(patient_data=patient)
```

### CrewAI Adapter
```python
from hacs_tools.adapters import CrewAIAdapter

adapter = CrewAIAdapter()
crew = adapter.create_medical_crew()
result = crew.kickoff(inputs={"patient": patient})
```

## Advanced Features

### Bulk Operations
```python
# Bulk create patients
patients = [Patient(display_name=f"Patient {i}") for i in range(100)]
patient_ids = crud.bulk_create_patients(patients)

# Bulk update observations
observations = crud.get_observations(patient_ids=patient_ids)
crud.bulk_update_observations(observations)
```

### Memory Management
```python
from hacs_tools import MemoryManager

memory = MemoryManager()
memory.store("patient_history", patient_data)
history = memory.retrieve("patient_history")
```

## Documentation

For complete documentation, see the [HACS Documentation](https://github.com/solanovisitor/hacs/blob/main/docs/README.md).

## License

Licensed under the Apache License, Version 2.0. See [LICENSE](https://github.com/solanovisitor/hacs/blob/main/LICENSE) for details.

## Contributing

See [Contributing Guidelines](https://github.com/solanovisitor/hacs/blob/main/docs/contributing/guidelines.md) for information on how to contribute to HACS Tools.
