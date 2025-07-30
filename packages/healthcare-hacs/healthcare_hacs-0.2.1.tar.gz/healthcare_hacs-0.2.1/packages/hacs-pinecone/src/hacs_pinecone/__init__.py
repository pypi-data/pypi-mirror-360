"""
HACS Pinecone Integration

Provides PineconeVectorStore class for vector storage and retrieval using Pinecone v7.x SDK.
"""

import time
import uuid
from typing import Any

from hacs_tools.vectorization import VectorMetadata, VectorStore

try:
    from pinecone import Pinecone, ServerlessSpec
except ImportError:
    raise ImportError("Pinecone package not found. Install with: pip install pinecone")


class PineconeVectorStore(VectorStore):
    def __init__(
        self,
        api_key: str,
        index_name: str = "hacs-vectors",
        dimension: int = 1536,
        metric: str = "cosine",
        cloud: str = "aws",
        region: str = "us-east-1",
        create_if_not_exists: bool = True,
        delete_if_exists: bool = False,
    ):
        """
        Initialize Pinecone vector store with v7.x SDK.

        Args:
            api_key: Pinecone API key
            index_name: Name of the Pinecone index
            dimension: Vector dimension (default: 1536 for OpenAI embeddings)
            metric: Distance metric (cosine, euclidean, dotproduct)
            cloud: Cloud provider (aws, gcp, azure)
            region: Cloud region
            create_if_not_exists: Create index if it doesn't exist
            delete_if_exists: Delete index if it exists (useful for testing)
        """
        super().__init__()

        self.api_key = api_key
        self.index_name = index_name
        self.dimension = dimension
        self.metric = metric
        self.cloud = cloud
        self.region = region

        # Initialize Pinecone client with v7.x SDK
        try:
            self.pc = Pinecone(api_key=api_key)
        except Exception as e:
            raise ValueError(f"Failed to initialize Pinecone client: {e}")

        # Store classes for use in methods
        self.Pinecone = Pinecone
        self.ServerlessSpec = ServerlessSpec
        self.index = None

        # Handle index creation/deletion
        if delete_if_exists and self._index_exists():
            self._delete_index()

        if create_if_not_exists and not self._index_exists():
            self._create_index()

        # Connect to index
        if self._index_exists():
            self.index = self.pc.Index(self.index_name)
        else:
            print(f"Warning: Index '{self.index_name}' does not exist")

    def _index_exists(self) -> bool:
        """Check if the index exists."""
        try:
            indexes = self.pc.list_indexes()
            return any(idx["name"] == self.index_name for idx in indexes)
        except Exception:
            return False

    def _create_index(self) -> bool:
        """Create a new Pinecone index with v7.x SDK."""
        try:
            print(f"Creating Pinecone index '{self.index_name}' with dimension {self.dimension}")

            self.pc.create_index(
                name=self.index_name,
                dimension=self.dimension,
                metric=self.metric,
                spec=self.ServerlessSpec(cloud=self.cloud, region=self.region),
            )

            # Wait for index to be ready
            max_wait = 60  # seconds
            wait_time = 0
            while wait_time < max_wait:
                try:
                    # Try to get index stats to check if it's ready
                    index = self.pc.Index(self.index_name)
                    index.describe_index_stats()
                    print(f"Index '{self.index_name}' is ready!")
                    return True
                except Exception:
                    pass

                time.sleep(2)
                wait_time += 2
                print(f"Waiting for index to be ready... ({wait_time}s)")

            print(f"Warning: Index creation may still be in progress after {max_wait}s")
            return True

        except Exception as e:
            print(f"Error creating index: {e}")
            return False

    def _delete_index(self) -> bool:
        """Delete the Pinecone index."""
        try:
            print(f"Deleting Pinecone index '{self.index_name}'")
            self.pc.delete_index(self.index_name)

            # Wait for deletion to complete
            max_wait = 30
            wait_time = 0
            while self._index_exists() and wait_time < max_wait:
                time.sleep(1)
                wait_time += 1

            print(f"Index '{self.index_name}' deleted")
            return True

        except Exception as e:
            print(f"Error deleting index: {e}")
            return False

    def store_vector(
        self, vector_id: str, embedding: list[float], metadata: VectorMetadata
    ) -> bool:
        """Store a vector in Pinecone."""
        if not self.index:
            print("Error: Index not initialized")
            return False

        try:
            # Ensure vector_id is a string
            if not isinstance(vector_id, str):
                vector_id = str(vector_id)

            # Validate embedding dimension
            if len(embedding) != self.dimension:
                print(
                    f"Error: Embedding dimension {len(embedding)} doesn't match index dimension {self.dimension}"
                )
                return False

            # Serialize metadata to ensure Pinecone compatibility (flat structure only)
            metadata_dict = metadata.model_dump()

            # Flatten metadata for Pinecone (only accepts string, number, boolean, list of strings)
            def flatten_for_pinecone(data, prefix=""):
                flat = {}
                for key, value in data.items():
                    full_key = f"{prefix}{key}" if prefix else key

                    if value is None:
                        continue  # Skip None values
                    elif isinstance(value, str | int | float | bool):
                        flat[full_key] = value
                    elif isinstance(value, list):
                        if all(isinstance(item, str) for item in value):
                            # Convert list to comma-separated string
                            flat[full_key] = ",".join(value) if value else ""
                        else:
                            # Convert non-string lists to string representation
                            flat[full_key] = str(value)
                    elif isinstance(value, dict):
                        # Recursively flatten nested dictionaries
                        nested = flatten_for_pinecone(value, f"{full_key}_")
                        flat.update(nested)
                    else:
                        # Convert other types to string
                        flat[full_key] = str(value)

                return flat

            pinecone_metadata = flatten_for_pinecone(metadata_dict)

            # Ensure we have valid metadata
            if not pinecone_metadata:
                pinecone_metadata = {"resource_type": metadata.resource_type or "unknown"}

            self.index.upsert(
                [{"id": vector_id, "values": embedding, "metadata": pinecone_metadata}]
            )
            return True

        except Exception as e:
            print(f"Error storing vector in Pinecone: {e}")
            return False

    def search_vectors(
        self,
        query_embedding: list[float],
        top_k: int = 10,
        filter_dict: dict[str, Any] | None = None,
    ) -> list[tuple[str, float, VectorMetadata]]:
        """Search for similar vectors in Pinecone."""
        if not self.index:
            print("Error: Index not initialized")
            return []

        try:
            # Validate embedding dimension
            if len(query_embedding) != self.dimension:
                print(
                    f"Error: Query embedding dimension {len(query_embedding)} doesn't match index dimension {self.dimension}"
                )
                return []

            results = self.index.query(
                vector=query_embedding, top_k=top_k, filter=filter_dict, include_metadata=True
            )

            return [
                (match.id, match.score, self._reconstruct_metadata_from_pinecone(match.metadata))
                for match in results.matches
            ]

        except Exception as e:
            print(f"Error searching in Pinecone: {e}")
            return []

    def _reconstruct_metadata_from_pinecone(self, pinecone_metadata: dict) -> VectorMetadata:
        """Reconstruct VectorMetadata from flattened Pinecone metadata."""
        try:
            # Create a nested structure from flattened keys
            reconstructed = {}

            for key, value in pinecone_metadata.items():
                if "_" in key:
                    # Split nested keys
                    parts = key.split("_", 1)
                    if len(parts) == 2:
                        parent_key, child_key = parts
                        if parent_key not in reconstructed:
                            reconstructed[parent_key] = {}
                        if isinstance(reconstructed[parent_key], dict):
                            reconstructed[parent_key][child_key] = value
                        else:
                            # If parent is not a dict, make it one
                            reconstructed[parent_key] = {child_key: value}
                    else:
                        reconstructed[key] = value
                else:
                    # Direct key
                    reconstructed[key] = value

            # Handle special conversions
            if "created_at" in reconstructed and isinstance(reconstructed["created_at"], str):
                try:
                    from datetime import datetime

                    reconstructed["created_at"] = datetime.fromisoformat(
                        reconstructed["created_at"]
                    )
                except (ValueError, TypeError):
                    pass  # Keep as string if parsing fails

            # Handle tags field specifically - convert empty string back to empty list
            if "tags" in reconstructed:
                if reconstructed["tags"] == "":
                    reconstructed["tags"] = []
                elif isinstance(reconstructed["tags"], str) and "," in reconstructed["tags"]:
                    # Convert comma-separated string back to list
                    reconstructed["tags"] = [
                        tag.strip() for tag in reconstructed["tags"].split(",") if tag.strip()
                    ]

            # Ensure required fields exist with defaults
            if "resource_type" not in reconstructed:
                reconstructed["resource_type"] = "unknown"
            if "resource_id" not in reconstructed:
                reconstructed["resource_id"] = str(uuid.uuid4())
            if "content_hash" not in reconstructed:
                reconstructed["content_hash"] = "unknown"
            if "metadata" not in reconstructed:
                reconstructed["metadata"] = {}
            if "tags" not in reconstructed:
                reconstructed["tags"] = []

            return VectorMetadata(**reconstructed)

        except Exception as e:
            print(f"Error reconstructing metadata: {e}")
            # Return minimal valid metadata
            return VectorMetadata(
                resource_type="unknown", resource_id=str(uuid.uuid4()), content_hash="unknown"
            )

    def get_vector(self, vector_id: str) -> tuple[list[float], VectorMetadata] | None:
        """Retrieve a specific vector by ID."""
        if not self.index:
            print("Error: Index not initialized")
            return None

        try:
            result = self.index.fetch([str(vector_id)])
            if str(vector_id) in result.vectors:
                vector_data = result.vectors[str(vector_id)]

                # Reconstruct metadata from flattened Pinecone metadata
                metadata = self._reconstruct_metadata_from_pinecone(vector_data.metadata)

                return (vector_data.values, metadata)
            return None

        except Exception as e:
            print(f"Error retrieving vector from Pinecone: {e}")
            return None

    def delete_vector(self, vector_id: str) -> bool:
        """Delete a vector from Pinecone."""
        if not self.index:
            print("Error: Index not initialized")
            return False

        try:
            self.index.delete([str(vector_id)])
            return True

        except Exception as e:
            print(f"Error deleting vector from Pinecone: {e}")
            return False

    def get_stats(self) -> dict[str, Any]:
        """Get index statistics."""
        if not self.index:
            return {"error": "Index not initialized"}

        try:
            stats = self.index.describe_index_stats()
            return {
                "total_vector_count": stats.total_vector_count,
                "dimension": stats.dimension,
                "index_fullness": stats.index_fullness,
                "namespaces": dict(stats.namespaces) if stats.namespaces else {},
            }
        except Exception as e:
            return {"error": str(e)}

    def cleanup(self) -> bool:
        """Clean up resources (delete index if it exists)."""
        try:
            if self._index_exists():
                return self._delete_index()
            return True
        except Exception as e:
            print(f"Error during cleanup: {e}")
            return False


# Convenience functions
def create_pinecone_store(
    api_key: str, index_name: str = "hacs-vectors", dimension: int = 1536, **kwargs
) -> PineconeVectorStore:
    """Create a Pinecone vector store with v7.x SDK."""
    return PineconeVectorStore(
        api_key=api_key, index_name=index_name, dimension=dimension, **kwargs
    )


def create_test_pinecone_store(api_key: str) -> PineconeVectorStore:
    """Create a test Pinecone store with cleanup enabled."""
    import time

    test_index_name = f"test-hacs-{int(time.time())}"

    return PineconeVectorStore(
        api_key=api_key,
        index_name=test_index_name,
        dimension=1536,
        create_if_not_exists=True,
        delete_if_exists=True,
    )


__all__ = ["PineconeVectorStore", "create_pinecone_store", "create_test_pinecone_store"]
