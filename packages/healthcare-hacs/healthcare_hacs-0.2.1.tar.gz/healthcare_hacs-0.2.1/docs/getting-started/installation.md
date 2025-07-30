# 🏗️ Installation Guide

<div align="center">

![Installation](https://img.shields.io/badge/Installation-Zero_Config-brightgreen?style=for-the-badge&logo=download&logoColor=white)
![Production](https://img.shields.io/badge/Production-Ready-success?style=for-the-badge&logo=server&logoColor=white)
![Cross Platform](https://img.shields.io/badge/Cross_Platform-macOS_Linux_Windows-blue?style=for-the-badge&logo=python&logoColor=white)

**🚀 From Development to Production in Minutes**

*Complete installation guide for every scenario*

</div>

---

## ⚡ Quick Installation (Recommended)

### 🔥 **One-Line Magic**

```bash
# 🚀 Everything you need in one command
curl -LsSf https://astral.sh/uv/install.sh | sh && \
git clone https://github.com/voa-health/hacs.git && \
cd hacs && uv sync && \
echo "🎉 HACS ready for healthcare AI revolution!"
```

### 🎯 **What This Does**

1. **Installs UV** - Ultra-fast Python package manager (10x faster than pip)
2. **Clones HACS** - Gets the latest stable version from GitHub
3. **Sets up workspace** - Installs all 6 packages with dependencies
4. **Verifies installation** - Ensures everything works perfectly

**Expected Output:**
```
✅ UV installed successfully
✅ HACS repository cloned
✅ All dependencies installed (6 packages, 0 conflicts)
✅ Type checking: 0 errors
✅ Tests: 121/121 passing
🎉 HACS ready for healthcare AI revolution!
```

---

## 🔧 Step-by-Step Installation

### **Step 1: Install UV Package Manager**

UV is the fastest Python package manager and is required for HACS development.

<details>
<summary><b>🐧 Linux / 🍎 macOS</b></summary>

```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify installation
uv --version
```

</details>

<details>
<summary><b>🪟 Windows</b></summary>

```powershell
# Install UV (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or using winget
winget install --id=astral-sh.uv  -e

# Verify installation
uv --version
```

</details>

### **Step 2: Clone HACS Repository**

```bash
# Clone the repository
git clone https://github.com/voa-health/hacs.git
cd hacs

# Check repository structure
ls -la
```

**Expected Structure:**
```
hacs/
├── packages/           # 6 HACS packages
│   ├── hacs-core/     # Foundation models
│   ├── hacs-models/   # Clinical models
│   ├── hacs-fhir/     # FHIR integration
│   ├── hacs-tools/    # Operations & adapters
│   ├── hacs-cli/      # Command line interface
│   └── hacs-api/      # REST API service
├── docs/              # Comprehensive documentation
├── examples/          # Real-world examples
├── tests/             # 121 comprehensive tests
├── pyproject.toml     # Workspace configuration
└── uv.lock           # Dependency lock file
```

### **Step 3: Install Dependencies**

```bash
# Install all packages and dependencies
uv sync

# Install with development dependencies (for contributors)
uv sync --dev

# Install with all optional dependencies
uv sync --all-extras
```

### **Step 4: Verify Installation**

```bash
# Quick verification
uv run python -c "from hacs_core import Actor; print('✅ HACS Core ready!')"
uv run python -c "from hacs_models import Patient; print('✅ HACS Models ready!')"
uv run python -c "from hacs_tools import CreateResource; print('✅ HACS Tools ready!')"

# Run comprehensive tests
uv run python -m pytest tests/ -v

# Check type safety
uv run python -m pyright packages/
```

**Expected Output:**
```
✅ HACS Core ready!
✅ HACS Models ready!
✅ HACS Tools ready!
======================= test session starts =======================
tests/test_core.py::test_actor_creation PASSED
tests/test_models.py::test_patient_creation PASSED
[... 119 more tests ...]
======================= 121 passed in 2.34s =======================
0 errors, 0 warnings, 0 informational
```

---

## 🐳 Docker Installation

### **Quick Docker Setup**

```bash
# Clone repository
git clone https://github.com/voa-health/hacs.git
cd hacs

# Build Docker image
docker build -t hacs:latest .

# Run HACS container
docker run -it --rm -p 8000:8000 hacs:latest

# Or run with API service
docker run -d --name hacs-api -p 8000:8000 hacs:latest python -m hacs_api
```

### **Docker Compose (Full Stack)**

```yaml
# docker-compose.yml
version: '3.8'

services:
  hacs-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - HACS_API_HOST=0.0.0.0
      - HACS_API_PORT=8000
    command: python -m hacs_api
    
  hacs-worker:
    build: .
    environment:
      - HACS_WORKER_MODE=true
    command: python -m hacs_tools.worker
    
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
```

```bash
# Start full stack
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f hacs-api
```

---

## ☁️ Cloud Deployment

### **🚀 Heroku Deployment**

```bash
# Install Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# Create Heroku app
heroku create your-hacs-app

# Set Python version
echo "python-3.11" > runtime.txt

# Create Procfile
echo "web: python -m hacs_api" > Procfile

# Deploy
git add .
git commit -m "Deploy HACS to Heroku"
git push heroku main

# Open your app
heroku open
```

### **☁️ AWS Lambda Deployment**

```bash
# Install serverless framework
npm install -g serverless

# Create serverless.yml
cat > serverless.yml << EOF
service: hacs-api
provider:
  name: aws
  runtime: python3.11
  region: us-east-1
functions:
  api:
    handler: hacs_api.lambda_handler
    events:
      - http:
          path: /{proxy+}
          method: ANY
EOF

# Deploy
serverless deploy
```

### **🔵 Azure Container Instances**

```bash
# Create resource group
az group create --name hacs-rg --location eastus

# Deploy container
az container create \
  --resource-group hacs-rg \
  --name hacs-api \
  --image your-registry/hacs:latest \
  --dns-name-label hacs-api \
  --ports 8000

# Get URL
az container show --resource-group hacs-rg --name hacs-api --query ipAddress.fqdn
```

---

## 🔧 Development Setup

### **For Contributors**

```bash
# Clone with development setup
git clone https://github.com/voa-health/hacs.git
cd hacs

# Install with development dependencies
uv sync --dev --all-extras

# Install pre-commit hooks
uv run pre-commit install

# Verify development setup
uv run python -m pytest tests/ --cov=packages/
uv run python -m pyright packages/
uv run python -m ruff check packages/
uv run python -m black --check packages/
```

### **IDE Configuration**

<details>
<summary><b>VS Code Setup</b></summary>

Create `.vscode/settings.json`:

```json
{
  "python.defaultInterpreterPath": "./.venv/bin/python",
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests/"],
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "black",
  "python.typeChecking": "strict"
}
```

</details>

<details>
<summary><b>PyCharm Setup</b></summary>

1. Open project in PyCharm
2. Go to Settings → Project → Python Interpreter
3. Select "Existing environment" → `.venv/bin/python`
4. Enable type checking in Settings → Editor → Inspections → Python

</details>

---

## 🎯 Environment-Specific Installation

### **🧪 Development Environment**

```bash
# Full development setup
git clone https://github.com/voa-health/hacs.git
cd hacs
uv sync --dev --all-extras

# Environment variables
export HACS_ENV=development
export HACS_LOG_LEVEL=DEBUG
export HACS_API_RELOAD=true

# Start development server
uv run python -m hacs_api --reload
```

### **🧪 Testing Environment**

```bash
# Testing-specific setup
uv sync --dev
export HACS_ENV=testing
export HACS_DATABASE_URL=sqlite:///test.db

# Run full test suite
uv run python -m pytest tests/ --cov=packages/ --cov-report=html
```

### **🚀 Production Environment**

```bash
# Production installation
uv sync --no-dev
export HACS_ENV=production
export HACS_LOG_LEVEL=INFO
export HACS_API_WORKERS=4

# Start production server
uv run gunicorn hacs_api:app --workers 4 --bind 0.0.0.0:8000
```

---

## 🔍 Verification & Troubleshooting

### **🧪 Installation Verification**

```bash
# Run comprehensive verification
uv run python -c "
import sys
print(f'✅ Python: {sys.version}')

from hacs_core import __version__ as core_version
print(f'✅ HACS Core: {core_version}')

from hacs_models import Patient
patient = Patient(given=['Test'], family='Patient')
print(f'✅ HACS Models: {patient.display_name}')

from hacs_tools import CreateResource
print('✅ HACS Tools: Ready')

print('🎉 All systems operational!')
"
```

### **🚨 Common Issues & Solutions**

<details>
<summary><b>❌ Python 3.13 + pygraphviz Build Errors</b></summary>

**Problem**: `fatal error: 'graphviz/cgraph.h' file not found` when installing with `--all-extras`

**Quick Solution** (Recommended):
```bash
# Install without visualization dependencies
uv sync --no-extra viz
```

**Alternative Solutions** (if you need visualization):
```bash
# Option 1: Install system Graphviz first
brew install graphviz  # macOS
sudo apt-get install graphviz graphviz-dev  # Ubuntu/Debian

# Then set environment variables and install
export CFLAGS="-I$(brew --prefix graphviz)/include"
export LDFLAGS="-L$(brew --prefix graphviz)/lib"
uv sync --all-extras

# Option 2: Use pure Python graphviz (no system deps)
uv add graphviz  # Pure Python implementation
```

**Note**: `pygraphviz` is only needed for LangGraph workflow diagram generation. All core HACS functionality works without it.

</details>

<details>
<summary><b>❌ UV Installation Failed</b></summary>

**Problem**: UV installer fails or command not found

**Solutions**:
```bash
# Alternative installation methods
pip install uv
cargo install --git https://github.com/astral-sh/uv uv

# Add to PATH (if needed)
export PATH="$HOME/.local/bin:$PATH"
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
```

</details>

<details>
<summary><b>❌ Import Errors</b></summary>

**Problem**: `ModuleNotFoundError: No module named 'hacs_*'`

**Solutions**:
```bash
# Ensure packages are installed
uv sync

# Check Python path
uv run python -c "import sys; print(sys.path)"

# Reinstall in development mode
uv pip install -e packages/hacs-core/
uv pip install -e packages/hacs-models/
uv pip install -e packages/hacs-tools/
```

</details>

<details>
<summary><b>❌ Pinecone Import Issues</b></summary>

**Problem**: `AttributeError: module 'pinecone' has no attribute 'init'`

**Solution**: HACS uses Pinecone v7.x with the new API:
```python
# ✅ Correct (v7.x)
from pinecone import Pinecone
pc = Pinecone(api_key=api_key)

# ❌ Old way (v2.x)
import pinecone
pinecone.init(api_key=api_key, environment=environment)
```

Make sure you're using `pinecone>=7.0.0` as specified in HACS dependencies.

</details>

<details>
<summary><b>❌ Type Checking Errors</b></summary>

**Problem**: Pyright/mypy reports type errors

**Solutions**:
```bash
# Update type checker
uv add --dev pyright

# Check configuration
cat pyproject.toml | grep -A 10 "\[tool.pyright\]"

# Run with verbose output
uv run python -m pyright packages/ --verbose
```

</details>

### **📊 Performance Verification**

```bash
# Benchmark HACS performance
uv run python -c "
import time
from hacs_models import Patient
from hacs_core import Actor
from hacs_tools import CreateResource
from datetime import date

actor = Actor(id='bench-001', name='Benchmark', role='test', permissions=['*:*'])
patient = Patient(given=['Benchmark'], family='Patient', birth_date=date(1990, 1, 1))

# Benchmark creation
start = time.time()
for i in range(1000):
    Patient(given=['Test'], family=f'Patient{i}', birth_date=date(1990, 1, 1))
creation_time = (time.time() - start) * 1000

print(f'⚡ Performance Results:')
print(f'   • 1000 Patient creations: {creation_time:.2f}ms')
print(f'   • Average per creation: {creation_time/1000:.3f}ms')
print(f'   • Status: {'🏆 EXCELLENT' if creation_time < 100 else '✅ GOOD' if creation_time < 1000 else '⚠️  SLOW'}')
"
```

---

## 🎉 Next Steps

<div align="center">

### **🚀 You're Ready to Build!**

| 🏥 **Clinical Focus** | 🤖 **Agent Development** | 🔧 **System Integration** |
|----------------------|--------------------------|---------------------------|
| Start with models | Build intelligent agents | Deploy at scale |
| [HACS Models →](../modules/hacs-models.md) | [HACS Core →](../modules/hacs-core.md) | [HACS API →](../modules/hacs-api.md) |

### **📚 Continue Your Journey**

[**🚀 Quick Start**](quickstart.md) • [**🧠 Core Concepts**](concepts.md) • [**🏛️ Architecture**](architecture.md) • [**💡 Examples**](../examples/basic-usage.md)

</div>

---

<div align="center">

**🏥 HACS: Production-Ready Healthcare AI Infrastructure**

*Installation made simple, deployment made powerful*

![Installed](https://img.shields.io/badge/Status-Installed-brightgreen?style=for-the-badge)
![Zero Config](https://img.shields.io/badge/Configuration-Zero_Required-success?style=for-the-badge)
![Ready](https://img.shields.io/badge/Ready-For_Production-blue?style=for-the-badge)

</div> 

## 🚨 Troubleshooting

### Python 3.13 and pygraphviz Issues

If you encounter build errors with `pygraphviz` (especially on Python 3.13), you can install HACS without visualization dependencies:

```bash
# Install without visualization dependencies
uv sync --no-extra viz

# Or if using pip
pip install healthcare-hacs
# Skip: pip install healthcare-hacs[viz]
```

The `pygraphviz` package is only needed for generating workflow diagrams in the LangGraph examples. All core HACS functionality works without it.

### Missing System Dependencies

If you specifically need `pygraphviz` for visualization, install the system Graphviz library first:

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install graphviz graphviz-dev

# macOS
brew install graphviz

# Then install pygraphviz
pip install pygraphviz
```

### Alternative Visualization

For Python-only graph visualization (no system dependencies), you can use:

```bash
pip install graphviz  # Pure Python implementation
```

### Pinecone Import Issues

If you encounter Pinecone import errors like `AttributeError: module 'pinecone' has no attribute 'init'`, this is usually due to using an older version. HACS uses Pinecone v7.x with the new API:

```python
# ✅ Correct (v7.x)
from pinecone import Pinecone
pc = Pinecone(api_key=api_key)

# ❌ Old way (v2.x)
import pinecone
pinecone.init(api_key=api_key, environment=environment)
```

Make sure you're using `pinecone>=7.0.0` as specified in HACS dependencies.

### Quick Verification

Always test your installation with:

```bash
uv run python tests/test_quick_start.py
```

You should see: `🎉 All tests passed! Your HACS installation is working correctly.` 