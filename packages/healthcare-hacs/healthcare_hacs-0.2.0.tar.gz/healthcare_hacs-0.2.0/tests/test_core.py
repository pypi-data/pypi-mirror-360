"""
Tests for hacs-core package.

Tests the BaseResource and MemoryBlock models to ensure proper functionality,
validation, and serialization.
"""

import pytest
from datetime import datetime

from hacs_core import BaseResource, MemoryBlock


class TestBaseResource:
    """Test cases for BaseResource class."""

    def test_basic_instantiation(self):
        """Test basic resource creation."""
        resource = BaseResource(resource_type="TestResource", id="test-001")

        assert resource.resource_type == "TestResource"
        assert resource.id == "test-001"
        assert isinstance(resource.created_at, datetime)
        assert isinstance(resource.updated_at, datetime)

    def test_model_json_schema(self):
        """Test JSON schema generation."""
        schema = BaseResource.model_json_schema()

        assert "properties" in schema
        assert "resource_type" in schema["properties"]
        assert "id" in schema["properties"]
        assert "created_at" in schema["properties"]
        assert "updated_at" in schema["properties"]

    def test_pretty_print(self):
        """Test __repr__ method."""
        resource = BaseResource(resource_type="TestResource", id="test-001")

        repr_str = repr(resource)
        assert "TestResource" in repr_str
        assert "test-001" in repr_str
        assert "created=" in repr_str

    def test_timestamp_methods(self):
        """Test timestamp-related methods."""
        resource = BaseResource(resource_type="TestResource", id="test-001")

        original_updated = resource.updated_at

        # Test update_timestamp
        resource.update_timestamp()
        assert resource.updated_at > original_updated

        # Test age calculation
        age = resource.get_age_seconds()
        assert age >= 0
        assert isinstance(age, float)

    def test_comparison_methods(self):
        """Test resource comparison methods."""
        resource1 = BaseResource(resource_type="TestResource", id="test-001")

        # Create second resource slightly later
        import time

        time.sleep(0.01)

        resource2 = BaseResource(resource_type="TestResource", id="test-002")

        assert resource2.is_newer_than(resource1)
        assert not resource1.is_newer_than(resource2)


