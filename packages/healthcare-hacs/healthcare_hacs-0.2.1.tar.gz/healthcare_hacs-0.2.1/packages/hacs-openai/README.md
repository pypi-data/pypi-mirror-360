# HACS OpenAI Integration

OpenAI embedding and generation integration for HACS (Healthcare Agent Communication Standard) vectorization.

## Installation

```bash
pip install hacs-openai
```

You'll also need a vector store package:

```bash
pip install hacs-openai hacs-qdrant  # or hacs-pinecone
```

## Quick Start

```python
import os
from hacs_openai import create_openai_vectorizer
from hacs_qdrant import QdrantVectorStore
from hacs_core import MemoryBlock, Actor

# Set up OpenAI API key
os.environ["OPENAI_API_KEY"] = "your-api-key-here"

# Create vector store
vector_store = QdrantVectorStore(collection_name="clinical_vectors")

# Create vectorizer with OpenAI embeddings
vectorizer = create_openai_vectorizer(
    model="text-embedding-3-small",
    api_key=os.getenv("OPENAI_API_KEY"),
    vector_store=vector_store
)

# Create test data
actor = Actor(id="doc1", name="Dr. Smith", role="physician")
memory = MemoryBlock(
    id="mem1",
    content="Patient presents with chest pain and shortness of breath",
    memory_type="clinical_observation"
)

# Vectorize and search
vector_id = vectorizer.vectorize_memory(memory, actor)
results = vectorizer.search_memories("cardiac symptoms", limit=5)
```

## Features

- **High-Quality Embeddings**: Uses OpenAI's state-of-the-art embedding models
- **Multiple Models**: Support for text-embedding-3-small, text-embedding-3-large, and ada-002
- **Healthcare Optimized**: Designed for medical and clinical content
- **Cost Efficient**: Optimized for healthcare AI workloads

## Supported Models

| Model | Dimensions | Cost (per 1M tokens) | Best For |
|-------|------------|---------------------|----------|
| text-embedding-3-small | 1536 | $0.02 | General purpose, cost-effective |
| text-embedding-3-large | 3072 | $0.13 | High accuracy, complex medical content |
| text-embedding-ada-002 | 1536 | $0.10 | Legacy model, good compatibility |

## Configuration

### Basic Usage

```python
from hacs_openai import OpenAIEmbedding

# Create embedding model
embedding_model = OpenAIEmbedding(
    model="text-embedding-3-small",
    api_key="your-api-key"
)

# Generate embeddings
embedding = embedding_model.embed("Patient has hypertension")
print(f"Embedding dimensions: {embedding_model.dimensions}")
```

### With Vector Store

```python
from hacs_openai import create_openai_vectorizer
from hacs_qdrant import QdrantVectorStore

# Complete setup
vector_store = QdrantVectorStore()
vectorizer = create_openai_vectorizer(
    model="text-embedding-3-large",  # Higher quality
    api_key="your-api-key",
    vector_store=vector_store
)
```

### Environment Variables

You can set your API key as an environment variable:

```bash
export OPENAI_API_KEY="your-api-key-here"
```

Then use without explicitly passing the key:

```python
from hacs_openai import OpenAIEmbedding

# API key will be read from environment
embedding_model = OpenAIEmbedding()
```

## API Reference

### OpenAIEmbedding

The main embedding model implementation.

#### Constructor

```python
OpenAIEmbedding(model="text-embedding-3-small", api_key=None)
```

- `model`: OpenAI embedding model name
- `api_key`: OpenAI API key (optional if set in environment)

#### Methods

- `embed(text)`: Generate embedding for text
- `dimensions`: Property returning embedding dimensions

### Helper Functions

#### create_openai_embedding

```python
create_openai_embedding(model="text-embedding-3-small", api_key=None)
```

Convenience function to create an OpenAI embedding model.

#### create_openai_vectorizer

```python
create_openai_vectorizer(model="text-embedding-3-small", api_key=None, vector_store=None)
```

Create a complete vectorizer with OpenAI embeddings and a vector store.

## Integration Examples

### Clinical Decision Support

```python
from hacs_openai import create_openai_vectorizer
from hacs_qdrant import QdrantVectorStore
from hacs_core import Evidence, EvidenceType

# Set up vectorizer
vector_store = QdrantVectorStore(collection_name="clinical_guidelines")
vectorizer = create_openai_vectorizer(
    model="text-embedding-3-large",  # High accuracy for guidelines
    vector_store=vector_store
)

# Add clinical guidelines
guideline = Evidence(
    id="guideline1",
    citation="AHA Hypertension Guidelines 2023",
    content="For adults with hypertension, lifestyle modifications should be the first-line treatment...",
    evidence_type=EvidenceType.CLINICAL_GUIDELINE,
    confidence_score=0.95
)

vectorizer.vectorize_evidence(guideline)

# Search for relevant guidelines
results = vectorizer.search_evidence("blood pressure management", limit=3)
```

### Patient Case Analysis

```python
from hacs_core import Patient, Observation
from hacs_models import ObservationType

# Create patient data
patient = Patient(
    id="patient1",
    display_name="John Doe",
    birth_date="1970-01-01"
)

observation = Observation(
    id="obs1",
    patient_id="patient1",
    observation_type=ObservationType.VITAL_SIGNS,
    value_quantity={"value": 180, "unit": "mmHg"},
    display_name="Systolic Blood Pressure"
)

# Vectorize patient data
patient_vector = vectorizer.vectorize_memory(
    MemoryBlock(
        id="patient_summary",
        content=f"Patient {patient.display_name} with systolic BP {observation.value_quantity['value']} mmHg",
        memory_type="patient_summary"
    )
)

# Find similar cases
similar_cases = vectorizer.search_memories("hypertensive patient", limit=5)
```

## Performance Tips

1. **Model Selection**: Use `text-embedding-3-small` for cost-effectiveness, `text-embedding-3-large` for accuracy
2. **Batch Processing**: Process multiple texts together when possible
3. **Caching**: Cache embeddings for frequently accessed content
4. **Rate Limits**: Be aware of OpenAI's rate limits in production

## Error Handling

```python
from hacs_openai import OpenAIEmbedding

try:
    embedding_model = OpenAIEmbedding(api_key="invalid-key")
    embedding = embedding_model.embed("test text")
except Exception as e:
    print(f"OpenAI error: {e}")
    # Handle error appropriately
```

## Requirements

- Python 3.10+
- openai>=1.0.0
- hacs-tools>=0.1.0
- A vector store package (hacs-qdrant, hacs-pinecone, etc.)

## License

Apache-2.0 License. See LICENSE file for details.

## Contributing

Contributions are welcome! Please see the main HACS repository for contribution guidelines.

## Support

For support, please open an issue in the main HACS repository. 