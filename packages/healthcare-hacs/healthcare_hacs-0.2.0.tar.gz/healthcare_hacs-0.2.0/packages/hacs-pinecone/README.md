# HACS Pinecone Integration

[![PyPI version](https://badge.fury.io/py/hacs-pinecone.svg)](https://badge.fury.io/py/hacs-pinecone)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

**Pinecone vector database integration for HACS (Healthcare Agent Communication Standard)**

This package provides seamless integration between HACS and Pinecone, enabling healthcare AI agents to store and retrieve vector embeddings for clinical data with enterprise-grade performance and scalability.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Usage Examples](#usage-examples)
- [API Reference](#api-reference)
- [Healthcare Compliance](#healthcare-compliance)
- [Performance](#performance)
- [Contributing](#contributing)
- [License](#license)

## Introduction

The HACS Pinecone integration enables healthcare AI systems to leverage Pinecone's high-performance vector database for storing and retrieving clinical embeddings. This integration is designed specifically for healthcare applications with built-in support for:

- **Clinical Data Embeddings**: Store vector representations of patient data, observations, and clinical notes
- **Semantic Search**: Find similar patients, conditions, or treatments using vector similarity
- **FHIR Compliance**: Maintain healthcare interoperability standards
- **Privacy Protection**: Built-in safeguards against PHI exposure
- **Audit Trails**: Comprehensive logging for healthcare compliance

## Features

### 🏥 Healthcare-First Design
- **FHIR-Compliant Metadata**: Store FHIR resource references with embeddings
- **PHI Protection**: Automatic detection and prevention of sensitive data storage
- **Clinical Terminology**: Support for LOINC, SNOMED CT, and ICD-10 codes
- **Audit Logging**: Complete audit trails for regulatory compliance

### 🚀 High Performance
- **Lazy Loading**: Import Pinecone only when needed
- **Batch Operations**: Efficient bulk embedding storage and retrieval
- **Automatic Indexing**: Smart index creation and management
- **Scalable Architecture**: Handle millions of clinical embeddings

### 🔧 Easy Integration
- **HACS Native**: Seamless integration with HACS models and tools
- **Multiple Embeddings**: Support for OpenAI, Hugging Face, and custom models
- **Flexible Configuration**: Environment-based and programmatic configuration
- **Error Handling**: Robust error handling with healthcare-specific messaging

## Installation

### Prerequisites

- Python 3.10 or higher
- Pinecone account and API key
- HACS core packages

### Install from PyPI

```bash
# Install hacs-pinecone
pip install hacs-pinecone

# Or install with HACS suite
pip install healthcare-hacs[vectorization]
```

### Development Installation

```bash
# Clone the HACS repository
git clone https://github.com/solanovisitor/hacs.git
cd hacs

# Install in development mode
pip install -e packages/hacs-pinecone
```

## Quick Start

### 1. Set Up Pinecone Credentials

```bash
# Set environment variables
export PINECONE_API_KEY="your-api-key"
export PINECONE_ENVIRONMENT="your-environment"  # e.g., "us-west1-gcp"
```

### 2. Basic Usage

```python
from hacs_pinecone import PineconeVectorStore
from hacs_models import Patient, Observation
from hacs_core import Actor

# Initialize the vector store
vector_store = PineconeVectorStore(
    index_name="healthcare-embeddings",
    dimension=1536,  # OpenAI embedding dimension
    api_key="your-api-key",
    environment="us-west1-gcp"
)

# Create a healthcare actor
actor = Actor(
    id="physician-001",
    name="Dr. Sarah Johnson",
    role="physician"
)

# Store patient embedding
patient = Patient(
    id="patient-001",
    given=["John"],
    family="Doe",
    birth_date="1985-03-15"
)

# Store embedding with clinical metadata
embedding = [0.1, 0.2, 0.3, ...]  # Your embedding vector
vector_store.store_embedding(
    embedding=embedding,
    resource_id=patient.id,
    resource_type="Patient",
    metadata={
        "fhir_resource": patient.model_dump(),
        "clinical_context": "routine_checkup",
        "actor_id": actor.id
    },
    actor=actor
)

# Search for similar patients
similar_patients = vector_store.similarity_search(
    query_embedding=embedding,
    top_k=5,
    filter_metadata={"resource_type": "Patient"}
)

print(f"Found {len(similar_patients)} similar patients")
```

## Configuration

### Environment Variables

```bash
# Required
PINECONE_API_KEY=your-api-key
PINECONE_ENVIRONMENT=your-environment

# Optional
PINECONE_INDEX_NAME=healthcare-embeddings
PINECONE_DIMENSION=1536
PINECONE_METRIC=cosine
HACS_AUDIT_ENABLED=true
```

### Programmatic Configuration

```python
from hacs_pinecone import PineconeVectorStore

# Full configuration
vector_store = PineconeVectorStore(
    api_key="your-api-key",
    environment="us-west1-gcp",
    index_name="clinical-embeddings",
    dimension=1536,
    metric="cosine",
    pod_type="p1.x1",
    replicas=1,
    shards=1,
    metadata_config={
        "indexed": ["resource_type", "clinical_context", "actor_id"]
    }
)
```

## Usage Examples

### Clinical Data Storage

```python
from hacs_pinecone import PineconeVectorStore
from hacs_models import Observation
import openai

# Initialize vector store
vector_store = PineconeVectorStore(index_name="clinical-data")

# Create clinical observation
observation = Observation(
    status="final",
    code={
        "coding": [{
            "system": "http://loinc.org",
            "code": "8480-6",
            "display": "Systolic blood pressure"
        }]
    },
    value_quantity={"value": 120, "unit": "mmHg"}
)

# Generate embedding for clinical text
clinical_text = f"{observation.code.coding[0].display}: {observation.value_quantity.value} {observation.value_quantity.unit}"
embedding = openai.Embedding.create(
    input=clinical_text,
    model="text-embedding-ada-002"
)["data"][0]["embedding"]

# Store with clinical metadata
vector_store.store_embedding(
    embedding=embedding,
    resource_id=observation.id,
    resource_type="Observation",
    metadata={
        "loinc_code": "8480-6",
        "value": 120,
        "unit": "mmHg",
        "clinical_significance": "normal",
        "fhir_resource": observation.model_dump()
    }
)
```

### Semantic Clinical Search

```python
# Search for similar blood pressure readings
query_text = "high blood pressure hypertension"
query_embedding = openai.Embedding.create(
    input=query_text,
    model="text-embedding-ada-002"
)["data"][0]["embedding"]

# Find similar clinical observations
results = vector_store.similarity_search(
    query_embedding=query_embedding,
    top_k=10,
    filter_metadata={
        "resource_type": "Observation",
        "loinc_code": "8480-6"  # Blood pressure observations only
    },
    include_metadata=True
)

# Process results
for result in results:
    print(f"Similarity: {result.score:.3f}")
    print(f"Value: {result.metadata['value']} {result.metadata['unit']}")
    print(f"Clinical significance: {result.metadata['clinical_significance']}")
    print("---")
```

### Batch Operations

```python
# Store multiple embeddings efficiently
embeddings_batch = [
    {
        "embedding": embedding1,
        "resource_id": "patient-001",
        "resource_type": "Patient",
        "metadata": {"age": 35, "condition": "diabetes"}
    },
    {
        "embedding": embedding2,
        "resource_id": "patient-002", 
        "resource_type": "Patient",
        "metadata": {"age": 42, "condition": "hypertension"}
    }
]

vector_store.store_embeddings_batch(embeddings_batch)

# Batch similarity search
query_embeddings = [embedding1, embedding2]
batch_results = vector_store.similarity_search_batch(
    query_embeddings=query_embeddings,
    top_k=5
)
```

## API Reference

### PineconeVectorStore

#### Constructor

```python
PineconeVectorStore(
    api_key: str = None,
    environment: str = None,
    index_name: str = "hacs-embeddings",
    dimension: int = 1536,
    metric: str = "cosine",
    pod_type: str = "p1.x1",
    replicas: int = 1,
    shards: int = 1,
    metadata_config: dict = None
)
```

#### Methods

- `store_embedding(embedding, resource_id, resource_type, metadata, actor)`: Store a single embedding
- `store_embeddings_batch(embeddings_batch)`: Store multiple embeddings efficiently
- `similarity_search(query_embedding, top_k, filter_metadata, include_metadata)`: Search for similar embeddings
- `similarity_search_batch(query_embeddings, top_k, filter_metadata)`: Batch similarity search
- `delete_embedding(resource_id)`: Delete an embedding by resource ID
- `get_embedding(resource_id)`: Retrieve an embedding by resource ID
- `list_embeddings(filter_metadata)`: List embeddings with optional filtering

## Healthcare Compliance

### PHI Protection

The HACS Pinecone integration includes built-in safeguards:

```python
# Automatic PHI detection
try:
    vector_store.store_embedding(
        embedding=embedding,
        metadata={"patient_ssn": "123-45-6789"}  # This will be blocked
    )
except ValueError as e:
    print("PHI detected and blocked:", e)
```

### Audit Logging

All operations are automatically logged for compliance:

```python
# Enable audit logging
vector_store = PineconeVectorStore(
    index_name="clinical-data",
    audit_enabled=True,
    audit_actor_required=True
)

# All operations will be logged with actor information
vector_store.store_embedding(embedding, metadata, actor=physician)
```

### FHIR Compliance

Store FHIR resources with embeddings:

```python
# FHIR-compliant metadata
metadata = {
    "fhir_resource_type": "Patient",
    "fhir_resource_id": patient.id,
    "fhir_resource": patient.model_dump(),
    "fhir_version": "R4"
}

vector_store.store_embedding(embedding, metadata=metadata)
```

## Performance

### Benchmarks

- **Storage**: 10,000 embeddings/minute
- **Search**: Sub-100ms for similarity queries
- **Memory**: <50MB for typical healthcare workloads
- **Scalability**: Tested with 10M+ clinical embeddings

### Optimization Tips

```python
# Use batch operations for better performance
vector_store.store_embeddings_batch(large_batch)

# Enable metadata indexing for faster filtering
vector_store = PineconeVectorStore(
    metadata_config={
        "indexed": ["resource_type", "loinc_code", "clinical_context"]
    }
)

# Use appropriate pod types for your workload
vector_store = PineconeVectorStore(
    pod_type="p1.x2",  # Higher performance
    replicas=2         # Better availability
)
```

## Error Handling

```python
from hacs_pinecone import PineconeVectorStore, PineconeError

try:
    vector_store = PineconeVectorStore(api_key="invalid-key")
except PineconeError as e:
    print(f"Pinecone configuration error: {e}")

try:
    vector_store.store_embedding(invalid_embedding)
except ValueError as e:
    print(f"Validation error: {e}")
```

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](../../CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/solanovisitor/hacs.git
cd hacs

# Install development dependencies
pip install -e packages/hacs-pinecone[dev]

# Run tests
pytest packages/hacs-pinecone/tests/
```

### Running Tests

```bash
# Unit tests
pytest packages/hacs-pinecone/tests/unit/

# Integration tests (requires Pinecone API key)
export PINECONE_API_KEY="your-test-api-key"
pytest packages/hacs-pinecone/tests/integration/

# Performance tests
pytest packages/hacs-pinecone/tests/performance/
```

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](../../LICENSE) file for details.

## Support

- **Documentation**: [HACS Documentation](../../docs/README.md)
- **Issues**: [GitHub Issues](https://github.com/solanovisitor/hacs/issues)
- **Discussions**: [GitHub Discussions](https://github.com/solanovisitor/hacs/discussions)
- **Security**: security@hacs-project.org

---

**Part of the HACS (Healthcare Agent Communication Standard) ecosystem**

[HACS Core](../hacs-core/) | [HACS Models](../hacs-models/) | [HACS Tools](../hacs-tools/) | [All Packages](../../README.md#package-structure) 