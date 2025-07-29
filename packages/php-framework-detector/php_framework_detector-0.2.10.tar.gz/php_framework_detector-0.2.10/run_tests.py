#!/usr/bin/env python3
"""
Test runner script for PHP Framework Detector.

This script runs all tests and generates coverage reports.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], description: str) -> bool:
    """Run a command and return success status."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print('='*60)
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        return False


def main() -> int:
    """Main test runner function."""
    print("🚀 PHP Framework Detector Test Suite")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path("pyproject.toml").exists():
        print("❌ Error: pyproject.toml not found. Please run from project root.")
        return 1
    
    # Install test dependencies if needed
    print("\n📦 Installing test dependencies...")
    install_cmd = ["uv", "pip", "install", "-e", ".[test,dev]"]
    if not run_command(install_cmd, "Install test dependencies"):
        return 1
    
    # Run linting checks
    print("\n🔍 Running code quality checks...")
    
    # Run ruff
    ruff_cmd = [sys.executable, "-m", "ruff", "check", "php_framework_detector", "tests"]
    if not run_command(ruff_cmd, "Ruff linting"):
        return 1
    
    # Run black check
    black_cmd = [sys.executable, "-m", "black", "--check", "php_framework_detector", "tests"]
    if not run_command(black_cmd, "Black formatting check"):
        return 1
    
    # Run isort check
    isort_cmd = [sys.executable, "-m", "isort", "--check-only", "php_framework_detector", "tests"]
    if not run_command(isort_cmd, "Import sorting check"):
        return 1
    
    # Run type checking
    print("\n🔍 Running type checking...")
    mypy_cmd = [sys.executable, "-m", "mypy", "php_framework_detector"]
    if not run_command(mypy_cmd, "MyPy type checking"):
        return 1
    
    # Run tests
    print("\n🧪 Running tests...")
    
    # Run unit tests
    pytest_cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "-v",
        "--tb=short",
        "--strict-markers",
        "-m", "not integration and not slow"
    ]
    if not run_command(pytest_cmd, "Unit tests"):
        return 1
    
    # Run integration tests (if any)
    pytest_integration_cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "-v",
        "--tb=short",
        "-m", "integration"
    ]
    run_command(pytest_integration_cmd, "Integration tests")
    
    # Run tests with coverage
    print("\n📊 Generating coverage report...")
    coverage_cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "--cov=php_framework_detector",
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov",
        "--cov-report=xml:coverage.xml",
        "--cov-fail-under=80",
        "-v"
    ]
    if not run_command(coverage_cmd, "Coverage report"):
        return 1
    
    # Run slow tests (if any)
    print("\n🐌 Running slow tests...")
    pytest_slow_cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "-v",
        "--tb=short",
        "-m", "slow"
    ]
    run_command(pytest_slow_cmd, "Slow tests")
    
    print("\n" + "="*60)
    print("🎉 All tests completed!")
    print("📁 Coverage report available in: htmlcov/index.html")
    print("📄 Coverage XML available in: coverage.xml")
    print("="*60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 