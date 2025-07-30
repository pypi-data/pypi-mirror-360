"""Tests for HACS CrewAI adapter."""

from hacs_core import Actor, Evidence, MemoryBlock
from hacs_crewai import (
    CrewAIAdapter,
    CrewAIAgentBinding,
    CrewAIAgentRole,
    CrewAITask,
    CrewAITaskType,
    create_agent_binding,
    task_to_crew_format,
)
from hacs_models import Observation, Patient


class TestCrewAIAdapter:
    """Test the CrewAIAdapter class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.adapter = CrewAIAdapter()
        self.actor = Actor(name="Dr. Test", role="physician")

    def test_create_agent_binding(self):
        """Test creating agent binding."""
        binding = self.adapter.create_agent_binding(
            role=CrewAIAgentRole.CLINICAL_ASSESSOR,
            actor=self.actor,
            specializations=["cardiology"],
        )

        assert binding.role == CrewAIAgentRole.CLINICAL_ASSESSOR
        assert binding.actor_binding == self.actor.id
        assert binding.hacs_permissions == self.actor.permissions
        assert "cardiology" in binding.specializations
        assert binding.metadata["actor_name"] == "Dr. Test"

    def test_create_agent_binding_without_actor(self):
        """Test creating agent binding without actor."""
        binding = self.adapter.create_agent_binding(
            role=CrewAIAgentRole.TREATMENT_PLANNER
        )

        assert binding.role == CrewAIAgentRole.TREATMENT_PLANNER
        assert binding.actor_binding is None
        assert binding.hacs_permissions == []
        assert isinstance(binding.agent_id, str)

    def test_create_task(self):
        """Test creating a basic task."""
        task = self.adapter.create_task(
            task_type=CrewAITaskType.PATIENT_ASSESSMENT,
            description="Test task description",
            expected_output="Test expected output",
            agent_role=CrewAIAgentRole.CLINICAL_ASSESSOR,
            actor=self.actor,
        )

        assert task.task_type == CrewAITaskType.PATIENT_ASSESSMENT
        assert task.description == "Test task description"
        assert task.expected_output == "Test expected output"
        assert task.agent_role == CrewAIAgentRole.CLINICAL_ASSESSOR
        assert task.actor_context["actor_name"] == "Dr. Test"
        assert task.priority == 5  # default

    def test_create_patient_assessment_task(self):
        """Test creating patient assessment task."""
        patient = Patient(full_name="John Doe", age=45)
        observations = [
            Observation(code_text="blood pressure", value_numeric=140, unit="mmHg"),
            Observation(code_text="heart rate", value_numeric=80, unit="bpm"),
        ]

        task = self.adapter.create_patient_assessment_task(
            patient=patient, observations=observations, actor=self.actor
        )

        assert task.task_type == CrewAITaskType.PATIENT_ASSESSMENT
        assert task.agent_role == CrewAIAgentRole.CLINICAL_ASSESSOR
        assert task.resources["patient"]["display_name"] == "John Doe"
        assert task.resources["observation_count"] == 2
        assert task.context["patient_name"] == "John Doe"
        assert task.context["observation_count"] == 2

    def test_create_evidence_synthesis_task(self):
        """Test creating evidence synthesis task."""
        evidence_list = [
            Evidence(
                title="Test Evidence 1",
                content="Test content 1",
                evidence_type="clinical_guideline",
                confidence_score=0.9,
                quality_score=0.8,
            ),
            Evidence(
                title="Test Evidence 2",
                content="Test content 2",
                evidence_type="clinical_trial",
                confidence_score=0.85,
                quality_score=0.9,
            ),
        ]

        task = self.adapter.create_evidence_synthesis_task(
            evidence_list=evidence_list,
            query="What is the best treatment?",
            actor=self.actor,
        )

        assert task.task_type == CrewAITaskType.EVIDENCE_SYNTHESIS
        assert task.agent_role == CrewAIAgentRole.EVIDENCE_REVIEWER
        assert task.resources["evidence_count"] == 2
        assert task.resources["query"] == "What is the best treatment?"
        assert task.context["average_confidence"] == 0.875  # (0.9 + 0.85) / 2

    def test_create_memory_consolidation_task(self):
        """Test creating memory consolidation task."""
        memories = [
            MemoryBlock(
                content="Memory 1",
                memory_type="clinical_observation",
                importance_score=0.8,
                confidence=0.9,
            ),
            MemoryBlock(
                content="Memory 2",
                memory_type="treatment_outcome",
                importance_score=0.7,
                confidence=0.85,
            ),
        ]

        task = self.adapter.create_memory_consolidation_task(
            memories=memories,
            consolidation_type="pattern_recognition",
            actor=self.actor,
        )

        assert task.task_type == CrewAITaskType.MEMORY_CONSOLIDATION
        assert task.agent_role == CrewAIAgentRole.MEMORY_MANAGER
        assert task.resources["memory_count"] == 2
        assert task.resources["consolidation_type"] == "pattern_recognition"
        assert task.context["avg_importance"] == 0.75  # (0.8 + 0.7) / 2

    def test_task_to_crew_format(self):
        """Test converting task to CrewAI format."""
        task = self.adapter.create_task(
            task_type=CrewAITaskType.PATIENT_ASSESSMENT,
            description="Test description",
            expected_output="Test output",
            agent_role=CrewAIAgentRole.CLINICAL_ASSESSOR,
            actor=self.actor,
            priority=8,
            timeout_minutes=45,
        )

        crew_format = self.adapter.task_to_crew_format(task)

        assert crew_format["description"] == "Test description"
        assert crew_format["expected_output"] == "Test output"
        assert crew_format["agent"] == "clinical_assessor"
        assert crew_format["priority"] == 8
        assert crew_format["timeout"] == "45m"
        assert crew_format["metadata"]["task_id"] == task.task_id
        assert crew_format["metadata"]["task_type"] == "patient_assessment"

    def test_get_task(self):
        """Test getting task by ID."""
        task = self.adapter.create_task(
            task_type=CrewAITaskType.PATIENT_ASSESSMENT,
            description="Test task",
            expected_output="Test output",
            agent_role=CrewAIAgentRole.CLINICAL_ASSESSOR,
            actor=self.actor,
        )

        retrieved_task = self.adapter.get_task(task.task_id)
        assert retrieved_task is not None
        assert retrieved_task.task_id == task.task_id
        assert retrieved_task.description == "Test task"

        # Test non-existent task
        assert self.adapter.get_task("non-existent") is None

    def test_get_agent(self):
        """Test getting agent by ID."""
        binding = self.adapter.create_agent_binding(
            role=CrewAIAgentRole.CLINICAL_ASSESSOR, actor=self.actor
        )

        retrieved_agent = self.adapter.get_agent(binding.agent_id)
        assert retrieved_agent is not None
        assert retrieved_agent.agent_id == binding.agent_id
        assert retrieved_agent.role == CrewAIAgentRole.CLINICAL_ASSESSOR

        # Test non-existent agent
        assert self.adapter.get_agent("non-existent") is None


class TestCrewAITask:
    """Test the CrewAITask model."""

    def test_task_creation(self):
        """Test creating a task with all fields."""
        task = CrewAITask(
            task_type=CrewAITaskType.PATIENT_ASSESSMENT,
            description="Test task",
            expected_output="Test output",
            agent_role=CrewAIAgentRole.CLINICAL_ASSESSOR,
            priority=7,
            timeout_minutes=60,
        )

        assert task.task_type == CrewAITaskType.PATIENT_ASSESSMENT
        assert task.description == "Test task"
        assert task.expected_output == "Test output"
        assert task.agent_role == CrewAIAgentRole.CLINICAL_ASSESSOR
        assert task.priority == 7
        assert task.timeout_minutes == 60
        assert isinstance(task.task_id, str)

    def test_task_defaults(self):
        """Test task default values."""
        task = CrewAITask(
            task_type=CrewAITaskType.PATIENT_ASSESSMENT,
            description="Test task",
            expected_output="Test output",
            agent_role=CrewAIAgentRole.CLINICAL_ASSESSOR,
        )

        assert task.priority == 5  # default
        assert task.timeout_minutes == 30  # default
        assert task.context == {}  # default
        assert task.tools == []  # default
        assert task.resources == {}  # default
        assert task.dependencies == []  # default


class TestCrewAIAgentBinding:
    """Test the CrewAIAgentBinding model."""

    def test_agent_binding_creation(self):
        """Test creating agent binding."""
        binding = CrewAIAgentBinding(
            role=CrewAIAgentRole.CLINICAL_ASSESSOR,
            goal="Test goal",
            backstory="Test backstory",
            capabilities=["assessment", "diagnosis"],
            tools=["tool1", "tool2"],
            specializations=["cardiology"],
        )

        assert binding.role == CrewAIAgentRole.CLINICAL_ASSESSOR
        assert binding.goal == "Test goal"
        assert binding.backstory == "Test backstory"
        assert binding.capabilities == ["assessment", "diagnosis"]
        assert binding.tools == ["tool1", "tool2"]
        assert binding.specializations == ["cardiology"]
        assert isinstance(binding.agent_id, str)

    def test_agent_binding_defaults(self):
        """Test agent binding default values."""
        binding = CrewAIAgentBinding(
            role=CrewAIAgentRole.CLINICAL_ASSESSOR,
            goal="Test goal",
            backstory="Test backstory",
        )

        assert binding.capabilities == []  # default
        assert binding.tools == []  # default
        assert binding.hacs_permissions == []  # default
        assert binding.memory_access is True  # default
        assert binding.evidence_access is True  # default
        assert binding.actor_binding is None  # default
        assert binding.specializations == []  # default
        assert binding.metadata == {}  # default


class TestConvenienceFunctions:
    """Test convenience functions."""

    def test_create_agent_binding_function(self):
        """Test create_agent_binding convenience function."""
        actor = Actor(name="Dr. Test", role="physician")

        binding = create_agent_binding(
            role="clinical_assessor", actor=actor, specializations=["cardiology"]
        )

        assert binding.role == CrewAIAgentRole.CLINICAL_ASSESSOR
        assert binding.actor_binding == actor.id
        assert "cardiology" in binding.specializations

    def test_task_to_crew_format_function(self):
        """Test task_to_crew_format convenience function."""
        task = CrewAITask(
            task_type=CrewAITaskType.PATIENT_ASSESSMENT,
            description="Test task",
            expected_output="Test output",
            agent_role=CrewAIAgentRole.CLINICAL_ASSESSOR,
            priority=6,
        )

        crew_format = task_to_crew_format(task)

        assert crew_format["description"] == "Test task"
        assert crew_format["expected_output"] == "Test output"
        assert crew_format["agent"] == "clinical_assessor"
        assert crew_format["priority"] == 6


class TestRoleConfigurations:
    """Test role-specific configurations."""

    def setup_method(self):
        """Set up test fixtures."""
        self.adapter = CrewAIAdapter()
        self.actor = Actor(name="Dr. Test", role="physician")

    def test_clinical_assessor_config(self):
        """Test clinical assessor role configuration."""
        binding = self.adapter.create_agent_binding(
            role=CrewAIAgentRole.CLINICAL_ASSESSOR, actor=self.actor
        )

        assert "patient_assessment" in binding.capabilities
        assert "diagnostic_reasoning" in binding.capabilities
        assert "observation_analyzer" in binding.tools
        assert "patient_profiler" in binding.tools

    def test_treatment_planner_config(self):
        """Test treatment planner role configuration."""
        binding = self.adapter.create_agent_binding(
            role=CrewAIAgentRole.TREATMENT_PLANNER, actor=self.actor
        )

        assert "treatment_planning" in binding.capabilities
        assert "medication_management" in binding.capabilities
        assert "treatment_optimizer" in binding.tools
        assert "drug_interaction_checker" in binding.tools

    def test_evidence_reviewer_config(self):
        """Test evidence reviewer role configuration."""
        binding = self.adapter.create_agent_binding(
            role=CrewAIAgentRole.EVIDENCE_REVIEWER, actor=self.actor
        )

        assert "evidence_synthesis" in binding.capabilities
        assert "quality_assessment" in binding.capabilities
        assert "evidence_grader" in binding.tools
        assert "meta_analyzer" in binding.tools

    def test_memory_manager_config(self):
        """Test memory manager role configuration."""
        binding = self.adapter.create_agent_binding(
            role=CrewAIAgentRole.MEMORY_MANAGER, actor=self.actor
        )

        assert "memory_consolidation" in binding.capabilities
        assert "knowledge_extraction" in binding.capabilities
        assert "memory_consolidator" in binding.tools
        assert "pattern_detector" in binding.tools