class TestMemoryBlock:
    """Test cases for MemoryBlock class."""

    def test_basic_instantiation(self):
        """Test basic memory block creation."""
        memory = MemoryBlock(
            id="mem-001",
            memory_type="episodic",
            content="Patient complained of headache",
        )

        assert memory.resource_type == "MemoryBlock"
        assert memory.id == "mem-001"
        assert memory.memory_type == "episodic"
        assert memory.content == "Patient complained of headache"
        assert memory.importance_score == 0.5  # default
        assert memory.access_count == 0  # default
        assert memory.metadata == {}  # default
        assert memory.related_memories == []  # default

    def test_memory_types(self):
        """Test all valid memory types."""
        # Test episodic memory
        memory_episodic = MemoryBlock(
            id="mem-episodic",
            memory_type="episodic",
            content="Test episodic memory",
        )
        assert memory_episodic.memory_type == "episodic"

        # Test procedural memory
        memory_procedural = MemoryBlock(
            id="mem-procedural",
            memory_type="procedural",
            content="Test procedural memory",
        )
        assert memory_procedural.memory_type == "procedural"

        # Test executive memory
        memory_executive = MemoryBlock(
            id="mem-executive",
            memory_type="executive",
            content="Test executive memory",
        )
        assert memory_executive.memory_type == "executive"

    def test_invalid_memory_type(self):
        """Test that invalid memory types are rejected."""
        from pydantic import ValidationError

        # Test invalid memory type - this should fail during validation
        # Use dynamic construction to avoid type checker complaints
        invalid_type = "invalid" + "_type"
        with pytest.raises(ValidationError):
            MemoryBlock(
                id="invalid-memory",
                memory_type=invalid_type,  # type: ignore
                content="Test content",
            )

    def test_content_validation(self):
        """Test content validation."""
        # Empty content should fail
        with pytest.raises(ValueError, match="Memory content cannot be empty"):
            MemoryBlock(id="mem-empty", memory_type="episodic", content="")

        # Whitespace-only content should fail
        with pytest.raises(ValueError, match="Memory content cannot be empty"):
            MemoryBlock(id="mem-whitespace", memory_type="episodic", content="   ")

    def test_importance_score_validation(self):
        """Test importance score validation."""
        # Valid scores
        for score in [0.0, 0.5, 1.0]:
            memory = MemoryBlock(
                id="mem-score",
                memory_type="episodic",
                content="Test content",
                importance_score=score,
            )
            assert memory.importance_score == score

        # Invalid scores should fail during creation
        with pytest.raises(ValueError):
            MemoryBlock(
                id="mem-invalid-score",
                memory_type="episodic",
                content="Test content",
                importance_score=1.5,  # > 1.0
            )

    def test_related_memories_management(self):
        """Test related memories management."""
        memory = MemoryBlock(
            id="mem-001", memory_type="episodic", content="Test content"
        )

        # Add related memory
        memory.add_related_memory("mem-002")
        assert "mem-002" in memory.related_memories

        # Adding same memory again should not duplicate
        memory.add_related_memory("mem-002")
        assert memory.related_memories.count("mem-002") == 1

        # Remove related memory
        removed = memory.remove_related_memory("mem-002")
        assert removed is True
        assert "mem-002" not in memory.related_memories

        # Removing non-existent memory should return False
        removed = memory.remove_related_memory("mem-999")
        assert removed is False

    def test_access_count_management(self):
        """Test access count increment."""
        memory = MemoryBlock(
            id="mem-001", memory_type="episodic", content="Test content"
        )

        assert memory.access_count == 0

        memory.increment_access()
        assert memory.access_count == 1

        memory.increment_access()
        assert memory.access_count == 2

    def test_importance_score_setting(self):
        """Test importance score setting method."""
        memory = MemoryBlock(
            id="mem-001", memory_type="episodic", content="Test content"
        )

        memory.set_importance(0.8)
        assert memory.importance_score == 0.8

        # Invalid score should raise error
        with pytest.raises(ValueError):
            memory.set_importance(1.5)

    def test_metadata_management(self):
        """Test metadata management methods."""
        memory = MemoryBlock(
            id="mem-001", memory_type="episodic", content="Test content"
        )

        # Add metadata
        memory.add_metadata("patient_id", "pat-001")
        assert memory.get_metadata("patient_id") == "pat-001"

        # Get non-existent metadata with default
        assert memory.get_metadata("non_existent", "default") == "default"

        # Update existing metadata
        memory.add_metadata("patient_id", "pat-002")
        assert memory.get_metadata("patient_id") == "pat-002"

    def test_memory_block_repr(self):
        """Test MemoryBlock __repr__ method."""
        memory = MemoryBlock(
            id="mem-001",
            memory_type="episodic",
            content="Test content",
            importance_score=0.8,
        )

        repr_str = repr(memory)
        assert "MemoryBlock" in repr_str
        assert "mem-001" in repr_str
        assert "episodic" in repr_str
        assert "0.8" in repr_str

    def test_json_serialization(self):
        """Test JSON serialization and deserialization."""
        memory = MemoryBlock(
            id="mem-001",
            memory_type="episodic",
            content="Patient complained of headache",
            importance_score=0.8,
            metadata={"patient_id": "pat-001"},
        )

        # Serialize to JSON
        json_data = memory.model_dump()

        # Check required fields are present
        assert json_data["resource_type"] == "MemoryBlock"
        assert json_data["id"] == "mem-001"
        assert json_data["memory_type"] == "episodic"
        assert json_data["content"] == "Patient complained of headache"
        assert json_data["importance_score"] == 0.8
        assert json_data["metadata"]["patient_id"] == "pat-001"

        # Deserialize from JSON
        memory2 = MemoryBlock(**json_data)
        assert memory2.id == memory.id
        assert memory2.memory_type == memory.memory_type
        assert memory2.content == memory.content
        assert memory2.importance_score == memory.importance_score
