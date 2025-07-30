"""
Observation model for healthcare measurements and findings.

This module provides the Observation model with FHIR-compliant fields,
code validation for LOINC/SNOMED CT, UCUM units, and agent-centric features.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import Field, field_validator, computed_field, model_validator

from hacs_core import BaseResource


class ObservationStatus(str, Enum):
    """FHIR-compliant observation status codes."""

    REGISTERED = "registered"
    PRELIMINARY = "preliminary"
    FINAL = "final"
    AMENDED = "amended"
    CORRECTED = "corrected"
    CANCELLED = "cancelled"
    ENTERED_IN_ERROR = "entered-in-error"
    UNKNOWN = "unknown"


class ObservationCategory(str, Enum):
    """Common observation categories."""

    VITAL_SIGNS = "vital-signs"
    LABORATORY = "laboratory"
    IMAGING = "imaging"
    PROCEDURE = "procedure"
    SURVEY = "survey"
    EXAM = "exam"
    THERAPY = "therapy"
    ACTIVITY = "activity"


class DataAbsentReason(str, Enum):
    """Reasons why data might be absent."""

    UNKNOWN = "unknown"
    ASKED_UNKNOWN = "asked-unknown"
    TEMP_UNKNOWN = "temp-unknown"
    NOT_ASKED = "not-asked"
    ASKED_DECLINED = "asked-declined"
    MASKED = "masked"
    NOT_APPLICABLE = "not-applicable"
    UNSUPPORTED = "unsupported"
    AS_TEXT = "as-text"
    ERROR = "error"
    NOT_A_NUMBER = "not-a-number"
    NEGATIVE_INFINITY = "negative-infinity"
    POSITIVE_INFINITY = "positive-infinity"
    NOT_PERFORMED = "not-performed"
    NOT_PERMITTED = "not-permitted"


class Observation(BaseResource):
    """
    Represents a healthcare observation or measurement.

    This model includes comprehensive observation data with FHIR compliance,
    code validation, unit validation, and agent-centric features.
    """

    resource_type: Literal["Observation"] = Field(
        default="Observation", description="Resource type identifier"
    )

    # Core observation fields
    status: ObservationStatus = Field(description="Status of the observation")

    category: List[Dict[str, Any]] = Field(
        default_factory=list, description="Classification of type of observation"
    )

    code: Dict[str, Any] = Field(
        description="Type of observation (LOINC, SNOMED CT, etc.)"
    )

    subject: str = Field(description="Who/what the observation is about")

    encounter: Optional[str] = Field(
        default=None,
        description="Healthcare encounter during which observation was made",
    )

    # Timing
    effective_datetime: Optional[datetime] = Field(
        default=None, description="Clinically relevant time/time-period for observation"
    )

    effective_period: Optional[Dict[str, Any]] = Field(
        default=None, description="Time period during which observation was made"
    )

    issued: Optional[datetime] = Field(
        default=None, description="Date/time the observation was made available"
    )

    # Value and results
    value_quantity: Optional[Dict[str, Any]] = Field(
        default=None, description="Actual result (Quantity)"
    )

    value_codeable_concept: Optional[Dict[str, Any]] = Field(
        default=None, description="Actual result (CodeableConcept)"
    )

    value_string: Optional[str] = Field(
        default=None, description="Actual result (string)"
    )

    value_boolean: Optional[bool] = Field(
        default=None, description="Actual result (boolean)"
    )

    value_integer: Optional[int] = Field(
        default=None, description="Actual result (integer)"
    )

    value_range: Optional[Dict[str, Any]] = Field(
        default=None, description="Actual result (Range)"
    )

    data_absent_reason: Optional[DataAbsentReason] = Field(
        default=None, description="Why the result is missing"
    )

    # Interpretation and reference ranges
    interpretation: List[Dict[str, Any]] = Field(
        default_factory=list, description="High, low, normal, etc."
    )

    note: List[Dict[str, Any]] = Field(
        default_factory=list, description="Comments about the observation"
    )

    body_site: Optional[Dict[str, Any]] = Field(
        default=None, description="Observed body part"
    )

    method: Optional[Dict[str, Any]] = Field(
        default=None, description="How the observation was performed"
    )

    specimen: Optional[str] = Field(
        default=None, description="Specimen used for this observation"
    )

    device: Optional[str] = Field(
        default=None, description="Device used for this observation"
    )

    reference_range: List[Dict[str, Any]] = Field(
        default_factory=list, description="Provides guide for interpretation"
    )

    # Related observations
    has_member: List[str] = Field(
        default_factory=list,
        description="Related resource that belongs to the observation group",
    )

    derived_from: List[str] = Field(
        default_factory=list,
        description="Related measurements the observation is made from",
    )

    # Components for multi-component observations
    component: List[Dict[str, Any]] = Field(
        default_factory=list, description="Component results"
    )

    # Performers
    performer: List[str] = Field(
        default_factory=list, description="Who is responsible for the observation"
    )

    # Agent-centric fields
    evidence_references: List[str] = Field(
        default_factory=list,
        description="References to evidence supporting this observation",
    )

    agent_context: Dict[str, Any] = Field(
        default_factory=dict, description="Agent-specific context and metadata"
    )

    @field_validator("subject")
    @classmethod
    def validate_subject(cls, v: str) -> str:
        """Ensure subject is not empty."""
        if not v.strip():
            raise ValueError("Subject cannot be empty")
        return v.strip()

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Validate observation code structure."""
        if not isinstance(v, dict):
            raise ValueError("Code must be a dictionary")
        if "coding" not in v:
            raise ValueError("Code must have a 'coding' field")
        if not isinstance(v["coding"], list) or len(v["coding"]) == 0:
            raise ValueError("Code coding must be a non-empty list")

        for coding in v["coding"]:
            if "system" not in coding or "code" not in coding:
                raise ValueError("Each coding must have 'system' and 'code' fields")

        return v

    @model_validator(mode="after")
    def validate_value_fields(self) -> "Observation":
        """Ensure only one value field is set."""
        value_fields = [
            self.value_quantity,
            self.value_codeable_concept,
            self.value_string,
            self.value_boolean,
            self.value_integer,
            self.value_range,
        ]

        non_none_values = [v for v in value_fields if v is not None]

        if len(non_none_values) > 1:
            raise ValueError("Only one value field can be set")

        if len(non_none_values) == 0 and self.data_absent_reason is None:
            raise ValueError(
                "Either a value field or data_absent_reason must be provided"
            )

        return self

    @model_validator(mode="after")
    def validate_effective_time(self) -> "Observation":
        """Ensure only one effective time field is set."""
        if self.effective_datetime is not None and self.effective_period is not None:
            raise ValueError(
                "Only one of effective_datetime or effective_period can be set"
            )
        return self

    @computed_field
    @property
    def has_value(self) -> bool:
        """Computed field indicating if observation has a value."""
        value_fields = [
            self.value_quantity,
            self.value_codeable_concept,
            self.value_string,
            self.value_boolean,
            self.value_integer,
            self.value_range,
        ]
        return any(v is not None for v in value_fields)

    @computed_field
    @property
    def primary_code(self) -> Optional[str]:
        """Computed field for primary observation code."""
        if "coding" in self.code and len(self.code["coding"]) > 0:
            return self.code["coding"][0].get("code")
        return None

    @computed_field
    @property
    def primary_system(self) -> Optional[str]:
        """Computed field for primary code system."""
        if "coding" in self.code and len(self.code["coding"]) > 0:
            return self.code["coding"][0].get("system")
        return None

    @computed_field
    @property
    def is_vital_sign(self) -> bool:
        """Computed field indicating if this is a vital sign."""
        for cat in self.category:
            if "coding" in cat:
                for coding in cat["coding"]:
                    if coding.get("code") == "vital-signs":
                        return True
        return False

    def validate_code_system(self, system: str) -> bool:
        """
        Validate if the observation code belongs to a specific system.

        Args:
            system: Code system to validate against

        Returns:
            True if code belongs to the system
        """
        if "coding" not in self.code:
            return False

        for coding in self.code["coding"]:
            if coding.get("system") == system:
                return True
        return False

    def is_loinc_code(self) -> bool:
        """Check if observation uses LOINC coding."""
        return self.validate_code_system("http://loinc.org")

    def is_snomed_code(self) -> bool:
        """Check if observation uses SNOMED CT coding."""
        return self.validate_code_system("http://snomed.info/sct")

    def add_component(
        self,
        code: Dict[str, Any],
        value: Union[Dict[str, Any], str, bool, int],
        data_absent_reason: Optional[str] = None,
    ) -> None:
        """Add a component to this observation."""
        component: Dict[str, Any] = {"code": code}

        if value is not None:
            if isinstance(value, dict):
                component["valueQuantity"] = value
            elif isinstance(value, str):
                component["valueString"] = value
            elif isinstance(value, bool):
                component["valueBoolean"] = value
            elif isinstance(value, int):
                component["valueInteger"] = value
        elif data_absent_reason:
            component["dataAbsentReason"] = {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/data-absent-reason",
                        "code": data_absent_reason,
                    }
                ]
            }

        self.component.append(component)
        self.update_timestamp()

    def set_reference_range(
        self,
        low: Optional[Dict[str, Any]] = None,
        high: Optional[Dict[str, Any]] = None,
        range_type: str = "normal",
        text: Optional[str] = None,
    ) -> None:
        """Set reference range for the observation."""
        ref_range = {}

        if low is not None:
            ref_range["low"] = low
        if high is not None:
            ref_range["high"] = high
        if text:
            ref_range["text"] = text

        ref_range["type"] = {
            "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/referencerange-meaning",
                    "code": range_type,
                    "display": range_type.title(),
                }
            ]
        }

        self.reference_range.append(ref_range)
        self.update_timestamp()

    def link_to_evidence(self, evidence_id: str) -> None:
        """Link this observation to evidence."""
        if evidence_id not in self.evidence_references:
            self.evidence_references.append(evidence_id)
            self.update_timestamp()

    def add_performer(self, performer_id: str) -> None:
        """Add a performer to this observation."""
        if performer_id not in self.performer:
            self.performer.append(performer_id)
            self.update_timestamp()

    def get_numeric_value(self) -> Optional[float]:
        """Get numeric value from the observation."""
        if self.value_quantity and "value" in self.value_quantity:
            return float(self.value_quantity["value"])
        elif self.value_integer is not None:
            return float(self.value_integer)
        return None

    def get_unit(self) -> Optional[str]:
        """Get unit of measurement."""
        if self.value_quantity and "unit" in self.value_quantity:
            return self.value_quantity["unit"]
        return None

    def __repr__(self) -> str:
        """Enhanced representation including code and value."""
        code_str = self.primary_code or "unknown"
        value_str = ""

        if self.value_quantity:
            val = self.value_quantity.get("value", "")
            unit = self.value_quantity.get("unit", "")
            value_str = f", value={val}{unit}"
        elif self.value_string:
            value_str = (
                f", value='{self.value_string[:20]}...'"
                if len(self.value_string) > 20
                else f", value='{self.value_string}'"
            )
        elif self.value_boolean is not None:
            value_str = f", value={self.value_boolean}"
        elif self.value_integer is not None:
            value_str = f", value={self.value_integer}"

        return f"Observation(id='{self.id}', code='{code_str}', status='{self.status}'{value_str})"
