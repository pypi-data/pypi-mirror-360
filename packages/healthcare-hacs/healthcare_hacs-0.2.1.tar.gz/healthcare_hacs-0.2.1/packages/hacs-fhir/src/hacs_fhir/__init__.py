"""
HACS FHIR Integration Package

This package provides comprehensive bidirectional mapping between HACS models
and FHIR resources, including Evidence → Citation mapping, validation, and
support for FHIR R5 with R6 preparation.
"""

__version__ = "0.1.0"

import logging
from datetime import datetime
from typing import Any, Dict, List, Union

try:
    from fhir.resources.citation import Citation as FHIRCitation
    from fhir.resources.communicationrequest import (
        CommunicationRequest as FHIRCommunicationRequest,
    )
    from fhir.resources.encounter import Encounter as FHIREncounter
    from fhir.resources.observation import Observation as FHIRObservation
    from fhir.resources.patient import Patient as FHIRPatient
    from fhir.resources.resource import Resource as FHIRResource

    FHIR_AVAILABLE = True
except ImportError as e:
    FHIR_AVAILABLE = False
    # Define placeholders for type hints
    FHIRResource = None
    FHIRPatient = None
    FHIREncounter = None
    FHIRObservation = None
    FHIRCitation = None
    FHIRCommunicationRequest = None
    logging.warning(
        f"fhir.resources not available: {e}. FHIR mapping will be disabled."
    )

from hacs_core import Actor, BaseResource, Evidence
from hacs_models import AgentMessage, Encounter, Observation, Patient


class FHIRMappingError(Exception):
    """Exception raised for FHIR mapping errors."""

    pass


class FHIRValidationError(Exception):
    """Exception raised for FHIR validation errors."""

    pass


def to_fhir(resource: BaseResource) -> dict[str, Any]:
    """
    Convert a HACS resource to FHIR format using dynamic dispatch.

    Args:
        resource: HACS resource to convert

    Returns:
        FHIR resource as dictionary

    Raises:
        FHIRMappingError: If resource type is not supported or mapping fails
    """
    if not FHIR_AVAILABLE:
        raise FHIRMappingError("fhir.resources package not available")

    resource_type = getattr(resource, "resource_type", None)
    if not resource_type:
        resource_type = resource.__class__.__name__

    # Dynamic dispatch based on resource type
    mapping_functions = {
        "Patient": _patient_to_fhir,
        "AgentMessage": _agent_message_to_fhir,
        "Encounter": _encounter_to_fhir,
        "Observation": _observation_to_fhir,
        "Evidence": _evidence_to_citation,  # Evidence → Citation mapping
        "Actor": _actor_to_practitioner,
    }

    mapping_func = mapping_functions.get(resource_type)
    if not mapping_func:
        raise FHIRMappingError(
            f"No FHIR mapping available for resource type: {resource_type}"
        )

    try:
        return mapping_func(resource)
    except Exception as e:
        raise FHIRMappingError(
            f"Failed to map {resource_type} to FHIR: {str(e)}"
        ) from e


def from_fhir(fhir_resource: dict[str, Any] | Any) -> BaseResource:
    """
    Convert a FHIR resource to HACS format with validation and type detection.

    Args:
        fhir_resource: FHIR resource as dictionary or FHIRResource object

    Returns:
        HACS resource

    Raises:
        FHIRMappingError: If resource type is not supported or mapping fails
    """
    if not FHIR_AVAILABLE:
        raise FHIRMappingError("fhir.resources package not available")

    # Convert FHIRResource to dict if needed
    if hasattr(fhir_resource, "dict"):
        # This is a FHIR resource object
        fhir_dict = fhir_resource.dict()  # type: ignore
    elif isinstance(fhir_resource, dict):
        fhir_dict = fhir_resource
    else:
        raise FHIRMappingError("Invalid FHIR resource format")

    if not isinstance(fhir_dict, dict):
        raise FHIRMappingError("Could not convert FHIR resource to dictionary")

    resource_type = fhir_dict.get("resourceType")
    if not resource_type:
        raise FHIRMappingError("FHIR resource missing resourceType")

    # Dynamic dispatch based on FHIR resource type
    mapping_functions = {
        "Patient": _fhir_to_patient,
        "CommunicationRequest": _fhir_to_agent_message,
        "Encounter": _fhir_to_encounter,
        "Observation": _fhir_to_observation,
        "Citation": _citation_to_evidence,  # Citation → Evidence mapping
        "Practitioner": _practitioner_to_actor,
    }

    mapping_func = mapping_functions.get(resource_type)
    if not mapping_func:
        raise FHIRMappingError(
            f"No HACS mapping available for FHIR resource type: {resource_type}"
        )

    try:
        return mapping_func(fhir_dict)
    except Exception as e:
        raise FHIRMappingError(
            f"Failed to map FHIR {resource_type} to HACS: {str(e)}"
        ) from e


