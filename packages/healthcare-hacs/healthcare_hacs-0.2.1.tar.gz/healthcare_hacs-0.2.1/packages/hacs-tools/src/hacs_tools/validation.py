"""
Validation System with Actor Context

This module provides comprehensive validation for HACS resources including
schema validation, business rule validation, cross-reference validation,
and permission validation with Actor context.
"""

import re
from datetime import date, datetime, timezone
from enum import Enum

from hacs_core import Actor, BaseResource
from hacs_fhir import validate_fhir_compliance as fhir_validate_compliance
from hacs_models import AgentMessage, Encounter, Observation, Patient
from pydantic import BaseModel, Field, ValidationError


class ValidationLevel(str, Enum):
    """Validation levels."""

    BASIC = "basic"
    STANDARD = "standard"
    STRICT = "strict"
    FHIR_COMPLIANT = "fhir_compliant"


class ValidationResult(BaseModel):
    """Result of validation."""

    valid: bool
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    level: ValidationLevel
    actor_id: str | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class BusinessRuleValidator:
    """Validates business rules for healthcare resources."""

    @staticmethod
    def validate_patient(patient: Patient) -> list[str]:
        """Validate Patient business rules."""
        errors = []

        # Age validation
        if patient.birth_date:
            today = date.today()

            # Check for future birth date
            if patient.birth_date > today:
                errors.append("Birth date cannot be in the future")
            else:
                age = patient.age_years
                if age and age > 150:
                    errors.append(
                        "Age exceeds reasonable maximum (150 years)"
                    )  # Maybe this will soon be just a warning :)

        # Name validation
        if not patient.given and not patient.family:
            errors.append("Patient must have either given name or family name")

        # Identifier validation
        for identifier in patient.identifiers:
            if not identifier.get("value"):
                errors.append("Identifier must have a value")
            if not identifier.get("system"):
                errors.append("Identifier must have a system")

        # Telecom validation
        for telecom in patient.telecom:
            if telecom.get("system") == "email":
                email = telecom.get("value", "")
                if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
                    errors.append(f"Invalid email format: {email}")
            elif telecom.get("system") == "phone":
                phone = telecom.get("value", "")
                if not re.match(r"^[\+\-\(\)\s\d]+$", phone):
                    errors.append(f"Invalid phone format: {phone}")

        return errors

    @staticmethod
    def validate_observation(observation: Observation) -> list[str]:
        """Validate Observation business rules."""
        errors = []

        # Value validation
        if observation.has_value:
            # Numeric value range checks
            if observation.value_quantity:
                value = observation.get_numeric_value()
                unit = observation.get_unit()

                # Only validate if we have a numeric value
                if value is not None:
                    # Blood pressure validation
                    if observation.is_loinc_code() and observation.primary_code in [
                        "8480-6",
                        "8462-4",
                    ]:  # Systolic/Diastolic BP
                        if unit == "mmHg":
                            if value < 40 or value > 300:
                                errors.append(
                                    f"Blood pressure value {value} mmHg is outside reasonable range (40-300)"
                                )

                    # Temperature validation
                    elif observation.primary_code in [
                        "8310-5",
                        "8331-1",
                    ]:  # Body temperature
                        if unit == "Cel":
                            if value < 25 or value > 45:
                                errors.append(
                                    f"Temperature {value}°C is outside reasonable range (25-45)"
                                )
                        elif unit == "degF":
                            if value < 77 or value > 113:
                                errors.append(
                                    f"Temperature {value}°F is outside reasonable range (77-113)"
                                )

                    # Heart rate validation
                    elif observation.primary_code == "8867-4":  # Heart rate
                        if unit == "/min":
                            if value < 20 or value > 300:
                                errors.append(
                                    f"Heart rate {value} bpm is outside reasonable range (20-300)"
                                )

        # Status validation
        status_value = (
            observation.status.value
            if hasattr(observation.status, "value")
            else observation.status
        )
        if status_value in ["cancelled", "entered-in-error"] and observation.has_value:
            errors.append("Cancelled or erroneous observations should not have values")

        # Component validation
        for component in observation.component:
            if "valueQuantity" in component:
                if "value" not in component["valueQuantity"]:
                    errors.append("Component valueQuantity must have a value")

        return errors

    @staticmethod
    def validate_encounter(encounter: Encounter) -> list[str]:
        """Validate Encounter business rules."""
        errors = []

        # Period validation
        if encounter.period:
            start = encounter.period.get("start")
            end = encounter.period.get("end")

            if start and end:
                try:
                    start_dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
                    end_dt = datetime.fromisoformat(end.replace("Z", "+00:00"))

                    if end_dt <= start_dt:
                        errors.append("Encounter end time must be after start time")

                    # Check for unreasonably long encounters
                    duration_days = (end_dt - start_dt).days
                    if duration_days > 365:
                        errors.append(
                            f"Encounter duration ({duration_days} days) exceeds reasonable maximum"
                        )

                except ValueError:
                    errors.append("Invalid datetime format in encounter period")

        # Status validation
        status_value = (
            encounter.status.value
            if hasattr(encounter.status, "value")
            else encounter.status
        )
        if status_value == "finished" and encounter.period:
            if not encounter.period.get("end"):
                errors.append("Finished encounters must have an end time")

        return errors

    @staticmethod
    def validate_agent_message(message: AgentMessage) -> list[str]:
        """Validate AgentMessage business rules."""
        errors = []

        # Content validation
        if not message.content.strip():
            errors.append("Message content cannot be empty")

        # Confidence score validation
        if message.confidence_score < 0 or message.confidence_score > 1:
            errors.append("Confidence score must be between 0 and 1")

        # Urgency score validation
        if message.urgency_score < 0 or message.urgency_score > 1:
            errors.append("Urgency score must be between 0 and 1")

        # Memory handles validation
        for handle in message.memory_handles:
            if not handle.strip():
                errors.append("Memory handles cannot be empty")

        return errors


