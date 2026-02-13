#!/usr/bin/env python3
"""
ScholarAI Backend - Verify Test Suite

Simple script to verify test structure and imports work correctly.
"""

import sys
import os
from pathlib import Path


def check_file_exists(filepath):
    """Check if file exists."""
    path = Path(filepath)
    if path.exists():
        print(f"  ✅ {filepath}")
        return True
    else:
        print(f"  ❌ {filepath} NOT FOUND")
        return False


def check_imports(module_name):
    """Check if module can be imported."""
    try:
        __import__(module_name)
        print(f"  ✅ {module_name}")
        return True
    except ImportError as e:
        print(f"  ❌ {module_name}: {e}")
        return False


def main():
    """Run verification checks."""
    print("\n" + "="*60)
    print("ScholarAI Backend - Test Suite Verification")
    print("="*60 + "\n")

    backend_dir = Path(__file__).parent

    print("📁 Checking test structure...")
    print("-" * 60)

    checks = [
        # Test infrastructure
        "backend/tests/__init__.py",
        "backend/tests/test_models.py",
        "backend/tests/test_routes.py",
        "backend/conftest.py",
        "backend/pytest.ini",
        "backend/run_tests.py",
        "backend/TEST_SUITE_SUMMARY.md",

        # Model files
        "backend/models/__init__.py",
        "backend/models/user.py",
        "backend/models/project.py",
        "backend/models/settings.py",
        "backend/models/favorites.py",

        # Route files
        "backend/routes/__init__.py",
        "backend/routes/auth.py",
        "backend/routes/papers.py",
        "backend/routes/ai.py",
        "backend/routes/projects.py",
        "backend/routes/favorites.py",
        "backend/routes/settings.py",
    ]

    files_found = sum(check_file_exists(backend_dir / Path(p).relative_to(backend_dir.parent.parent)) for p in checks)

    print(f"\n📊 Test Structure: {files_found}/{len(checks)} files found")

    print("\n🔍 Checking module imports...")
    print("-" * 60)

    # Add backend to path
    sys.path.insert(0, str(backend_dir))

    import_checks = [
        "pytest",
        "models.user",
        "models.project",
        "models.settings",
        "models.favorites",
    ]

    modules_found = sum(check_imports(m) for m in import_checks)

    print(f"\n📦 Modules: {modules_found}/{len(import_checks)} can be imported")

    print("\n" + "="*60)
    if files_found == len(checks) and modules_found == len(import_checks):
        print("✅ Test suite is ready!")
        print("="*60)
        print("\nRun tests with:")
        print("  pytest tests/ -v --cov")
        print("  python run_tests.py --coverage")
        return 0
    else:
        print("⚠️  Test suite has issues!")
        print("="*60)
        return 1


if __name__ == '__main__':
    sys.exit(main())