def validate_fhir_compliance(resource: BaseResource) -> list[str]:
    """
    Validate FHIR compliance of a HACS resource with detailed error messages.

    Args:
        resource: HACS resource to validate

    Returns:
        List of validation error messages (empty if valid)
    """
    if not FHIR_AVAILABLE:
        return ["fhir.resources package not available for validation"]

    errors = []

    try:
        # Convert to FHIR and validate
        fhir_dict = to_fhir(resource)

        # Validate using fhir.resources
        resource_type = fhir_dict.get("resourceType")
        if resource_type == "Patient" and FHIRPatient is not None:
            FHIRPatient(**fhir_dict)
        elif resource_type == "Encounter" and FHIREncounter is not None:
            FHIREncounter(**fhir_dict)
        elif resource_type == "Observation" and FHIRObservation is not None:
            FHIRObservation(**fhir_dict)
        elif resource_type == "Citation" and FHIRCitation is not None:
            FHIRCitation(**fhir_dict)
        elif (
            resource_type == "CommunicationRequest"
            and FHIRCommunicationRequest is not None
        ):
            FHIRCommunicationRequest(**fhir_dict)
        else:
            errors.append(
                f"Validation not implemented for resource type: {resource_type}"
            )

    except Exception as e:
        errors.append(f"FHIR validation failed: {str(e)}")

    return errors


def _patient_to_fhir(patient: Patient) -> dict[str, Any]:
    """Convert HACS Patient to FHIR Patient."""
    fhir_patient = {
        "resourceType": "Patient",
        "id": patient.id,
        "meta": {
            "lastUpdated": patient.updated_at.isoformat()
            if patient.updated_at
            else None
        },
    }

    # Name
    if patient.given or patient.family:
        name = {
            "use": "official",
            "family": patient.family,
            "given": patient.given or [],
        }
        fhir_patient["name"] = [name]

    # Gender
    if patient.gender:
        fhir_patient["gender"] = (
            patient.gender.value if hasattr(patient.gender, "value") else patient.gender
        )

    # Birth date
    if patient.birth_date:
        fhir_patient["birthDate"] = patient.birth_date.isoformat()

    # Identifiers
    if patient.identifiers:
        fhir_patient["identifier"] = patient.identifiers

    # Telecom
    if patient.telecom:
        fhir_patient["telecom"] = patient.telecom

    # Address
    if patient.address:
        fhir_patient["address"] = patient.address

    # Marital status
    if patient.marital_status:
        marital_code = str(patient.marital_status)
        fhir_patient["maritalStatus"] = {
            "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus",
                    "code": marital_code,
                }
            ]
        }

    # Active status
    fhir_patient["active"] = patient.active

    return fhir_patient


def _fhir_to_patient(fhir_dict: dict[str, Any]) -> Patient:
    """Convert FHIR Patient to HACS Patient."""
    from datetime import date

    # Extract basic fields
    patient_data = {"id": fhir_dict["id"], "active": fhir_dict.get("active", True)}

    # Name
    if "name" in fhir_dict and fhir_dict["name"]:
        name = fhir_dict["name"][0]  # Use first name
        patient_data["family"] = name.get("family", "")
        patient_data["given"] = name.get("given", [])

    # Gender
    if "gender" in fhir_dict:
        from hacs_models import AdministrativeGender

        try:
            patient_data["gender"] = AdministrativeGender(fhir_dict["gender"])
        except ValueError:
            patient_data["gender"] = AdministrativeGender.UNKNOWN

    # Birth date
    if "birthDate" in fhir_dict:
        birth_date_str = fhir_dict["birthDate"]
        patient_data["birth_date"] = date.fromisoformat(birth_date_str)

    # Identifiers
    if "identifier" in fhir_dict:
        patient_data["identifiers"] = fhir_dict["identifier"]

    # Telecom
    if "telecom" in fhir_dict:
        patient_data["telecom"] = fhir_dict["telecom"]

    # Address
    if "address" in fhir_dict:
        patient_data["address"] = fhir_dict["address"]

    return Patient(**patient_data)