class CrossReferenceValidator:
    """Validates cross-references between resources."""

    def __init__(self, storage_manager):
        self.storage = storage_manager

    def validate_patient_references(self, resource: BaseResource) -> list[str]:
        """Validate patient references in a resource."""
        errors = []

        subject = getattr(resource, "subject", None)
        if subject:
            # Check if referenced patient exists
            patient = self.storage.retrieve("Patient", subject)
            if not patient:
                errors.append(f"Referenced patient {subject} not found")

        return errors

    def validate_encounter_references(self, resource: BaseResource) -> list[str]:
        """Validate encounter references in a resource."""
        errors = []

        encounter_id = getattr(resource, "encounter", None)
        if encounter_id:
            # Check if referenced encounter exists
            encounter = self.storage.retrieve("Encounter", encounter_id)
            if not encounter:
                errors.append(f"Referenced encounter {encounter_id} not found")

        return errors

    def validate_evidence_references(self, resource: BaseResource) -> list[str]:
        """Validate evidence references in a resource."""
        errors = []

        evidence_references = getattr(resource, "evidence_references", None)
        if evidence_references:
            for evidence_id in evidence_references:
                evidence = self.storage.retrieve("Evidence", evidence_id)
                if not evidence:
                    errors.append(f"Referenced evidence {evidence_id} not found")

        return errors


class PermissionValidator:
    """Validates Actor permissions for operations."""

    @staticmethod
    def validate_create_permission(actor: Actor, resource: BaseResource) -> list[str]:
        """Validate create permission."""
        errors = []

        if not actor.is_active:
            errors.append("Actor is not active")
            return errors

        required_permission = f"{resource.resource_type.lower()}:create"
        wildcard_permission = f"{resource.resource_type.lower()}:*"
        global_permission = "*:*"

        if not any(
            perm in [required_permission, wildcard_permission, global_permission]
            for perm in actor.permissions
        ):
            errors.append(f"Actor lacks permission to create {resource.resource_type}")

        return errors

    @staticmethod
    def validate_read_permission(actor: Actor, resource_type: str) -> list[str]:
        """Validate read permission."""
        errors = []

        if not actor.is_active:
            errors.append("Actor is not active")
            return errors

        required_permission = f"{resource_type.lower()}:read"
        wildcard_permission = f"{resource_type.lower()}:*"
        global_permission = "*:*"

        if not any(
            perm in [required_permission, wildcard_permission, global_permission]
            for perm in actor.permissions
        ):
            errors.append(f"Actor lacks permission to read {resource_type}")

        return errors


def validate_before_create(
    resource: BaseResource,
    actor: Actor,
    level: ValidationLevel = ValidationLevel.STANDARD,
) -> ValidationResult:
    """
    Validate a resource before creation.

    Args:
        resource: Resource to validate
        actor: Actor performing the operation
        level: Validation level

    Returns:
        ValidationResult
    """
    result = ValidationResult(valid=True, level=level, actor_id=actor.id)

    try:
        # Schema validation (Pydantic already handles this)
        pass
    except ValidationError as e:
        result.errors.extend([str(err) for err in e.errors()])
        result.valid = False

    # Permission validation
    permission_errors = PermissionValidator.validate_create_permission(actor, resource)
    result.errors.extend(permission_errors)

    # Business rule validation
    if isinstance(resource, Patient):
        business_errors = BusinessRuleValidator.validate_patient(resource)
    elif isinstance(resource, Observation):
        business_errors = BusinessRuleValidator.validate_observation(resource)
    elif isinstance(resource, Encounter):
        business_errors = BusinessRuleValidator.validate_encounter(resource)
    elif isinstance(resource, AgentMessage):
        business_errors = BusinessRuleValidator.validate_agent_message(resource)
    else:
        business_errors = []

    result.errors.extend(business_errors)

    # FHIR compliance validation
    if level == ValidationLevel.FHIR_COMPLIANT:
        try:
            fhir_errors = fhir_validate_compliance(resource)
            result.errors.extend(fhir_errors)
        except Exception as e:
            result.warnings.append(f"FHIR validation failed: {str(e)}")

    # Set final validation status
    if result.errors:
        result.valid = False

    return result


