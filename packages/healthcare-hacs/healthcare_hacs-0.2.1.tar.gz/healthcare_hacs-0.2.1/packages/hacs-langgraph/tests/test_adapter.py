"""Tests for HACS LangGraph adapter."""

from hacs_core import Actor, MemoryBlock
from hacs_langgraph import (
    CustomStateBuilder,
    HACSToolRegistry,
    LangGraphAdapter,
    LangGraphStateType,
    MemoryManager,
    StateTransition,
    create_custom_workflow_state,
    create_state_bridge,
)
from hacs_models import Observation, Patient


class TestLangGraphAdapter:
    """Test the LangGraphAdapter class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.adapter = LangGraphAdapter()
        self.actor = Actor(name="Dr. Test", role="physician")

    def test_create_hacs_state(self):
        """Test creating a basic HACS state."""
        state = self.adapter.create_hacs_state(
            workflow_type=LangGraphStateType.CLINICAL_ASSESSMENT, actor=self.actor
        )

        assert state["workflow_type"] == "clinical_assessment"
        assert state["actor_context"]["actor_name"] == "Dr. Test"
        assert state["actor_context"]["actor_role"] == "physician"
        assert state["current_step"] == "start"
        assert state["version"] == 1
        assert isinstance(state["workflow_id"], str)
        assert len(state["workflow_id"]) > 0

    def test_create_clinical_workflow_state(self):
        """Test creating clinical workflow state with patient and observations."""
        patient = Patient(full_name="John Doe", age=45)
        observations = [
            Observation(code_text="blood pressure", value_numeric=140, unit="mmHg")
        ]

        state = self.adapter.create_clinical_workflow_state(
            patient=patient, observations=observations, actor=self.actor
        )

        assert state["patient"]["display_name"] == "John Doe"
        assert len(state["observations"]) == 1
        assert state["observations"][0]["value_numeric"] == 140
        assert state["clinical_context"]["patient_name"] == "John Doe"
        assert state["clinical_context"]["observation_count"] == 1

    def test_add_resource_to_state(self):
        """Test adding resources to state."""
        state = self.adapter.create_hacs_state(
            workflow_type=LangGraphStateType.CLINICAL_ASSESSMENT, actor=self.actor
        )

        patient = Patient(full_name="Jane Smith", age=30)
        observation = Observation(code_text="heart rate", value_numeric=72, unit="bpm")

        # Add patient
        state = self.adapter.add_resource_to_state(state, patient)
        assert state["patient"]["display_name"] == "Jane Smith"

        # Add observation
        state = self.adapter.add_resource_to_state(state, observation)
        assert len(state["observations"]) == 1
        assert state["observations"][0]["value_numeric"] == 72

    def test_tool_registry(self):
        """Test tool registry functionality."""

        def mock_tool(param1: str, param2: int = 10) -> dict:
            return {"result": f"{param1}_{param2}"}

        self.adapter.register_tool(
            "mock_tool", mock_tool, description="A mock tool for testing"
        )

        assert "mock_tool" in self.adapter.tool_registry.list_tools()

        tool = self.adapter.tool_registry.get_tool("mock_tool")
        assert tool is not None

        result = tool("test", param2=20)
        assert result["result"] == "test_20"

    def test_execute_tool(self):
        """Test tool execution with state update."""

        def risk_calculator(age: int, **kwargs) -> dict:
            return {"risk": age * 0.01}

        self.adapter.register_tool("risk_calculator", risk_calculator)

        state = self.adapter.create_hacs_state(
            workflow_type=LangGraphStateType.CLINICAL_ASSESSMENT, actor=self.actor
        )

        # Execute tool
        state = self.adapter.execute_tool(state, "risk_calculator", age=45)

        assert "risk_calculator" in state["tool_results"]
        assert state["tool_results"]["risk_calculator"]["risk"] == 0.45
        assert len(state["tool_history"]) == 1
        assert state["tool_history"][0]["success"] is True

    def test_state_transitions(self):
        """Test state transitions."""

        def high_risk_condition(state):
            return state.get("risk_level") == "high"

        def set_urgent_priority(state):
            return {**state, "priority": "urgent"}

        transition = StateTransition(
            from_step="assessment",
            to_step="intervention",
            condition=high_risk_condition,
            action=set_urgent_priority,
        )

        self.adapter.add_state_transition(transition)

        state = self.adapter.create_hacs_state(
            workflow_type=LangGraphStateType.CLINICAL_ASSESSMENT,
            actor=self.actor,
            initial_step="assessment",
        )

        # Should not transition without condition
        state = self.adapter.transition_state(state)
        assert state["current_step"] == "assessment"

        # Should transition with condition
        state["risk_level"] = "high"
        state = self.adapter.transition_state(state)
        assert state["current_step"] == "intervention"
        assert state["priority"] == "urgent"

    def test_memory_management(self):
        """Test memory management functionality."""
        memory = MemoryBlock(
            content="Patient shows signs of hypertension",
            memory_type="clinical_observation",
            confidence=0.85,
        )

        workflow_id = "test-workflow-123"
        self.adapter.add_memory_to_workflow(workflow_id, memory)

        memories = self.adapter.get_workflow_memories(workflow_id)
        assert len(memories) == 1
        assert memories[0].content == "Patient shows signs of hypertension"

        # Test filtered retrieval
        clinical_memories = self.adapter.get_workflow_memories(
            workflow_id, "clinical_observation"
        )
        assert len(clinical_memories) == 1

        other_memories = self.adapter.get_workflow_memories(workflow_id, "other_type")
        assert len(other_memories) == 0


class TestCustomStateBuilder:
    """Test the CustomStateBuilder class."""

    def test_add_field(self):
        """Test adding custom fields."""
        builder = CustomStateBuilder()
        builder.add_field("custom_field", str, "default_value")
        builder.add_field("numeric_field", float, 0.0)

        assert "custom_field" in builder.custom_fields
        assert builder.custom_fields["custom_field"] == (str, "default_value")
        assert builder.custom_fields["numeric_field"] == (float, 0.0)

    def test_add_validator(self):
        """Test adding validators."""
        builder = CustomStateBuilder()

        def validate_positive(state):
            return state.get("value", 0) > 0

        builder.add_validator(validate_positive)
        assert len(builder.validators) == 1


class TestHACSToolRegistry:
    """Test the HACSToolRegistry class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.registry = HACSToolRegistry()

    def test_register_tool(self):
        """Test tool registration."""

        def test_tool(param: str) -> dict:
            return {"result": param}

        self.registry.register_tool(
            "test_tool", test_tool, description="Test tool", requires_actor=False
        )

        assert "test_tool" in self.registry.list_tools()

        tool = self.registry.get_tool("test_tool")
        assert tool is not None

        metadata = self.registry.get_tool_metadata("test_tool")
        assert metadata["description"] == "Test tool"
        assert metadata["requires_actor"] is False

    def test_tool_execution(self):
        """Test tool execution."""

        def calculator(x: int, y: int) -> dict:
            return {"sum": x + y, "product": x * y}

        self.registry.register_tool("calculator", calculator)

        tool = self.registry.get_tool("calculator")
        result = tool(5, 3)

        assert result["sum"] == 8
        assert result["product"] == 15


