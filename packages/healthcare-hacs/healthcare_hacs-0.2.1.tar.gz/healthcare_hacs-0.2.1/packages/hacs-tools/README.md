# HACS Tools

Core tools and utilities for Healthcare Agent Communication Standard (HACS).

## Overview

`hacs-tools` provides essential tools for working with HACS data, including CRUD operations, search functionality, validation, and core utilities. This package focuses on the core functionality, while protocol adapters have been moved to dedicated packages for better modularity.

## 📦 **Modular Adapter Packages**

Protocol adapters have been moved to separate packages for better dependency management:

- **[hacs-langgraph](https://pypi.org/project/hacs-langgraph/)**: LangGraph workflow integration
- **[hacs-crewai](https://pypi.org/project/hacs-crewai/)**: CrewAI multi-agent workflows  
- **[hacs-autogen](https://pypi.org/project/hacs-autogen/)**: AutoGen UI integration *(coming soon)*
- **[hacs-mcp](https://pypi.org/project/hacs-mcp/)**: Model Context Protocol *(coming soon)*
- **[hacs-a2a](https://pypi.org/project/hacs-a2a/)**: Agent-to-Agent communication *(coming soon)*

Install only the adapters you need:
```bash
pip install hacs-tools hacs-langgraph  # Core tools + LangGraph
pip install hacs-tools hacs-crewai     # Core tools + CrewAI
```

## Key Components

### CRUD Operations
- Create, Read, Update, Delete operations for all HACS models
- Bulk operations for efficient data processing
- Transaction support and rollback capabilities
- Data validation and integrity checks

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

### Validation and Utilities
- Data validation and schema checking
- Structured data processing
- Evidence management utilities
- Clinical data transformation

### Vectorization (Base Classes)
- Abstract embedding model interfaces
- Vector store protocols
- Metadata management for vectors
- Base vectorization utilities

## Installation

```bash
pip install hacs-tools
```

## Quick Start

```python
from hacs_tools import (
    CreateResource, ReadResource, UpdateResource, DeleteResource,
    StorageManager, PermissionManager
)
from hacs_models import Patient, Observation

# CRUD operations
storage = StorageManager()
permissions = PermissionManager()

# Create a patient
create_op = CreateResource()
patient = Patient(full_name="Alice Johnson", age=35)
patient_id = create_op.execute(patient, actor=doctor)

# Read patient
read_op = ReadResource()
retrieved_patient = read_op.execute(Patient, patient_id, actor=doctor)

# Update patient
update_op = UpdateResource()
retrieved_patient.full_name = "Alice Johnson-Smith"
update_op.execute(retrieved_patient, actor=doctor)

# Search functionality
from hacs_tools.search import SemanticSearch
search = SemanticSearch()
results = search.find_patients(query="hypertension", limit=10)
```

## Core Tools

### CRUD Operations
```python
from hacs_tools import CreatePatient, ReadPatient, CreateObservation

# Specialized CRUD operations
create_patient = CreatePatient()
patient = create_patient.execute(patient_data, actor=doctor)

read_patient = ReadPatient()
patient = read_patient.execute(patient_id, actor=nurse)

create_obs = CreateObservation()
observation = create_obs.execute(obs_data, actor=doctor)
```

### Memory Management
```python
from hacs_tools.memory import MemoryManager

memory = MemoryManager()
memory.store_memory(memory_block, actor=doctor)
memories = memory.retrieve_memories(patient_id, actor=doctor)
```

### Evidence Management
```python
from hacs_tools.evidence import EvidenceManager

evidence_mgr = EvidenceManager()
evidence = evidence_mgr.create_evidence(content, evidence_type, actor=researcher)
evidence_mgr.link_to_patient(evidence, patient_id, actor=doctor)
```

### Validation
```python
from hacs_tools.validation import DataValidator

validator = DataValidator()
is_valid = validator.validate_patient(patient_data)
errors = validator.get_validation_errors(patient_data)
```

### Structured Data Processing
```python
from hacs_tools.structured import StructuredProcessor

processor = StructuredProcessor()
structured_data = processor.process_clinical_text(text, actor=doctor)
```

## Legacy Protocol Adapters

⚠️ **DEPRECATION NOTICE**: The following adapters are still available in `hacs-tools` but will be moved to dedicated packages:

### MCP Adapter *(will move to hacs-mcp)*
```python
from hacs_tools.adapters import MCPAdapter

adapter = MCPAdapter()
adapter.register_tool("search_patients", search.find_patients)
adapter.start_server(port=8080)
```

### A2A Adapter *(will move to hacs-a2a)*
```python
from hacs_tools.adapters import A2AAdapter

adapter = A2AAdapter()
envelope = adapter.create_envelope(message, recipient="agent-2")
```

### AG-UI Adapter *(will move to hacs-autogen)*
```python
from hacs_tools.adapters import AGUIAdapter

adapter = AGUIAdapter()
ui_event = adapter.create_notification("Patient updated", "success")
```

## Migration Guide

### From Monolithic to Modular

**Old approach** (still works):
```python
from hacs_tools.adapters import LangGraphAdapter, CrewAIAdapter
```

**New modular approach** (recommended):
```python
from hacs_langgraph import LangGraphAdapter
from hacs_crewai import CrewAIAdapter
```

### Benefits of Modular Packages
- **Smaller installations**: Install only what you need
- **Faster imports**: No unused dependencies
- **Independent versioning**: Each adapter evolves separately
- **Better testing**: Isolated test suites

## Advanced Features

### Bulk Operations
```python
# Bulk create patients
patients = [Patient(full_name=f"Patient {i}", age=30+i) for i in range(100)]
bulk_create = CreateResource()
patient_ids = bulk_create.bulk_execute(patients, actor=admin)
```

### Storage Backend Configuration
```python
from hacs_tools import set_storage_backend, StorageBackend

# Configure storage backend
set_storage_backend(StorageBackend.POSTGRESQL)
storage = get_storage_manager()
```

### Permission Management
```python
from hacs_tools import PermissionManager

permissions = PermissionManager()
permissions.grant_permission(actor, "read:patient", resource_id)
can_access = permissions.check_permission(actor, "read:patient", resource_id)
```

## Documentation

For complete documentation, see the [HACS Documentation](https://github.com/solanovisitor/hacs/blob/main/docs/README.md).

## Related Packages

- **[hacs-core](https://pypi.org/project/hacs-core/)**: Core HACS data models and utilities
- **[hacs-models](https://pypi.org/project/hacs-models/)**: Clinical data models (Patient, Observation, etc.)
- **[hacs-langgraph](https://pypi.org/project/hacs-langgraph/)**: LangGraph workflow integration
- **[hacs-crewai](https://pypi.org/project/hacs-crewai/)**: CrewAI multi-agent workflows

## License

Licensed under the Apache License, Version 2.0. See [LICENSE](https://github.com/solanovisitor/hacs/blob/main/LICENSE) for details.

## Contributing

See [Contributing Guidelines](https://github.com/solanovisitor/hacs/blob/main/docs/contributing/guidelines.md) for information on how to contribute to HACS Tools.
