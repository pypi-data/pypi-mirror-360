# Pull Request

## Description

<!-- Provide a brief description of the changes in this PR -->

**What does this PR do?**
- 

**Why is this change needed?**
- 

**Related Issue(s):**
- Fixes #(issue number)
- Relates to #(issue number)

## Type of Change

<!-- Mark the relevant option with an "x" -->

- [ ] 🐛 Bug fix (non-breaking change which fixes an issue)
- [ ] ✨ New feature (non-breaking change which adds functionality)
- [ ] 💥 Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] 📚 Documentation update
- [ ] 🔧 Refactoring (no functional changes, no api changes)
- [ ] ⚡ Performance improvement
- [ ] 🧪 Test update
- [ ] 🔒 Security fix

## Component(s) Affected

<!-- Mark all that apply -->

- [ ] hacs-core (Base models and classes)
- [ ] hacs-models (Patient, Observation, etc.)
- [ ] hacs-tools (CRUD operations, vectorization)
- [ ] hacs-fhir (FHIR integration)
- [ ] hacs-api (REST API)
- [ ] hacs-cli (Command line interface)
- [ ] hacs-qdrant (Qdrant integration)
- [ ] hacs-openai (OpenAI integration)
- [ ] hacs-pinecone (Pinecone integration)
- [ ] Documentation
- [ ] CI/CD
- [ ] Other: ___________

## Healthcare Compliance

<!-- Ensure healthcare data protection requirements are met -->

- [ ] ✅ **No PHI**: This PR contains no real patient data or Protected Health Information
- [ ] ✅ **Synthetic Data Only**: Any healthcare examples use synthetic or de-identified data
- [ ] ✅ **FHIR Compliance**: Changes maintain FHIR R4 compliance (if applicable)
- [ ] ✅ **Privacy Preserved**: No changes that could compromise patient privacy
- [ ] ✅ **Regulatory Aware**: Considered healthcare regulatory requirements

## Testing

<!-- Describe the testing you've performed -->

### Test Coverage

- [ ] ✅ **Unit Tests**: Added/updated unit tests for new functionality
- [ ] ✅ **Integration Tests**: Added/updated integration tests
- [ ] ✅ **End-to-End Tests**: Verified complete workflows work
- [ ] ✅ **Healthcare Tests**: Tested healthcare-specific scenarios
- [ ] ✅ **Performance Tests**: Verified performance requirements (if applicable)

### Manual Testing

<!-- Describe manual testing performed -->

**Testing Steps:**
1. 
2. 
3. 

**Test Results:**
- [ ] All tests pass locally
- [ ] No new linting errors
- [ ] No type checking errors
- [ ] Performance is acceptable

### Test Data

<!-- Describe test data used -->

- [ ] Used synthetic patient data only
- [ ] No real healthcare information included
- [ ] Test data is properly documented

## Code Quality

<!-- Ensure code quality standards are met -->

- [ ] ✅ **Linting**: Code passes all linting checks (`uv run ruff check`)
- [ ] ✅ **Type Checking**: Code passes type checking (`uv run pyright`)
- [ ] ✅ **Formatting**: Code is properly formatted (`uv run ruff format`)
- [ ] ✅ **Documentation**: Code includes proper docstrings and comments
- [ ] ✅ **Type Hints**: All functions include proper type hints

### Code Review Checklist

- [ ] Code follows project style guidelines
- [ ] Functions are well-documented with clear docstrings
- [ ] Error handling is appropriate and informative
- [ ] No hardcoded values that should be configurable
- [ ] No TODO comments left in production code

## Documentation

<!-- Document any documentation changes -->

- [ ] ✅ **API Documentation**: Updated API documentation (if applicable)
- [ ] ✅ **User Documentation**: Updated user-facing documentation
- [ ] ✅ **Code Comments**: Added/updated inline code comments
- [ ] ✅ **README Updates**: Updated relevant README files
- [ ] ✅ **CHANGELOG**: Added entry to CHANGELOG.md

