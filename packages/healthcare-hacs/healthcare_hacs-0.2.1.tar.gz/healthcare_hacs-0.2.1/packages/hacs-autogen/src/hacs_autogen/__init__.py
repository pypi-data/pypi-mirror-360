"""
HACS AutoGen UI Integration

This package provides AutoGen UI integration for HACS (Healthcare Agent
Communication Standard). It enables seamless integration between HACS clinical
data models and AutoGen UI components.
"""

from .adapter import (
    AGUIAdapter,
    AGUIComponent,
    AGUIEvent,
    AGUIEventType,
    format_for_ag_ui,
    parse_ag_ui_event,
)

__version__ = "0.2.0"
__all__ = [
    "AGUIAdapter",
    "AGUIEventType",
    "AGUIComponent",
    "AGUIEvent",
    "format_for_ag_ui",
    "parse_ag_ui_event",
]
