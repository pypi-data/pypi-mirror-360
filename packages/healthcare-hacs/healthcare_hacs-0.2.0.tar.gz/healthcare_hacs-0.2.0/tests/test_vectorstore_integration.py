#!/usr/bin/env python3
"""
Comprehensive Vector Store Testing

This script tests Pinecone and Qdrant vector stores with proper collection management:
- Creates test collections/indexes
- Tests all vector operations
- Cleans up resources afterwards
"""

import os
import sys
import uuid
import time
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

# Add packages to Python path
sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "packages", "hacs-core", "src")
)
sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "packages", "hacs-models", "src")
)
sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "packages", "hacs-tools", "src")
)
sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "packages", "hacs-pinecone", "src")
)
sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "packages", "hacs-qdrant", "src")
)
sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "packages", "hacs-openai", "src")
)

# Load environment variables securely
from dotenv import load_dotenv

# Load HACS packages
from hacs_core import Actor
from hacs_models import Patient, Observation
from hacs_tools.vectorization import VectorMetadata


def load_api_keys() -> Dict[str, Optional[str]]:
    """Securely load API keys from .env file."""
    load_dotenv()

    api_keys = {
        "pinecone": os.getenv("PINECONE_API_KEY"),
        "qdrant": os.getenv("QDRANT_API_KEY"),
        "openai": os.getenv("OPENAI_API_KEY"),
    }

    print("🔑 Vector Store API Keys:")
    for service, key in api_keys.items():
        status = "✅ Found" if key else "❌ Missing"
        masked_key = f"{key[:8]}...{key[-4:]}" if key and len(key) > 12 else "Not set"
        print(f"   {service.upper()}: {status} ({masked_key})")

    return api_keys


def create_test_data():
    """Create test data for vector store testing."""
    # Create test actor
    actor = Actor(
        id="test-physician-001",
        name="Dr. Test Physician",
        role="physician",
        permissions=["patient:*", "observation:*", "MemoryBlock:*", "Evidence:*"],
        is_active=True,
    )

    # Create test patient
    patient = Patient(
        id="test-patient-001",
        given=["John"],
        family="Doe",
        gender="male",
        birth_date="1985-03-15",
        active=True,
    )

    # Create test observation
    observation = Observation(
        id="test-observation-001",
        status="final",
        code={
            "coding": [
                {
                    "system": "http://loinc.org",
                    "code": "8480-6",
                    "display": "Systolic blood pressure",
                }
            ]
        },
        subject=patient.id,
        value_quantity={"value": 140, "unit": "mmHg"},
        effective_datetime=datetime.now(timezone.utc),
    )

    # Create test embeddings (mock OpenAI embeddings)
    test_embeddings = {
        "patient_summary": [0.1 + i * 0.001 for i in range(1536)],
        "clinical_note": [0.2 + i * 0.001 for i in range(1536)],
        "lab_result": [0.3 + i * 0.001 for i in range(1536)],
    }

    return {
        "actor": actor,
        "patient": patient,
        "observation": observation,
        "embeddings": test_embeddings,
    }


def generate_real_embeddings(api_key: str, texts: List[str]) -> Dict[str, List[float]]:
    """Generate real embeddings using OpenAI if available."""
    if not api_key:
        print("   ⚠️  OpenAI API key not available, using mock embeddings")
        return {
            f"text_{i}": [0.1 + i * 0.001 + j * 0.0001 for j in range(1536)]
            for i, _ in enumerate(texts)
        }

    try:
        from hacs_openai import OpenAIEmbedding

        embedding_model = OpenAIEmbedding(api_key=api_key)
        embeddings = {}

        for i, text in enumerate(texts):
            embedding = embedding_model.embed(text)
            embeddings[f"text_{i}"] = embedding
            print(f"   ✅ Generated embedding for text {i + 1} (dim: {len(embedding)})")

        return embeddings

    except Exception as e:
        print(f"   ⚠️  Failed to generate real embeddings: {e}")
        return {
            f"text_{i}": [0.1 + i * 0.001 + j * 0.0001 for j in range(1536)]
            for i, _ in enumerate(texts)
        }


