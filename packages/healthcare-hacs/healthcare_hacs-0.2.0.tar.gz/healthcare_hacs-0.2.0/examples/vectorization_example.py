#!/usr/bin/env python3
"""
HACS Vectorization Example

This example demonstrates how to use HACS vectorization capabilities
to enable semantic search and retrieval for Evidence and Memory content.

Supports multiple embedding models:
- Sentence Transformers (local, no API key required)
- OpenAI (requires API key)
- Cohere (requires API key)

Supports multiple vector stores:
- Qdrant (local or cloud)
- Pinecone (cloud)
- Mem0 (managed service)
"""

import os
from datetime import datetime

from hacs_core import Actor, MemoryBlock, Evidence, EvidenceType
from hacs_tools.vectorization import (
    create_sentence_transformer_vectorizer,
    create_openai_vectorizer,
    create_cohere_vectorizer,
    HACSVectorizer,
)


def create_sample_data():
    """Create sample healthcare data for vectorization."""

    # Create a healthcare actor
    physician = Actor(
        id="physician-001",
        name="Dr. Sarah Johnson",
        role="physician",
        permissions=["patient:read", "patient:write", "observation:*"],
        is_active=True,
    )

    # Create sample memories
    memories = [
        MemoryBlock(
            id="mem-001",
            memory_type="episodic",
            content="Patient John Doe expressed significant anxiety about upcoming cardiac catheterization procedure. Discussed risks, benefits, and alternatives. Patient verbalized understanding and provided informed consent.",
            importance_score=0.8,
            metadata={
                "patient_id": "patient-001",
                "procedure": "cardiac_catheterization",
                "tags": ["anxiety", "informed_consent", "cardiology"],
            },
        ),
        MemoryBlock(
            id="mem-002",
            memory_type="procedural",
            content="To calculate BMI: divide weight in kilograms by height in meters squared. Normal BMI range is 18.5-24.9. Overweight is 25-29.9. Obese is 30 or higher.",
            importance_score=0.6,
            metadata={
                "category": "clinical_calculations",
                "tags": ["bmi", "assessment", "guidelines"],
            },
        ),
        MemoryBlock(
            id="mem-003",
            memory_type="executive",
            content="Current workflow priority: Complete all patient discharges by 2 PM to prepare for incoming emergency cases. Coordinate with nursing staff and social services for discharge planning.",
            importance_score=0.9,
            metadata={
                "workflow": "discharge_planning",
                "urgency": "high",
                "tags": ["workflow", "discharge", "coordination"],
            },
        ),
    ]

    # Create sample evidence
    evidence_items = [
        Evidence(
            id="evd-001",
            citation="American Heart Association. (2024). Guidelines for Cardiac Catheterization. Circulation, 149(8), e123-e145.",
            content="Cardiac catheterization is indicated for patients with suspected coronary artery disease when non-invasive testing is inconclusive. Pre-procedure anxiety is common and should be addressed through patient education and psychological support.",
            evidence_type=EvidenceType.GUIDELINE,
            confidence_score=0.95,
            tags=["cardiology", "catheterization", "guidelines", "anxiety"],
        ),
        Evidence(
            id="evd-002",
            citation="Smith, J. et al. (2024). BMI and Cardiovascular Risk. New England Journal of Medicine, 380(12), 1123-1135.",
            content="Body mass index remains a useful screening tool for cardiovascular risk assessment. However, it should be interpreted in context with other risk factors including waist circumference, blood pressure, and lipid profiles.",
            evidence_type=EvidenceType.RESEARCH_PAPER,
            confidence_score=0.87,
            tags=["bmi", "cardiovascular", "risk_assessment", "screening"],
        ),
        Evidence(
            id="evd-003",
            citation="Hospital Discharge Planning Protocol v2.1 (2024). Internal Quality Guidelines.",
            content="Effective discharge planning reduces readmission rates by 25%. Key components include medication reconciliation, follow-up appointment scheduling, patient education, and coordination with outpatient providers.",
            evidence_type=EvidenceType.CLINICAL_NOTE,
            confidence_score=0.82,
            tags=["discharge", "planning", "readmission", "quality"],
        ),
    ]

    return physician, memories, evidence_items


