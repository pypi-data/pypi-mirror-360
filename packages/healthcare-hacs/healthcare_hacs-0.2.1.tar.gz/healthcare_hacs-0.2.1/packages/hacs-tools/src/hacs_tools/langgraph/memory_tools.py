"""
Memory tools for HACS-LangGraph integration.

This module provides utilities for creating, managing, and consolidating
memories within LangGraph workflows.
"""

import uuid
from typing import Any

from hacs_core import MemoryBlock

from .base_tools import BaseHACSTool, ToolCallResult


class MemoryTool(BaseHACSTool):
    """Tool for managing memories in workflows."""

    def __init__(self):
        super().__init__(
            "memory_manager",
            "Manages memory creation, retrieval, and consolidation in workflows",
        )

    def execute(self, state: dict[str, Any], **kwargs) -> ToolCallResult:
        """Execute memory management operations."""
        operation = kwargs.get("operation", "consolidate")

        if operation == "create":
            return self._create_memory(state, **kwargs)
        elif operation == "consolidate":
            return self._consolidate_memories(state, **kwargs)
        elif operation == "search":
            return self._search_memories(state, **kwargs)
        else:
            return ToolCallResult(
                tool_name=self.name,
                success=False,
                error=f"Unknown operation: {operation}",
            )

    def _create_memory(self, state: dict[str, Any], **kwargs) -> ToolCallResult:
        """Create a new memory from workflow context."""
        try:
            content = kwargs.get("content", "")
            memory_type = kwargs.get("memory_type", "episodic")
            importance_score = kwargs.get("importance_score", 0.5)

            if not content:
                # Generate content from state
                content = self._generate_memory_content(state)

            memory = MemoryBlock(
                id=str(uuid.uuid4()),
                memory_type=memory_type,
                content=content,
                importance_score=importance_score,
                metadata={
                    "workflow_id": state["workflow_id"],
                    "created_from": "langgraph_workflow",
                    "actor_id": state["actor_context"]["actor_id"],
                },
            )

            return ToolCallResult(
                tool_name=self.name,
                success=True,
                result={
                    "memory_id": memory.id,
                    "memory": memory.model_dump(),
                    "operation": "create",
                },
            )

        except Exception as e:
            return ToolCallResult(tool_name=self.name, success=False, error=str(e))

    def _consolidate_memories(self, state: dict[str, Any], **kwargs) -> ToolCallResult:
        """Consolidate memories from the workflow."""
        try:
            memories_data = state.get("memories", [])

            # Convert dict data back to MemoryBlock objects
            memories = []
            for mem_data in memories_data:
                if isinstance(mem_data, dict):
                    memories.append(MemoryBlock(**mem_data))

            # Consolidate by type
            consolidated = {
                "total_memories": len(memories),
                "by_type": {},
                "by_importance": {"high": [], "medium": [], "low": []},
                "key_insights": [],
                "timeline": [],
            }

            for memory in memories:
                # Group by type
                if memory.memory_type not in consolidated["by_type"]:
                    consolidated["by_type"][memory.memory_type] = []
                consolidated["by_type"][memory.memory_type].append(memory.model_dump())

                # Group by importance
                if memory.importance_score >= 0.7:
                    consolidated["by_importance"]["high"].append(memory.model_dump())
                elif memory.importance_score >= 0.4:
                    consolidated["by_importance"]["medium"].append(memory.model_dump())
                else:
                    consolidated["by_importance"]["low"].append(memory.model_dump())

                # Add to timeline
                consolidated["timeline"].append(
                    {
                        "memory_id": memory.id,
                        "timestamp": memory.created_at.isoformat()
                        if memory.created_at
                        else "unknown",
                        "content_preview": memory.content[:100] + "..."
                        if len(memory.content) > 100
                        else memory.content,
                        "importance": memory.importance_score,
                    }
                )

            # Sort timeline by timestamp
            consolidated["timeline"].sort(key=lambda x: x["timestamp"])

            # Extract key insights from high-importance memories
            high_importance = consolidated["by_importance"]["high"]
            if high_importance:
                consolidated["key_insights"] = [
                    mem["content"] for mem in high_importance[:3]
                ]

            return ToolCallResult(
                tool_name=self.name, success=True, result=consolidated
            )

        except Exception as e:
            return ToolCallResult(tool_name=self.name, success=False, error=str(e))

    def _search_memories(self, state: dict[str, Any], **kwargs) -> ToolCallResult:
        """Search memories by content or metadata."""
        try:
            query = kwargs.get("query", "")
            memory_type = kwargs.get("memory_type")
            min_importance = kwargs.get("min_importance", 0.0)

            memories_data = state.get("memories", [])
            matching_memories = []

            for mem_data in memories_data:
                if isinstance(mem_data, dict):
                    # Check importance threshold
                    if mem_data.get("importance_score", 0) < min_importance:
                        continue

                    # Check memory type filter
                    if memory_type and mem_data.get("memory_type") != memory_type:
                        continue

                    # Check query match
                    if query:
                        content = mem_data.get("content", "").lower()
                        if query.lower() not in content:
                            continue

                    matching_memories.append(mem_data)

            return ToolCallResult(
                tool_name=self.name,
                success=True,
                result={
                    "query": query,
                    "total_found": len(matching_memories),
                    "memories": matching_memories,
                },
            )

        except Exception as e:
            return ToolCallResult(tool_name=self.name, success=False, error=str(e))

    def _generate_memory_content(self, state: dict[str, Any]) -> str:
        """Generate memory content from workflow state."""
        content_parts = []

        # Add workflow info
        workflow_type = state.get("workflow_type", "unknown")
        current_step = state.get("current_step", "unknown")
        content_parts.append(f"Workflow: {workflow_type}, Step: {current_step}")

        # Add patient info if available
        patient = state.get("patient")
        if patient:
            patient_name = patient.get("display_name", "Unknown Patient")
            content_parts.append(f"Patient: {patient_name}")

        # Add observation summary
        observations = state.get("observations", [])
        if observations:
            content_parts.append(f"Processed {len(observations)} observations")

        # Add tool results summary
        tool_results = state.get("tool_results", [])
        if tool_results:
            successful_tools = [tr for tr in tool_results if tr.get("success", False)]
            content_parts.append(f"Executed {len(successful_tools)} successful tools")

        return ". ".join(content_parts)


