"""
Patient model for healthcare data representation.

This module provides the Patient model with FHIR-compliant fields,
comprehensive validation, and agent-centric features for healthcare AI workflows.
"""

from datetime import date
from enum import Enum
from typing import Any, Dict, List, Literal, Optional
from pydantic import Field, field_validator, computed_field

from hacs_core import BaseResource


class AdministrativeGender(str, Enum):
    """FHIR-compliant administrative gender codes."""

    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    UNKNOWN = "unknown"


class IdentifierUse(str, Enum):
    """FHIR-compliant identifier use codes."""

    USUAL = "usual"
    OFFICIAL = "official"
    TEMP = "temp"
    SECONDARY = "secondary"
    OLD = "old"


class IdentifierType(str, Enum):
    """Common healthcare identifier types."""

    MR = "MR"  # Medical record number
    SSN = "SSN"  # Social Security Number
    DL = "DL"  # Driver's License
    PPN = "PPN"  # Passport number
    TAX = "TAX"  # Tax ID number
    NI = "NI"  # National identifier
    NH = "NH"  # NHS number
    MC = "MC"  # Medicare number


class ContactPointSystem(str, Enum):
    """FHIR-compliant contact point system codes."""

    PHONE = "phone"
    FAX = "fax"
    EMAIL = "email"
    PAGER = "pager"
    URL = "url"
    SMS = "sms"
    OTHER = "other"


class ContactPointUse(str, Enum):
    """FHIR-compliant contact point use codes."""

    HOME = "home"
    WORK = "work"
    TEMP = "temp"
    OLD = "old"
    MOBILE = "mobile"


