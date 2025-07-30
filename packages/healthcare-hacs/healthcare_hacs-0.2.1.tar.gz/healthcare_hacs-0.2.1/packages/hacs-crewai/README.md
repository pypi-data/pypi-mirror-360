# 🤖 HACS CrewAI Adapter

[![PyPI version](https://badge.fury.io/py/hacs-crewai.svg)](https://badge.fury.io/py/hacs-crewai)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

**CrewAI integration for HACS (Healthcare Agent Communication Standard)**

Seamlessly integrate HACS clinical data models with CrewAI multi-agent workflows for collaborative healthcare AI applications.

## 🚀 Quick Start

### Installation

```bash
pip install hacs-crewai
```

### Basic Usage

```python
from hacs_crewai import CrewAIAdapter, CrewAIAgentRole, CrewAITaskType
from hacs_core import Actor
from hacs_models import Patient, Observation

# Create adapter
adapter = CrewAIAdapter()

# Create actor
actor = Actor(name="Dr. Smith", role="physician")

# Create clinical assessor agent
assessor = adapter.create_agent_binding(
    role=CrewAIAgentRole.CLINICAL_ASSESSOR,
    actor=actor,
    specializations=["cardiology", "internal_medicine"]
)

# Create patient and observations
patient = Patient(full_name="John Doe", age=65)
observations = [
    Observation(code_text="blood pressure", value_numeric=160, unit="mmHg"),
    Observation(code_text="heart rate", value_numeric=95, unit="bpm")
]

# Create assessment task
task = adapter.create_patient_assessment_task(
    patient=patient,
    observations=observations,
    actor=actor
)

print(f"Agent: {assessor.role.value}")
print(f"Task: {task.task_type.value}")
print(f"Expected Output: {task.expected_output}")
```

## 🎯 Key Features

### 🤖 Multi-Agent Collaboration
- **Specialized Agents**: Pre-configured clinical agent roles
- **Agent Binding**: Connect CrewAI agents to HACS actors
- **Role-Based Access**: Permissions based on clinical roles
- **Task Orchestration**: Coordinate complex clinical workflows

### 📋 Clinical Task Management
- **Task Types**: Pre-defined clinical task categories
- **Resource Integration**: Embed HACS resources in tasks
- **Priority Management**: Task prioritization and scheduling
- **Dependency Tracking**: Manage task dependencies and workflows

### 🏥 Healthcare-Specific Workflows
- **Patient Assessment**: Comprehensive patient evaluation tasks
- **Evidence Synthesis**: Clinical evidence review and synthesis
- **Memory Consolidation**: Clinical knowledge management
- **Treatment Planning**: Evidence-based treatment recommendations

### 🔧 CrewAI Integration
- **Native Format**: Convert HACS tasks to CrewAI format
- **Tool Integration**: Healthcare-specific tools and capabilities
- **Context Preservation**: Maintain clinical context across agents
- **Audit Trail**: Complete workflow tracking and logging

## 📚 Core Components

### CrewAIAdapter

The main adapter class for integrating HACS with CrewAI:

```python
from hacs_crewai import CrewAIAdapter, CrewAIAgentRole
from hacs_core import Actor

adapter = CrewAIAdapter()

# Create agent binding
agent = adapter.create_agent_binding(
    role=CrewAIAgentRole.CLINICAL_ASSESSOR,
    actor=actor,
    specializations=["emergency_medicine"]
)

# Create task
task = adapter.create_task(
    task_type=CrewAITaskType.PATIENT_ASSESSMENT,
    description="Assess patient condition",
    expected_output="Clinical assessment report",
    agent_role=CrewAIAgentRole.CLINICAL_ASSESSOR,
    actor=actor
)

# Convert to CrewAI format
crew_task = adapter.task_to_crew_format(task)
```

### Agent Roles

Pre-configured clinical agent roles:

```python
from hacs_crewai import CrewAIAgentRole

# Available roles
roles = [
    CrewAIAgentRole.CLINICAL_ASSESSOR,     # Patient assessment and diagnosis
    CrewAIAgentRole.TREATMENT_PLANNER,     # Treatment planning and optimization
    CrewAIAgentRole.EVIDENCE_REVIEWER,     # Clinical evidence synthesis
    CrewAIAgentRole.MEMORY_MANAGER,        # Knowledge management
    CrewAIAgentRole.DATA_ANALYST,          # Clinical data analysis
    CrewAIAgentRole.PATIENT_ADVOCATE,      # Patient advocacy and communication
    CrewAIAgentRole.QUALITY_ASSURANCE,     # Quality control and validation
    CrewAIAgentRole.DECISION_SUPPORT,      # Clinical decision support
]

# Each role has pre-configured:
# - Goal and backstory
# - Capabilities and tools
# - Clinical specializations
# - Permission requirements
```

### Task Types

Specialized clinical task categories:

```python
from hacs_crewai import CrewAITaskType

# Available task types
task_types = [
    CrewAITaskType.PATIENT_ASSESSMENT,     # Comprehensive patient evaluation
    CrewAITaskType.OBSERVATION_ANALYSIS,   # Clinical observation analysis
    CrewAITaskType.TREATMENT_PLANNING,     # Treatment plan development
    CrewAITaskType.EVIDENCE_SYNTHESIS,     # Evidence review and synthesis
    CrewAITaskType.MEMORY_CONSOLIDATION,   # Knowledge consolidation
    CrewAITaskType.QUALITY_REVIEW,         # Quality assurance review
    CrewAITaskType.DECISION_MAKING,        # Clinical decision support
    CrewAITaskType.REPORT_GENERATION,      # Clinical report generation
]
```

## 🏥 Clinical Workflow Examples

### Multi-Agent Patient Assessment

```python
from hacs_crewai import CrewAIAdapter, CrewAIAgentRole, CrewAITaskType
from hacs_core import Actor
from hacs_models import Patient, Observation

# Setup
adapter = CrewAIAdapter()
physician = Actor(name="Dr. Johnson", role="physician")
nurse = Actor(name="Sarah RN", role="nurse")

# Create specialized agents
assessor = adapter.create_agent_binding(
    role=CrewAIAgentRole.CLINICAL_ASSESSOR,
    actor=physician,
    specializations=["cardiology"]
)

planner = adapter.create_agent_binding(
    role=CrewAIAgentRole.TREATMENT_PLANNER,
    actor=physician,
    specializations=["cardiology"]
)

advocate = adapter.create_agent_binding(
    role=CrewAIAgentRole.PATIENT_ADVOCATE,
    actor=nurse
)

# Create patient data
patient = Patient(full_name="Maria Rodriguez", age=59)
observations = [
    Observation(code_text="systolic blood pressure", value_numeric=165, unit="mmHg"),
    Observation(code_text="cholesterol", value_numeric=240, unit="mg/dL"),
    Observation(code_text="BMI", value_numeric=28.5, unit="kg/m2")
]

# Create assessment task
assessment_task = adapter.create_patient_assessment_task(
    patient=patient,
    observations=observations,
    actor=physician,
    priority=8
)

# Create follow-up tasks
planning_task = adapter.create_task(
    task_type=CrewAITaskType.TREATMENT_PLANNING,
    description="Develop treatment plan based on assessment",
    expected_output="Comprehensive treatment plan with medications and lifestyle recommendations",
    agent_role=CrewAIAgentRole.TREATMENT_PLANNER,
    dependencies=[assessment_task.task_id],
    actor=physician
)

advocacy_task = adapter.create_task(
    task_type=CrewAITaskType.PATIENT_ASSESSMENT,
    description="Review treatment plan for patient understanding and compliance",
    expected_output="Patient education plan and compliance recommendations",
    agent_role=CrewAIAgentRole.PATIENT_ADVOCATE,
    dependencies=[planning_task.task_id],
    actor=nurse
)

# Convert to CrewAI format
crew_tasks = [
    adapter.task_to_crew_format(assessment_task),
    adapter.task_to_crew_format(planning_task),
    adapter.task_to_crew_format(advocacy_task)
]
```

### Evidence Synthesis Workflow

```python
from hacs_crewai import CrewAIAdapter, CrewAIAgentRole
from hacs_core import Actor, Evidence

# Setup
adapter = CrewAIAdapter()
researcher = Actor(name="Dr. Chen", role="researcher")

# Create evidence reviewer agent
reviewer = adapter.create_agent_binding(
    role=CrewAIAgentRole.EVIDENCE_REVIEWER,
    actor=researcher,
    specializations=["clinical_research", "meta_analysis"]
)

# Create evidence list
evidence_list = [
    Evidence(
        title="Hypertension Management Guidelines",
        content="Updated guidelines for hypertension management...",
        evidence_type="clinical_guideline",
        confidence_score=0.95,
        quality_score=0.9
    ),
    Evidence(
        title="ACE Inhibitor Efficacy Study",
        content="Randomized controlled trial of ACE inhibitors...",
        evidence_type="clinical_trial",
        confidence_score=0.88,
        quality_score=0.85
    )
]

# Create evidence synthesis task
synthesis_task = adapter.create_evidence_synthesis_task(
    evidence_list=evidence_list,
    query="What is the optimal first-line treatment for hypertension in elderly patients?",
    actor=researcher,
    priority=7
)

# Convert to CrewAI format
crew_task = adapter.task_to_crew_format(synthesis_task)
```

### Memory Consolidation Workflow

```python
from hacs_crewai import CrewAIAdapter, CrewAIAgentRole
from hacs_core import Actor, MemoryBlock

# Setup
adapter = CrewAIAdapter()
clinician = Actor(name="Dr. Williams", role="physician")

# Create memory manager agent
memory_manager = adapter.create_agent_binding(
    role=CrewAIAgentRole.MEMORY_MANAGER,
    actor=clinician,
    specializations=["knowledge_management"]
)

# Create memory blocks
memories = [
    MemoryBlock(
        content="Patient responded well to ACE inhibitor therapy",
        memory_type="treatment_outcome",
        importance_score=0.8,
        confidence=0.9
    ),
    MemoryBlock(
        content="Side effects noted with beta-blocker in elderly patients",
        memory_type="adverse_event",
        importance_score=0.9,
        confidence=0.85
    )
]

# Create memory consolidation task
consolidation_task = adapter.create_memory_consolidation_task(
    memories=memories,
    consolidation_type="clinical_patterns",
    actor=clinician,
    priority=6
)

# Convert to CrewAI format
crew_task = adapter.task_to_crew_format(consolidation_task)
```

## 🔧 Advanced Usage

### Custom Agent Configuration

```python
from hacs_crewai import CrewAIAdapter, CrewAIAgentRole

adapter = CrewAIAdapter()

# Create custom agent with specific configuration
custom_agent = adapter.create_agent_binding(
    role=CrewAIAgentRole.CLINICAL_ASSESSOR,
    actor=actor,
    goal="Specialized pediatric assessment with focus on developmental milestones",
    backstory="You are a pediatric specialist with 15 years of experience...",
    capabilities=["pediatric_assessment", "developmental_screening", "family_counseling"],
    tools=["pediatric_calculator", "growth_chart", "developmental_screener"],
    specializations=["pediatrics", "developmental_medicine"]
)
```

### Task Dependencies and Workflows

```python
# Create dependent tasks
initial_task = adapter.create_task(
    task_type=CrewAITaskType.PATIENT_ASSESSMENT,
    description="Initial patient assessment",
    expected_output="Assessment report",
    agent_role=CrewAIAgentRole.CLINICAL_ASSESSOR,
    actor=actor
)

follow_up_task = adapter.create_task(
    task_type=CrewAITaskType.TREATMENT_PLANNING,
    description="Develop treatment plan",
    expected_output="Treatment plan",
    agent_role=CrewAIAgentRole.TREATMENT_PLANNER,
    dependencies=[initial_task.task_id],  # Depends on initial assessment
    actor=actor
)

quality_task = adapter.create_task(
    task_type=CrewAITaskType.QUALITY_REVIEW,
    description="Quality review of treatment plan",
    expected_output="Quality assessment",
    agent_role=CrewAIAgentRole.QUALITY_ASSURANCE,
    dependencies=[follow_up_task.task_id],  # Depends on treatment plan
    actor=actor
)
```

### CrewAI Integration

```python
from crewai import Agent, Task, Crew

# Convert HACS agents to CrewAI agents
def hacs_to_crewai_agent(binding: CrewAIAgentBinding) -> Agent:
    return Agent(
        role=binding.role.value,
        goal=binding.goal,
        backstory=binding.backstory,
        tools=binding.tools,
        verbose=True
    )

# Convert HACS tasks to CrewAI tasks
def hacs_to_crewai_task(task: CrewAITask, agent: Agent) -> Task:
    return Task(
        description=task.description,
        expected_output=task.expected_output,
        agent=agent,
        tools=task.tools
    )

# Create CrewAI crew
assessor_agent = hacs_to_crewai_agent(assessor)
planner_agent = hacs_to_crewai_agent(planner)

assessment_crewai_task = hacs_to_crewai_task(assessment_task, assessor_agent)
planning_crewai_task = hacs_to_crewai_task(planning_task, planner_agent)

crew = Crew(
    agents=[assessor_agent, planner_agent],
    tasks=[assessment_crewai_task, planning_crewai_task],
    verbose=True
)

# Execute crew
result = crew.kickoff()
```

## 🧪 Testing

The package includes comprehensive tests:

```bash
# Run tests
pytest tests/

# Run with coverage
pytest tests/ --cov=hacs_crewai --cov-report=html

# Run specific test
pytest tests/test_adapter.py::test_create_agent_binding -v
```

## 📖 Documentation

- **[HACS Documentation](https://github.com/solanovisitor/hacs/tree/main/docs)**: Complete HACS documentation
- **[CrewAI Documentation](https://docs.crewai.com/)**: Official CrewAI documentation
- **[Examples](./examples/)**: Comprehensive usage examples
- **[API Reference](./docs/api.md)**: Detailed API documentation

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guidelines](https://github.com/solanovisitor/hacs/blob/main/CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](https://github.com/solanovisitor/hacs/blob/main/LICENSE) file for details.

## 🔗 Related Packages

- **[hacs-core](https://pypi.org/project/hacs-core/)**: Core HACS data models and utilities
- **[hacs-models](https://pypi.org/project/hacs-models/)**: Clinical data models (Patient, Observation, etc.)
- **[hacs-tools](https://pypi.org/project/hacs-tools/)**: Core tools and utilities
- **[hacs-langgraph](https://pypi.org/project/hacs-langgraph/)**: LangGraph integration
- **[hacs-autogen](https://pypi.org/project/hacs-autogen/)**: AutoGen integration

---

**Built with ❤️ for collaborative healthcare AI** 