def _agent_message_to_fhir(message: AgentMessage) -> dict[str, Any]:
    """Convert HACS AgentMessage to FHIR CommunicationRequest."""
    fhir_comm = {
        "resourceType": "CommunicationRequest",
        "id": message.id,
        "status": "active",  # Map message status to FHIR status
        "intent": "order",
        "meta": {
            "lastUpdated": message.updated_at.isoformat()
            if message.updated_at
            else None
        },
    }

    # Content/payload
    if message.content:
        fhir_comm["payload"] = [{"contentString": message.content}]

    # Subject (patient reference)
    if hasattr(message, "patient_id") and message.patient_id:
        fhir_comm["subject"] = {"reference": f"Patient/{message.patient_id}"}

    # Priority mapping
    if message.priority:
        priority_map = {
            "low": "routine",
            "normal": "routine",
            "high": "urgent",
            "critical": "stat",
        }
        priority_value = (
            message.priority.value
            if hasattr(message.priority, "value")
            else message.priority
        )
        fhir_comm["priority"] = priority_map.get(priority_value, "routine")

    # Add extensions for HACS-specific fields
    extensions = []

    if message.confidence_score is not None:
        extensions.append(
            {
                "url": "http://hacs.dev/fhir/StructureDefinition/confidence-score",
                "valueDecimal": message.confidence_score,
            }
        )

    if message.memory_handles:
        extensions.append(
            {
                "url": "http://hacs.dev/fhir/StructureDefinition/memory-handles",
                "valueString": ",".join(message.memory_handles),
            }
        )

    if extensions:
        fhir_comm["extension"] = extensions

    return fhir_comm


def _fhir_to_agent_message(fhir_dict: dict[str, Any]) -> AgentMessage:
    """Convert FHIR CommunicationRequest to HACS AgentMessage."""
    from hacs_models import MessagePriority, MessageRole

    message_data = {
        "id": fhir_dict["id"],
        "role": MessageRole.ASSISTANT,  # Default role
        "content": "",
    }

    # Extract content from payload
    if "payload" in fhir_dict and fhir_dict["payload"]:
        payload = fhir_dict["payload"][0]
        if "contentString" in payload:
            message_data["content"] = payload["contentString"]

    # Map priority
    if "priority" in fhir_dict:
        priority_map = {
            "routine": MessagePriority.NORMAL,
            "urgent": MessagePriority.HIGH,
            "stat": MessagePriority.CRITICAL,
        }
        message_data["priority"] = priority_map.get(
            fhir_dict["priority"], MessagePriority.NORMAL
        )

    # Extract HACS-specific extensions
    if "extension" in fhir_dict:
        for ext in fhir_dict["extension"]:
            url = ext.get("url", "")
            if "confidence-score" in url and "valueDecimal" in ext:
                message_data["confidence_score"] = ext["valueDecimal"]
            elif "memory-handles" in url and "valueString" in ext:
                message_data["memory_handles"] = ext["valueString"].split(",")

    return AgentMessage(**message_data)


def _encounter_to_fhir(encounter: Encounter) -> dict[str, Any]:
    """Convert HACS Encounter to FHIR Encounter."""
    fhir_encounter = {
        "resourceType": "Encounter",
        "id": encounter.id,
        "status": encounter.status.value
        if hasattr(encounter.status, "value")
        else encounter.status,
        "class": {
            "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
            "code": encounter.class_fhir.value
            if hasattr(encounter.class_fhir, "value")
            else encounter.class_fhir,
        },
        "meta": {
            "lastUpdated": encounter.updated_at.isoformat()
            if encounter.updated_at
            else None
        },
    }

    # Subject
    if encounter.subject:
        fhir_encounter["subject"] = {"reference": f"Patient/{encounter.subject}"}

    # Period
    if encounter.period:
        fhir_encounter["period"] = encounter.period

    # Participants
    if encounter.participants:
        fhir_encounter["participant"] = encounter.participants

    # Diagnosis
    if encounter.diagnosis:
        fhir_encounter["diagnosis"] = encounter.diagnosis

    # Location
    if encounter.location:
        fhir_encounter["location"] = encounter.location

    # Service provider
    if encounter.service_provider:
        fhir_encounter["serviceProvider"] = {
            "reference": f"Organization/{encounter.service_provider}"
        }

    return fhir_encounter


