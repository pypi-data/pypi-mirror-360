"""
HACS + LangGraph Demo Package

This package contains a clean demonstration of integrating HACS with LangGraph
using the Functional API for simple, readable clinical workflows.
"""

from .graph import run_example, create_workflow_graph, create_example_data
from .state import ClinicalWorkflowState, create_initial_state

__all__ = [
    "run_example",
    "create_workflow_graph",
    "create_example_data",
    "ClinicalWorkflowState",
    "create_initial_state",
]
