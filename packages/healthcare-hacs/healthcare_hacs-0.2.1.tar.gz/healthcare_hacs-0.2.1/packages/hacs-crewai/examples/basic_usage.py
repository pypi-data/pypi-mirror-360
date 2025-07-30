"""
Basic Usage Example for HACS CrewAI Integration

This example demonstrates the basic usage of the HACS CrewAI adapter
for creating multi-agent clinical workflows.
"""

from hacs_core import Actor, Evidence, MemoryBlock
from hacs_crewai import CrewAIAdapter, CrewAIAgentRole, CrewAITaskType
from hacs_models import Observation, Patient


def main():
    """Demonstrate basic HACS CrewAI integration."""
    print("🤖 HACS CrewAI Basic Usage Example")
    print("=" * 50)

    # Create adapter
    adapter = CrewAIAdapter()

    # Create actors
    physician = Actor(name="Dr. Sarah Chen", role="physician")
    nurse = Actor(name="Maria Rodriguez RN", role="nurse")
    researcher = Actor(name="Dr. James Wilson", role="researcher")

    print(f"👩‍⚕️ Created physician: {physician.name}")
    print(f"👩‍⚕️ Created nurse: {nurse.name}")
    print(f"🔬 Created researcher: {researcher.name}")

    # Create specialized agents
    adapter.create_agent_binding(
        role=CrewAIAgentRole.CLINICAL_ASSESSOR,
        actor=physician,
        specializations=["cardiology", "internal_medicine"],
    )

    adapter.create_agent_binding(
        role=CrewAIAgentRole.TREATMENT_PLANNER,
        actor=physician,
        specializations=["cardiology"],
    )

    adapter.create_agent_binding(
        role=CrewAIAgentRole.PATIENT_ADVOCATE,
        actor=nurse,
        specializations=["patient_education"],
    )

    adapter.create_agent_binding(
        role=CrewAIAgentRole.EVIDENCE_REVIEWER,
        actor=researcher,
        specializations=["clinical_research", "meta_analysis"],
    )

    print(f"\n🤖 Created {len(adapter.agent_registry)} specialized agents:")
    for _agent_id, agent in adapter.agent_registry.items():
        print(f"   - {agent.role.value}: {agent.metadata.get('actor_name', 'Unknown')}")

    # Create patient and observations
    patient = Patient(full_name="Robert Johnson", age=62)
    observations = [
        Observation(
            code_text="systolic blood pressure", value_numeric=155, unit="mmHg"
        ),
        Observation(
            code_text="diastolic blood pressure", value_numeric=95, unit="mmHg"
        ),
        Observation(code_text="heart rate", value_numeric=88, unit="bpm"),
        Observation(code_text="cholesterol", value_numeric=220, unit="mg/dL"),
        Observation(code_text="BMI", value_numeric=29.2, unit="kg/m2"),
    ]

    print(f"\n👤 Patient: {patient.display_name}, age {patient.age_years}")
    print(f"📊 Observations: {len(observations)}")

    # Create patient assessment task
    assessment_task = adapter.create_patient_assessment_task(
        patient=patient, observations=observations, actor=physician, priority=8
    )

    print("\n📋 Created assessment task:")
    print(f"   Task ID: {assessment_task.task_id}")
    print(f"   Type: {assessment_task.task_type.value}")
    print(f"   Agent: {assessment_task.agent_role.value}")
    print(f"   Priority: {assessment_task.priority}")

    # Create treatment planning task (depends on assessment)
    planning_task = adapter.create_task(
        task_type=CrewAITaskType.TREATMENT_PLANNING,
        description=f"Develop comprehensive treatment plan for {patient.display_name} based on assessment findings",
        expected_output="Evidence-based treatment plan with medication recommendations, lifestyle modifications, and follow-up schedule",
        agent_role=CrewAIAgentRole.TREATMENT_PLANNER,
        dependencies=[assessment_task.task_id],
        actor=physician,
        priority=7,
        context={
            "patient_id": patient.id,
            "assessment_task_id": assessment_task.task_id,
            "focus_areas": ["hypertension", "cardiovascular_risk"],
        },
    )

    print("\n📋 Created treatment planning task:")
    print(f"   Task ID: {planning_task.task_id}")
    print(f"   Dependencies: {planning_task.dependencies}")
    print(f"   Priority: {planning_task.priority}")

    # Create evidence synthesis task
    evidence_list = [
        Evidence(
            title="2023 Hypertension Management Guidelines",
            content="Updated evidence-based guidelines for hypertension management in adults",
            evidence_type="clinical_guideline",
            confidence_score=0.95,
            quality_score=0.92,
        ),
        Evidence(
            title="ACE Inhibitor Efficacy in Elderly Patients",
            content="Meta-analysis of ACE inhibitor effectiveness in patients over 60",
            evidence_type="systematic_review",
            confidence_score=0.88,
            quality_score=0.85,
        ),
        Evidence(
            title="Lifestyle Interventions for Cardiovascular Risk",
            content="Randomized controlled trial of lifestyle modifications",
            evidence_type="clinical_trial",
            confidence_score=0.82,
            quality_score=0.78,
        ),
    ]

    synthesis_task = adapter.create_evidence_synthesis_task(
        evidence_list=evidence_list,
        query="What is the optimal first-line treatment approach for hypertension in a 62-year-old male with elevated cardiovascular risk?",
        actor=researcher,
        priority=6,
    )

    print("\n📋 Created evidence synthesis task:")
    print(f"   Task ID: {synthesis_task.task_id}")
    print(f"   Evidence sources: {synthesis_task.resources['evidence_count']}")
    print(f"   Query: {synthesis_task.resources['query']}")

    # Create patient advocacy task
    advocacy_task = adapter.create_task(
        task_type=CrewAITaskType.PATIENT_ASSESSMENT,
        description="Review treatment plan for patient understanding and develop education materials",
        expected_output="Patient education plan, compliance strategies, and communication recommendations",
        agent_role=CrewAIAgentRole.PATIENT_ADVOCATE,
        dependencies=[planning_task.task_id],
        actor=nurse,
        priority=7,
        context={
            "patient_id": patient.id,
            "education_focus": [
                "medication_compliance",
                "lifestyle_changes",
                "monitoring",
            ],
        },
    )

    print("\n📋 Created patient advocacy task:")
    print(f"   Task ID: {advocacy_task.task_id}")
    print(f"   Dependencies: {advocacy_task.dependencies}")

    # Create memory consolidation task
    memories = [
        MemoryBlock(
            content="Patient shows good response to ACE inhibitor therapy with minimal side effects",
            memory_type="treatment_outcome",
            importance_score=0.85,
            confidence=0.9,
        ),
        MemoryBlock(
            content="Elderly patients often require dose adjustments for antihypertensive medications",
            memory_type="clinical_pattern",
            importance_score=0.8,
            confidence=0.88,
        ),
        MemoryBlock(
            content="Patient education about medication timing improves compliance significantly",
            memory_type="patient_education",
            importance_score=0.75,
            confidence=0.85,
        ),
    ]

    consolidation_task = adapter.create_memory_consolidation_task(
        memories=memories,
        consolidation_type="clinical_patterns",
        actor=physician,
        priority=5,
    )

    print("\n📋 Created memory consolidation task:")
    print(f"   Task ID: {consolidation_task.task_id}")
    print(f"   Memory blocks: {consolidation_task.resources['memory_count']}")
    print(
        f"   Consolidation type: {consolidation_task.resources['consolidation_type']}"
    )

    # Convert tasks to CrewAI format
    print("\n🔄 Converting tasks to CrewAI format:")

    tasks = [
        assessment_task,
        planning_task,
        synthesis_task,
        advocacy_task,
        consolidation_task,
    ]
    crew_tasks = []

    for task in tasks:
        crew_task = adapter.task_to_crew_format(task)
        crew_tasks.append(crew_task)
        print(f"   ✅ {task.task_type.value} -> CrewAI format")

    # Display task workflow
    print("\n🔗 Task Workflow:")
    print(
        f"   1. {assessment_task.task_type.value} (Priority: {assessment_task.priority})"
    )
    print(
        f"   2. {planning_task.task_type.value} (Priority: {planning_task.priority}) [depends on #1]"
    )
    print(
        f"   3. {synthesis_task.task_type.value} (Priority: {synthesis_task.priority}) [parallel]"
    )
    print(
        f"   4. {advocacy_task.task_type.value} (Priority: {advocacy_task.priority}) [depends on #2]"
    )
    print(
        f"   5. {consolidation_task.task_type.value} (Priority: {consolidation_task.priority}) [parallel]"
    )

    # Show agent capabilities
    print("\n🧠 Agent Capabilities:")
    for _agent_id, agent in adapter.agent_registry.items():
        print(f"   {agent.role.value}:")
        print(f"     - Capabilities: {', '.join(agent.capabilities)}")
        print(f"     - Tools: {', '.join(agent.tools)}")
        print(f"     - Specializations: {', '.join(agent.specializations)}")

    # Show task registry summary
    print("\n📊 Task Registry Summary:")
    print(f"   Total tasks created: {len(adapter.task_registry)}")
    print(f"   Total agents created: {len(adapter.agent_registry)}")

    task_types = {}
    for task in adapter.task_registry.values():
        task_type = task.task_type.value
        if task_type not in task_types:
            task_types[task_type] = 0
        task_types[task_type] += 1

    print("   Task distribution:")
    for task_type, count in task_types.items():
        print(f"     - {task_type}: {count}")

    print("\n✅ Multi-agent clinical workflow created successfully!")
    print(f"   Ready for CrewAI execution with {len(crew_tasks)} tasks")
    print("   Workflow covers: Assessment → Planning → Advocacy → Evidence → Memory")


if __name__ == "__main__":
    main()
