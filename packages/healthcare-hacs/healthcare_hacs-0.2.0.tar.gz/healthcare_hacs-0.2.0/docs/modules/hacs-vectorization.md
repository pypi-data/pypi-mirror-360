# HACS Vectorization

HACS provides comprehensive vectorization capabilities to enable semantic search and retrieval for Evidence and Memory content. This allows AI agents to find relevant information based on meaning rather than just keyword matching.

## Overview

The vectorization system supports:

- **Multiple Embedding Models**: Sentence Transformers, OpenAI, Cohere
- **Multiple Vector Stores**: Qdrant, Pinecone, Mem0
- **Automatic Vectorization**: Evidence and MemoryBlock content
- **Semantic Search**: Find similar content by meaning
- **Metadata Filtering**: Filter by type, confidence, actor, etc.
- **Performance Optimization**: Efficient storage and retrieval

## Quick Start

### Basic Setup with Sentence Transformers

```python
from hacs_tools import create_sentence_transformer_vectorizer
from hacs_core import MemoryBlock, Evidence, Actor

# Create vectorizer (no API key required)
vectorizer = create_sentence_transformer_vectorizer(
    model_name="all-MiniLM-L6-v2",
    vector_store_type="qdrant"
)

# Create sample data
actor = Actor(id="doc-001", name="Dr. Smith", role="physician")
memory = MemoryBlock(
    id="mem-001",
    memory_type="episodic", 
    content="Patient showed improvement after medication adjustment",
    importance_score=0.8
)

# Vectorize content
vector_id = vectorizer.vectorize_memory(memory, actor)
print(f"Vectorized: {vector_id}")

# Search for similar content
results = vectorizer.search_memories("medication changes", limit=5)
for vector_id, score, metadata in results:
    print(f"Found: {metadata.resource_id} (score: {score:.3f})")
```

## Embedding Models

### Sentence Transformers (Recommended for Getting Started)

```python
from hacs_tools import create_sentence_transformer_vectorizer

# Local embedding model - no API key required
vectorizer = create_sentence_transformer_vectorizer(
    model_name="all-MiniLM-L6-v2",  # Fast, 384 dimensions
    # model_name="all-mpnet-base-v2",  # Higher quality, 768 dimensions
    vector_store_type="qdrant"
)
```

**Popular Models:**
- `all-MiniLM-L6-v2`: Fast, 384 dimensions, good for most use cases
- `all-mpnet-base-v2`: Higher quality, 768 dimensions
- `all-MiniLM-L12-v2`: Balance of speed and quality, 384 dimensions
- `multi-qa-MiniLM-L6-cos-v1`: Optimized for Q&A tasks

### OpenAI Embeddings

```python
from hacs_tools import create_openai_vectorizer
import os

# Requires OpenAI API key
vectorizer = create_openai_vectorizer(
    model="text-embedding-3-small",  # 1536 dimensions, cost-effective
    # model="text-embedding-3-large",  # 3072 dimensions, highest quality
    api_key=os.getenv("OPENAI_API_KEY"),
    vector_store_type="qdrant"
)
```

**Available Models:**
- `text-embedding-3-small`: 1536 dimensions, cost-effective
- `text-embedding-3-large`: 3072 dimensions, highest quality
- `text-embedding-ada-002`: 1536 dimensions, legacy model

### Cohere Embeddings

```python
from hacs_tools import create_cohere_vectorizer
import os

# Requires Cohere API key
vectorizer = create_cohere_vectorizer(
    model="embed-english-v3.0",  # 1024 dimensions
    # model="embed-multilingual-v3.0",  # Multilingual support
    api_key=os.getenv("COHERE_API_KEY"),
    vector_store_type="qdrant"
)
```

**Available Models:**
- `embed-english-v3.0`: 1024 dimensions, English-optimized
- `embed-multilingual-v3.0`: 1024 dimensions, multilingual
- `embed-english-light-v3.0`: 384 dimensions, faster
- `embed-multilingual-light-v3.0`: 384 dimensions, multilingual + faster

## Vector Stores

### Qdrant (Recommended)

```python
from hacs_tools import QdrantVectorStore, HACSVectorizer, SentenceTransformerEmbedding
from qdrant_client import QdrantClient

# In-memory (for development)
vectorizer = create_sentence_transformer_vectorizer(
    vector_store_type="qdrant"
)

# Persistent local storage
client = QdrantClient(path="./qdrant_storage")
vector_store = QdrantVectorStore(client=client, collection_name="hacs_vectors")
embedding_model = SentenceTransformerEmbedding("all-MiniLM-L6-v2")
vectorizer = HACSVectorizer(embedding_model, vector_store)

# Qdrant Cloud
client = QdrantClient(
    url="https://your-cluster.qdrant.io",
    api_key="your-api-key"
)
vector_store = QdrantVectorStore(client=client, collection_name="hacs_vectors")
```

