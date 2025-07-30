# ⚙️ Configuration Reference

<div align="center">

![Configuration](https://img.shields.io/badge/Configuration-Production_Ready-brightgreen?style=for-the-badge&logo=settings&logoColor=white)
![Environment](https://img.shields.io/badge/Multi_Environment-Dev_Test_Prod-success?style=for-the-badge&logo=server&logoColor=white)
![Flexible](https://img.shields.io/badge/Setup-Zero_Config_to_Custom-blue?style=for-the-badge&logo=wrench&logoColor=white)

**🔧 Complete HACS Configuration Guide**

*From zero-config development to enterprise production deployment*

</div>

---

## 🎯 Configuration Philosophy

HACS follows a **"zero-config to fully-custom"** approach:

> **🚀 Works out of the box, configures for any environment**

- **Development**: Zero configuration required
- **Testing**: Minimal configuration for CI/CD
- **Production**: Full customization for enterprise needs

---

## 📁 Configuration File Structure

```
hacs/
├── pyproject.toml              # Main workspace configuration
├── packages/
│   ├── hacs-core/
│   │   └── pyproject.toml     # Core package configuration
│   ├── hacs-models/
│   │   └── pyproject.toml     # Models package configuration
│   ├── hacs-tools/
│   │   └── pyproject.toml     # Tools package configuration
│   └── ...
├── .env                        # Environment variables (optional)
├── .env.local                  # Local overrides (optional)
├── .env.production            # Production environment (optional)
└── hacs.config.yaml           # HACS-specific configuration (optional)
```

---

## 🔧 Main Configuration (`pyproject.toml`)

### **Workspace Configuration**

```toml
[tool.uv.workspace]
members = [
    "packages/hacs-core",
    "packages/hacs-models", 
    "packages/hacs-fhir",
    "packages/hacs-tools",
    "packages/hacs-cli",
    "packages/hacs-api"
]

[tool.uv]
dev-dependencies = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "pyright>=1.1.350",
    "ruff>=0.1.0",
    "pre-commit>=3.0.0"
]

[project]
name = "hacs"
version = "0.1.0"
description = "Healthcare Agent Communication Standard"
readme = "README.md"
license = {text = "Apache-2.0"}
authors = [
    {name = "HACS Contributors", email = "contributors@hacs.dev"}
]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Healthcare Industry",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: Apache Software License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Scientific/Engineering :: Medical Science Apps.",
    "Topic :: Software Development :: Libraries :: Python Modules"
]
```

### **Type Checking Configuration**

```toml
[tool.pyright]
include = ["packages/", "tests/", "main.py"]
exclude = ["examples/", "samples/", ".trunk/", "**/__pycache__", "**/node_modules"]
pythonVersion = "3.10"
typeCheckingMode = "strict"
reportMissingTypeStubs = false
reportUnknownParameterType = false
reportUnknownMemberType = false
reportUnknownArgumentType = false
reportUnknownVariableType = false
reportUnknownLambdaType = false
reportImplicitStringConcatenation = false
```

### **Code Quality Configuration**

```toml
[tool.ruff]
target-version = "py310"
line-length = 100
exclude = [
    ".bzr",
    ".direnv", 
    ".eggs",
    ".git",
    ".hg",
    ".mypy_cache",
    ".nox",
    ".pants.d",
    ".pytype",
    ".ruff_cache",
    ".svn",
    ".tox",
    ".venv",
    "__pypackages__",
    "_build",
    "buck-out",
    "build",
    "dist",
    "node_modules",
    "venv",
    "examples",
    "samples"
]

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
]
ignore = [
    "E501",  # line too long, handled by black
    "B008",  # do not perform function calls in argument defaults
    "C901",  # too complex
    "W191",  # indentation contains tabs
]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
skip-source-first-line = false
line-ending = "auto"
```

### **Testing Configuration**

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--strict-config",
    "--verbose",
    "--tb=short",
    "--cov=packages",
    "--cov-report=term-missing",
    "--cov-report=html",
    "--cov-report=xml",
    "--cov-fail-under=90"
]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
    "fhir: marks tests as FHIR compliance tests",
    "performance: marks tests as performance benchmarks"
]
```

---

## 🌍 Environment Variables

### **Core Environment Variables**

```bash
# Basic Configuration
HACS_ENV=development                    # Environment: development, testing, production
HACS_LOG_LEVEL=INFO                    # Logging: DEBUG, INFO, WARNING, ERROR
HACS_DEBUG=false                       # Debug mode: true/false

# API Configuration
HACS_API_HOST=localhost                # API host
HACS_API_PORT=8000                     # API port
HACS_API_WORKERS=1                     # Number of API workers
HACS_API_RELOAD=false                  # Auto-reload on changes

# Database Configuration
HACS_DATABASE_URL=sqlite:///hacs.db    # Database connection string
HACS_DATABASE_ECHO=false               # SQL query logging

# Security Configuration
HACS_SECRET_KEY=your-secret-key        # JWT secret key
HACS_ACCESS_TOKEN_EXPIRE_MINUTES=30    # Token expiration
HACS_ENABLE_CORS=true                  # CORS support
HACS_CORS_ORIGINS=*                    # Allowed CORS origins

# Performance Configuration
HACS_CACHE_TTL=3600                    # Cache TTL in seconds
HACS_MAX_MEMORY_SIZE=1000              # Max memory blocks per query
HACS_MAX_EVIDENCE_SIZE=100             # Max evidence items per query

# Healthcare Configuration
HACS_FHIR_VERSION=R5                   # FHIR version
HACS_TERMINOLOGY_SERVER=https://tx.fhir.org  # FHIR terminology server
HACS_ENABLE_FHIR_VALIDATION=true       # Enable FHIR validation

# Agent Configuration
HACS_DEFAULT_ACTOR_PERMISSIONS=patient:read,observation:read  # Default permissions
HACS_MAX_REASONING_TRACE_LENGTH=50     # Max reasoning trace steps
HACS_ENABLE_MEMORY_CONSOLIDATION=true  # Enable memory consolidation
```

### **Environment-Specific Configuration**

#### **Development (`.env.development`)**
```bash
HACS_ENV=development
HACS_LOG_LEVEL=DEBUG
HACS_DEBUG=true
HACS_API_RELOAD=true
HACS_DATABASE_ECHO=true
HACS_ENABLE_FHIR_VALIDATION=false
HACS_CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

#### **Testing (`.env.testing`)**
```bash
HACS_ENV=testing
HACS_LOG_LEVEL=WARNING
HACS_DEBUG=false
HACS_DATABASE_URL=sqlite:///:memory:
HACS_CACHE_TTL=0
HACS_ENABLE_FHIR_VALIDATION=true
```

#### **Production (`.env.production`)**
```bash
HACS_ENV=production
HACS_LOG_LEVEL=INFO
HACS_DEBUG=false
HACS_API_HOST=0.0.0.0
HACS_API_WORKERS=4
HACS_DATABASE_URL=postgresql://user:pass@host:5432/hacs
HACS_SECRET_KEY=${SECRET_KEY}
HACS_ENABLE_CORS=false
HACS_ENABLE_FHIR_VALIDATION=true
```

---

## 📋 HACS-Specific Configuration (`hacs.config.yaml`)

```yaml
# HACS Configuration File
version: "0.1.0"

# Core Settings
core:
  default_actor_role: "user"
  enable_audit_logging: true
  audit_log_level: "INFO"
  max_resource_age_days: 365

# Model Settings
models:
  patient:
    require_birth_date: false
    validate_identifiers: true
    default_active: true
  
  observation:
    require_effective_date: true
    validate_reference_ranges: true
    auto_interpret_values: true
  
  encounter:
    require_participant: true
    validate_period: true
    auto_calculate_duration: true

# Memory Settings
memory:
  default_importance_threshold: 0.5
  max_memory_blocks: 10000
  consolidation_interval_hours: 24
  episodic_retention_days: 90
  procedural_retention_days: 365
  executive_retention_days: 1095
  semantic_retention_days: -1  # Permanent

# Evidence Settings
evidence:
  default_confidence_threshold: 0.7
  max_evidence_items: 1000
  auto_quality_scoring: true
  require_citations: true
  validate_publication_dates: true

# FHIR Settings
fhir:
  version: "R5"
  validate_on_conversion: true
  preserve_extensions: true
  terminology_server: "https://tx.fhir.org"
  code_systems:
    - "http://loinc.org"
    - "http://snomed.info/sct"
    - "http://unitsofmeasure.org"

# API Settings
api:
  enable_openapi: true
  enable_redoc: true
  max_request_size: "10MB"
  rate_limiting:
    enabled: true
    requests_per_minute: 100
    burst_size: 10

# Security Settings
security:
  enable_actor_validation: true
  require_permissions: true
  audit_all_operations: true
  encrypt_sensitive_fields: true
  password_policy:
    min_length: 12
    require_uppercase: true
    require_lowercase: true
    require_numbers: true
    require_symbols: true

# Performance Settings
performance:
  enable_caching: true
  cache_backend: "memory"  # memory, redis, memcached
  query_timeout_seconds: 30
  max_concurrent_requests: 100
  enable_compression: true

# Logging Settings
logging:
  level: "INFO"
  format: "json"  # json, text
  include_timestamps: true
  include_request_ids: true
  log_sql_queries: false
  sensitive_field_masking: true

# Integration Settings
integrations:
  langraph:
    enable_state_persistence: true
    max_state_size: "1MB"
  
  crewai:
    enable_agent_binding: true
    max_agents_per_crew: 10
  
  mcp:
    enable_task_conversion: true
    preserve_context: true
```

---

## 🐳 Docker Configuration

### **Dockerfile**
```dockerfile
FROM python:3.11-slim

# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml uv.lock ./
COPY packages/ packages/

# Install dependencies
RUN uv sync --no-dev

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uv", "run", "python", "-m", "hacs_api"]
```

### **docker-compose.yml**
```yaml
version: '3.8'

services:
  hacs-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - HACS_ENV=production
      - HACS_DATABASE_URL=postgresql://hacs:${DB_PASSWORD}@db:5432/hacs
      - HACS_SECRET_KEY=${SECRET_KEY}
    depends_on:
      - db
      - redis
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=hacs
      - POSTGRES_USER=hacs
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - hacs-api
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

---

## ☁️ Cloud Configuration

### **Kubernetes Deployment**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hacs-api
  labels:
    app: hacs-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: hacs-api
  template:
    metadata:
      labels:
        app: hacs-api
    spec:
      containers:
      - name: hacs-api
        image: hacs:latest
        ports:
        - containerPort: 8000
        env:
        - name: HACS_ENV
          value: "production"
        - name: HACS_DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: hacs-secrets
              key: database-url
        - name: HACS_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: hacs-secrets
              key: secret-key
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

### **AWS ECS Configuration**
```json
{
  "family": "hacs-api",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::ACCOUNT:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::ACCOUNT:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "hacs-api",
      "image": "ACCOUNT.dkr.ecr.REGION.amazonaws.com/hacs:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "HACS_ENV",
          "value": "production"
        }
      ],
      "secrets": [
        {
          "name": "HACS_DATABASE_URL",
          "valueFrom": "arn:aws:ssm:REGION:ACCOUNT:parameter/hacs/database-url"
        },
        {
          "name": "HACS_SECRET_KEY",
          "valueFrom": "arn:aws:ssm:REGION:ACCOUNT:parameter/hacs/secret-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/hacs-api",
          "awslogs-region": "REGION",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 60
      }
    }
  ]
}
```

---

## 🔧 Advanced Configuration

### **Custom Package Configuration**

Each HACS package can be configured independently:

```toml
# packages/hacs-core/pyproject.toml
[project]
name = "hacs-core"
version = "0.1.0"
dependencies = [
    "pydantic>=2.0.0",
    "python-dateutil>=2.8.0"
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0"
]
performance = [
    "orjson>=3.8.0",
    "uvloop>=0.17.0"
]
```

### **Plugin System Configuration**

```yaml
# plugins.yaml
plugins:
  - name: "custom-validator"
    type: "validation"
    module: "hacs_plugins.validators.custom"
    enabled: true
    config:
      strict_mode: true
      
  - name: "external-terminology"
    type: "terminology"
    module: "hacs_plugins.terminology.external"
    enabled: false
    config:
      server_url: "https://custom-terminology.example.com"
      api_key: "${TERMINOLOGY_API_KEY}"
