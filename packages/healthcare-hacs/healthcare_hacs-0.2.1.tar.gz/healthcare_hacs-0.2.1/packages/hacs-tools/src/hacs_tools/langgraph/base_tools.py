"""
Base tools for HACS-LangGraph integration.

This module provides base tool classes and common clinical tools that can be
reused across different LangGraph workflows.
"""

from abc import ABC, abstractmethod
from typing import Any

from hacs_core import Evidence
from pydantic import BaseModel


class ToolCallResult(BaseModel):
    """Result of a tool call execution."""

    tool_name: str
    success: bool
    result: dict[str, Any] | None = None
    error: str | None = None


class BaseHACSTool(ABC):
    """Base class for HACS-compatible tools."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    def execute(self, state: dict[str, Any], **kwargs) -> ToolCallResult:
        """Execute the tool with the given state."""
        pass

    def __call__(self, state: dict[str, Any], **kwargs) -> ToolCallResult:
        """Make the tool callable."""
        return self.execute(state, **kwargs)


class ClinicalTool(BaseHACSTool):
    """Base class for clinical assessment tools."""

    def __init__(
        self,
        name: str,
        description: str,
        risk_thresholds: dict[str, float] | None = None,
    ):
        super().__init__(name, description)
        self.risk_thresholds = risk_thresholds or {
            "low": 0.3,
            "medium": 0.6,
            "high": 0.8,
        }

    def calculate_risk_level(self, score: float) -> str:
        """Calculate risk level based on score."""
        if score >= self.risk_thresholds["high"]:
            return "high"
        elif score >= self.risk_thresholds["medium"]:
            return "medium"
        else:
            return "low"


class CardiovascularRiskTool(ClinicalTool):
    """Tool for calculating cardiovascular risk."""

    def __init__(self):
        super().__init__(
            "cardiovascular_risk_calculator",
            "Calculates 10-year cardiovascular risk based on patient data and observations",
        )

    def execute(self, state: dict[str, Any], **kwargs) -> ToolCallResult:
        """Calculate cardiovascular risk."""
        try:
            patient_data = state.get("patient")
            observations = state.get("observations", [])

            if not patient_data:
                return ToolCallResult(
                    tool_name=self.name,
                    success=False,
                    error="No patient data available",
                )

            # Extract relevant data
            age = patient_data.get("age_years", 0)
            gender = patient_data.get("gender", "unknown")

            # Find blood pressure and cholesterol values
            systolic_bp = None
            cholesterol = None

            for obs in observations:
                if "blood pressure" in obs.get("code", {}).get("text", "").lower():
                    if "value_quantity" in obs:
                        systolic_bp = obs["value_quantity"].get("value")
                elif "cholesterol" in obs.get("code", {}).get("text", "").lower():
                    if "value_quantity" in obs:
                        cholesterol = obs["value_quantity"].get("value")

            # Simple risk calculation (simplified Framingham-like)
            risk_score = 0.0

            # Age factor
            if age > 65:
                risk_score += 0.3
            elif age > 50:
                risk_score += 0.2
            elif age > 40:
                risk_score += 0.1

            # Gender factor
            if gender == "male":
                risk_score += 0.1

            # Blood pressure factor
            if systolic_bp:
                if systolic_bp >= 160:
                    risk_score += 0.3
                elif systolic_bp >= 140:
                    risk_score += 0.2
                elif systolic_bp >= 130:
                    risk_score += 0.1

            # Cholesterol factor
            if cholesterol:
                if cholesterol >= 240:
                    risk_score += 0.2
                elif cholesterol >= 200:
                    risk_score += 0.1

            # Convert to percentage
            risk_percentage = min(risk_score * 100, 100)
            risk_level = self.calculate_risk_level(risk_score)

            result = {
                "ten_year_risk_percent": round(risk_percentage, 1),
                "risk_category": risk_level,
                "risk_factors": [],
                "recommendations": [],
            }

            # Add risk factors and recommendations
            if systolic_bp and systolic_bp >= 140:
                result["risk_factors"].append("Hypertension")
                result["recommendations"].append("Blood pressure management")

            if cholesterol and cholesterol >= 200:
                result["risk_factors"].append("High cholesterol")
                result["recommendations"].append("Cholesterol management")

            if age > 50:
                result["risk_factors"].append("Age")

            if risk_level == "high":
                result["recommendations"].append("Immediate cardiology consultation")
            elif risk_level == "medium":
                result["recommendations"].append(
                    "Lifestyle modifications and follow-up"
                )

            return ToolCallResult(tool_name=self.name, success=True, result=result)

        except Exception as e:
            return ToolCallResult(tool_name=self.name, success=False, error=str(e))


class EvidenceTool(BaseHACSTool):
    """Tool for searching and retrieving clinical evidence."""

    def __init__(self, evidence_database: list[Evidence] | None = None):
        super().__init__(
            "evidence_search",
            "Searches clinical evidence database for relevant guidelines and research",
        )
        self.evidence_database = evidence_database or []

    def add_evidence(self, evidence: Evidence) -> None:
        """Add evidence to the database."""
        self.evidence_database.append(evidence)

    def execute(self, state: dict[str, Any], **kwargs) -> ToolCallResult:
        """Search for relevant evidence."""
        try:
            search_terms = kwargs.get("search_terms", [])
            evidence_type = kwargs.get("evidence_type")
            max_results = kwargs.get("max_results", 10)

            if isinstance(search_terms, str):
                search_terms = [search_terms]

            # Search evidence database
            relevant_evidence = []

            for evidence in self.evidence_database:
                relevance_score = 0

                # Check tags
                for term in search_terms:
                    if term.lower() in [tag.lower() for tag in evidence.tags]:
                        relevance_score += 1

                # Check content
                for term in search_terms:
                    if term.lower() in evidence.content.lower():
                        relevance_score += 0.5

                # Check citation
                for term in search_terms:
                    if term.lower() in evidence.citation.lower():
                        relevance_score += 0.3

                # Filter by evidence type if specified
                if evidence_type and evidence.evidence_type != evidence_type:
                    continue

                if relevance_score > 0:
                    relevant_evidence.append(
                        {
                            "evidence": evidence.model_dump(),
                            "relevance_score": relevance_score,
                        }
                    )

            # Sort by relevance
            relevant_evidence.sort(key=lambda x: x["relevance_score"], reverse=True)

            # Limit results
            relevant_evidence = relevant_evidence[:max_results]

            result = {
                "search_terms": search_terms,
                "evidence_type": evidence_type,
                "total_found": len(relevant_evidence),
                "evidence": [item["evidence"] for item in relevant_evidence],
                "relevance_scores": [
                    item["relevance_score"] for item in relevant_evidence
                ],
            }

            return ToolCallResult(tool_name=self.name, success=True, result=result)

        except Exception as e:
            return ToolCallResult(tool_name=self.name, success=False, error=str(e))


class DiagnosisAssistantTool(ClinicalTool):
    """Tool for diagnostic assistance based on symptoms and observations."""

    def __init__(self):
        super().__init__(
            "diagnosis_assistant",
            "Provides diagnostic suggestions based on patient symptoms and observations",
        )

        # Simple symptom-diagnosis mapping
        self.diagnosis_patterns = {
            "chest_pain": {
                "diagnoses": ["Angina", "Myocardial Infarction", "Pulmonary Embolism"],
                "urgency": "high",
            },
            "shortness_of_breath": {
                "diagnoses": ["Asthma", "COPD", "Pulmonary Edema", "Pneumonia"],
                "urgency": "medium",
            },
            "hypertension": {
                "diagnoses": ["Essential Hypertension", "Secondary Hypertension"],
                "urgency": "medium",
            },
            "diabetes": {
                "diagnoses": [
                    "Type 1 Diabetes",
                    "Type 2 Diabetes",
                    "Gestational Diabetes",
                ],
                "urgency": "medium",
            },
        }

    def execute(self, state: dict[str, Any], **kwargs) -> ToolCallResult:
        """Provide diagnostic assistance."""
        try:
            symptoms = kwargs.get("symptoms", [])
            observations = state.get("observations", [])

            if isinstance(symptoms, str):
                symptoms = [symptoms]

            # Extract symptoms from observations if not provided
            if not symptoms:
                for obs in observations:
                    obs_text = obs.get("code", {}).get("text", "").lower()
                    if "blood pressure" in obs_text:
                        value = obs.get("value_quantity", {}).get("value", 0)
                        if value >= 140:
                            symptoms.append("hypertension")
                    elif "glucose" in obs_text:
                        value = obs.get("value_quantity", {}).get("value", 0)
                        if value >= 126:
                            symptoms.append("diabetes")

            # Find matching diagnoses
            suggested_diagnoses = []
            max_urgency = "low"

            for symptom in symptoms:
                for pattern, data in self.diagnosis_patterns.items():
                    if pattern in symptom.lower():
                        for diagnosis in data["diagnoses"]:
                            if diagnosis not in suggested_diagnoses:
                                suggested_diagnoses.append(diagnosis)

                        # Update urgency
                        if data["urgency"] == "high":
                            max_urgency = "high"
                        elif data["urgency"] == "medium" and max_urgency != "high":
                            max_urgency = "medium"

            result = {
                "symptoms_analyzed": symptoms,
                "suggested_diagnoses": suggested_diagnoses,
                "urgency_level": max_urgency,
                "recommendations": [],
                "confidence": 0.7 if suggested_diagnoses else 0.3,
            }

            # Add recommendations based on urgency
            if max_urgency == "high":
                result["recommendations"].append(
                    "Immediate medical evaluation required"
                )
            elif max_urgency == "medium":
                result["recommendations"].append(
                    "Schedule appointment within 24-48 hours"
                )
            else:
                result["recommendations"].append("Routine follow-up recommended")

            return ToolCallResult(tool_name=self.name, success=True, result=result)

        except Exception as e:
            return ToolCallResult(tool_name=self.name, success=False, error=str(e))