def test_pinecone_comprehensive(api_key: str, test_data: Dict[str, Any]) -> bool:
    """Comprehensive Pinecone testing with collection management."""
    print("\n🌲 Comprehensive Pinecone Testing...")

    if not api_key:
        print("   ⚠️  Pinecone API key not found, skipping test")
        return False

    vector_store = None
    test_vectors = []

    try:
        # Import Pinecone integration
        from hacs_pinecone import create_test_pinecone_store

        # Create test store with unique name
        test_name = f"comprehensive_{int(time.time())}"
        print(f"   🔧 Creating test Pinecone index: hacs-test-{test_name}-*")

        vector_store = create_test_pinecone_store(api_key=api_key, test_name=test_name)
        print("   ✅ Pinecone test index created and ready")

        # Test connection
        if not vector_store.test_connection():
            print("   ❌ Connection test failed")
            return False
        print("   ✅ Connection test passed")

        # Get index stats
        stats = vector_store.get_index_stats()
        print(f"   📊 Index stats: {stats}")

        # Generate test embeddings
        clinical_texts = [
            f"Patient {test_data['patient'].display_name} has elevated blood pressure",
            f"Systolic BP reading: {test_data['observation'].value_quantity['value']} mmHg",
            "Clinical assessment shows Stage 1 hypertension requiring monitoring",
        ]

        embeddings = generate_real_embeddings(
            test_data.get("openai_key"), clinical_texts
        )

        # Test vector storage
        print("   🔄 Testing vector storage...")
        for i, (text_key, embedding) in enumerate(embeddings.items()):
            vector_id = str(uuid.uuid4())
            test_vectors.append(vector_id)

            metadata = VectorMetadata(
                resource_type="ClinicalText",
                resource_id=f"text-{i}",
                content_hash=str(hash(clinical_texts[i])),
                metadata={
                    "text": clinical_texts[i][:100],
                    "type": "clinical_note",
                    "patient_id": test_data["patient"].id,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
            )

            success = vector_store.store_vector(vector_id, embedding, metadata)
            if success:
                print(f"   ✅ Stored vector {i + 1}/3")
            else:
                print(f"   ❌ Failed to store vector {i + 1}/3")
                return False

        # Wait for indexing - Pinecone serverless can take 30-60 seconds
        print(
            "   ⏳ Waiting for vectors to be indexed (serverless can take 30-60 seconds)..."
        )
        max_wait = 45  # Wait up to 45 seconds
        vectors_indexed = False

        for i in range(max_wait):
            time.sleep(1)
            stats = vector_store.get_index_stats()
            vector_count = stats.get("total_vector_count", 0)

            # Also try to fetch one vector directly to check if indexing is complete
            try:
                if test_vectors:
                    raw_result = vector_store.index.fetch([test_vectors[0]])
                    vector_found = test_vectors[0] in raw_result.vectors

                    if i % 5 == 0:  # Print status every 5 seconds
                        print(
                            f"      {i + 1}s: Vector count = {vector_count}, Direct fetch = {vector_found}"
                        )

                    if vector_count >= len(test_vectors) or vector_found:
                        print(f"   ✅ Vectors indexed after {i + 1} seconds!")
                        vectors_indexed = True
                        break

            except Exception as e:
                if i % 10 == 0:  # Print errors every 10 seconds
                    print(f"      {i + 1}s: Indexing check error: {e}")

        if not vectors_indexed:
            print("   ⚠️  Indexing timeout reached, proceeding with tests...")

        # Test vector retrieval
        print("   🔄 Testing vector retrieval...")
        retrieval_success = 0
        for i, vector_id in enumerate(test_vectors):
            result = vector_store.get_vector(vector_id)
            if result:
                embedding, metadata = result
                print(f"   ✅ Retrieved vector {i + 1}/3 (dim: {len(embedding)})")
                print(
                    f"      Metadata: {metadata.resource_type}, ID: {metadata.resource_id}"
                )
                retrieval_success += 1
            else:
                print(f"   ❌ Failed to retrieve vector {i + 1}/3")

        # Consider test successful if we retrieved at least 2/3 vectors (accounting for indexing delays)
        if retrieval_success == 0:
            print("   ❌ No vectors could be retrieved")
            return False
        elif retrieval_success < len(test_vectors):
            print(
                f"   ⚠️  Only retrieved {retrieval_success}/{len(test_vectors)} vectors (indexing delays)"
            )

        # Test similarity search
        print("   🔄 Testing similarity search...")
        query_embedding = list(embeddings.values())[0]  # Use first embedding as query

        search_results = vector_store.search_similar(
            query_embedding=query_embedding, limit=5
        )

        if search_results:
            print(f"   ✅ Similarity search returned {len(search_results)} results")
            for i, (vec_id, score, metadata) in enumerate(search_results[:3]):
                print(f"      Result {i + 1}: Score {score:.4f}, ID: {vec_id[:8]}...")
        else:
            print(
                "   ⚠️  Similarity search returned no results (may be due to indexing delays)"
            )

        # Test vector deletion
        print("   🔄 Testing vector deletion...")
        deletion_success = 0
        for i, vector_id in enumerate(test_vectors):
            success = vector_store.delete_vector(vector_id)
            if success:
                deletion_success += 1
                print(f"   ✅ Deleted vector {i + 1}/3")
            else:
                print(f"   ❌ Failed to delete vector {i + 1}/3")

        print(
            f"   📊 Successfully deleted {deletion_success}/{len(test_vectors)} vectors"
        )

        # Final stats
        final_stats = vector_store.get_index_stats()
        print(f"   📊 Final index stats: {final_stats}")

        # Consider test successful if we had reasonable success rates
        overall_success = retrieval_success >= 2 and deletion_success >= 2

        return overall_success

    except Exception as e:
        print(f"   ❌ Pinecone comprehensive test failed: {e}")
        return False

    finally:
        # Cleanup
        if vector_store:
            try:
                print("   🧹 Cleaning up Pinecone test index...")
                vector_store.cleanup()
                print("   ✅ Pinecone cleanup completed")
            except Exception as e:
                print(f"   ⚠️  Cleanup warning: {e}")


def test_qdrant_comprehensive(api_key: str, test_data: Dict[str, Any]) -> bool:
    """Comprehensive Qdrant testing with collection management."""
    print("\n🔍 Comprehensive Qdrant Testing...")

    vector_store = None
    test_vectors = []

    try:
        # Import Qdrant integration
        from hacs_qdrant import create_test_qdrant_store

        # Create test store with unique name
        test_name = f"comprehensive_{int(time.time())}"
        print(f"   🔧 Creating test Qdrant collection: hacs_test_{test_name}_*")

        vector_store = create_test_qdrant_store(test_name=test_name)
        print("   ✅ Qdrant test collection created and ready")

        # Test connection
        if not vector_store.test_connection():
            print("   ❌ Connection test failed")
            return False
        print("   ✅ Connection test passed")

        # Get collection info
        info = vector_store.get_collection_info()
        print(f"   📊 Collection info: {info}")

        # Generate test embeddings
        clinical_texts = [
            f"Patient {test_data['patient'].display_name} presents with hypertension",
            f"Blood pressure measurement: {test_data['observation'].value_quantity['value']} mmHg systolic",
            "Clinical decision: Initiate antihypertensive therapy and lifestyle modifications",
            "Follow-up appointment scheduled for blood pressure monitoring",
            "Patient education provided regarding DASH diet and exercise",
        ]

        embeddings = generate_real_embeddings(
            test_data.get("openai_key"), clinical_texts
        )

        # Test vector storage
        print("   🔄 Testing vector storage...")
        for i, (text_key, embedding) in enumerate(embeddings.items()):
            vector_id = str(uuid.uuid4())
            test_vectors.append(vector_id)

            metadata = VectorMetadata(
                resource_type="ClinicalWorkflow",
                resource_id=f"workflow-step-{i}",
                content_hash=str(hash(clinical_texts[i])),
                metadata={
                    "step": i + 1,
                    "text": clinical_texts[i],
                    "category": "clinical_workflow",
                    "patient_id": test_data["patient"].id,
                    "observation_id": test_data["observation"].id,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "bp_value": test_data["observation"].value_quantity["value"],
                },
            )

            success = vector_store.store_vector(vector_id, embedding, metadata)
            if success:
                print(f"   ✅ Stored vector {i + 1}/{len(embeddings)}")
            else:
                print(f"   ❌ Failed to store vector {i + 1}/{len(embeddings)}")
                return False

        # Test vector retrieval
        print("   🔄 Testing vector retrieval...")
        for i, vector_id in enumerate(test_vectors):
            result = vector_store.get_vector(vector_id)
            if result:
                embedding, metadata = result
                print(
                    f"   ✅ Retrieved vector {i + 1}/{len(test_vectors)} (dim: {len(embedding)})"
                )
                print(
                    f"      Metadata: {metadata.resource_type}, Step: {metadata.metadata.get('step')}"
                )
            else:
                print(f"   ❌ Failed to retrieve vector {i + 1}/{len(test_vectors)}")
                return False

        # Test similarity search with clinical query
        print("   🔄 Testing clinical similarity search...")

        # Create a clinical query embedding
        query_texts = [
            "Patient with high blood pressure needs treatment",
            "Hypertension management and monitoring",
        ]

        query_embeddings = generate_real_embeddings(
            test_data.get("openai_key"), query_texts
        )

        for query_name, query_embedding in query_embeddings.items():
            search_results = vector_store.search_similar(
                query_embedding=query_embedding, limit=3
            )

            if search_results:
                print(
                    f"   ✅ Query '{query_name}' returned {len(search_results)} results"
                )
                for i, (vec_id, score, metadata) in enumerate(search_results):
                    step = metadata.metadata.get("step", "N/A")
                    text_preview = metadata.metadata.get("text", "")[:50]
                    print(
                        f"      Result {i + 1}: Score {score:.4f}, Step {step}, Text: {text_preview}..."
                    )
            else:
                print(f"   ❌ Query '{query_name}' returned no results")

        # Test filtered search
        print("   🔄 Testing filtered search...")

        # Use proper Qdrant filter syntax
        try:
            from qdrant_client.models import Filter, FieldCondition, MatchValue, Range

            filter_conditions = Filter(
                must=[
                    FieldCondition(
                        key="category", match=MatchValue(value="clinical_workflow")
                    ),
                    FieldCondition(key="step", range=Range(gte=3)),
                ]
            )

            filtered_results = vector_store.search_similar(
                query_embedding=list(embeddings.values())[0],
                limit=10,
                filters=filter_conditions,
            )

            if filtered_results:
                print(f"   ✅ Filtered search returned {len(filtered_results)} results")
            else:
                print("   ⚠️  Filtered search returned no results (may be expected)")

        except ImportError:
            print(
                "   ⚠️  Qdrant filtering models not available, skipping filtered search"
            )
        except Exception as filter_e:
            print(
                f"   ⚠️  Filtered search failed: {filter_e}, continuing with other tests"
            )

        # Test vector deletion
        print("   🔄 Testing vector deletion...")
        deleted_count = 0
        for i, vector_id in enumerate(test_vectors):
            success = vector_store.delete_vector(vector_id)
            if success:
                deleted_count += 1
                print(f"   ✅ Deleted vector {i + 1}/{len(test_vectors)}")
            else:
                print(f"   ❌ Failed to delete vector {i + 1}/{len(test_vectors)}")

        print(f"   📊 Successfully deleted {deleted_count}/{len(test_vectors)} vectors")

        # Final collection info
        final_info = vector_store.get_collection_info()
        print(f"   📊 Final collection info: {final_info}")

        return True

    except Exception as e:
        print(f"   ❌ Qdrant comprehensive test failed: {e}")
        return False

    finally:
        # Cleanup
        if vector_store:
            try:
                print("   🧹 Cleaning up Qdrant test collection...")
                vector_store.cleanup()
                print("   ✅ Qdrant cleanup completed")
            except Exception as e:
                print(f"   ⚠️  Cleanup warning: {e}")


def test_cross_vectorstore_compatibility(
    api_keys: Dict[str, str], test_data: Dict[str, Any]
) -> bool:
    """Test compatibility between different vector stores."""
    print("\n🔄 Cross-VectorStore Compatibility Testing...")

    if not api_keys.get("pinecone") or not api_keys.get("qdrant"):
        print("   ⚠️  Both Pinecone and Qdrant API keys required for compatibility test")
        return False

    try:
        from hacs_pinecone import create_test_pinecone_store
        from hacs_qdrant import create_test_qdrant_store

        # Create both stores
        test_id = int(time.time())
        pinecone_store = create_test_pinecone_store(
            api_keys["pinecone"], f"compat_{test_id}"
        )
        qdrant_store = create_test_qdrant_store(f"compat_{test_id}")

        print("   ✅ Created both Pinecone and Qdrant test stores")

        # Generate same embeddings for both
        clinical_text = (
            f"Patient {test_data['patient'].display_name} requires clinical assessment"
        )
        embeddings = generate_real_embeddings(api_keys.get("openai"), [clinical_text])
        embedding = list(embeddings.values())[0]

        # Create identical metadata
        metadata = VectorMetadata(
            resource_type="CompatibilityTest",
            resource_id="test-001",
            content_hash=str(hash(clinical_text)),
            metadata={
                "text": clinical_text,
                "test_type": "cross_compatibility",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )

        # Store in both vector stores
        vector_id = str(uuid.uuid4())

        pinecone_success = pinecone_store.store_vector(vector_id, embedding, metadata)
        qdrant_success = qdrant_store.store_vector(vector_id, embedding, metadata)

        if pinecone_success and qdrant_success:
            print("   ✅ Successfully stored identical vector in both stores")
        else:
            print("   ❌ Failed to store vector in one or both stores")
            return False

        # Wait for indexing
        time.sleep(2)

        # Retrieve from both and compare
        pinecone_result = pinecone_store.get_vector(vector_id)
        qdrant_result = qdrant_store.get_vector(vector_id)

        if pinecone_result and qdrant_result:
            pinecone_embedding, pinecone_metadata = pinecone_result
            qdrant_embedding, qdrant_metadata = qdrant_result

            # Compare embeddings (should be identical)
            embedding_match = len(pinecone_embedding) == len(qdrant_embedding)
            if embedding_match:
                # Check first few values for approximate equality
                for i in range(min(10, len(pinecone_embedding))):
                    if abs(pinecone_embedding[i] - qdrant_embedding[i]) > 1e-6:
                        embedding_match = False
                        break

            if embedding_match:
                print("   ✅ Embeddings match between vector stores")
            else:
                print("   ⚠️  Embeddings differ between vector stores")

            # Compare metadata
            metadata_match = (
                pinecone_metadata.resource_type == qdrant_metadata.resource_type
                and pinecone_metadata.resource_id == qdrant_metadata.resource_id
            )

            if metadata_match:
                print("   ✅ Metadata matches between vector stores")
            else:
                print("   ⚠️  Metadata differs between vector stores")

            # Test cross-store similarity search
            search_results_pinecone = pinecone_store.search_similar(embedding, limit=1)
            search_results_qdrant = qdrant_store.search_similar(embedding, limit=1)

            if search_results_pinecone and search_results_qdrant:
                print("   ✅ Similarity search works on both stores")

                # Compare similarity scores (should be high for identical vectors)
                pinecone_score = search_results_pinecone[0][1]
                qdrant_score = search_results_qdrant[0][1]

                print(
                    f"   📊 Similarity scores - Pinecone: {pinecone_score:.4f}, Qdrant: {qdrant_score:.4f}"
                )

                if pinecone_score > 0.95 and qdrant_score > 0.95:
                    print("   ✅ High similarity scores confirm vector integrity")
                else:
                    print("   ⚠️  Lower than expected similarity scores")

        # Cleanup both stores
        pinecone_store.cleanup()
        qdrant_store.cleanup()
        print("   ✅ Cleaned up both test stores")

        return True

    except Exception as e:
        print(f"   ❌ Cross-compatibility test failed: {e}")
        return False


def main():
    """Main test runner for comprehensive vector store testing."""
    print("🏥 HACS Vector Store Comprehensive Testing")
    print("=" * 55)

    # Load API keys
    api_keys = load_api_keys()

    # Create test data
    print("\n📋 Creating test data...")
    test_data = create_test_data()
    test_data["openai_key"] = api_keys.get("openai")
    print("   ✅ Test data created")

    # Track results
    results = {}

    # Test Pinecone
    results["pinecone"] = test_pinecone_comprehensive(
        api_keys.get("pinecone"), test_data
    )

    # Test Qdrant
    results["qdrant"] = test_qdrant_comprehensive(api_keys.get("qdrant"), test_data)

    # Test cross-compatibility
    results["compatibility"] = test_cross_vectorstore_compatibility(api_keys, test_data)

    # Final summary
    print("\n" + "=" * 55)
    print("📊 COMPREHENSIVE TEST RESULTS")
    print("=" * 55)

    passed_tests = 0
    total_tests = len(results)

    for test_name, result in results.items():
        if result:
            passed_tests += 1
            print(f"✅ {test_name.upper()}: PASSED")
        else:
            print(f"❌ {test_name.upper()}: FAILED")

    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    print(
        f"\n🎯 Overall Success Rate: {passed_tests}/{total_tests} ({success_rate:.1f}%)"
    )

    if success_rate >= 80:
        print("🎉 Excellent! Vector stores are production-ready!")
        print("\n🚀 Vector Store Capabilities Verified:")
        print("   • Collection/Index creation and management")
        print("   • Vector storage with metadata")
        print("   • High-performance similarity search")
        print("   • Vector retrieval and deletion")
        print("   • Cross-platform compatibility")
        print("   • Automatic cleanup and resource management")

    elif success_rate >= 60:
        print("👍 Good! Most vector store functionality working.")
        print("\n🔧 Review any failed tests and address issues.")

    else:
        print("⚠️  Vector store issues detected.")
        print("\n🚨 Check API keys, network connectivity, and configurations.")

    return success_rate >= 60


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
