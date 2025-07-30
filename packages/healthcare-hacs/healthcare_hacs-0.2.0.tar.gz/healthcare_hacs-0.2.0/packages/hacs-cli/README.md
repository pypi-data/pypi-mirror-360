# HACS CLI

Command-line interface for Healthcare Agent Communication Standard (HACS).

## Overview

`hacs-cli` provides a comprehensive command-line interface for managing HACS healthcare data, performing CRUD operations, running validations, and integrating with various healthcare systems and agent frameworks.

## Key Features

### Data Management
- Patient, observation, and encounter management
- Bulk data operations and imports
- Data validation and integrity checks
- Export to various formats (JSON, CSV, FHIR)

### Agent Integration
- Agent registration and management
- Message routing and delivery
- Protocol adapter configuration
- Workflow execution and monitoring

### System Operations
- Health checks and diagnostics
- Performance monitoring
- Configuration management
- Database operations

## Installation

```bash
pip install hacs-cli
```

## Quick Start

### Basic Commands
```bash
# Get help
hacs --help

# Create a patient
hacs patient create --name "John Doe" --birth-date "1980-01-01" --gender "male"

# List patients
hacs patient list

# Get patient details
hacs patient get --id PATIENT_ID

# Create observation
hacs observation create --patient-id PATIENT_ID --type "blood_pressure" --value "120/80" --unit "mmHg"

# List observations for a patient
hacs observation list --patient-id PATIENT_ID
```

### Bulk Operations
```bash
# Import patients from CSV
hacs patient import --file patients.csv --format csv

# Export patients to JSON
hacs patient export --format json --output patients.json

# Bulk create observations
hacs observation import --file observations.json --format json
```

## Commands Reference

### Patient Management
```bash
# Create patient
hacs patient create --name "Jane Smith" --birth-date "1985-03-15"

# Update patient
hacs patient update --id PATIENT_ID --name "Jane Smith-Jones"

# Delete patient
hacs patient delete --id PATIENT_ID

# Search patients
hacs patient search --query "hypertension" --limit 10
```

### Observation Management
```bash
# Create observation
hacs observation create \
    --patient-id PATIENT_ID \
    --type "vital_signs" \
    --value '{"systolic": 120, "diastolic": 80}' \
    --unit "mmHg"

# List observations
hacs observation list --patient-id PATIENT_ID --type "blood_pressure"

# Update observation
hacs observation update --id OBS_ID --value '{"systolic": 125, "diastolic": 82}'
```

### Agent Operations
```bash
# Register agent
hacs agent register --id "dr_smith" --type "clinician" --name "Dr. Sarah Smith"

# Send message
hacs agent message send \
    --from "dr_smith" \
    --to "nurse_jones" \
    --content "Patient needs follow-up" \
    --type "clinical_note"

# List messages
hacs agent message list --agent-id "dr_smith"
```

### System Operations
```bash
# Health check
hacs system health

# Database status
hacs system db status

# Run migrations
hacs system db migrate

# Performance metrics
hacs system metrics

# Configuration
hacs system config show
hacs system config set --key "api.timeout" --value "30"
```

## Configuration

### Configuration File
Create `~/.hacs/config.yaml`:
```yaml
database:
  url: postgresql://user:pass@localhost/hacs
  
api:
  base_url: http://localhost:8000
  timeout: 30
  
auth:
  token: your-api-token
  
logging:
  level: INFO
  file: ~/.hacs/logs/hacs.log
```

### Environment Variables
```bash
export HACS_DATABASE_URL=postgresql://user:pass@localhost/hacs
export HACS_API_BASE_URL=http://localhost:8000
export HACS_AUTH_TOKEN=your-token
export HACS_LOG_LEVEL=INFO
```

## Integration Examples

### FHIR Integration
```bash
# Export to FHIR format
hacs patient export --format fhir --output patients.fhir.json

# Import from FHIR server
hacs patient import --fhir-server https://fhir.example.com --format fhir
```

### Agent Framework Integration
```bash
# Start MCP adapter
hacs adapter mcp start --port 8080

# Configure LangGraph workflow
hacs adapter langgraph configure --workflow clinical_assessment

# Run CrewAI integration
hacs adapter crewai run --crew medical_team --input patient_data.json
```

## Scripting and Automation

### Batch Processing
```bash
#!/bin/bash
# Process multiple patients
for patient_file in patients/*.json; do
    hacs patient import --file "$patient_file" --format json
done
```

### Monitoring Script
```bash
#!/bin/bash
# Health monitoring
hacs system health --format json | jq '.status'
hacs system metrics --format json | jq '.memory_usage'
```

## Documentation

For complete documentation, see the [HACS Documentation](https://github.com/solanovisitor/hacs/blob/main/docs/README.md).

## License

Licensed under the Apache License, Version 2.0. See [LICENSE](https://github.com/solanovisitor/hacs/blob/main/LICENSE) for details.

## Contributing

See [Contributing Guidelines](https://github.com/solanovisitor/hacs/blob/main/docs/contributing/guidelines.md) for information on how to contribute to HACS CLI.