### Documentation Changes

<!-- List specific documentation changes -->

- 
- 

## Breaking Changes

<!-- If this introduces breaking changes, describe them -->

### Breaking Change Details

- [ ] This PR introduces breaking changes
- [ ] Migration guide provided
- [ ] Deprecation warnings added (for gradual migration)
- [ ] Version bump required

**Breaking Changes:**
- 

**Migration Path:**
- 

## Security Considerations

<!-- Address any security implications -->

- [ ] ✅ **Security Review**: Changes reviewed for security implications
- [ ] ✅ **No Secrets**: No API keys, passwords, or secrets in code
- [ ] ✅ **Input Validation**: Proper input validation implemented
- [ ] ✅ **Healthcare Security**: Healthcare-specific security considerations addressed

### Security Changes

<!-- Describe any security-related changes -->

- 

## Performance Impact

<!-- Describe any performance implications -->

- [ ] ✅ **Performance Tested**: Performance impact evaluated
- [ ] ✅ **Benchmarks**: Benchmarks run (if applicable)
- [ ] ✅ **Memory Usage**: Memory usage considered
- [ ] ✅ **Database Impact**: Database performance considered (if applicable)

### Performance Notes

<!-- Describe performance impact -->

- 

## Deployment Considerations

<!-- Consider deployment and operational aspects -->

- [ ] Database migrations required
- [ ] Configuration changes required
- [ ] Environment variable changes
- [ ] Third-party service changes
- [ ] Backward compatibility maintained

### Deployment Notes

<!-- Describe deployment considerations -->

- 

## Screenshots/Examples

<!-- Include screenshots or code examples if helpful -->

### Before

<!-- Show current behavior -->

### After

<!-- Show new behavior -->

### Code Examples

```python
# Example usage of new functionality

```

## Additional Notes

<!-- Any additional information for reviewers -->

### Review Focus Areas

<!-- Highlight specific areas that need attention -->

- 
- 

### Known Issues

<!-- List any known issues or limitations -->

- 
- 

### Future Work

<!-- Describe any follow-up work needed -->

- 
- 

## Checklist

<!-- Final checklist before submission -->

### Pre-Submission Checklist

- [ ] 🔍 **Self-Review**: I have performed a self-review of my code
- [ ] 📝 **Clear Description**: PR description clearly explains what and why
- [ ] 🧪 **Tests Pass**: All tests pass locally
- [ ] 📚 **Documentation**: Documentation updated for user-facing changes
- [ ] 🔒 **No PHI**: No real patient data or PHI included
- [ ] 🏥 **Healthcare Compliant**: Healthcare requirements considered
- [ ] 🎯 **Focused**: PR addresses a single concern/feature
- [ ] 📋 **Issue Linked**: Related issues are linked

### Code Quality Checklist

- [ ] ✨ **Linting**: `uv run ruff check` passes
- [ ] 🔍 **Type Checking**: `uv run pyright` passes
- [ ] 🎨 **Formatting**: `uv run ruff format` applied
- [ ] 🧪 **Tests**: `uv run pytest` passes
- [ ] 📖 **Docstrings**: All public functions documented

### Healthcare Checklist

- [ ] 🏥 **Clinical Accuracy**: Healthcare information is accurate
- [ ] 🔒 **Privacy Protected**: No real patient data exposed
- [ ] 📋 **FHIR Compliant**: Maintains FHIR standards (if applicable)
- [ ] ⚖️ **Regulatory Aware**: Regulatory requirements considered

---

**By submitting this PR, I confirm that:**

- [ ] I have read and agree to follow the project's Code of Conduct
- [ ] I understand this is a public repository and will not share sensitive information
- [ ] I have the right to submit this code and agree to the project license
- [ ] I understand that this PR may be publicly visible and discussed 