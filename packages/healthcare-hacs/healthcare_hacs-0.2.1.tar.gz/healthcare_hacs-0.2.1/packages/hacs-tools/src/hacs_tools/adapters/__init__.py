"""
HACS Protocol Adapters

This module provides protocol adapters for integrating HACS with various
agent frameworks and communication standards.

DEPRECATION NOTICE:
- LangGraph adapter has been moved to 'hacs-langgraph' package
- CrewAI adapter has been moved to 'hacs-crewai' package
- AutoGen UI adapter will be moved to 'hacs-autogen' package

Please install the specific adapter packages you need:
- pip install hacs-langgraph
- pip install hacs-crewai
- pip install hacs-autogen (coming soon)
"""

from .a2a_adapter import A2AAdapter, create_a2a_envelope, extract_from_a2a_envelope
from .ag_ui_adapter import AGUIAdapter, format_for_ag_ui, parse_ag_ui_event
from .mcp_adapter import MCPAdapter, convert_from_mcp_result, convert_to_mcp_task

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
    # AG-UI Adapter (will be moved to hacs-autogen)
    "AGUIAdapter",
    "format_for_ag_ui",
    "parse_ag_ui_event",
]