### Pinecone

```python
from hacs_tools import create_sentence_transformer_vectorizer

# Requires Pinecone API key and environment
vectorizer = create_sentence_transformer_vectorizer(
    vector_store_type="pinecone",
    api_key="your-pinecone-api-key",
    environment="your-environment",
    index_name="hacs-vectors"
)
```

### Mem0

```python
from hacs_tools import create_sentence_transformer_vectorizer

# Mem0 managed service
vectorizer = create_sentence_transformer_vectorizer(
    vector_store_type="mem0",
    config={
        "vector_store": {
            "provider": "qdrant",
            "config": {
                "host": "localhost",
                "port": 6333
            }
        }
    }
)
```

## Vectorizing Content

### Memory Vectorization

```python
from hacs_core import MemoryBlock, Actor

# Create memory
memory = MemoryBlock(
    id="mem-001",
    memory_type="episodic",
    content="Patient reported chest pain during exercise stress test. ECG showed ST depression in leads V4-V6. Recommended cardiac catheterization.",
    importance_score=0.9,
    metadata={
        "patient_id": "pat-123",
        "procedure": "stress_test",
        "tags": ["chest_pain", "cardiology", "catheterization"]
    }
)

# Vectorize
actor = Actor(id="doc-001", name="Dr. Smith", role="physician")
vector_id = vectorizer.vectorize_memory(memory, actor)

# The memory.vector_id is automatically updated
print(f"Memory vector ID: {memory.vector_id}")
```

### Evidence Vectorization

```python
from hacs_core import Evidence, EvidenceType

# Create evidence
evidence = Evidence(
    id="evd-001", 
    citation="AHA/ACC 2021 Guidelines for Coronary Artery Disease",
    content="Exercise stress testing is recommended for patients with intermediate pretest probability of coronary artery disease. ST depression ≥1mm in multiple leads suggests significant coronary stenosis.",
    evidence_type=EvidenceType.GUIDELINE,
    confidence_score=0.95,
    tags=["stress_test", "coronary_disease", "guidelines"]
)

# Vectorize
vector_id = vectorizer.vectorize_evidence(evidence, actor)
print(f"Evidence vector ID: {evidence.vector_id}")
```

## Semantic Search

### Basic Search

```python
# Search memories
memory_results = vectorizer.search_memories(
    query="chest pain during exercise",
    limit=10
)

for vector_id, similarity_score, metadata in memory_results:
    print(f"Memory {metadata.resource_id}: {similarity_score:.3f}")
    print(f"  Type: {metadata.memory_type}")
    print(f"  Preview: {metadata.content_preview}")
```

### Filtered Search

```python
# Search specific memory types
episodic_results = vectorizer.search_memories(
    query="patient consultation",
    limit=5,
    memory_type="episodic",  # Only episodic memories
    actor=actor  # Only memories from this actor
)

# Search high-confidence evidence
high_conf_evidence = vectorizer.search_evidence(
    query="treatment guidelines",
    limit=5,
    evidence_type="guideline",  # Only guidelines
    min_confidence=0.9,  # High confidence only
    actor=actor
)
```

### Cross-Content Search

```python
# Search across both memories and evidence
all_results = vectorizer.search_all(
    query="cardiac catheterization complications",
    limit=5,
    actor=actor
)

print("Memories:")
for vector_id, score, metadata in all_results["memories"]:
    print(f"  {metadata.resource_id}: {score:.3f}")

print("Evidence:")
for vector_id, score, metadata in all_results["evidence"]:
    print(f"  {metadata.resource_id}: {score:.3f}")
```

## Advanced Usage

### Custom Vector Store

