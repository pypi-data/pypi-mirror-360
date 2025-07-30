# Contributing to HACS

Welcome! 👋 We're excited you want to contribute to HACS. This guide will help you get started, whether you're a healthcare professional, AI developer, or just someone who wants to help.

## 🚀 Quick Start for Contributors

### 1. Set Up Your Development Environment

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR_USERNAME/hacs.git
cd hacs

# Install dependencies
curl -LsSf https://astral.sh/uv/install.sh | sh  # Install uv
uv sync

# Test your setup
uv run python tests/test_quick_start.py
```

If you see "🎉 All tests passed!" you're ready to contribute!

### 2. Find Something to Work On

**New to the project?** Look for issues labeled [`good first issue`](https://github.com/solanovisitor/hacs/labels/good%20first%20issue).

**Have questions?** Use [GitHub Discussions](https://github.com/solanovisitor/hacs/discussions) - we're here to help!

### 3. Make Your Changes

```bash
# Create a new branch
git checkout -b feature/your-feature-name

# Make your changes
# ... edit files ...

# Test your changes
uv run python tests/test_quick_start.py
uv run pytest  # Run all tests (optional)

# Commit your changes
git add .
git commit -m "Add your feature description"
git push origin feature/your-feature-name
```

### 4. Submit a Pull Request

1. Go to your fork on GitHub
2. Click "New Pull Request"
3. Fill out the description
4. Submit!

We'll review your changes and help you get them merged.

## 🎯 Ways to Contribute

### 👩‍⚕️ Healthcare Professionals
- **Review clinical accuracy** of examples and documentation
- **Suggest healthcare workflows** that HACS should support
- **Validate medical terminology** and FHIR compliance
- **Share use cases** from your clinical experience

### 👩‍💻 Developers
- **Fix bugs** and improve code quality
- **Add features** requested by the community
- **Improve tests** and documentation
- **Integrate new AI frameworks** (LangGraph, CrewAI, etc.)

### 📝 Documentation Writers
- **Improve examples** and tutorials
- **Write beginner-friendly guides**
- **Fix typos** and unclear explanations
- **Translate documentation** (future)

### 🧪 Testers
- **Report bugs** you find
- **Test new features** before release
- **Validate on different platforms** (Windows, Mac, Linux)
- **Test with different Python versions**

## 📋 Development Guidelines

### Code Style (Keep It Simple!)

```python
# Good: Clear and simple
def create_patient(name: str, birth_date: str) -> Patient:
    """Create a patient with the given name and birth date."""
    return Patient(
        given=[name.split()[0]],
        family=name.split()[-1],
        birth_date=birth_date
    )

# Avoid: Overly complex
def create_patient_with_advanced_validation_and_error_handling(...):
    # 50 lines of complex logic
```

### Testing (We'll Help You!)

```bash
# Quick test (always run this)
uv run python tests/test_quick_start.py

# Full test suite (optional)
uv run pytest

# Test a specific file
uv run pytest tests/test_models.py
```

**Don't worry if you're new to testing** - we'll help you write tests in the pull request review.

### Healthcare Data Safety 🔒

**NEVER use real patient data.** Always use fake/synthetic data like:

```python
# ✅ Good: Obviously fake data
patient = Patient(
    given=["Test"],
    family="Patient", 
    birth_date="1990-01-01"
)

# ❌ Bad: Could be real data
patient = Patient(
    given=["Sarah"],
    family="Johnson",
    birth_date="1987-03-22"
)
```

## 🐛 Reporting Issues

Found a bug? Here's how to report it:

1. **Check existing issues** first
2. **Use the issue template** on GitHub
3. **Include steps to reproduce** the problem
4. **Share error messages** if any
5. **Mention your environment** (OS, Python version)

### Example Bug Report

```
**What happened?**
When I create a patient with an empty name, the system crashes.

**Steps to reproduce:**
1. Run: `Patient(given=[], family="Doe")`
2. See error

**Expected:** Should show a helpful error message
**Actual:** System crashes with stack trace

**Environment:** 
- OS: macOS 14.0
- Python: 3.11
- HACS: 0.1.0
```

## 🎉 Getting Help

**Stuck? Don't worry!** We're here to help:

- **[GitHub Discussions](https://github.com/solanovisitor/hacs/discussions)** - Ask questions, share ideas
- **[GitHub Issues](https://github.com/solanovisitor/hacs/issues)** - Report bugs, request features
- **Pull Request Comments** - Get help during code review

### Common Questions

**Q: I'm new to healthcare/FHIR. Can I still contribute?**
A: Absolutely! Many contributions don't require healthcare knowledge.

**Q: I'm new to Python. Is this project for me?**
A: Yes! Look for `good first issue` labels and ask for help.

**Q: How do I know if my contribution is valuable?**
A: If it helps you, it probably helps others too. When in doubt, ask!

**Q: I made a mistake in my pull request. What do I do?**
A: No problem! Just push more commits to the same branch and we'll review them.

## 📚 Project Structure (For Reference)

```
hacs/
├── packages/           # The main HACS packages
│   ├── hacs-core/     # Basic models (Actor, Memory, Evidence)
│   ├── hacs-models/   # Healthcare models (Patient, Observation)
│   └── hacs-tools/    # Tools and AI framework adapters
├── docs/              # Documentation
├── examples/          # Usage examples
├── tests/             # Test suite
└── samples/           # Sample data files
```

**You don't need to understand everything!** Focus on the part you're working on.

## ✅ Pull Request Checklist

Before submitting, make sure:

- [ ] **Tests pass**: `uv run python tests/test_quick_start.py`
- [ ] **No real healthcare data**: Only synthetic/fake data
- [ ] **Clear description**: Explain what your change does
- [ ] **One thing at a time**: Keep changes focused

**Don't worry about perfect code** - we'll help you improve it during review!

## 🌟 Recognition

We appreciate all contributors:

- Your name goes in [CONTRIBUTORS.md](CONTRIBUTORS.md)
- Significant contributions get highlighted in release notes
- All contributions show up on your GitHub profile

## 📜 Code of Conduct

Be respectful, inclusive, and helpful. See our [Code of Conduct](CODE_OF_CONDUCT.md) for details.

## 🚨 Security

Found a security issue? **Don't create a public issue.** Email us at: security@hacs-project.org

---

## 💝 Thank You!

Every contribution, no matter how small, makes HACS better for the healthcare AI community. We're grateful for your help in building the future of healthcare AI communication.

**Ready to contribute?** [Find a good first issue](https://github.com/solanovisitor/hacs/labels/good%20first%20issue) or [start a discussion](https://github.com/solanovisitor/hacs/discussions)! 