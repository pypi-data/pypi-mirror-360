"""
HACS Models - Healthcare Agent Communication Standard Clinical Models.

This package provides clinical models with FHIR compliance and agent-centric features.
"""

from .agent_message import AgentMessage, MessagePriority, MessageRole, MessageType
from .encounter import (
    Encounter,
    EncounterClass,
    EncounterStatus,
    LocationStatus,
    ParticipantType,
)
from .observation import (
    DataAbsentReason,
    Observation,
    ObservationCategory,
    ObservationStatus,
)
from .patient import (
    AdministrativeGender,
    ContactPointSystem,
    ContactPointUse,
    IdentifierType,
    IdentifierUse,
    Patient,
)

__version__ = "0.1.0"

__all__ = [
    # Patient model and enums
    "Patient",
    "AdministrativeGender",
    "IdentifierUse",
    "IdentifierType",
    "ContactPointSystem",
    "ContactPointUse",
    # AgentMessage model and enums
    "AgentMessage",
    "MessageRole",
    "MessageType",
    "MessagePriority",
    # Encounter model and enums
    "Encounter",
    "EncounterStatus",
    "EncounterClass",
    "ParticipantType",
    "LocationStatus",
    # Observation model and enums
    "Observation",
    "ObservationStatus",
    "ObservationCategory",
    "DataAbsentReason",
]


def hello() -> str:
    return "Hello from hacs-models!"