```python
from hacs_tools import VectorStore, VectorMetadata
from typing import List, Tuple, Optional, Dict, Any

class CustomVectorStore(VectorStore):
    """Custom vector store implementation."""
    
    def __init__(self):
        self.vectors = {}
    
    def store_vector(self, vector_id: str, embedding: List[float], 
                    metadata: VectorMetadata) -> bool:
        self.vectors[vector_id] = (embedding, metadata)
        return True
    
    def search_similar(self, query_embedding: List[float], limit: int = 10,
                      filters: Optional[Dict[str, Any]] = None) -> List[Tuple[str, float, VectorMetadata]]:
        # Implement similarity search
        results = []
        for vid, (embedding, metadata) in self.vectors.items():
            score = self._cosine_similarity(query_embedding, embedding)
            results.append((vid, score, metadata))
        
        # Sort by similarity and return top results
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:limit]
    
    def get_vector(self, vector_id: str) -> Optional[Tuple[List[float], VectorMetadata]]:
        return self.vectors.get(vector_id)
    
    def delete_vector(self, vector_id: str) -> bool:
        if vector_id in self.vectors:
            del self.vectors[vector_id]
            return True
        return False
    
    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        import numpy as np
        a_np = np.array(a)
        b_np = np.array(b)
        return float(np.dot(a_np, b_np) / (np.linalg.norm(a_np) * np.linalg.norm(b_np)))

# Use custom vector store
from hacs_tools import SentenceTransformerEmbedding, HACSVectorizer

embedding_model = SentenceTransformerEmbedding("all-MiniLM-L6-v2")
vector_store = CustomVectorStore()
vectorizer = HACSVectorizer(embedding_model, vector_store)
```

### Batch Operations

```python
# Vectorize multiple items
memories = [memory1, memory2, memory3]
evidence_items = [evidence1, evidence2, evidence3]

# Batch vectorize memories
for memory in memories:
    vector_id = vectorizer.vectorize_memory(memory, actor)
    if vector_id:
        print(f"✅ Vectorized {memory.id}")
    else:
        print(f"❌ Failed {memory.id}")

# Batch search
queries = ["chest pain", "medication side effects", "discharge planning"]
for query in queries:
    results = vectorizer.search_all(query, limit=3)
    print(f"Query '{query}': {len(results['memories'])} memories, {len(results['evidence'])} evidence")
```

## Performance Optimization

### Model Selection

| Model | Dimensions | Speed | Quality | Use Case |
|-------|------------|-------|---------|----------|
| all-MiniLM-L6-v2 | 384 | Fast | Good | General purpose |
| all-mpnet-base-v2 | 768 | Medium | Better | Higher quality needed |
| text-embedding-3-small | 1536 | Medium | High | Production with API budget |
| text-embedding-3-large | 3072 | Slow | Highest | Maximum quality |

### Vector Store Comparison

| Store | Setup | Scalability | Features | Cost |
|-------|-------|-------------|----------|------|
| Qdrant (local) | Easy | Medium | Full-featured | Free |
| Qdrant Cloud | Easy | High | Full-featured | Paid |
| Pinecone | Medium | High | Managed | Paid |
| Mem0 | Easy | High | AI-native | Paid |

### Best Practices

1. **Choose the Right Model**:
   - Start with Sentence Transformers for development
   - Use OpenAI for production if budget allows
   - Consider Cohere for multilingual content

2. **Optimize Vector Dimensions**:
   - Lower dimensions = faster search, less storage
   - Higher dimensions = better quality, more storage
   - 384-768 dimensions work well for most healthcare content

3. **Implement Caching**:
   ```python
   # Cache embeddings to avoid recomputation
   content_hash = vectorizer._hash_content(content)
   if content_hash in embedding_cache:
       embedding = embedding_cache[content_hash]
   else:
       embedding = vectorizer.embedding_model.embed(content)
       embedding_cache[content_hash] = embedding
   ```

4. **Use Metadata Filtering**:
   ```python
   # Filter by actor, type, confidence, etc. for faster search
   results = vectorizer.search_evidence(
       query="treatment options",
       evidence_type="guideline",
       min_confidence=0.8,
       actor=actor
   )
   ```

## Integration with AI Agents

### LangGraph Integration

```python
from hacs_tools.adapters import LangGraphAdapter

def search_relevant_memories(state):
    """LangGraph node to search for relevant memories."""
    query = state.get("current_query", "")
    
    # Search memories
    results = vectorizer.search_memories(query, limit=5)
    
    # Add to state
    relevant_memories = []
    for vector_id, score, metadata in results:
        if score > 0.7:  # Only high-similarity results
            relevant_memories.append({
                "id": metadata.resource_id,
                "content": metadata.content_preview,
                "score": score,
                "type": metadata.memory_type
            })
    
    return {**state, "relevant_memories": relevant_memories}

# Add to LangGraph workflow
workflow.add_node("search_memories", search_relevant_memories)
```

### CrewAI Integration

