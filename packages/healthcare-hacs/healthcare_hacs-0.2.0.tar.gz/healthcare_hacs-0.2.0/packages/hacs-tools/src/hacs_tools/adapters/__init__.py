"""
HACS Protocol Adapters

This module provides protocol adapters for integrating HACS with various
agent frameworks and communication standards including MCP, A2A, AG-UI,
LangGraph, and CrewAI.
"""

from .mcp_adapter import MCPAdapter, convert_to_mcp_task, convert_from_mcp_result
from .a2a_adapter import A2AAdapter, create_a2a_envelope, extract_from_a2a_envelope
from .ag_ui_adapter import AGUIAdapter, format_for_ag_ui, parse_ag_ui_event
from .langgraph_adapter import (
    LangGraphAdapter,
    create_custom_workflow_state,
    create_state_bridge,
)
from .crewai_adapter import CrewAIAdapter, create_agent_binding, task_to_crew_format

__version__ = "0.1.0"

__all__ = [
    # MCP Adapter
    "MCPAdapter",
    "convert_to_mcp_task",
    "convert_from_mcp_result",
    # A2A Adapter
    "A2AAdapter",
    "create_a2a_envelope",
    "extract_from_a2a_envelope",
    # AG-UI Adapter
    "AGUIAdapter",
    "format_for_ag_ui",
    "parse_ag_ui_event",
    # LangGraph Adapter
    "LangGraphAdapter",
    "create_custom_workflow_state",
    "create_state_bridge",
    # CrewAI Adapter
    "CrewAIAdapter",
    "create_agent_binding",
    "task_to_crew_format",
]
