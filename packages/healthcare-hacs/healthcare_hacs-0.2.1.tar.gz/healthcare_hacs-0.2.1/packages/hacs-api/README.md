# HACS API

FastAPI service for Healthcare Agent Communication Standard (HACS).

## Overview

`hacs-api` provides a production-ready REST API service built with FastAPI for managing HACS healthcare data. It offers comprehensive endpoints for patients, observations, encounters, and agent communications with built-in authentication, validation, and FHIR compliance.

## Key Features

### REST API Endpoints
- **Patients**: CRUD operations for patient management
- **Observations**: Clinical data and measurements
- **Encounters**: Healthcare visits and episodes
- **Agent Messages**: Inter-agent communications
- **Evidence**: Clinical evidence and guidelines

### Authentication & Security
- JWT-based authentication
- Role-based access control
- API key management
- Request rate limiting
- CORS support

### FHIR Compliance
- FHIR R5 compatible endpoints
- Standard resource formats
- FHIR search parameters
- Bulk data operations

## Installation

```bash
pip install hacs-api
```

## Quick Start

### Start the API Server
```bash
# Using the CLI
hacs-api

# Or using uvicorn directly
uvicorn hacs_api.main:app --host 0.0.0.0 --port 8000
```

### API Usage
```python
import requests

# Create a patient
patient_data = {
    "display_name": "John Doe",
    "birth_date": "1980-01-01",
    "gender": "male"
}

response = requests.post(
    "http://localhost:8000/api/v1/patients",
    json=patient_data,
    headers={"Authorization": "Bearer YOUR_TOKEN"}
)

patient = response.json()
patient_id = patient["id"]

# Get patient
response = requests.get(
    f"http://localhost:8000/api/v1/patients/{patient_id}",
    headers={"Authorization": "Bearer YOUR_TOKEN"}
)

# Create observation
observation_data = {
    "patient_id": patient_id,
    "observation_type": "blood_pressure",
    "value": {"systolic": 120, "diastolic": 80},
    "unit": "mmHg"
}

response = requests.post(
    "http://localhost:8000/api/v1/observations",
    json=observation_data,
    headers={"Authorization": "Bearer YOUR_TOKEN"}
)
```

## API Endpoints

### Patient Management
- `GET /api/v1/patients` - List patients
- `POST /api/v1/patients` - Create patient
- `GET /api/v1/patients/{id}` - Get patient
- `PUT /api/v1/patients/{id}` - Update patient
- `DELETE /api/v1/patients/{id}` - Delete patient

### Clinical Data
- `GET /api/v1/observations` - List observations
- `POST /api/v1/observations` - Create observation
- `GET /api/v1/patients/{id}/observations` - Get patient observations

### Agent Communications
- `GET /api/v1/messages` - List messages
- `POST /api/v1/messages` - Send message
- `GET /api/v1/messages/{id}` - Get message

## Configuration

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost/hacs

# Authentication
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# API Settings
API_V1_PREFIX=/api/v1
CORS_ORIGINS=["http://localhost:3000"]
```

### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "hacs_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Authentication

### JWT Token Authentication
```python
import requests

# Login to get token
response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    json={"username": "user", "password": "pass"}
)
token = response.json()["access_token"]

# Use token in requests
headers = {"Authorization": f"Bearer {token}"}
```

## Documentation

- **Interactive API Docs**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI Spec**: `http://localhost:8000/openapi.json`

For complete documentation, see the [HACS Documentation](https://github.com/solanovisitor/hacs/blob/main/docs/README.md).

## License

Licensed under the Apache License, Version 2.0. See [LICENSE](https://github.com/solanovisitor/hacs/blob/main/LICENSE) for details.

## Contributing

See [Contributing Guidelines](https://github.com/solanovisitor/hacs/blob/main/docs/contributing/guidelines.md) for information on how to contribute to HACS API.