def demonstrate_sentence_transformers():
    """Demonstrate vectorization with Sentence Transformers (local, no API key)."""
    print("\n🤖 Sentence Transformers Vectorization Demo")
    print("=" * 50)

    # Create vectorizer with Sentence Transformers + Qdrant (in-memory)
    vectorizer = create_sentence_transformer_vectorizer(
        model_name="all-MiniLM-L6-v2",  # Small, fast model
        vector_store_type="qdrant",
    )

    physician, memories, evidence_items = create_sample_data()

    # Vectorize memories
    print("\n📝 Vectorizing memories...")
    for memory in memories:
        vector_id = vectorizer.vectorize_memory(memory, physician)
        if vector_id:
            print(f"  ✅ Vectorized memory {memory.id} -> {vector_id}")
        else:
            print(f"  ❌ Failed to vectorize memory {memory.id}")

    # Vectorize evidence
    print("\n📚 Vectorizing evidence...")
    for evidence in evidence_items:
        vector_id = vectorizer.vectorize_evidence(evidence, physician)
        if vector_id:
            print(f"  ✅ Vectorized evidence {evidence.id} -> {vector_id}")
        else:
            print(f"  ❌ Failed to vectorize evidence {evidence.id}")

    # Semantic search examples
    print("\n🔍 Semantic Search Examples")
    print("-" * 30)

    # Search memories
    print("\n1. Searching memories for 'patient anxiety':")
    memory_results = vectorizer.search_memories("patient anxiety", limit=3)
    for vector_id, score, metadata in memory_results:
        print(f"   📝 {metadata.resource_id} (score: {score:.3f})")
        print(f"      Type: {metadata.memory_type}")
        print(f"      Preview: {metadata.content_preview[:100]}...")

    # Search evidence
    print("\n2. Searching evidence for 'cardiac procedures':")
    evidence_results = vectorizer.search_evidence("cardiac procedures", limit=3)
    for vector_id, score, metadata in evidence_results:
        print(f"   📚 {metadata.resource_id} (score: {score:.3f})")
        print(f"      Type: {metadata.evidence_type}")
        print(f"      Confidence: {metadata.confidence_score}")
        print(f"      Preview: {metadata.content_preview[:100]}...")

    # Search across both
    print("\n3. Searching all content for 'discharge planning':")
    all_results = vectorizer.search_all("discharge planning", limit=2)

    if all_results["memories"]:
        print("   Memories:")
        for vector_id, score, metadata in all_results["memories"]:
            print(f"     📝 {metadata.resource_id} (score: {score:.3f})")

    if all_results["evidence"]:
        print("   Evidence:")
        for vector_id, score, metadata in all_results["evidence"]:
            print(f"     📚 {metadata.resource_id} (score: {score:.3f})")

    return vectorizer


def demonstrate_openai_vectorization():
    """Demonstrate vectorization with OpenAI embeddings (requires API key)."""
    print("\n🔥 OpenAI Vectorization Demo")
    print("=" * 50)

    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  OPENAI_API_KEY not found. Skipping OpenAI demo.")
        print("   Set your API key: export OPENAI_API_KEY='your-key-here'")
        return None

    try:
        # Create vectorizer with OpenAI + Qdrant
        vectorizer = create_openai_vectorizer(
            model="text-embedding-3-small", api_key=api_key, vector_store_type="qdrant"
        )

        physician, memories, evidence_items = create_sample_data()

        # Vectorize a sample memory
        print("\n📝 Vectorizing sample memory with OpenAI...")
        sample_memory = memories[0]
        vector_id = vectorizer.vectorize_memory(sample_memory, physician)

        if vector_id:
            print(f"  ✅ Vectorized with OpenAI: {vector_id}")
            print(f"  📊 Embedding dimensions: {vectorizer.embedding_model.dimensions}")

            # Test search
            results = vectorizer.search_memories(
                "patient anxiety cardiac procedure", limit=1
            )
            if results:
                vector_id, score, metadata = results[0]
                print(f"  🔍 Search result score: {score:.3f}")
        else:
            print("  ❌ Failed to vectorize with OpenAI")

        return vectorizer

    except Exception as e:
        print(f"❌ OpenAI vectorization failed: {e}")
        return None


