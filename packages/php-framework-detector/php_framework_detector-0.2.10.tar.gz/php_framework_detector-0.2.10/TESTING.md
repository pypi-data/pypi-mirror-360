# Testing Guide

This document describes how to run tests for the PHP Framework Detector project.

## Overview

The project uses modern Python testing tools and practices:

- **pytest**: Main testing framework
- **pytest-asyncio**: For testing async code
- **pytest-cov**: For code coverage reporting
- **pytest-mock**: For mocking in tests
- **mypy**: For static type checking
- **ruff**: For linting and code formatting
- **black**: For code formatting
- **isort**: For import sorting

## Quick Start

### Run All Tests

```bash
# Install test dependencies
pip install -e .[test,dev]

# Run all tests with coverage
python run_tests.py
```

### Run Tests Manually

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=php_framework_detector --cov-report=html

# Run specific test file
pytest tests/test_core_models.py

# Run specific test class
pytest tests/test_core_models.py::TestFrameworkType

# Run specific test method
pytest tests/test_core_models.py::TestFrameworkType::test_enum_creation
```

## Test Structure

```
tests/
├── conftest.py              # Pytest configuration and fixtures
├── test_core_models.py      # Tests for data models
├── test_exceptions.py       # Tests for custom exceptions
├── test_factory.py          # Tests for factory class
├── test_detector.py         # Tests for base detector class
├── test_frameworks.py       # Tests for specific framework detectors
├── test_framework_type_enum.py  # Tests for framework type enum
└── simple_enum_test.py      # Legacy enum tests
```

## Test Categories

### Unit Tests
- Test individual components in isolation
- Use mocks for dependencies
- Fast execution
- Marked with `@pytest.mark.unit` (optional)

### Integration Tests
- Test component interactions
- May use real file system
- Slower execution
- Marked with `@pytest.mark.integration`

### Async Tests
- Test async functionality
- Use `@pytest.mark.asyncio` decorator
- Use `AsyncTestCase` base class for complex async tests

### Slow Tests
- Tests that take longer to run
- May involve file I/O or network calls
- Marked with `@pytest.mark.slow`

## Running Different Test Types

```bash
# Run only unit tests
pytest -m "not integration and not slow"

# Run only integration tests
pytest -m integration

# Run only slow tests
pytest -m slow

# Run async tests
pytest -m asyncio
```

## Code Quality Checks

### Linting
```bash
# Run ruff linter
ruff check php_framework_detector tests

# Fix ruff issues
ruff check --fix php_framework_detector tests
```

### Type Checking
```bash
# Run mypy type checker
mypy php_framework_detector

# Run with strict mode
mypy --strict php_framework_detector
```

### Code Formatting
```bash
# Check formatting
black --check php_framework_detector tests
isort --check-only php_framework_detector tests

# Fix formatting
black php_framework_detector tests
isort php_framework_detector tests
```

## Coverage

### Generate Coverage Report
```bash
# Generate HTML coverage report
pytest --cov=php_framework_detector --cov-report=html

# Generate XML coverage report (for CI)
pytest --cov=php_framework_detector --cov-report=xml

# Generate both
pytest --cov=php_framework_detector --cov-report=html --cov-report=xml
```

### Coverage Requirements
- Minimum coverage: 80%
- Coverage reports are generated in `htmlcov/` directory
- XML reports are generated for CI integration

## Test Fixtures

Common test fixtures are defined in `conftest.py`:

- `temp_project_dir`: Temporary directory for testing
- `sample_composer_json`: Sample composer.json content
- `sample_composer_lock`: Sample composer.lock content
- `detection_config`: Default detection configuration
- `laravel_project_files`: Laravel project structure
- `symfony_project_files`: Symfony project structure
- `empty_project_dir`: Empty project directory

## Writing Tests

### Test Naming Convention
- Test files: `test_*.py`
- Test classes: `Test*`
- Test methods: `test_*`

### Example Test Structure
```python
import pytest
from php_framework_detector.core.models import FrameworkType

class TestFrameworkType:
    """Test FrameworkType enum functionality."""
    
    def test_enum_creation(self):
        """Test creating FrameworkType enums."""
        laravel = FrameworkType.LARAVEL
        assert laravel.value == "laravel"
        assert laravel.display_name == "Laravel"
    
    @pytest.mark.asyncio
    async def test_async_functionality(self):
        """Test async functionality."""
        # Async test code here
        result = await some_async_function()
        assert result == expected_value
```

### Using Fixtures
```python
def test_with_fixture(temp_project_dir, sample_composer_json):
    """Test using fixtures."""
    # Use temp_project_dir and sample_composer_json
    composer_file = temp_project_dir / "composer.json"
    composer_file.write_text(json.dumps(sample_composer_json))
    # ... test logic
```

### Mocking
```python
from unittest.mock import MagicMock, patch

def test_with_mock():
    """Test using mocks."""
    with patch('module.function') as mock_func:
        mock_func.return_value = "mocked_result"
        # ... test logic
        mock_func.assert_called_once()
```

## Continuous Integration

The project includes CI configuration that runs:

1. Code quality checks (ruff, black, isort)
2. Type checking (mypy)
3. Unit tests with coverage
4. Integration tests
5. Slow tests (if any)

## Debugging Tests

### Verbose Output
```bash
# Run tests with verbose output
pytest -v

# Run with very verbose output
pytest -vv

# Show local variables on failure
pytest -l
```

### Debug Mode
```bash
# Run with debugger on failure
pytest --pdb

# Run with debugger on first failure
pytest --pdb --maxfail=1
```

### Test Discovery
```bash
# Show which tests would be run
pytest --collect-only

# Show test collection with more detail
pytest --collect-only -v
```

## Performance

### Parallel Execution
```bash
# Run tests in parallel (requires pytest-xdist)
pytest -n auto

# Run with specific number of workers
pytest -n 4
```

### Test Timing
```bash
# Show test timing
pytest --durations=10

# Show slowest tests
pytest --durations=0
```

## Best Practices

1. **Write descriptive test names** that explain what is being tested
2. **Use fixtures** for common setup and teardown
3. **Mock external dependencies** to keep tests fast and reliable
4. **Test both success and failure cases**
5. **Use parametrized tests** for testing multiple scenarios
6. **Keep tests independent** - they should not depend on each other
7. **Use appropriate assertions** - prefer specific assertions over generic ones
8. **Document complex test logic** with comments
9. **Maintain high test coverage** but focus on quality over quantity
10. **Run tests frequently** during development

## Troubleshooting

### Common Issues

1. **Import errors**: Make sure you're in the project root directory
2. **Missing dependencies**: Run `pip install -e .[test,dev]`
3. **Async test failures**: Ensure you're using `@pytest.mark.asyncio`
4. **Type checking errors**: Check that all functions have proper type annotations
5. **Coverage issues**: Make sure you're running tests from the correct directory

### Getting Help

- Check the pytest documentation: https://docs.pytest.org/
- Review existing tests for examples
- Check the project's CI logs for common issues
- Use `pytest --help` for command-line options 