def create_clinical_memory(
    content: str,
    patient_id: str | None = None,
    importance_score: float = 0.7,
    **metadata,
) -> MemoryBlock:
    """Create a clinical memory block."""
    memory_metadata = {
        "memory_category": "clinical",
        "patient_id": patient_id,
        **metadata,
    }

    return MemoryBlock(
        id=str(uuid.uuid4()),
        memory_type="episodic",
        content=content,
        importance_score=importance_score,
        metadata=memory_metadata,
    )


def create_evidence_memory(
    evidence_summary: str,
    evidence_ids: list[str],
    confidence_score: float = 0.8,
    **metadata,
) -> MemoryBlock:
    """Create a memory block for evidence synthesis."""
    memory_metadata = {
        "memory_category": "evidence",
        "evidence_ids": evidence_ids,
        "confidence_score": confidence_score,
        **metadata,
    }

    return MemoryBlock(
        id=str(uuid.uuid4()),
        memory_type="episodic",
        content=evidence_summary,
        importance_score=confidence_score,
        metadata=memory_metadata,
    )


def create_decision_memory(
    decision_context: dict[str, Any],
    reasoning_trace: list[dict[str, Any]],
    outcome: str,
    **metadata,
) -> MemoryBlock:
    """Create a memory block for decision-making processes."""
    content = f"Decision outcome: {outcome}. "
    content += f"Based on {len(reasoning_trace)} reasoning steps. "
    content += f"Context: {decision_context.get('summary', 'No summary available')}"

    memory_metadata = {
        "memory_category": "decision",
        "decision_context": decision_context,
        "reasoning_trace": reasoning_trace,
        "outcome": outcome,
        **metadata,
    }

    return MemoryBlock(
        id=str(uuid.uuid4()),
        memory_type="procedural",
        content=content,
        importance_score=0.8,
        metadata=memory_metadata,
    )
