"""
HACS Core - Base models and core functionality.

This package provides the foundational classes and utilities for the
Healthcare Agent Communication Standard (HACS).
"""

from .actor import Actor, ActorRole, PermissionLevel, SessionStatus
from .base_resource import BaseResource
from .evidence import Evidence, EvidenceType
from .memory import MemoryBlock

__version__ = "0.1.0"

__all__ = [
    "BaseResource",
    "MemoryBlock",
    "Evidence",
    "EvidenceType",
    "Actor",
    "ActorRole",
    "PermissionLevel",
    "SessionStatus",
]
