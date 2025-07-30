"""
Tests for Evidence and Actor models.

Tests the Evidence and Actor models to ensure proper functionality,
validation, business logic, and security features.
"""

import pytest
from datetime import datetime, timezone

from hacs_core import Evidence, EvidenceType, Actor, ActorRole, SessionStatus


class TestEvidence:
    """Test cases for Evidence class."""

    def test_basic_instantiation(self):
        """Test basic evidence creation."""
        evidence = Evidence(
            id="ev-001",
            citation="Test Citation",
            content="Test evidence content",
            evidence_type=EvidenceType.CLINICAL_NOTE,
        )

        assert evidence.resource_type == "Evidence"
        assert evidence.id == "ev-001"
        assert evidence.citation == "Test Citation"
        assert evidence.content == "Test evidence content"
        assert evidence.evidence_type == EvidenceType.CLINICAL_NOTE
        assert evidence.confidence_score == 0.8  # default
        assert evidence.quality_score == 0.8  # default
        assert evidence.vector_id is None  # default
        assert evidence.provenance == {}  # default
        assert evidence.linked_resources == []  # default
        assert evidence.review_status == "pending"  # default

    def test_evidence_types(self):
        """Test all valid evidence types."""
        for evidence_type in EvidenceType:
            evidence = Evidence(
                id=f"ev-{evidence_type.value}",
                citation="Test Citation",
                content="Test content",
                evidence_type=evidence_type,
            )
            assert evidence.evidence_type == evidence_type

    def test_content_validation(self):
        """Test content validation."""
        # Empty content should fail
        with pytest.raises(ValueError, match="Evidence content cannot be empty"):
            Evidence(
                id="ev-empty",
                citation="Test Citation",
                content="",
                evidence_type=EvidenceType.CLINICAL_NOTE,
            )

        # Whitespace-only content should fail
        with pytest.raises(ValueError, match="Evidence content cannot be empty"):
            Evidence(
                id="ev-whitespace",
                citation="Test Citation",
                content="   ",
                evidence_type=EvidenceType.CLINICAL_NOTE,
            )

    def test_citation_validation(self):
        """Test citation validation."""
        # Empty citation should fail
        with pytest.raises(ValueError, match="Citation cannot be empty"):
            Evidence(
                id="ev-no-citation",
                citation="",
                content="Test content",
                evidence_type=EvidenceType.CLINICAL_NOTE,
            )

    def test_confidence_quality_scores(self):
        """Test confidence and quality score validation."""
        # Valid scores
        evidence = Evidence(
            id="ev-scores",
            citation="Test Citation",
            content="Test content",
            evidence_type=EvidenceType.CLINICAL_NOTE,
            confidence_score=0.9,
            quality_score=0.7,
        )
        assert evidence.confidence_score == 0.9
        assert evidence.quality_score == 0.7
        assert evidence.overall_reliability == 0.8  # (0.9 + 0.7) / 2

        # Invalid scores should fail
        with pytest.raises(ValueError):
            Evidence(
                id="ev-invalid-confidence",
                citation="Test Citation",
                content="Test content",
                evidence_type=EvidenceType.CLINICAL_NOTE,
                confidence_score=1.5,  # > 1.0
            )

    def test_vector_reference_management(self):
        """Test vector reference management."""
        evidence = Evidence(
            id="ev-vector",
            citation="Test Citation",
            content="Test content",
            evidence_type=EvidenceType.CLINICAL_NOTE,
        )

        # Add vector reference
        evidence.add_vector_reference("vec_123")
        assert evidence.vector_id == "vec_123"

        # Update vector reference
        evidence.add_vector_reference("vec_456")
        assert evidence.vector_id == "vec_456"

    def test_provenance_management(self):
        """Test provenance management."""
        evidence = Evidence(
            id="ev-provenance",
            citation="Test Citation",
            content="Test content",
            evidence_type=EvidenceType.CLINICAL_NOTE,
        )

        # Add provenance
        evidence.update_provenance("source", "Epic EHR")
        assert evidence.provenance["source"] == "Epic EHR"

        # Update existing provenance
        evidence.update_provenance("source", "Cerner")
        assert evidence.provenance["source"] == "Cerner"

    def test_resource_linking(self):
        """Test resource linking functionality."""
        evidence = Evidence(
            id="ev-linking",
            citation="Test Citation",
            content="Test content",
            evidence_type=EvidenceType.CLINICAL_NOTE,
        )

        # Link to resource
        evidence.link_to_resource("patient-001")
        assert "patient-001" in evidence.linked_resources

        # Linking same resource again should not duplicate
        evidence.link_to_resource("patient-001")
        assert evidence.linked_resources.count("patient-001") == 1

        # Link to another resource
        evidence.link_to_resource("encounter-123")
        assert "encounter-123" in evidence.linked_resources

        # Unlink resource
        unlinked = evidence.unlink_from_resource("patient-001")
        assert unlinked is True
        assert "patient-001" not in evidence.linked_resources

        # Unlinking non-existent resource should return False
        unlinked = evidence.unlink_from_resource("non-existent")
        assert unlinked is False

    def test_score_setting_methods(self):
        """Test score setting methods."""
        evidence = Evidence(
            id="ev-scores",
            citation="Test Citation",
            content="Test content",
            evidence_type=EvidenceType.CLINICAL_NOTE,
        )

        # Set confidence score
        evidence.set_confidence(0.95)
        assert evidence.confidence_score == 0.95

        # Set quality score
        evidence.set_quality(0.85)
        assert evidence.quality_score == 0.85

        # Invalid scores should raise errors
        with pytest.raises(ValueError):
            evidence.set_confidence(1.5)

        with pytest.raises(ValueError):
            evidence.set_quality(-0.1)

    def test_tag_management(self):
        """Test tag management."""
        evidence = Evidence(
            id="ev-tags",
            citation="Test Citation",
            content="Test content",
            evidence_type=EvidenceType.CLINICAL_NOTE,
        )

        # Add tags
        evidence.add_tag("Cardiology")
        evidence.add_tag("HYPERTENSION")  # Should be normalized to lowercase
        assert "cardiology" in evidence.tags
        assert "hypertension" in evidence.tags

        # Adding same tag should not duplicate
        evidence.add_tag("cardiology")
        assert evidence.tags.count("cardiology") == 1

        # Remove tag
        removed = evidence.remove_tag("cardiology")
        assert removed is True
        assert "cardiology" not in evidence.tags

        # Removing non-existent tag should return False
        removed = evidence.remove_tag("non-existent")
        assert removed is False

    def test_review_status_management(self):
        """Test review status management."""
        evidence = Evidence(
            id="ev-review",
            citation="Test Citation",
            content="Test content",
            evidence_type=EvidenceType.CLINICAL_NOTE,
        )

        assert evidence.review_status == "pending"

        evidence.update_review_status("reviewed")
        assert evidence.review_status == "reviewed"

        evidence.update_review_status("approved")
        assert evidence.review_status == "approved"

    def test_quality_assessment(self):
        """Test quality assessment methods."""
        evidence = Evidence(
            id="ev-quality",
            citation="Test Citation",
            content="Test content",
            evidence_type=EvidenceType.CLINICAL_NOTE,
            confidence_score=0.9,
            quality_score=0.85,
        )

        # High quality evidence
        assert evidence.is_high_quality()  # default threshold 0.8
        assert evidence.is_high_quality(0.8)

        # Lower quality evidence
        evidence.set_confidence(0.6)
        evidence.set_quality(0.6)
        assert not evidence.is_high_quality()  # overall_reliability = 0.6
        assert evidence.is_high_quality(0.5)  # lower threshold

    def test_evidence_repr(self):
        """Test Evidence __repr__ method."""
        evidence = Evidence(
            id="ev-repr",
            citation="Test Citation",
            content="Test content",
            evidence_type=EvidenceType.LAB_RESULT,
            confidence_score=0.9,
            quality_score=0.8,
        )

        repr_str = repr(evidence)
        assert "Evidence" in repr_str
        assert "ev-repr" in repr_str
        assert "lab_result" in repr_str
        assert "0.85" in repr_str  # overall_reliability


