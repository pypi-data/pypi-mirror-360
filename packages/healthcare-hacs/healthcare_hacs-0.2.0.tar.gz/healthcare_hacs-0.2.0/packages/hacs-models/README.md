# HACS Models

Clinical models for Healthcare Agent Communication Standard (HACS).

## Overview

`hacs-models` provides comprehensive clinical data models that are FHIR-compliant and designed for healthcare agent communication. These models represent core healthcare entities like patients, observations, encounters, and agent messages.

## Key Models

### Patient
Represents a healthcare patient with:
- Demographics and identification
- Contact information
- Medical record integration
- FHIR R5 compliance

### Observation
Clinical observations and measurements:
- Vital signs and lab results
- Coded values with standard terminologies
- Temporal data with timestamps
- Quality indicators and reliability

### Encounter
Healthcare encounters and visits:
- Encounter classification and status
- Participant information
- Location and timing
- Care team assignments

### AgentMessage
Messages exchanged between healthcare agents:
- Structured message content
- Agent identification and routing
- Message threading and correlation
- Priority and urgency indicators

## Installation

```bash
pip install hacs-models
```

## Quick Start

```python
from hacs_models import Patient, Observation, Encounter, AgentMessage
from hacs_core import Actor

# Create a patient
patient = Patient(
    display_name="John Doe",
    birth_date="1980-01-01",
    gender="male"
)

# Create an observation
observation = Observation(
    patient_id=patient.id,
    observation_type="vital_signs",
    value={"systolic": 120, "diastolic": 80},
    unit="mmHg",
    timestamp="2024-01-15T10:30:00Z"
)

# Create an encounter
encounter = Encounter(
    patient_id=patient.id,
    encounter_type="outpatient",
    status="in_progress",
    start_time="2024-01-15T10:00:00Z"
)

# Create an agent message
actor = Actor(actor_id="dr_smith", actor_type="clinician")
message = AgentMessage(
    sender_id="dr_smith",
    content="Patient shows elevated blood pressure",
    message_type="clinical_note",
    actor_context=actor
)
```

## FHIR Compliance

All models are designed to be FHIR R5 compliant:
- Standard resource structures
- Coded values using standard terminologies
- Proper resource relationships
- Validation against FHIR specifications

## Documentation

For complete documentation, see the [HACS Models Documentation](https://github.com/solanovisitor/hacs/blob/main/docs/modules/hacs-models.md).

## License

Licensed under the Apache License, Version 2.0. See [LICENSE](https://github.com/solanovisitor/hacs/blob/main/LICENSE) for details.

## Contributing

See [Contributing Guidelines](https://github.com/solanovisitor/hacs/blob/main/docs/contributing/guidelines.md) for information on how to contribute to HACS Models.