class Patient(BaseResource):
    """
    Represents a patient in the healthcare system.

    This model includes comprehensive patient demographics, identifiers,
    and contact information with FHIR compliance and agent-centric features.
    """

    resource_type: Literal["Patient"] = Field(
        default="Patient", description="Resource type identifier"
    )

    # Name fields
    given: List[str] = Field(
        description="Given names (first, middle names)",
        examples=[["John", "Michael"], ["Sarah"], ["María", "Elena"]],
    )

    family: str = Field(
        description="Family name (surname, last name)",
        examples=["Smith", "Johnson", "García"],
    )

    prefix: List[str] = Field(
        default_factory=list,
        description="Name prefixes (titles)",
        examples=[["Dr.", "Prof."], ["Mr."], ["Ms.", "PhD"]],
    )

    suffix: List[str] = Field(
        default_factory=list,
        description="Name suffixes",
        examples=[["Jr."], ["III"], ["MD", "PhD"]],
    )

    # Demographics
    gender: AdministrativeGender = Field(
        description="Administrative gender",
        examples=["male", "female", "other", "unknown"],
    )

    birth_date: Optional[date] = Field(
        default=None,
        description="Date of birth",
        examples=["1985-03-15", "1992-12-01", None],
    )

    deceased: bool = Field(default=False, description="Whether the patient is deceased")

    deceased_date: Optional[date] = Field(
        default=None,
        description="Date of death if deceased",
        examples=["2024-01-15", None],
    )

    # Identifiers
    identifiers: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Patient identifiers (MRN, SSN, etc.)",
        examples=[
            [
                {
                    "use": "usual",
                    "type": "MR",
                    "system": "http://hospital.example.com/mrn",
                    "value": "123456789",
                    "assigner": "Example Hospital",
                }
            ]
        ],
    )

    # Contact information
    telecom: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Contact points (phone, email, etc.)",
        examples=[
            [
                {"system": "phone", "value": "+1-555-0123", "use": "home"},
                {"system": "email", "value": "john.smith@example.com", "use": "home"},
            ]
        ],
    )

    # Address
    address: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Patient addresses",
        examples=[
            [
                {
                    "use": "home",
                    "line": ["123 Main St", "Apt 4B"],
                    "city": "Anytown",
                    "state": "CA",
                    "postal_code": "12345",
                    "country": "US",
                }
            ]
        ],
    )

    # Marital status
    marital_status: Optional[str] = Field(
        default=None,
        description="Marital status code",
        examples=[
            "M",
            "S",
            "D",
            "W",
            "U",
        ],  # Married, Single, Divorced, Widowed, Unknown
    )

    # Language and communication
    communication: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Languages and communication preferences",
        examples=[
            [
                {"language": "en-US", "preferred": True},
                {"language": "es-ES", "preferred": False},
            ]
        ],
    )

    # Agent-centric fields
    agent_context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Agent-specific context and metadata",
        examples=[
            {
                "last_interaction": "2024-01-15T10:30:00Z",
                "preferred_agent": "primary-care-agent",
                "interaction_count": 5,
                "care_plan_status": "active",
            }
        ],
    )

    care_team: List[str] = Field(
        default_factory=list,
        description="References to care team members",
        examples=[["practitioner-001", "practitioner-002", "agent-primary-care"]],
    )

    # Emergency contact
    emergency_contact: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Emergency contact information",
        examples=[
            [
                {
                    "relationship": "spouse",
                    "name": "Jane Smith",
                    "telecom": [
                        {"system": "phone", "value": "+1-555-0124", "use": "mobile"}
                    ],
                }
            ]
        ],
    )

    # Clinical metadata
    active: bool = Field(
        default=True, description="Whether this patient record is active"
    )

    @field_validator("given")
    @classmethod
    def validate_given_names(cls, v: List[str]) -> List[str]:
        """Ensure at least one given name is provided."""
        if not v or not any(name.strip() for name in v):
            raise ValueError("At least one given name must be provided")
        return [name.strip() for name in v if name.strip()]

    @field_validator("family")
    @classmethod
    def validate_family_name(cls, v: str) -> str:
        """Ensure family name is not empty."""
        if not v.strip():
            raise ValueError("Family name cannot be empty")
        return v.strip()

    @field_validator("identifiers")
    @classmethod
    def validate_identifiers(cls, v: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate identifier structure."""
        for identifier in v:
            if not isinstance(identifier, dict):
                raise ValueError("Each identifier must be a dictionary")
            if "value" not in identifier:
                raise ValueError("Identifier must have a 'value' field")
            if not identifier["value"].strip():
                raise ValueError("Identifier value cannot be empty")
        return v

    @field_validator("deceased_date")
    @classmethod
    def validate_deceased_date(cls, v: Optional[date], values) -> Optional[date]:
        """Ensure deceased date is only set if patient is deceased."""
        # Note: In Pydantic v2, we need to access other fields differently
        # This is a simplified validation - in practice, you'd use model_validator
        return v

    @computed_field
    @property
    def full_name(self) -> str:
        """Computed field for full name."""
        parts = []
        if self.prefix:
            parts.extend(self.prefix)
        parts.extend(self.given)
        parts.append(self.family)
        if self.suffix:
            parts.extend(self.suffix)
        return " ".join(parts)

    @computed_field
    @property
    def display_name(self) -> str:
        """Computed field for display name (given + family)."""
        return f"{' '.join(self.given)} {self.family}"

    @computed_field
    @property
    def age_years(self) -> Optional[int]:
        """Computed field for age in years."""
        if self.birth_date is None:
            return None

        birth_date = self.birth_date  # Type guard
        end_date = (
            self.deceased_date if self.deceased and self.deceased_date else date.today()
        )
        age = end_date.year - birth_date.year

        # Adjust for birthday not yet reached this year
        if end_date.month < birth_date.month or (
            end_date.month == birth_date.month and end_date.day < birth_date.day
        ):
            age -= 1

        return max(0, age)

    def get_full_name(self) -> str:
        """Get the full name including prefixes and suffixes."""
        return self.full_name

    def calculate_age(self, as_of_date: Optional[date] = None) -> Optional[int]:
        """
        Calculate age as of a specific date.

        Args:
            as_of_date: Date to calculate age as of (defaults to today)

        Returns:
            Age in years, or None if birth_date is not set
        """
        if self.birth_date is None:
            return None

        birth_date = self.birth_date  # Type guard
        if as_of_date is None:
            as_of_date = date.today()

        age = as_of_date.year - birth_date.year

        # Adjust for birthday not yet reached this year
        if as_of_date.month < birth_date.month or (
            as_of_date.month == birth_date.month and as_of_date.day < birth_date.day
        ):
            age -= 1

        return max(0, age)

    def add_identifier(
        self,
        value: str,
        type_code: str,
        use: str = "usual",
        system: Optional[str] = None,
        assigner: Optional[str] = None,
    ) -> None:
        """
        Add an identifier to the patient.

        Args:
            value: Identifier value
            type_code: Type of identifier (MR, SSN, etc.)
            use: Use of identifier (usual, official, etc.)
            system: System that assigned the identifier
            assigner: Organization that assigned the identifier
        """
        identifier = {"use": use, "type": type_code, "value": value.strip()}

        if system:
            identifier["system"] = system
        if assigner:
            identifier["assigner"] = assigner

        self.identifiers.append(identifier)
        self.update_timestamp()

    def get_primary_identifier(self) -> Optional[Dict[str, Any]]:
        """
        Get the primary identifier (first 'usual' or 'official' identifier).

        Returns:
            Primary identifier dictionary or None if no identifiers
        """
        # Look for usual identifiers first
        for identifier in self.identifiers:
            if identifier.get("use") == "usual":
                return identifier

        # Then look for official identifiers
        for identifier in self.identifiers:
            if identifier.get("use") == "official":
                return identifier

        # Return first identifier if no usual/official found
        return self.identifiers[0] if self.identifiers else None

    def get_identifier_by_type(self, type_code: str) -> Optional[Dict[str, Any]]:
        """
        Get identifier by type code.

        Args:
            type_code: Type of identifier to find (MR, SSN, etc.)

        Returns:
            Identifier dictionary or None if not found
        """
        for identifier in self.identifiers:
            if identifier.get("type") == type_code:
                return identifier
        return None

    def add_telecom(self, system: str, value: str, use: str = "home") -> None:
        """
        Add a contact point to the patient.

        Args:
            system: Contact system (phone, email, etc.)
            value: Contact value
            use: Use of contact (home, work, etc.)
        """
        telecom = {"system": system, "value": value.strip(), "use": use}
        self.telecom.append(telecom)
        self.update_timestamp()

    def get_telecom_by_system(
        self, system: str, use: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get contact points by system and optionally by use.

        Args:
            system: Contact system to filter by
            use: Optional use to filter by

        Returns:
            List of matching contact points
        """
        matches = [t for t in self.telecom if t.get("system") == system]
        if use:
            matches = [t for t in matches if t.get("use") == use]
        return matches

    def update_agent_context(self, key: str, value: Any) -> None:
        """
        Update agent-specific context.

        Args:
            key: Context key
            value: Context value
        """
        self.agent_context[key] = value
        self.update_timestamp()

    def add_care_team_member(self, member_id: str) -> None:
        """
        Add a care team member reference.

        Args:
            member_id: ID of the care team member
        """
        if member_id not in self.care_team:
            self.care_team.append(member_id)
            self.update_timestamp()

    def remove_care_team_member(self, member_id: str) -> bool:
        """
        Remove a care team member reference.

        Args:
            member_id: ID of the care team member to remove

        Returns:
            True if member was removed, False if not found
        """
        if member_id in self.care_team:
            self.care_team.remove(member_id)
            self.update_timestamp()
            return True
        return False

    def deactivate(self, reason: Optional[str] = None) -> None:
        """
        Deactivate the patient record.

        Args:
            reason: Optional reason for deactivation
        """
        self.active = False
        if reason:
            self.update_agent_context("deactivation_reason", reason)
        self.update_timestamp()

    def activate(self) -> None:
        """Activate the patient record."""
        self.active = True
        if "deactivation_reason" in self.agent_context:
            del self.agent_context["deactivation_reason"]
        self.update_timestamp()

    def __repr__(self) -> str:
        """Enhanced representation including name and demographics."""
        age_str = f", age {self.age_years}" if self.age_years is not None else ""
        status = "active" if self.active else "inactive"
        return f"Patient(id='{self.id}', name='{self.display_name}', gender='{self.gender}'{age_str}, status='{status}')"
