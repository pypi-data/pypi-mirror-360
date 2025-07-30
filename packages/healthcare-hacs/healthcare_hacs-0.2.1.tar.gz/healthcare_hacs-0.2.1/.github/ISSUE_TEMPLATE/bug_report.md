---
name: Bug Report
about: Create a report to help us improve HACS
title: '[BUG] '
labels: ['bug', 'needs-triage']
assignees: ''
---

## 🐛 Bug Description

**Clear and concise description of the bug**

## 🔄 Reproduction Steps

Steps to reproduce the behavior:

1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Minimal code example:**
```python
# Provide minimal code that reproduces the issue
from hacs_core import Actor

# Your code here
```

## 🎯 Expected Behavior

**What you expected to happen**

## 📊 Actual Behavior

**What actually happened**

## 🖥️ Environment

**System Information:**
- OS: [e.g., macOS 14.0, Ubuntu 22.04, Windows 11]
- Python Version: [e.g., 3.11.0]
- HACS Version: [e.g., 0.1.0]
- UV Version: [e.g., 0.4.0] (if using UV)

**Package Versions:**
```bash
# Output of: uv run pip list | grep hacs
# Or relevant package versions
```

## 🏥 Healthcare Context

**Clinical relevance and impact (if applicable):**
- Does this affect patient data handling?
- Are there clinical workflow implications?
- FHIR compliance concerns?

## 📝 Additional Context

**Add any other context about the problem here:**
- Screenshots
- Log output
- Related issues
- Workarounds attempted

## 🔍 Error Logs

**Relevant error messages or stack traces:**
```
Paste error logs here
```

## ✅ Checklist

- [ ] I have searched existing issues to ensure this is not a duplicate
- [ ] I have provided a minimal code example that reproduces the issue
- [ ] I have included relevant environment information
- [ ] I have considered any healthcare/clinical implications
- [ ] I have checked the [documentation](https://github.com/voa-health/hacs/docs) for solutions

## 🏷️ Labels

**Please add relevant labels:**
- Component: `core`, `models`, `fhir`, `tools`, `cli`, `api`
- Priority: `low`, `medium`, `high`, `critical`
- Type: `bug`, `regression`, `performance`
- Healthcare: `fhir-compliance`, `clinical-safety`, `privacy` 