def _fhir_to_encounter(fhir_dict: dict[str, Any]) -> Encounter:
    """Convert FHIR Encounter to HACS Encounter."""
    from hacs_models import EncounterClass, EncounterStatus

    encounter_data = {
        "id": fhir_dict["id"],
        "status": EncounterStatus(fhir_dict["status"]),
    }

    # Map FHIR class back to EncounterClass
    if "class" in fhir_dict:
        fhir_class_code = fhir_dict["class"].get("code", "AMB")
        try:
            encounter_data["class"] = EncounterClass(fhir_class_code)
        except ValueError:
            encounter_data["class"] = EncounterClass.AMB  # Default fallback

    # Subject
    if "subject" in fhir_dict and "reference" in fhir_dict["subject"]:
        ref = fhir_dict["subject"]["reference"]
        if ref.startswith("Patient/"):
            encounter_data["subject"] = ref.replace("Patient/", "")

    # Period
    if "period" in fhir_dict:
        encounter_data["period"] = fhir_dict["period"]

    # Participants
    if "participant" in fhir_dict:
        encounter_data["participants"] = fhir_dict["participant"]

    # Diagnosis
    if "diagnosis" in fhir_dict:
        encounter_data["diagnosis"] = fhir_dict["diagnosis"]

    # Location
    if "location" in fhir_dict:
        encounter_data["location"] = fhir_dict["location"]

    return Encounter(**encounter_data)


def _observation_to_fhir(observation: Observation) -> dict[str, Any]:
    """Convert HACS Observation to FHIR Observation."""
    fhir_obs = {
        "resourceType": "Observation",
        "id": observation.id,
        "status": observation.status.value
        if hasattr(observation.status, "value")
        else observation.status,
        "code": observation.code,
        "subject": {"reference": f"Patient/{observation.subject}"},
        "meta": {
            "lastUpdated": observation.updated_at.isoformat()
            if observation.updated_at
            else None
        },
    }

    # Category
    if observation.category:
        fhir_obs["category"] = observation.category

    # Encounter
    if observation.encounter:
        fhir_obs["encounter"] = {"reference": f"Encounter/{observation.encounter}"}

    # Effective time
    if observation.effective_datetime:
        fhir_obs["effectiveDateTime"] = observation.effective_datetime.isoformat()
    elif observation.effective_period:
        fhir_obs["effectivePeriod"] = observation.effective_period

    # Issued
    if observation.issued:
        fhir_obs["issued"] = observation.issued.isoformat()

    # Value
    if observation.value_quantity:
        fhir_obs["valueQuantity"] = observation.value_quantity
    elif observation.value_codeable_concept:
        fhir_obs["valueCodeableConcept"] = observation.value_codeable_concept
    elif observation.value_string:
        fhir_obs["valueString"] = observation.value_string
    elif observation.value_boolean is not None:
        fhir_obs["valueBoolean"] = observation.value_boolean
    elif observation.value_integer is not None:
        fhir_obs["valueInteger"] = observation.value_integer
    elif observation.value_range:
        fhir_obs["valueRange"] = observation.value_range
    elif observation.data_absent_reason:
        fhir_obs["dataAbsentReason"] = {
            "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/data-absent-reason",
                    "code": observation.data_absent_reason.value
                    if hasattr(observation.data_absent_reason, "value")
                    else observation.data_absent_reason,
                }
            ]
        }

    # Interpretation
    if observation.interpretation:
        fhir_obs["interpretation"] = observation.interpretation

    # Note
    if observation.note:
        fhir_obs["note"] = observation.note

    # Body site
    if observation.body_site:
        fhir_obs["bodySite"] = observation.body_site

    # Method
    if observation.method:
        fhir_obs["method"] = observation.method

    # Specimen
    if observation.specimen:
        fhir_obs["specimen"] = {"reference": f"Specimen/{observation.specimen}"}

    # Device
    if observation.device:
        fhir_obs["device"] = {"reference": f"Device/{observation.device}"}

    # Reference range
    if observation.reference_range:
        fhir_obs["referenceRange"] = observation.reference_range

    # Has member
    if observation.has_member:
        fhir_obs["hasMember"] = [
            {"reference": f"Observation/{obs_id}"} for obs_id in observation.has_member
        ]

    # Derived from
    if observation.derived_from:
        fhir_obs["derivedFrom"] = [
            {"reference": f"Observation/{obs_id}"}
            for obs_id in observation.derived_from
        ]

    # Component
    if observation.component:
        fhir_obs["component"] = observation.component

    # Performer
    if observation.performer:
        fhir_obs["performer"] = [
            {"reference": f"Practitioner/{perf_id}"}
            for perf_id in observation.performer
        ]

    return fhir_obs