class TestActor:
    """Test cases for Actor class."""

    def test_basic_instantiation(self):
        """Test basic actor creation."""
        actor = Actor(
            id="actor-001", name="Dr. Sarah Johnson", role=ActorRole.PHYSICIAN
        )

        assert actor.resource_type == "Actor"
        assert actor.id == "actor-001"
        assert actor.name == "Dr. Sarah Johnson"
        assert actor.role == ActorRole.PHYSICIAN
        assert actor.permissions == []  # default
        assert actor.auth_context == {}  # default
        assert actor.session_id is None  # default
        assert actor.session_status == SessionStatus.INACTIVE  # default
        assert actor.is_active is True  # default
        assert actor.security_level == "medium"  # default

    def test_actor_roles(self):
        """Test all valid actor roles."""
        for role in ActorRole:
            actor = Actor(
                id=f"actor-{role.value}", name=f"Test {role.value}", role=role
            )
            assert actor.role == role

    def test_name_validation(self):
        """Test name validation."""
        # Empty name should fail
        with pytest.raises(ValueError, match="Actor name cannot be empty"):
            Actor(id="actor-empty", name="", role=ActorRole.PHYSICIAN)

        # Whitespace-only name should fail
        with pytest.raises(ValueError, match="Actor name cannot be empty"):
            Actor(id="actor-whitespace", name="   ", role=ActorRole.PHYSICIAN)

    def test_permission_validation(self):
        """Test permission validation."""
        # Valid permissions
        actor = Actor(
            id="actor-perms",
            name="Test Actor",
            role=ActorRole.PHYSICIAN,
            permissions=["read:patient", "write:observation", "admin:system"],
        )
        assert "read:patient" in actor.permissions
        assert "write:observation" in actor.permissions
        assert "admin:system" in actor.permissions

        # Invalid permission format should fail
        with pytest.raises(ValueError, match="must be in format 'action:resource'"):
            Actor(
                id="actor-invalid-perm",
                name="Test Actor",
                role=ActorRole.PHYSICIAN,
                permissions=["invalid_permission"],  # missing colon
            )

    def test_authentication_status(self):
        """Test authentication status computation."""
        actor = Actor(id="actor-auth", name="Test Actor", role=ActorRole.PHYSICIAN)

        # No auth context - not authenticated
        assert not actor.is_authenticated

        # Add auth context but no session
        actor.update_auth_context("token", "abc123")
        assert not actor.is_authenticated  # session not active

        # Start session
        actor.start_session("sess_123")
        assert actor.is_authenticated

        # Add expiry in future - still authenticated
        future_time = datetime.now(timezone.utc).replace(hour=23, minute=59).isoformat()
        actor.update_auth_context("expires_at", future_time)
        assert actor.is_authenticated

        # Add expiry in past - not authenticated
        past_time = datetime.now(timezone.utc).replace(hour=0, minute=1).isoformat()
        actor.update_auth_context("expires_at", past_time)
        assert not actor.is_authenticated

    def test_permission_checking(self):
        """Test permission checking logic."""
        actor = Actor(
            id="actor-perms",
            name="Test Actor",
            role=ActorRole.PHYSICIAN,
            permissions=["read:patient", "write:observation", "admin:system"],
        )

        # Start session for authentication
        actor.start_session("sess_123")

        # Exact permission match
        assert actor.has_permission("read:patient")
        assert actor.has_permission("write:observation")

        # Case insensitive
        assert actor.has_permission("READ:PATIENT")

        # Permission not granted
        assert not actor.has_permission("delete:patient")

        # Wildcard permissions
        actor.add_permission("read:*")
        assert actor.has_permission("read:encounter")
        assert actor.has_permission("read:anything")

        # Admin permissions
        actor.add_permission("admin:*")
        assert actor.has_permission("delete:patient")
        assert actor.has_permission("write:anything")

        # Inactive actor should not have permissions
        actor.deactivate()
        assert not actor.has_permission("read:patient")

    def test_permission_management(self):
        """Test permission management methods."""
        actor = Actor(id="actor-mgmt", name="Test Actor", role=ActorRole.PHYSICIAN)

        # Add permission
        actor.add_permission("read:patient")
        assert "read:patient" in actor.permissions

        # Adding same permission should not duplicate
        actor.add_permission("read:patient")
        assert actor.permissions.count("read:patient") == 1

        # Remove permission
        removed = actor.remove_permission("read:patient")
        assert removed is True
        assert "read:patient" not in actor.permissions

        # Removing non-existent permission should return False
        removed = actor.remove_permission("non:existent")
        assert removed is False

        # Invalid permission format should raise error
        with pytest.raises(ValueError):
            actor.add_permission("invalid_format")

    def test_session_management(self):
        """Test session management."""
        actor = Actor(id="actor-session", name="Test Actor", role=ActorRole.PHYSICIAN)

        # Start session
        actor.start_session("sess_123", ip_address="192.168.1.100")
        assert actor.session_id == "sess_123"
        assert actor.session_status == SessionStatus.ACTIVE
        assert actor.last_activity is not None
        assert actor.auth_context["ip_address"] == "192.168.1.100"

        # Update activity
        old_activity = actor.last_activity
        actor.update_activity()
        assert actor.last_activity > old_activity

        # End session
        actor.end_session("user_logout")
        assert actor.session_id is None
        assert actor.session_status == SessionStatus.TERMINATED

    def test_actor_activation_deactivation(self):
        """Test actor activation and deactivation."""
        actor = Actor(id="actor-active", name="Test Actor", role=ActorRole.PHYSICIAN)

        # Start with active actor
        assert actor.is_active

        # Start session
        actor.start_session("sess_123")
        assert actor.session_status == SessionStatus.ACTIVE

        # Deactivate actor
        actor.deactivate("security_violation")
        assert not actor.is_active
        assert actor.session_status == SessionStatus.TERMINATED

        # Activate actor
        actor.activate("cleared_security")
        assert actor.is_active

    def test_audit_trail(self):
        """Test audit trail functionality."""
        actor = Actor(id="actor-audit", name="Test Actor", role=ActorRole.PHYSICIAN)

        # Start session (creates audit event)
        actor.start_session("sess_123")

        # Add permission (creates audit event)
        actor.add_permission("read:patient")

        # Remove permission (creates audit event)
        actor.remove_permission("read:patient")

        # Deactivate (creates audit event)
        actor.deactivate()

        # Check audit events
        all_events = actor.get_audit_events()
        assert len(all_events) >= 4

        # Filter by action
        session_events = actor.get_audit_events(action_filter="session_started")
        assert len(session_events) == 1
        assert session_events[0]["action"] == "session_started"

        # Check event structure
        event = all_events[0]
        assert "action" in event
        assert "timestamp" in event
        assert "actor_id" in event
        assert "details" in event

    def test_session_expiry(self):
        """Test session expiry checking."""
        actor = Actor(id="actor-expiry", name="Test Actor", role=ActorRole.PHYSICIAN)

        # No session - expired
        assert actor.is_session_expired()

        # Start session
        actor.start_session("sess_123")
        assert not actor.is_session_expired(timeout_minutes=480)  # 8 hours

        # Very short timeout - should be expired
        assert actor.is_session_expired(timeout_minutes=0)

        # Inactive session - expired
        actor.session_status = SessionStatus.INACTIVE
        assert actor.is_session_expired()

    def test_permission_summary(self):
        """Test permission summary computation."""
        actor = Actor(
            id="actor-summary",
            name="Test Actor",
            role=ActorRole.PHYSICIAN,
            permissions=[
                "read:patient",
                "read:encounter",
                "write:observation",
                "admin:system",
            ],
        )

        summary = actor.permission_summary
        assert "read" in summary
        assert "write" in summary
        assert "admin" in summary
        assert "patient" in summary["read"]
        assert "encounter" in summary["read"]
        assert "observation" in summary["write"]
        assert "system" in summary["admin"]

    def test_actor_repr(self):
        """Test Actor __repr__ method."""
        actor = Actor(id="actor-repr", name="Dr. Test", role=ActorRole.PHYSICIAN)

        repr_str = repr(actor)
        assert "Actor" in repr_str
        assert "actor-repr" in repr_str
        assert "Dr. Test" in repr_str
        assert "physician" in repr_str
        assert "active" in repr_str
        assert "unauthenticated" in repr_str

        # Start session and check authenticated status
        actor.start_session("sess_123")
        repr_str = repr(actor)
        assert "authenticated" in repr_str

    def test_json_serialization(self):
        """Test JSON serialization and deserialization."""
        actor = Actor(
            id="actor-json",
            name="Dr. Test",
            role=ActorRole.PHYSICIAN,
            permissions=["read:patient", "write:observation"],
            auth_context={"token": "abc123"},
            organization="Test Hospital",
        )

        # Serialize to JSON
        json_data = actor.model_dump()

        # Check required fields are present
        assert json_data["resource_type"] == "Actor"
        assert json_data["id"] == "actor-json"
        assert json_data["name"] == "Dr. Test"
        assert json_data["role"] == "physician"
        assert json_data["permissions"] == ["read:patient", "write:observation"]
        assert json_data["auth_context"]["token"] == "abc123"
        assert json_data["organization"] == "Test Hospital"

        # Deserialize from JSON
        actor2 = Actor(**json_data)
        assert actor2.id == actor.id
        assert actor2.name == actor.name
        assert actor2.role == actor.role
        assert actor2.permissions == actor.permissions