```python
from crewai import Agent, Task

def create_memory_search_agent():
    """Create CrewAI agent with memory search capability."""
    
    def search_memories_tool(query: str) -> str:
        """Search HACS memories for relevant information."""
        results = vectorizer.search_memories(query, limit=3)
        
        if not results:
            return "No relevant memories found."
        
        formatted_results = []
        for vector_id, score, metadata in results:
            formatted_results.append(
                f"Memory {metadata.resource_id} (relevance: {score:.2f}): "
                f"{metadata.content_preview[:200]}..."
            )
        
        return "\n\n".join(formatted_results)
    
    agent = Agent(
        role="Clinical Memory Specialist",
        goal="Find relevant clinical memories to support decision making",
        backstory="Expert at searching and retrieving relevant clinical information",
        tools=[search_memories_tool],
        verbose=True
    )
    
    return agent
```

## Error Handling

```python
try:
    # Vectorize content
    vector_id = vectorizer.vectorize_memory(memory, actor)
    if not vector_id:
        print("Vectorization failed - check content and model")
        
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Install with: pip install sentence-transformers")
    
except Exception as e:
    print(f"Vectorization error: {e}")
    # Implement fallback or retry logic
```

## Installation

### Basic Installation

```bash
# Core HACS with basic vectorization
pip install hacs-tools

# With Sentence Transformers
pip install hacs-tools[vectorization]
```

### Full Installation

```bash
# All embedding models and vector stores
pip install sentence-transformers openai cohere qdrant-client pinecone-client mem0ai numpy
```

### Development Setup

```bash
git clone https://github.com/solanovisitor/hacs.git
cd hacs
uv sync --extra vectorization
```

## Examples

See `examples/vectorization_example.py` for a comprehensive demonstration of all vectorization features.

## API Reference

### HACSVectorizer

Main class for vectorizing and searching HACS content.

#### Methods

- `vectorize_memory(memory: MemoryBlock, actor: Optional[Actor]) -> Optional[str]`
- `vectorize_evidence(evidence: Evidence, actor: Optional[Actor]) -> Optional[str]`
- `search_memories(query: str, limit: int, memory_type: Optional[str], actor: Optional[Actor]) -> List[Tuple[str, float, VectorMetadata]]`
- `search_evidence(query: str, limit: int, evidence_type: Optional[str], min_confidence: Optional[float], actor: Optional[Actor]) -> List[Tuple[str, float, VectorMetadata]]`
- `search_all(query: str, limit: int, actor: Optional[Actor]) -> Dict[str, List[Tuple[str, float, VectorMetadata]]]`
- `delete_vector(vector_id: str) -> bool`

### VectorMetadata

Metadata stored with each vector.

#### Fields

- `resource_id: str` - ID of the original resource
- `resource_type: str` - "MemoryBlock" or "Evidence"
- `content_hash: str` - Hash of vectorized content
- `embedding_model: str` - Model used for embedding
- `dimensions: int` - Vector dimensions
- `created_at: datetime` - Creation timestamp
- `actor_id: Optional[str]` - Actor who created the vector
- `tags: List[str]` - Tags for categorization
- `content_preview: str` - First 200 characters
- `content_length: int` - Original content length

For Evidence:
- `evidence_type: Optional[str]` - Type of evidence
- `confidence_score: Optional[float]` - Confidence score

For MemoryBlock:
- `memory_type: Optional[str]` - Type of memory
- `importance_score: Optional[float]` - Importance score

## Troubleshooting

### Common Issues

1. **Import Errors**:
   ```
   ImportError: sentence-transformers not available
   ```
   Solution: `pip install sentence-transformers`

2. **API Key Errors**:
   ```
   openai.AuthenticationError: Invalid API key
   ```
   Solution: Set `OPENAI_API_KEY` environment variable

3. **Vector Store Connection**:
   ```
   ConnectionError: Could not connect to Qdrant
   ```
   Solution: Check Qdrant server is running or use in-memory mode

4. **Dimension Mismatch**:
   ```
   ValueError: Vector dimensions don't match collection
   ```
   Solution: Recreate collection or use consistent embedding model

### Performance Issues

1. **Slow Embedding**:
   - Use smaller models (all-MiniLM-L6-v2 vs all-mpnet-base-v2)
   - Batch process multiple items
   - Cache embeddings for repeated content

2. **Slow Search**:
   - Use metadata filters to reduce search space
   - Optimize vector store configuration
   - Consider approximate search for large datasets

3. **Memory Usage**:
   - Use smaller embedding dimensions
   - Implement vector cleanup for old content
   - Use disk-based vector stores for large datasets 