def _fhir_to_observation(fhir_dict: dict[str, Any]) -> Observation:
    """Convert FHIR Observation to HACS Observation."""
    from hacs_models import DataAbsentReason, ObservationStatus

    obs_data = {
        "id": fhir_dict["id"],
        "status": ObservationStatus(fhir_dict["status"]),
        "code": fhir_dict["code"],
        "subject": fhir_dict["subject"]["reference"].replace("Patient/", ""),
    }

    # Category
    if "category" in fhir_dict:
        obs_data["category"] = fhir_dict["category"]

    # Encounter
    if "encounter" in fhir_dict:
        obs_data["encounter"] = fhir_dict["encounter"]["reference"].replace(
            "Encounter/", ""
        )

    # Effective time
    if "effectiveDateTime" in fhir_dict:
        obs_data["effective_datetime"] = datetime.fromisoformat(
            fhir_dict["effectiveDateTime"].replace("Z", "+00:00")
        )
    elif "effectivePeriod" in fhir_dict:
        obs_data["effective_period"] = fhir_dict["effectivePeriod"]

    # Issued
    if "issued" in fhir_dict:
        obs_data["issued"] = datetime.fromisoformat(
            fhir_dict["issued"].replace("Z", "+00:00")
        )

    # Value
    if "valueQuantity" in fhir_dict:
        obs_data["value_quantity"] = fhir_dict["valueQuantity"]
    elif "valueCodeableConcept" in fhir_dict:
        obs_data["value_codeable_concept"] = fhir_dict["valueCodeableConcept"]
    elif "valueString" in fhir_dict:
        obs_data["value_string"] = fhir_dict["valueString"]
    elif "valueBoolean" in fhir_dict:
        obs_data["value_boolean"] = fhir_dict["valueBoolean"]
    elif "valueInteger" in fhir_dict:
        obs_data["value_integer"] = fhir_dict["valueInteger"]
    elif "valueRange" in fhir_dict:
        obs_data["value_range"] = fhir_dict["valueRange"]
    elif "dataAbsentReason" in fhir_dict:
        reason_code = fhir_dict["dataAbsentReason"]["coding"][0]["code"]
        obs_data["data_absent_reason"] = DataAbsentReason(reason_code)

    # Other fields
    for field in [
        "interpretation",
        "note",
        "bodySite",
        "method",
        "referenceRange",
        "component",
    ]:
        fhir_field = field
        if field == "bodySite":
            fhir_field = "bodySite"
            hacs_field = "body_site"
        elif field == "referenceRange":
            fhir_field = "referenceRange"
            hacs_field = "reference_range"
        else:
            hacs_field = field

        if fhir_field in fhir_dict:
            obs_data[hacs_field] = fhir_dict[fhir_field]

    return Observation(**obs_data)


def _evidence_to_citation(evidence: Evidence) -> dict[str, Any]:
    """Convert HACS Evidence to FHIR Citation."""
    fhir_citation = {
        "resourceType": "Citation",
        "id": evidence.id,
        "status": "active",
        "meta": {
            "lastUpdated": evidence.updated_at.isoformat()
            if evidence.updated_at
            else None
        },
    }

    # Citation detail
    citation_detail: dict[str, Any] = {
        "type": {
            "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/citation-artifact-classifier",
                    "code": (
                        evidence.evidence_type.value
                        if hasattr(evidence.evidence_type, "value")
                        else evidence.evidence_type
                    ).replace("_", "-"),
                }
            ]
        }
    }

    if evidence.citation:
        citation_detail["title"] = evidence.citation

    fhir_citation["citedArtifact"] = citation_detail

    # Summary
    if evidence.content:
        fhir_citation["summary"] = [
            {
                "type": {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/citation-summary-style",
                            "code": "narrative",
                        }
                    ]
                },
                "text": evidence.content,
            }
        ]

    # Add extensions for HACS-specific fields
    extensions = []

    if evidence.confidence_score is not None:
        extensions.append(
            {
                "url": "http://hacs.dev/fhir/StructureDefinition/confidence-score",
                "valueDecimal": evidence.confidence_score,
            }
        )

    if evidence.quality_score is not None:
        extensions.append(
            {
                "url": "http://hacs.dev/fhir/StructureDefinition/quality-score",
                "valueDecimal": evidence.quality_score,
            }
        )

    if evidence.vector_id:
        extensions.append(
            {
                "url": "http://hacs.dev/fhir/StructureDefinition/vector-id",
                "valueString": evidence.vector_id,
            }
        )

    if extensions:
        fhir_citation["extension"] = extensions

    return fhir_citation