```

### **Monitoring Configuration**

```yaml
# monitoring.yaml
metrics:
  enabled: true
  endpoint: "/metrics"
  include_default_metrics: true
  custom_metrics:
    - name: "hacs_operations_total"
      type: "counter"
      description: "Total HACS operations"
      labels: ["operation", "resource_type", "actor_role"]

tracing:
  enabled: true
  service_name: "hacs-api"
  jaeger_endpoint: "http://jaeger:14268/api/traces"
  sample_rate: 0.1

alerts:
  enabled: true
  webhook_url: "${ALERT_WEBHOOK_URL}"
  rules:
    - name: "high_error_rate"
      condition: "error_rate > 0.05"
      severity: "warning"
    - name: "database_connection_failure"
      condition: "db_connection_failures > 0"
      severity: "critical"
```

---

## 🎯 Configuration Best Practices

### ✅ **Recommended Practices**

1. **Environment Separation**
   ```bash
   # Use different configurations for each environment
   .env.development
   .env.testing  
   .env.production
   ```

2. **Secret Management**
   ```bash
   # Never commit secrets to version control
   echo "*.env*" >> .gitignore
   echo "hacs.config.yaml" >> .gitignore  # If it contains secrets
   ```

3. **Configuration Validation**
   ```python
   # Validate configuration on startup
   from hacs_tools import validate_configuration
   
   if not validate_configuration():
       raise RuntimeError("Invalid configuration")
   ```

4. **Performance Tuning**
   ```yaml
   # Tune for your workload
   performance:
     cache_size: 1000        # For high-read workloads
     worker_processes: 4     # For high-concurrency
     batch_size: 100         # For bulk operations
   ```

### ⚠️ **Common Pitfalls**

1. **Over-configuration**: Start simple, add complexity as needed
2. **Hardcoded values**: Use environment variables for deployment-specific values
3. **Insecure defaults**: Always change default passwords and keys
4. **Missing validation**: Validate configuration early and fail fast
5. **Performance assumptions**: Profile and measure before optimizing

---

## 🎉 Configuration Summary

<div align="center">

### **🔧 HACS Configuration Capabilities**

| Aspect | Development | Testing | Production |
|--------|-------------|---------|------------|
| **Setup Complexity** | Zero config | Minimal | Full custom |
| **Performance** | Basic | Optimized | Enterprise |
| **Security** | Relaxed | Strict | Maximum |
| **Monitoring** | Basic | Comprehensive | Full observability |
| **Scalability** | Single instance | Multi-instance | Auto-scaling |

### **📊 Configuration Coverage**

![Environment](https://img.shields.io/badge/Environments-Dev_Test_Prod-success?style=for-the-badge)
![Deployment](https://img.shields.io/badge/Deployment-Docker_K8s_Cloud-blue?style=for-the-badge)
![Monitoring](https://img.shields.io/badge/Monitoring-Metrics_Tracing_Alerts-orange?style=for-the-badge)

### **🚀 Ready for Any Environment**

[**🚀 Quick Start**](../getting-started/quickstart.md) • [**🏗️ Installation**](../getting-started/installation.md) • [**💡 Examples**](../examples/basic-usage.md) • [**🤝 Contributing**](../contributing/guidelines.md)

</div>

---

<div align="center">

**⚙️ HACS: Configuration Made Simple**

*Zero config to start, infinite customization for enterprise*

![Zero Config](https://img.shields.io/badge/Zero_Config-Ready-brightgreen?style=for-the-badge)
![Enterprise](https://img.shields.io/badge/Enterprise-Scalable-success?style=for-the-badge)
![Flexible](https://img.shields.io/badge/Deployment-Any_Environment-blue?style=for-the-badge)

</div> 