# HACS FHIR

FHIR integration for Healthcare Agent Communication Standard (HACS).

## Overview

`hacs-fhir` provides seamless integration between HACS models and FHIR R5 resources, enabling bidirectional conversion and full interoperability with FHIR-compliant healthcare systems.

## Key Features

### Bidirectional Conversion
- Convert HACS models to FHIR resources
- Convert FHIR resources to HACS models
- Lossless round-trip conversion
- Validation against FHIR specifications

### FHIR R5 Compliance
- Full support for FHIR R5 specification
- Standard resource types and profiles
- Coded values with standard terminologies
- Proper resource relationships and references

### Integration Capabilities
- EHR system integration
- FHIR server connectivity
- Bulk data operations
- Real-time synchronization

## Installation

```bash
pip install hacs-fhir
```

## Quick Start

```python
from hacs_models import Patient, Observation
from hacs_fhir import FHIRConverter

# Create a HACS patient
patient = Patient(
    display_name="Jane Smith",
    birth_date="1985-03-15",
    gender="female"
)

# Convert to FHIR
converter = FHIRConverter()
fhir_patient = converter.to_fhir(patient)

# Convert back to HACS
hacs_patient = converter.from_fhir(fhir_patient)

# Work with observations
observation = Observation(
    patient_id=patient.id,
    observation_type="blood_pressure",
    value={"systolic": 135, "diastolic": 85},
    unit="mmHg"
)

fhir_observation = converter.to_fhir(observation)
```

## Supported Resources

### Patient Resources
- Patient demographics and identification
- Contact information and addresses
- Emergency contacts and relationships
- Insurance and coverage information

### Clinical Resources
- Observations (vital signs, lab results)
- Encounters (visits, admissions)
- Conditions and diagnoses
- Medications and prescriptions

### Communication Resources
- Agent messages and communications
- Care team communications
- Patient-provider messaging
- System notifications

## FHIR Server Integration

```python
from hacs_fhir import FHIRClient

# Connect to FHIR server
client = FHIRClient(base_url="https://fhir.example.com")

# Upload HACS data to FHIR server
patient_ref = client.create_patient(patient)
observation_ref = client.create_observation(observation)

# Query FHIR server
patients = client.search_patients(family_name="Smith")
observations = client.get_patient_observations(patient_ref)
```

## Documentation

For complete documentation, see the [HACS Documentation](https://github.com/solanovisitor/hacs/blob/main/docs/README.md).

## License

Licensed under the Apache License, Version 2.0. See [LICENSE](https://github.com/solanovisitor/hacs/blob/main/LICENSE) for details.

## Contributing

See [Contributing Guidelines](https://github.com/solanovisitor/hacs/blob/main/docs/contributing/guidelines.md) for information on how to contribute to HACS FHIR.
