#!/usr/bin/env python3
"""
Quick validation script to check if HACS packages are ready for PyPI publishing.
"""

import tomllib
from pathlib import Path
from typing import Dict, Any


def check_pyproject_toml(path: Path) -> Dict[str, Any]:
    """Check a pyproject.toml file for PyPI readiness."""
    results = {
        "path": str(path),
        "exists": path.exists(),
        "errors": [],
        "warnings": [],
        "metadata": {},
    }

    if not path.exists():
        results["errors"].append("pyproject.toml not found")
        return results

    try:
        with open(path, "rb") as f:
            data = tomllib.load(f)

        project = data.get("project", {})
        results["metadata"] = project

        # Required fields
        required_fields = ["name", "version", "description", "authors"]
        for field in required_fields:
            if field not in project:
                results["errors"].append(f"Missing required field: {field}")

        # Check license
        if "license" not in project:
            results["errors"].append("Missing license field")
        elif isinstance(project["license"], dict):
            if "text" not in project["license"]:
                results["errors"].append("License must specify text")

        # Check authors format
        if "authors" in project:
            authors = project["authors"]
            if not isinstance(authors, list) or not authors:
                results["errors"].append("Authors must be a non-empty list")
            else:
                for author in authors:
                    if not isinstance(author, dict) or "name" not in author:
                        results["errors"].append("Each author must have a name")

        # Check URLs
        if "urls" not in project:
            results["warnings"].append("No project URLs specified")
        else:
            urls = project["urls"]
            expected_urls = ["Homepage", "Repository", "Bug Tracker"]
            for url in expected_urls:
                if url not in urls:
                    results["warnings"].append(f"Missing URL: {url}")

        # Check classifiers
        if "classifiers" not in project:
            results["warnings"].append("No classifiers specified")

        # Check keywords
        if "keywords" not in project:
            results["warnings"].append("No keywords specified")

        # Check README
        readme_path = path.parent / "README.md"
        if not readme_path.exists():
            results["warnings"].append("README.md not found")

    except Exception as e:
        results["errors"].append(f"Error parsing pyproject.toml: {e}")

    return results


def main():
    """Main validation function."""
    print("🔍 HACS PyPI Readiness Validation")
    print("=" * 50)

    # Define packages to check
    packages = [
        ("Main Package", Path("pyproject.toml")),
        ("hacs-core", Path("packages/hacs-core/pyproject.toml")),
        ("hacs-models", Path("packages/hacs-models/pyproject.toml")),
        ("hacs-fhir", Path("packages/hacs-fhir/pyproject.toml")),
        ("hacs-tools", Path("packages/hacs-tools/pyproject.toml")),
        ("hacs-api", Path("packages/hacs-api/pyproject.toml")),
        ("hacs-cli", Path("packages/hacs-cli/pyproject.toml")),
    ]

    all_good = True

    for package_name, pyproject_path in packages:
        print(f"\n📦 {package_name}")
        print("-" * 30)

        results = check_pyproject_toml(pyproject_path)

        if results["errors"]:
            all_good = False
            print("❌ ERRORS:")
            for error in results["errors"]:
                print(f"   • {error}")

        if results["warnings"]:
            print("⚠️  WARNINGS:")
            for warning in results["warnings"]:
                print(f"   • {warning}")

        if not results["errors"] and not results["warnings"]:
            print("✅ All checks passed")
        elif not results["errors"]:
            print("✅ No errors (warnings only)")

        # Show key metadata
        if results["metadata"]:
            metadata = results["metadata"]
            if "name" in metadata:
                print(f"   Name: {metadata['name']}")
            if "version" in metadata:
                print(f"   Version: {metadata['version']}")
            if "authors" in metadata and metadata["authors"]:
                author = metadata["authors"][0]
                print(f"   Author: {author.get('name', 'Unknown')}")

    print("\n" + "=" * 50)
    if all_good:
        print("🎉 All packages are ready for PyPI publishing!")
        print("\nNext steps:")
        print("1. Run: python publish.py --check")
        print("2. Run: python publish.py --test")
        print("3. Run: python publish.py --production")
    else:
        print("❌ Some packages have errors that need to be fixed")
        print("\nFix the errors above before publishing.")

    print("\n📚 For detailed publishing instructions, see PUBLISHING.md")


if __name__ == "__main__":
    main()
