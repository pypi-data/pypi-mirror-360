#!/usr/bin/env python3
"""
HACS PyPI Publishing Script

This script helps publish all HACS packages to PyPI with proper validation
and dependency management.

Usage:
    python publish.py --help
    python publish.py --check         # Validate packages without publishing
    python publish.py --test          # Publish to TestPyPI
    python publish.py --production     # Publish to PyPI (production)
    python publish.py --package hacs-core  # Publish specific package
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List, Optional
import glob

# Package order for publishing (dependencies first)
PACKAGE_ORDER = [
    "hacs-core",
    "hacs-models",
    "hacs-fhir",
    "hacs-tools",
    "hacs-api",
    "hacs-cli",
    "hacs",  # Main package last
]

PACKAGE_PATHS = {
    "hacs-core": "packages/hacs-core",
    "hacs-models": "packages/hacs-models",
    "hacs-fhir": "packages/hacs-fhir",
    "hacs-tools": "packages/hacs-tools",
    "hacs-api": "packages/hacs-api",
    "hacs-cli": "packages/hacs-cli",
    "hacs": ".",  # Main workspace
}


def run_command(cmd: List[str], cwd: Optional[Path] = None) -> bool:
    """Run a command and return True if successful."""
    try:
        # Handle glob patterns in commands
        expanded_cmd = []
        for arg in cmd:
            if "*" in arg:
                # Expand glob patterns
                expanded = glob.glob(arg)
                if expanded:
                    expanded_cmd.extend(expanded)
                else:
                    expanded_cmd.append(arg)
            else:
                expanded_cmd.append(arg)

        result = subprocess.run(
            expanded_cmd, check=True, capture_output=True, text=True, cwd=cwd
        )
        print(f"✅ {' '.join(cmd)}")
        if result.stdout:
            print(f"   Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {' '.join(cmd)}")
        print(f"   Error: {e.stderr.strip()}")
        return False


def validate_package(package_name: str) -> bool:
    """Validate a package configuration."""
    print(f"\n📦 Validating {package_name}...")

    package_path = Path(PACKAGE_PATHS[package_name])
    if not package_path.exists():
        print(f"❌ Package path does not exist: {package_path}")
        return False

    pyproject_path = package_path / "pyproject.toml"
    if not pyproject_path.exists():
        print(f"❌ pyproject.toml not found: {pyproject_path}")
        return False

    # Check if README exists
    readme_path = package_path / "README.md"
    if not readme_path.exists():
        print(f"⚠️  README.md not found: {readme_path}")

    # Clean previous builds
    root_dist = Path("dist")
    if root_dist.exists():
        run_command(["rm", "-rf", "dist"])

    # Validate package can be built
    if not run_command(["uv", "build"], cwd=package_path):
        return False

    # Check package metadata - files are in root dist directory
    if not run_command(["uv", "run", "python", "-m", "twine", "check", "dist/*"]):
        return False

    print(f"✅ {package_name} validation passed")
    return True


def build_package(package_name: str) -> bool:
    """Build a package."""
    print(f"\n🔨 Building {package_name}...")

    package_path = Path(PACKAGE_PATHS[package_name])

    # Clean previous builds
    root_dist = Path("dist")
    if root_dist.exists():
        run_command(["rm", "-rf", "dist"])

    # Build package
    if not run_command(["uv", "build"], cwd=package_path):
        return False

    print(f"✅ {package_name} built successfully")
    return True


def publish_package(package_name: str, test: bool = False) -> bool:
    """Publish a package to PyPI or TestPyPI."""
    target = "TestPyPI" if test else "PyPI"
    print(f"\n🚀 Publishing {package_name} to {target}...")

    # Determine repository URL
    if test:
        repo_args = ["--repository", "testpypi"]
    else:
        repo_args = []

    # Publish using twine - files are in root dist directory
    cmd = ["uv", "run", "python", "-m", "twine", "upload"] + repo_args + ["dist/*"]
    if not run_command(cmd):
        return False

    print(f"✅ {package_name} published to {target}")
    return True


def check_prerequisites() -> bool:
    """Check if all required tools are installed."""
    print("🔍 Checking prerequisites...")

    tools = ["uv", "python"]
    for tool in tools:
        if not run_command(["which", tool]):
            print(f"❌ {tool} not found. Please install it first.")
            return False

    # Check if twine is available
    if not run_command(["uv", "run", "python", "-c", "import twine"]):
        print("📦 Installing twine...")
        if not run_command(["uv", "add", "--dev", "twine"]):
            return False

    print("✅ All prerequisites satisfied")
    return True


def main():
    parser = argparse.ArgumentParser(description="Publish HACS packages to PyPI")
    parser.add_argument("--check", action="store_true", help="Only validate packages")
    parser.add_argument("--test", action="store_true", help="Publish to TestPyPI")
    parser.add_argument("--production", action="store_true", help="Publish to PyPI")
    parser.add_argument("--package", help="Publish specific package only")
    parser.add_argument(
        "--skip-validation", action="store_true", help="Skip validation step"
    )

    args = parser.parse_args()

    if not any([args.check, args.test, args.production]):
        print("❌ Please specify --check, --test, or --production")
        sys.exit(1)

    if args.test and args.production:
        print("❌ Cannot specify both --test and --production")
        sys.exit(1)

    # Check prerequisites
    if not check_prerequisites():
        sys.exit(1)

    # Determine packages to process
    if args.package:
        if args.package not in PACKAGE_PATHS:
            print(f"❌ Unknown package: {args.package}")
            print(f"Available packages: {', '.join(PACKAGE_PATHS.keys())}")
            sys.exit(1)
        packages = [args.package]
    else:
        packages = PACKAGE_ORDER

    print(f"\n📋 Processing packages: {', '.join(packages)}")

    # Validation phase
    if not args.skip_validation:
        print("\n" + "=" * 50)
        print("🔍 VALIDATION PHASE")
        print("=" * 50)

        for package in packages:
            if not validate_package(package):
                print(f"❌ Validation failed for {package}")
                sys.exit(1)

        print("\n✅ All packages validated successfully!")

    if args.check:
        print("\n🎉 Validation complete. Packages are ready for publishing!")
        return

    # Build phase
    print("\n" + "=" * 50)
    print("🔨 BUILD PHASE")
    print("=" * 50)

    for package in packages:
        if not build_package(package):
            print(f"❌ Build failed for {package}")
            sys.exit(1)

    print("\n✅ All packages built successfully!")

    # Publishing phase
    print("\n" + "=" * 50)
    print("🚀 PUBLISHING PHASE")
    print("=" * 50)

    if args.test:
        print("📡 Publishing to TestPyPI...")
        print("ℹ️  You can install from TestPyPI with:")
        print("   pip install --index-url https://test.pypi.org/simple/ hacs")
    else:
        print("📡 Publishing to PyPI...")
        print("⚠️  This will make packages publicly available!")

        # Confirm production publishing
        response = input("Are you sure you want to publish to PyPI? (yes/no): ")
        if response.lower() != "yes":
            print("❌ Publishing cancelled")
            sys.exit(1)

    for package in packages:
        if not publish_package(package, test=args.test):
            print(f"❌ Publishing failed for {package}")
            sys.exit(1)

    target = "TestPyPI" if args.test else "PyPI"
    print(f"\n🎉 All packages published successfully to {target}!")

    if args.production:
        print("\n📦 Installation commands:")
        print("   pip install hacs                    # Full HACS suite")
        print("   pip install hacs-core               # Core models only")
        print("   pip install hacs-models             # Clinical models")
        print("   pip install hacs-fhir               # FHIR integration")
        print("   pip install hacs-tools              # CRUD tools")
        print("   pip install hacs-api                # FastAPI service")
        print("   pip install hacs-cli                # CLI interface")


if __name__ == "__main__":
    main()
