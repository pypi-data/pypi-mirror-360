# HACS Documentation

[![Version](https://img.shields.io/badge/version-0.2.0-blue)](https://github.com/solanovisitor/hacs)
[![Tests](https://img.shields.io/badge/tests-passing-green)](https://github.com/solanovisitor/hacs/actions)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://python.org)

Healthcare Agent Communication Standard - Production-ready healthcare AI data models and tools.

## Quick Start

```bash
pip install healthcare-hacs
```

Verify installation:
```bash
git clone https://github.com/solanovisitor/hacs.git
cd hacs && uv sync
uv run python tests/test_quick_start.py
```

## Core Components

### Data Models
- **Patient**: Demographics, identifiers, contact information
- **Observation**: Clinical measurements with LOINC codes
- **Encounter**: Healthcare visits and interactions
- **AgentMessage**: AI agent communications with clinical context
- **Actor**: Healthcare providers with role-based permissions
- **MemoryBlock**: Structured memory for AI agents
- **Evidence**: Clinical evidence with confidence scoring

### Tools
- **CRUD Operations**: Create, read, update, delete resources
- **FHIR Integration**: Bidirectional FHIR R4/R5 conversion
- **Validation**: Resource validation and error checking
- **Vector Support**: Metadata for vector databases
- **CLI Interface**: Command-line operations

### AI Integration
- **Vector Stores**: Pinecone and Qdrant integration
- **Memory Management**: Episodic, procedural, and executive memory
- **LangGraph**: Workflow adapter for clinical decision support
- **CrewAI**: Multi-agent healthcare workflows

## Documentation

| Guide | Purpose | Status |
|-------|---------|--------|
| [Installation](getting-started/installation.md) | Setup and dependencies | Complete |
| [Quick Start](getting-started/quickstart.md) | 5-minute tutorial | Complete |
| [Core Concepts](getting-started/concepts.md) | Understanding HACS | Complete |
| [Architecture](getting-started/architecture.md) | System design | Complete |
| [Basic Usage](examples/basic-usage.md) | Code examples | Complete |
| [API Reference](reference/api.md) | Complete API documentation | Complete |
| [Configuration](reference/configuration.md) | Configuration options | Complete |
| [Error Handling](reference/errors.md) | Error codes and handling | Complete |

## Module Documentation

| Module | Purpose | Status |
|--------|---------|--------|
| [HACS Core](modules/hacs-core.md) | Base models, Actor, Memory, Evidence | Complete |
| [HACS Models](modules/hacs-models.md) | Patient, Observation, Encounter, AgentMessage | Complete |
| [HACS Vectorization](modules/hacs-vectorization.md) | Vector storage and semantic search | Complete |

## Getting Started

### For Healthcare Developers
Start with [Basic Usage](examples/basic-usage.md) to understand clinical data models.

### For AI Developers
Start with [Core Concepts](getting-started/concepts.md) to understand agent integration.

### For System Integrators
Start with [Architecture](getting-started/architecture.md) for technical overview.

## Testing

All features are tested with comprehensive coverage:

```bash
# Run all tests
uv run pytest tests/ -v

# Quick verification
uv run python tests/test_quick_start.py

# LLM-friendly features
uv run python tests/test_llm_friendly.py
```

## Package Structure

```
hacs/
├── packages/
│   ├── hacs-core/      # Base models and security
│   ├── hacs-models/    # Clinical data models
│   ├── hacs-tools/     # CRUD operations and adapters
│   ├── hacs-fhir/      # FHIR conversion
│   ├── hacs-api/       # FastAPI service
│   ├── hacs-cli/       # Command-line interface
│   ├── hacs-qdrant/    # Qdrant vector store
│   ├── hacs-openai/    # OpenAI embeddings
│   └── hacs-pinecone/  # Pinecone vector store
├── docs/               # Documentation
├── examples/           # Working examples
├── tests/              # Test suite
└── samples/            # Sample data files
```

## Support

- [GitHub Issues](https://github.com/solanovisitor/hacs/issues) - Bug reports and feature requests
- [GitHub Discussions](https://github.com/solanovisitor/hacs/discussions) - Questions and community support
- [Contributing Guidelines](contributing/guidelines.md) - How to contribute 