def _citation_to_evidence(fhir_dict: dict[str, Any]) -> Evidence:
    """Convert FHIR Citation to HACS Evidence."""
    from hacs_core import EvidenceType

    evidence_data = {
        "id": fhir_dict["id"],
        "evidence_type": EvidenceType.RESEARCH_PAPER,  # Default
        "citation": "",
        "content": "",
    }

    # Extract citation details
    if "citedArtifact" in fhir_dict:
        artifact = fhir_dict["citedArtifact"]

        if "title" in artifact:
            evidence_data["citation"] = artifact["title"]

        if "type" in artifact and "coding" in artifact["type"]:
            type_code = artifact["type"]["coding"][0]["code"].replace("-", "_")
            try:
                evidence_data["evidence_type"] = EvidenceType(type_code)
            except ValueError:
                pass  # Keep default

    # Extract summary
    if "summary" in fhir_dict and fhir_dict["summary"]:
        summary = fhir_dict["summary"][0]
        if "text" in summary:
            evidence_data["content"] = summary["text"]

    # Extract HACS-specific extensions
    if "extension" in fhir_dict:
        for ext in fhir_dict["extension"]:
            url = ext.get("url", "")
            if "confidence-score" in url and "valueDecimal" in ext:
                evidence_data["confidence_score"] = ext["valueDecimal"]
            elif "quality-score" in url and "valueDecimal" in ext:
                evidence_data["quality_score"] = ext["valueDecimal"]
            elif "vector-id" in url and "valueString" in ext:
                evidence_data["vector_id"] = ext["valueString"]

    return Evidence(**evidence_data)


def _actor_to_practitioner(actor: Actor) -> dict[str, Any]:
    """Convert HACS Actor to FHIR Practitioner."""
    fhir_practitioner = {
        "resourceType": "Practitioner",
        "id": actor.id,
        "active": actor.is_active,
        "meta": {
            "lastUpdated": actor.updated_at.isoformat() if actor.updated_at else None
        },
    }

    # Name
    if actor.name:
        fhir_practitioner["name"] = [{"use": "official", "text": actor.name}]

    # Qualification (role)
    if actor.role:
        fhir_practitioner["qualification"] = [
            {
                "code": {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/v2-0360",
                            "code": actor.role.value
                            if hasattr(actor.role, "value")
                            else actor.role,
                        }
                    ]
                }
            }
        ]

    return fhir_practitioner


def _practitioner_to_actor(fhir_dict: dict[str, Any]) -> Actor:
    """Convert FHIR Practitioner to HACS Actor."""
    from hacs_core import ActorRole

    actor_data = {
        "id": fhir_dict["id"],
        "name": "",
        "role": ActorRole.SYSTEM,  # Default
        "is_active": fhir_dict.get("active", True),
    }

    # Name
    if "name" in fhir_dict and fhir_dict["name"]:
        name = fhir_dict["name"][0]
        if "text" in name:
            actor_data["name"] = name["text"]
        elif "family" in name or "given" in name:
            parts = []
            if "given" in name:
                parts.extend(name["given"])
            if "family" in name:
                parts.append(name["family"])
            actor_data["name"] = " ".join(parts)

    # Role from qualification
    if "qualification" in fhir_dict and fhir_dict["qualification"]:
        qual = fhir_dict["qualification"][0]
        if "code" in qual and "coding" in qual["code"]:
            role_code = qual["code"]["coding"][0]["code"]
            try:
                actor_data["role"] = ActorRole(role_code)
            except ValueError:
                pass  # Keep default

    return Actor(**actor_data)


__all__ = [
    "to_fhir",
    "from_fhir",
    "validate_fhir_compliance",
    "FHIRMappingError",
    "FHIRValidationError",
]
