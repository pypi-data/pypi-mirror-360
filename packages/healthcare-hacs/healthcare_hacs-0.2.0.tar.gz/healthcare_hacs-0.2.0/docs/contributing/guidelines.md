# Contributing Guidelines

Welcome to the HACS community! We're excited to have you contribute to the Healthcare Agent Communication Standard. This guide will help you get started with contributing to the project.

## 🤝 Code of Conduct

HACS follows the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). By participating, you are expected to uphold this code.

### Our Pledge
- Foster an open and welcoming environment
- Respect differing viewpoints and experiences
- Accept constructive criticism gracefully
- Focus on what's best for the community
- Show empathy towards other community members

## 🚀 Getting Started

### Prerequisites
- Python 3.10 or higher
- UV package manager (recommended)
- Git for version control
- Basic understanding of healthcare data standards (helpful but not required)

### Development Setup

1. **Fork and Clone**
   ```bash
   # Fork the repository on GitHub
   git clone https://github.com/YOUR_USERNAME/hacs.git
   cd hacs
   ```

2. **Set Up Development Environment**
   ```bash
   # Install UV if not already installed
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Install all dependencies
   uv sync
   
   # Verify installation
   uv run python -c "from hacs_core import Actor; print('✅ Setup complete!')"
   ```

3. **Create a Development Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/issue-description
   ```

## 📝 Contribution Types

We welcome various types of contributions:

### 🐛 Bug Reports
- Use the bug report template
- Include reproduction steps
- Provide system information
- Add relevant logs or screenshots

### ✨ Feature Requests
- Use the feature request template
- Explain the use case and benefits
- Consider healthcare compliance implications
- Provide implementation suggestions if possible

### 📚 Documentation
- Fix typos and improve clarity
- Add examples and use cases
- Update API documentation
- Create tutorials and guides

### 🔧 Code Contributions
- Bug fixes
- New features
- Performance improvements
- Test coverage improvements

### 🏥 Healthcare Domain Expertise
- FHIR compliance improvements
- Clinical workflow validation
- Healthcare standards alignment
- Medical terminology accuracy

## 🛠️ Development Workflow

### 1. Code Style and Standards

HACS follows strict code quality standards:

```bash
# Format code with ruff
uv run ruff format .

# Lint code
uv run ruff check .

# Type checking
uv run pyright

# Run all quality checks
uv run ruff check . && uv run ruff format --check . && uv run pyright
```

#### Code Style Guidelines
- **100% typed code**: All functions and classes must have type hints
- **Pydantic models**: Use Pydantic v2 for all data models
- **Descriptive names**: Use clear, healthcare-appropriate naming
- **Documentation**: Include docstrings for all public APIs
- **Error handling**: Provide meaningful error messages

### 2. Testing Requirements

All contributions must include appropriate tests:

```bash
# Run all tests
uv run pytest

# Run tests for specific package
uv run --package hacs-core pytest

# Run tests with coverage
uv run pytest --cov=hacs_core --cov=hacs_models --cov=hacs_tools

# Run integration tests
uv run python tests/test_integration_e2e.py
```

#### Testing Guidelines
- **Unit tests**: Test individual functions and methods
- **Integration tests**: Test cross-package functionality
- **Performance tests**: Ensure <300ms CRUD operations
- **FHIR compliance tests**: Validate round-trip conversions
- **Edge cases**: Test boundary conditions and error scenarios

### 3. Documentation Requirements

All contributions should include documentation updates:

```bash
# Update module documentation
docs/modules/hacs-[package].md

# Add examples
docs/examples/

