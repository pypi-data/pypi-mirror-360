# HACS Qdrant Integration

Qdrant vector store integration for HACS (Healthcare Agent Communication Standard) vectorization.

## Installation

```bash
pip install hacs-qdrant
```

## Quick Start

```python
from hacs_qdrant import QdrantVectorStore
from hacs_tools.vectorization import HACSVectorizer

# Create Qdrant vector store
vector_store = QdrantVectorStore(collection_name="my_collection")

# Use with any embedding model
from your_embedding_provider import YourEmbeddingModel
embedding_model = YourEmbeddingModel()

# Create vectorizer
vectorizer = HACSVectorizer(embedding_model, vector_store)

# Vectorize HACS resources
vector_id = vectorizer.vectorize_memory(memory_block, actor)
results = vectorizer.search_memories("patient symptoms", limit=5)
```

## Features

- **Local and Cloud**: Works with local Qdrant instances or Qdrant Cloud
- **Automatic Scaling**: Automatically adjusts collection dimensions based on embeddings
- **Metadata Support**: Full support for HACS vector metadata
- **Performance**: Optimized for healthcare AI workloads

## Configuration

### Local Qdrant

```python
from qdrant_client import QdrantClient
from hacs_qdrant import QdrantVectorStore

# In-memory (default)
store = QdrantVectorStore()

# Local instance
client = QdrantClient(url="http://localhost:6333")
store = QdrantVectorStore(client=client)
```

### Qdrant Cloud

```python
from qdrant_client import QdrantClient
from hacs_qdrant import QdrantVectorStore

client = QdrantClient(
    url="https://your-cluster.qdrant.io",
    api_key="your-api-key"
)
store = QdrantVectorStore(client=client)
```

## API Reference

### QdrantVectorStore

The main vector store implementation for Qdrant.

#### Constructor

```python
QdrantVectorStore(client=None, collection_name="hacs_vectors")
```

- `client`: Optional Qdrant client instance. If None, uses in-memory storage.
- `collection_name`: Name of the Qdrant collection to use.

#### Methods

- `store_vector(vector_id, embedding, metadata)`: Store a vector with metadata
- `search_similar(query_embedding, limit, filters)`: Search for similar vectors
- `get_vector(vector_id)`: Retrieve a specific vector
- `delete_vector(vector_id)`: Delete a vector

## Integration with HACS

This package integrates seamlessly with the HACS ecosystem:

```python
from hacs_core import MemoryBlock, Evidence, Actor
from hacs_qdrant import QdrantVectorStore
from hacs_tools.vectorization import HACSVectorizer

# Your embedding model (from any provider)
embedding_model = YourEmbeddingModel()

# Qdrant vector store
vector_store = QdrantVectorStore(collection_name="clinical_vectors")

# Create vectorizer
vectorizer = HACSVectorizer(embedding_model, vector_store)

# Create test data
actor = Actor(id="doc1", name="Dr. Smith", role="physician")
memory = MemoryBlock(
    id="mem1",
    content="Patient shows signs of hypertension",
    memory_type="clinical_observation"
)

# Vectorize and search
vector_id = vectorizer.vectorize_memory(memory, actor)
results = vectorizer.search_memories("blood pressure", limit=5)
```

## Requirements

- Python 3.10+
- qdrant-client>=1.6.0
- hacs-tools>=0.1.0

## License

Apache-2.0 License. See LICENSE file for details.

## Contributing

Contributions are welcome! Please see the main HACS repository for contribution guidelines.

## Support

For support, please open an issue in the main HACS repository. 