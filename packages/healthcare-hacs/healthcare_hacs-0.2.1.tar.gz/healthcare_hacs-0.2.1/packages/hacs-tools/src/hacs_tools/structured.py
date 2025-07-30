"""
Structured-IO for LLM Integration

This module provides helpers for LLM function-binding, including auto-generation
of function specifications from JSON Schema, validation and coercion of LLM
responses, and integration with tool calling patterns.
"""

from datetime import date, datetime
from enum import Enum
from typing import Any

from hacs_core import Actor, BaseResource
from hacs_models import AgentMessage, Encounter, Observation, Patient
from pydantic import BaseModel, ValidationError


class FunctionSpecError(Exception):
    """Exception raised for function specification errors."""

    pass


class LLMValidationError(Exception):
    """Exception raised for LLM output validation errors."""

    pass


class ToolCallPattern(str, Enum):
    """Supported tool calling patterns."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GENERIC = "generic"


class ToolCall(BaseModel):
    """Represents a tool call from an LLM."""

    function_name: str
    arguments: dict[str, Any]
    call_id: str | None = None


class ToolCallResult(BaseModel):
    """Result of a tool call execution."""

    call_id: str | None = None
    success: bool
    result: Any | None = None
    error: str | None = None
    execution_time_ms: float | None = None


def generate_function_spec(
    model: type[BaseResource], pattern: ToolCallPattern = ToolCallPattern.OPENAI
) -> dict[str, Any]:
    """
    Auto-generate LLM function specification from a HACS model.

    Args:
        model: HACS model class
        pattern: Tool calling pattern to use

    Returns:
        Function specification dictionary
    """
    try:
        # Get JSON schema from the model
        schema = model.model_json_schema()

        # Extract model name and description
        model_name = model.__name__
        description = schema.get(
            "description", f"Create or validate a {model_name} resource"
        )

        # Build function specification based on pattern
        if pattern == ToolCallPattern.OPENAI:
            return {
                "type": "function",
                "function": {
                    "name": f"create_{model_name.lower()}",
                    "description": description,
                    "parameters": {
                        "type": "object",
                        "properties": schema.get("properties", {}),
                        "required": schema.get("required", []),
                    },
                },
            }

        elif pattern == ToolCallPattern.ANTHROPIC:
            return {
                "name": f"create_{model_name.lower()}",
                "description": description,
                "input_schema": {
                    "type": "object",
                    "properties": schema.get("properties", {}),
                    "required": schema.get("required", []),
                },
            }

        else:  # GENERIC
            return {
                "name": f"create_{model_name.lower()}",
                "description": description,
                "parameters": schema,
                "returns": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string", "description": "Created resource ID"},
                        "success": {
                            "type": "boolean",
                            "description": "Whether creation succeeded",
                        },
                    },
                },
            }

    except Exception as e:
        raise FunctionSpecError(
            f"Failed to generate function spec for {model.__name__}: {str(e)}"
        )


def validate_llm_output(
    spec: dict[str, Any],
    output: dict[str, Any],
    model: type[BaseResource] | None = None,
) -> BaseResource | dict[str, Any]:
    """
    Validate and coerce LLM output against a function specification.

    Args:
        spec: Function specification
        output: LLM output to validate
        model: Optional model class for direct validation

    Returns:
        Validated and coerced output

    Raises:
        LLMValidationError: If validation fails
    """
    try:
        # Extract parameters schema from spec
        if "function" in spec and "parameters" in spec["function"]:
            # OpenAI format
            parameters_schema = spec["function"]["parameters"]
        elif "input_schema" in spec:
            # Anthropic format
            parameters_schema = spec["input_schema"]
        elif "parameters" in spec:
            # Generic format
            parameters_schema = spec["parameters"]
        else:
            raise LLMValidationError("Invalid function specification format")

        # Validate required fields
        required_fields = parameters_schema.get("required", [])
        for field in required_fields:
            if field not in output:
                raise LLMValidationError(
                    f"Required field '{field}' missing from LLM output"
                )

        # If we have a model class, validate against it
        if model:
            try:
                # Handle datetime strings
                cleaned_output = _clean_datetime_fields(output)
                validated_resource = model(**cleaned_output)
                return validated_resource
            except ValidationError as e:
                raise LLMValidationError(f"Pydantic validation failed: {str(e)}")

        # Otherwise, validate against JSON schema
        validated_output = _validate_against_schema(output, parameters_schema)
        return validated_output

    except Exception as e:
        raise LLMValidationError(f"Failed to validate LLM output: {str(e)}")


def _clean_datetime_fields(data: dict[str, Any]) -> dict[str, Any]:
    """Clean datetime fields in LLM output."""
    cleaned = data.copy()

    # Common datetime field names
    datetime_fields = [
        "created_at",
        "updated_at",
        "effective_datetime",
        "issued",
        "birth_date",
    ]

    for field in datetime_fields:
        if field in cleaned and isinstance(cleaned[field], str):
            try:
                # Try to parse as datetime
                if "T" in cleaned[field] or " " in cleaned[field]:
                    # Full datetime
                    cleaned[field] = datetime.fromisoformat(
                        cleaned[field].replace("Z", "+00:00")
                    )
                else:
                    # Date only
                    cleaned[field] = date.fromisoformat(cleaned[field])
            except ValueError:
                # Leave as string if parsing fails
                pass

    return cleaned


def _validate_against_schema(
    data: dict[str, Any], schema: dict[str, Any]
) -> dict[str, Any]:
    """Validate data against JSON schema."""
    # Basic validation - in production, use jsonschema library
    properties = schema.get("properties", {})
    validated = {}

    for key, value in data.items():
        if key in properties:
            prop_schema = properties[key]
            prop_type = prop_schema.get("type")

            # Basic type validation
            if prop_type == "string" and not isinstance(value, str):
                validated[key] = str(value)
            elif prop_type == "number" and not isinstance(value, int | float):
                try:
                    validated[key] = float(value)
                except ValueError:
                    raise LLMValidationError(f"Cannot convert {key} to number: {value}")
            elif prop_type == "integer" and not isinstance(value, int):
                try:
                    validated[key] = int(value)
                except ValueError:
                    raise LLMValidationError(
                        f"Cannot convert {key} to integer: {value}"
                    )
            elif prop_type == "boolean" and not isinstance(value, bool):
                if isinstance(value, str):
                    validated[key] = value.lower() in ("true", "1", "yes", "on")
                else:
                    validated[key] = bool(value)
            else:
                validated[key] = value
        else:
            validated[key] = value

    return validated


def create_tool_executor(actor: Actor) -> "ToolExecutor":
    """
    Create a tool executor with Actor context.

    Args:
        actor: Actor to use for tool execution

    Returns:
        ToolExecutor instance
    """
    return ToolExecutor(actor)


class ToolExecutor:
    """Executes tool calls with Actor context."""

    def __init__(self, actor: Actor):
        self.actor = actor
        self.available_functions = {}
        self._register_default_functions()

    def _register_default_functions(self):
        """Register default CRUD functions."""
        from .crud import CreateResource, DeleteResource, ReadResource, UpdateResource

        # Register CRUD functions for each model type
        model_types = [Patient, AgentMessage, Encounter, Observation]

        for model_type in model_types:
            model_name = model_type.__name__.lower()

            # Create function
            def make_create_func(model_cls):
                def create_func(**kwargs):
                    resource = model_cls(**kwargs)
                    return CreateResource(resource, self.actor)

                return create_func

            # Read function
            def make_read_func(model_cls):
                def read_func(id: str):
                    return ReadResource(model_cls.__name__, id, self.actor)

                return read_func

            # Update function
            def make_update_func(model_cls):
                def update_func(**kwargs):
                    resource = model_cls(**kwargs)
                    return UpdateResource(resource, self.actor)

                return update_func

            # Delete function
            def make_delete_func(model_cls):
                def delete_func(id: str, cascade: bool = False):
                    return DeleteResource(model_cls.__name__, id, self.actor, cascade)

                return delete_func

            self.available_functions[f"create_{model_name}"] = make_create_func(
                model_type
            )
            self.available_functions[f"read_{model_name}"] = make_read_func(model_type)
            self.available_functions[f"update_{model_name}"] = make_update_func(
                model_type
            )
            self.available_functions[f"delete_{model_name}"] = make_delete_func(
                model_type
            )

    def execute_tool_call(self, tool_call: ToolCall) -> ToolCallResult:
        """Execute a tool call."""
        start_time = datetime.now()

        try:
            if tool_call.function_name not in self.available_functions:
                return ToolCallResult(
                    call_id=tool_call.call_id,
                    success=False,
                    error=f"Function {tool_call.function_name} not found",
                )

            func = self.available_functions[tool_call.function_name]
            result = func(**tool_call.arguments)

            execution_time = (datetime.now() - start_time).total_seconds() * 1000

            return ToolCallResult(
                call_id=tool_call.call_id,
                success=True,
                result=result,
                execution_time_ms=execution_time,
            )

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds() * 1000

            return ToolCallResult(
                call_id=tool_call.call_id,
                success=False,
                error=str(e),
                execution_time_ms=execution_time,
            )


# Convenience functions
def get_patient_function_specs(
    pattern: ToolCallPattern = ToolCallPattern.OPENAI,
) -> dict[str, Any]:
    """Get function specifications for Patient operations."""
    return generate_function_spec(Patient, pattern)


def validate_patient_output(output: dict[str, Any]) -> Patient:
    """Validate LLM output as a Patient resource."""
    spec = generate_function_spec(Patient)
    result = validate_llm_output(spec, output, Patient)
    if isinstance(result, Patient):
        return result
    else:
        raise LLMValidationError("Expected Patient object but got Dict")


def validate_observation_output(output: dict[str, Any]) -> Observation:
    """Validate LLM output as an Observation resource."""
    spec = generate_function_spec(Observation)
    result = validate_llm_output(spec, output, Observation)
    if isinstance(result, Observation):
        return result
    else:
        raise LLMValidationError("Expected Observation object but got Dict")