# Update API reference
docs/reference/api.md
```

#### Documentation Standards
- **Clear examples**: Provide working code examples
- **Healthcare context**: Explain clinical relevance
- **API documentation**: Document all public interfaces
- **Migration guides**: For breaking changes
- **Performance notes**: Document performance characteristics

## 📦 Package-Specific Guidelines

### HACS Core (`hacs-core`)
- **Base models**: Extend `BaseResource` for new resource types
- **Security**: All operations must respect Actor permissions
- **Performance**: Optimize for agent workloads
- **Validation**: Comprehensive Pydantic validation

### HACS Models (`hacs-models`)
- **FHIR compliance**: All models must map to FHIR resources
- **Clinical accuracy**: Validate with healthcare professionals
- **Agent features**: Include memory handles and evidence links
- **Internationalization**: Consider multi-language support

### HACS FHIR (`hacs-fhir`)
- **Round-trip fidelity**: Preserve all data in conversions
- **Standards compliance**: Follow FHIR R5 specifications
- **Error handling**: Provide detailed validation errors
- **Performance**: Optimize for large datasets

### HACS Tools (`hacs-tools`)
- **Security first**: All operations require Actor authentication
- **Protocol adapters**: Maintain clinical context across protocols
- **Validation**: Comprehensive business rule validation
- **Performance**: Sub-millisecond operations

### HACS CLI (`hacs-cli`)
- **User experience**: Rich, intuitive interface
- **Error messages**: Clear, actionable error messages
- **Progress indicators**: For long-running operations
- **Help system**: Comprehensive help and examples

### HACS API (`hacs-api`)
- **REST standards**: Follow REST API best practices
- **Authentication**: Secure Actor-based authentication
- **Documentation**: Auto-generated OpenAPI documentation
- **Rate limiting**: Protect against abuse

## 🏥 Healthcare Compliance

### FHIR Compliance
- All models must map to FHIR resources
- Use proper FHIR terminology (LOINC, SNOMED CT, etc.)
- Validate against FHIR specifications
- Include FHIR examples in documentation

### Clinical Accuracy
- Validate medical concepts with healthcare professionals
- Use appropriate medical terminology
- Consider clinical workflows and use cases
- Ensure patient safety considerations

### Privacy and Security
- Follow HIPAA guidelines for patient data
- Implement proper access controls
- Audit all data access and modifications
- Secure data transmission and storage

## 🔄 Pull Request Process

### 1. Before Submitting
- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] Documentation is updated
- [ ] Performance benchmarks are met
- [ ] FHIR compliance is maintained

### 2. Pull Request Template
Use the provided PR template and include:
- **Description**: Clear description of changes
- **Type**: Bug fix, feature, documentation, etc.
- **Testing**: How the changes were tested
- **Healthcare Impact**: Clinical relevance and safety considerations
- **Breaking Changes**: Any breaking changes and migration path

### 3. Review Process
- **Automated checks**: CI/CD pipeline must pass
- **Code review**: At least one maintainer approval
- **Healthcare review**: Clinical validation for healthcare-related changes
- **Documentation review**: Documentation updates reviewed
- **Performance review**: Performance impact assessed

### 4. Merge Requirements
- All CI checks pass
- At least one maintainer approval
- No unresolved review comments
- Documentation is complete
- Tests provide adequate coverage

## 🎯 Issue Guidelines

### Bug Reports
```markdown
**Bug Description**
Clear description of the bug

**Reproduction Steps**
1. Step one
2. Step two
3. Step three

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Environment**
- OS: [e.g., macOS 14.0]
- Python: [e.g., 3.11.0]
- HACS Version: [e.g., 0.1.0]

**Healthcare Context**
Clinical relevance and impact
```

### Feature Requests
```markdown
**Feature Description**
Clear description of the proposed feature

**Use Case**
Healthcare workflow or agent use case

**Benefits**
How this improves HACS

**Implementation Ideas**
Suggestions for implementation

**FHIR Compliance**
How this aligns with FHIR standards

**Clinical Validation**
Healthcare professional input needed
```

## 🏆 Recognition

We recognize contributors in several ways:

### Contributor Types
- **Code Contributors**: Bug fixes, features, improvements
- **Documentation Contributors**: Guides, examples, API docs
- **Healthcare Experts**: Clinical validation, FHIR compliance
- **Community Leaders**: Issue triage, community support
- **Testers**: Bug reports, testing, quality assurance

### Recognition Methods
- **Contributors file**: Listed in CONTRIBUTORS.md
- **Release notes**: Mentioned in release announcements
- **Community spotlight**: Featured in community updates
- **Maintainer status**: For significant ongoing contributions

## 📞 Getting Help

### Community Support
- **GitHub Discussions**: Ask questions and share ideas
- **Discord**: Real-time community chat
- **Issues**: Report bugs and request features
- **Email**: Maintainer contact for sensitive issues

### Mentorship Program
- **New contributor onboarding**: Guided first contributions
- **Healthcare domain guidance**: Clinical workflow education
- **Technical mentorship**: Code review and architecture guidance
- **FHIR training**: Healthcare standards education

## 🔒 Security

### Reporting Security Issues
- **Email**: security@hacs.dev (private disclosure)
- **Scope**: Authentication, authorization, data leakage
- **Response**: 24-hour acknowledgment, 90-day disclosure
- **Credit**: Security researcher recognition

### Security Guidelines
- Never commit sensitive data (API keys, patient data)
- Use secure coding practices
- Follow OWASP guidelines
- Implement proper input validation

## 📋 Checklist for Contributors

Before submitting your contribution:

- [ ] Code follows HACS style guidelines
- [ ] All tests pass (`uv run pytest`)
- [ ] Code is properly typed (`uv run pyright`)
- [ ] Code is formatted (`uv run ruff format .`)
- [ ] Documentation is updated
- [ ] Examples are provided
- [ ] FHIR compliance is maintained
- [ ] Performance benchmarks are met
- [ ] Security considerations are addressed
- [ ] Healthcare accuracy is validated

## 🎉 Thank You!

Thank you for contributing to HACS! Your contributions help build the future of healthcare AI communication standards. Together, we're creating tools that will improve patient care and advance healthcare technology.

---

*This document is a living guide that evolves with our community. Please suggest improvements through issues or pull requests.* 