class TestMemoryManager:
    """Test the MemoryManager class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = MemoryManager()

    def test_add_memory(self):
        """Test adding memory to workflow."""
        memory = MemoryBlock(content="Test memory", memory_type="test", confidence=0.9)

        self.manager.add_memory("workflow-1", memory)

        memories = self.manager.get_memories("workflow-1")
        assert len(memories) == 1
        assert memories[0].content == "Test memory"

    def test_get_memories_filtered(self):
        """Test filtered memory retrieval."""
        memory1 = MemoryBlock(content="Memory 1", memory_type="type1", confidence=0.8)
        memory2 = MemoryBlock(content="Memory 2", memory_type="type2", confidence=0.9)

        self.manager.add_memory("workflow-1", memory1)
        self.manager.add_memory("workflow-1", memory2)

        type1_memories = self.manager.get_memories("workflow-1", "type1")
        assert len(type1_memories) == 1
        assert type1_memories[0].content == "Memory 1"

        type2_memories = self.manager.get_memories("workflow-1", "type2")
        assert len(type2_memories) == 1
        assert type2_memories[0].content == "Memory 2"

    def test_consolidation_rules(self):
        """Test memory consolidation rules."""

        def keep_high_confidence(memories):
            return [m for m in memories if m.confidence > 0.8]

        self.manager.add_consolidation_rule(keep_high_confidence)

        memory1 = MemoryBlock(
            content="Low confidence", memory_type="test", confidence=0.5
        )
        memory2 = MemoryBlock(
            content="High confidence", memory_type="test", confidence=0.9
        )

        self.manager.add_memory("workflow-1", memory1)
        self.manager.add_memory("workflow-1", memory2)

        consolidated = self.manager.consolidate_memories("workflow-1")
        assert len(consolidated) == 1
        assert consolidated[0].content == "High confidence"


class TestConvenienceFunctions:
    """Test convenience functions."""

    def test_create_custom_workflow_state(self):
        """Test creating custom workflow state."""
        actor = Actor(name="Dr. Test", role="physician")

        state = create_custom_workflow_state(
            workflow_type="emergency_assessment",
            actor=actor,
            custom_fields={"triage_level": "urgent", "chief_complaint": "chest pain"},
        )

        assert state["workflow_type"] == "emergency_assessment"
        assert state["triage_level"] == "urgent"
        assert state["chief_complaint"] == "chest pain"

    def test_create_state_bridge(self):
        """Test state bridging functionality."""
        actor = Actor(name="Dr. Test", role="physician")

        # Create source state
        source_state = {
            "workflow_id": "source-123",
            "workflow_type": "assessment",
            "patient": {"name": "John Doe"},
            "observations": [{"type": "bp", "value": 140}],
            "metadata": {"source": "test"},
        }

        # Bridge to new workflow type
        target_state = create_state_bridge(
            source_state=source_state,
            target_workflow_type="treatment_planning",
            actor=actor,
            preserve_data=True,
        )

        assert target_state["workflow_type"] == "treatment_planning"
        assert target_state["patient"]["name"] == "John Doe"
        assert len(target_state["observations"]) == 1
        assert target_state["metadata"]["source"] == "test"
        assert target_state["metadata"]["bridged_from"] == "assessment"