def validate_before_update(
    resource: BaseResource,
    actor: Actor,
    level: ValidationLevel = ValidationLevel.STANDARD,
) -> ValidationResult:
    """
    Validate a resource before update.

    Args:
        resource: Resource to validate
        actor: Actor performing the operation
        level: Validation level

    Returns:
        ValidationResult
    """
    result = ValidationResult(valid=True, level=level, actor_id=actor.id)

    # Similar validation to create, but with update-specific checks
    create_result = validate_before_create(resource, actor, level)
    result.errors.extend(create_result.errors)
    result.warnings.extend(create_result.warnings)

    # Additional update-specific validations
    if not resource.id:
        result.errors.append("Resource must have an ID for update")

    # Check if resource has been modified (basic version)
    if hasattr(resource, "updated_at"):
        # This would be enhanced with proper conflict detection
        pass

    if result.errors:
        result.valid = False

    return result


def validate_fhir_compliance(resource: BaseResource) -> ValidationResult:
    """
    Validate FHIR compliance of a resource.

    Args:
        resource: Resource to validate

    Returns:
        ValidationResult
    """
    result = ValidationResult(valid=True, level=ValidationLevel.FHIR_COMPLIANT)

    try:
        fhir_errors = fhir_validate_compliance(resource)
        result.errors.extend(fhir_errors)
    except Exception as e:
        result.errors.append(f"FHIR validation failed: {str(e)}")

    if result.errors:
        result.valid = False

    return result


def validate_resource_comprehensive(
    resource: BaseResource, actor: Actor, storage_manager=None
) -> ValidationResult:
    """
    Perform comprehensive validation including cross-references.

    Args:
        resource: Resource to validate
        actor: Actor performing the operation
        storage_manager: Storage manager for cross-reference validation

    Returns:
        ValidationResult
    """
    result = ValidationResult(
        valid=True, level=ValidationLevel.STRICT, actor_id=actor.id
    )

    # Basic validation
    basic_result = validate_before_create(resource, actor, ValidationLevel.STRICT)
    result.errors.extend(basic_result.errors)
    result.warnings.extend(basic_result.warnings)

    # Cross-reference validation
    if storage_manager:
        cross_ref_validator = CrossReferenceValidator(storage_manager)

        # Validate patient references
        patient_errors = cross_ref_validator.validate_patient_references(resource)
        result.errors.extend(patient_errors)

        # Validate encounter references
        encounter_errors = cross_ref_validator.validate_encounter_references(resource)
        result.errors.extend(encounter_errors)

        # Validate evidence references
        evidence_errors = cross_ref_validator.validate_evidence_references(resource)
        result.errors.extend(evidence_errors)

    # FHIR compliance
    fhir_result = validate_fhir_compliance(resource)
    result.errors.extend(fhir_result.errors)
    result.warnings.extend(fhir_result.warnings)

    if result.errors:
        result.valid = False

    return result


# Convenience functions for specific resource types
def validate_patient(
    patient: Patient, actor: Actor, level: ValidationLevel = ValidationLevel.STANDARD
) -> ValidationResult:
    """Validate a Patient resource."""
    return validate_before_create(patient, actor, level)


def validate_observation(
    observation: Observation,
    actor: Actor,
    level: ValidationLevel = ValidationLevel.STANDARD,
) -> ValidationResult:
    """Validate an Observation resource."""
    return validate_before_create(observation, actor, level)


def validate_encounter(
    encounter: Encounter,
    actor: Actor,
    level: ValidationLevel = ValidationLevel.STANDARD,
) -> ValidationResult:
    """Validate an Encounter resource."""
    return validate_before_create(encounter, actor, level)


def validate_agent_message(
    message: AgentMessage,
    actor: Actor,
    level: ValidationLevel = ValidationLevel.STANDARD,
) -> ValidationResult:
    """Validate an AgentMessage resource."""
    return validate_before_create(message, actor, level)
