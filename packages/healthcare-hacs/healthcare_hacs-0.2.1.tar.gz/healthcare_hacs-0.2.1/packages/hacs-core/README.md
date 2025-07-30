# HACS Core

Core models and base classes for Healthcare Agent Communication Standard (HACS).

## Overview

`hacs-core` provides the foundational models and base classes that all other HACS packages build upon. It defines the core abstractions for healthcare agent communication, including actors, resources, memory management, and evidence handling.

## Key Components

### BaseResource
The foundational class for all HACS resources, providing:
- Unique resource identification
- Metadata management
- Serialization/deserialization
- Validation framework

### Actor
Represents entities that can perform actions in the healthcare system:
- Actor identification and authentication
- Role-based access control
- Audit trail management
- Permission validation

### MemoryBlock
Manages structured memory for healthcare agents:
- Persistent memory storage
- Memory retrieval and querying
- Memory lifecycle management
- Cross-agent memory sharing

### Evidence
Handles clinical evidence and supporting documentation:
- Evidence classification and scoring
- Source attribution and provenance
- Evidence linking and relationships
- Quality assessment metrics

## Installation

```bash
pip install hacs-core
```

## Quick Start

```python
from hacs_core import BaseResource, Actor, MemoryBlock, Evidence

# Create an actor
actor = Actor(
    actor_id="dr_smith",
    actor_type="clinician",
    display_name="Dr. Sarah Smith"
)

# Create a memory block
memory = MemoryBlock(
    memory_id="patient_history",
    content={"diagnosis": "hypertension"},
    actor_context=actor
)

# Create evidence
evidence = Evidence(
    evidence_id="guideline_001",
    title="Hypertension Management Guidelines",
    confidence_score=0.95,
    source="American Heart Association"
)
```

## Documentation

For complete documentation, see the [HACS Documentation](https://github.com/solanovisitor/hacs/blob/main/docs/modules/hacs-core.md).

## License

Licensed under the Apache License, Version 2.0. See [LICENSE](https://github.com/solanovisitor/hacs/blob/main/LICENSE) for details.

## Contributing

See [Contributing Guidelines](https://github.com/solanovisitor/hacs/blob/main/docs/contributing/guidelines.md) for information on how to contribute to HACS Core.