def demonstrate_cohere_vectorization():
    """Demonstrate vectorization with Cohere embeddings (requires API key)."""
    print("\n🌟 Cohere Vectorization Demo")
    print("=" * 50)

    # Check for API key
    api_key = os.getenv("COHERE_API_KEY")
    if not api_key:
        print("⚠️  COHERE_API_KEY not found. Skipping Cohere demo.")
        print("   Set your API key: export COHERE_API_KEY='your-key-here'")
        return None

    try:
        # Create vectorizer with Cohere + Qdrant
        vectorizer = create_cohere_vectorizer(
            model="embed-english-v3.0", api_key=api_key, vector_store_type="qdrant"
        )

        physician, memories, evidence_items = create_sample_data()

        # Vectorize a sample evidence
        print("\n📚 Vectorizing sample evidence with Cohere...")
        sample_evidence = evidence_items[0]
        vector_id = vectorizer.vectorize_evidence(sample_evidence, physician)

        if vector_id:
            print(f"  ✅ Vectorized with Cohere: {vector_id}")
            print(f"  📊 Embedding dimensions: {vectorizer.embedding_model.dimensions}")

            # Test search
            results = vectorizer.search_evidence(
                "heart catheterization guidelines", limit=1
            )
            if results:
                vector_id, score, metadata = results[0]
                print(f"  🔍 Search result score: {score:.3f}")
        else:
            print("  ❌ Failed to vectorize with Cohere")

        return vectorizer

    except Exception as e:
        print(f"❌ Cohere vectorization failed: {e}")
        return None


def demonstrate_advanced_features(vectorizer: HACSVectorizer):
    """Demonstrate advanced vectorization features."""
    print("\n🚀 Advanced Vectorization Features")
    print("=" * 50)

    physician, memories, evidence_items = create_sample_data()

    # Filtered searches
    print("\n1. Filtered Searches:")

    # Search only episodic memories
    episodic_results = vectorizer.search_memories(
        "patient care", limit=5, memory_type="episodic", actor=physician
    )
    print(f"   📝 Found {len(episodic_results)} episodic memories about patient care")

    # Search high-confidence evidence
    high_conf_results = vectorizer.search_evidence(
        "clinical guidelines", limit=5, min_confidence=0.9, actor=physician
    )
    print(f"   📚 Found {len(high_conf_results)} high-confidence evidence items")

    # Vector retrieval
    print("\n2. Vector Retrieval:")
    if memories[0].vector_id:
        vector_data = vectorizer.vector_store.get_vector(memories[0].vector_id)
        if vector_data:
            embedding, metadata = vector_data
            print(f"   📊 Retrieved vector with {len(embedding)} dimensions")
            print(f"   📅 Created: {metadata.created_at}")
            print(f"   🏷️  Tags: {metadata.tags}")

    # Performance metrics
    print("\n3. Performance Metrics:")
    start_time = datetime.now()

    # Batch search
    queries = [
        "cardiac procedures",
        "patient education",
        "workflow management",
        "clinical calculations",
    ]

    total_results = 0
    for query in queries:
        results = vectorizer.search_all(query, limit=2)
        total_results += len(results["memories"]) + len(results["evidence"])

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds() * 1000

    print(f"   ⚡ Processed {len(queries)} queries in {duration:.1f}ms")
    print(f"   📊 Found {total_results} total results")
    print(f"   🎯 Average: {duration / len(queries):.1f}ms per query")


def main():
    """Main demo function."""
    print("🏥 HACS Vectorization Demonstration")
    print("=" * 60)
    print(
        "This demo shows how to vectorize and search HACS Evidence and Memory content"
    )
    print("using various embedding models and vector stores.\n")

    # Always available: Sentence Transformers
    vectorizer = demonstrate_sentence_transformers()

    # Optional: OpenAI (requires API key)
    _ = demonstrate_openai_vectorization()

    # Optional: Cohere (requires API key)
    _ = demonstrate_cohere_vectorization()

    # Advanced features demo
    demonstrate_advanced_features(vectorizer)

    print("\n🎉 Vectorization Demo Complete!")
    print("\n💡 Next Steps:")
    print("   • Try different embedding models for your use case")
    print("   • Set up persistent vector stores (Qdrant Cloud, Pinecone)")
    print("   • Integrate with your AI agent workflows")
    print("   • Experiment with hybrid search (keyword + semantic)")

    print("\n📚 Available Vector Stores:")
    print("   • Qdrant: Local or cloud, open source")
    print("   • Pinecone: Managed cloud service")
    print("   • Mem0: AI-native memory platform")

    print("\n🤖 Available Embedding Models:")
    print("   • Sentence Transformers: Local, no API key, many models")
    print("   • OpenAI: High quality, requires API key")
    print("   • Cohere: Multilingual support, requires API key")


if __name__ == "__main__":
    main()
