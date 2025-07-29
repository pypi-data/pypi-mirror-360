# Development Guide

This guide covers development workflows, testing, and CI/CD setup for ES2InfluxDB.

## Development Setup

### Prerequisites

- Python 3.9+
- Node.js (for elasticdump)
- InfluxDB CLI
- uv (recommended) or pip

### Quick Setup

```bash
# Using uv (recommended)
uv sync
uv pip install -e ".[dev]"

# Or using pip
pip install -e ".[dev]"
```

### Using Make Commands

We provide a comprehensive Makefile for common development tasks:

```bash
# See all available commands
make help

# Development setup
make setup-dev

# Code quality
make format          # Format code with black and isort
make lint           # Run linting with flake8
make type-check     # Run type checking with mypy
make security       # Run security checks with bandit and safety

# Testing
make test           # Run tests
make test-cov       # Run tests with coverage
make test-unit      # Run only unit tests
make test-integration # Run only integration tests

# Quality gate (run all checks)
make all-checks     # Format, lint, type-check, test with coverage, security

# Build and publish
make build          # Build package
make clean          # Clean build artifacts
make upload-test    # Upload to TestPyPI
make upload         # Upload to PyPI

# Development cycle
make dev-cycle      # Format, lint, type-check, test (quick cycle)
make ci             # Simulate CI checks
```

## Testing

### Test Structure

```
tests/
├── __init__.py
├── test_config.py       # Configuration loading and validation
├── test_transform.py    # Data transformation functions
└── test_utils.py        # Utility functions and bucket operations
```

### Test Categories

Tests are organized with pytest markers:

- `@pytest.mark.unit` - Fast unit tests
- `@pytest.mark.integration` - Integration tests requiring external services
- `@pytest.mark.slow` - Slow tests

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_config.py

# Run with coverage
pytest --cov=es2influx --cov-report=html

# Run only unit tests
pytest -m unit

# Run excluding slow tests
pytest -m "not slow"

# Run specific test
pytest tests/test_config.py::TestEnvironmentSubstitution::test_substitute_env_variables_with_default -v
```

### Test Configuration

Tests use `pytest.ini` configuration:

```ini
[tool:pytest]
testpaths = tests
addopts = 
    -v
    --tb=short
    --strict-markers
    --strict-config
    --cov=es2influx
    --cov-report=term-missing
    --cov-report=html:htmlcov
    --cov-fail-under=80
```

### Writing Tests

Follow these patterns when writing tests:

```python
import pytest
from unittest.mock import patch, MagicMock
from es2influx.config import MigrationConfig, FieldMapping

class TestFeature:
    """Test class for a specific feature"""
    
    def test_basic_functionality(self):
        """Test basic functionality"""
        # Test implementation
        pass
    
    @patch('es2influx.utils.subprocess.run')
    def test_with_mocking(self, mock_run):
        """Test with mocked external dependencies"""
        mock_run.return_value.returncode = 0
        # Test implementation
    
    @pytest.mark.integration
    def test_integration_scenario(self):
        """Integration test requiring external services"""
        # Test implementation
```

## Code Quality

### Formatting

We use `black` and `isort` for code formatting:

```bash
# Format code
make format

# Check formatting
make format-check
```

### Linting

We use `flake8` for linting:

```bash
# Run linting
make lint

# Configuration in pyproject.toml and Makefile
```

### Type Checking

We use `mypy` for static type checking:

```bash
# Run type checking
make type-check
```

### Security

We use `bandit` and `safety` for security checks:

```bash
# Run security checks
make security
```

## CI/CD Pipeline

### GitHub Actions Workflows

We have two main workflows:

#### 1. CI Workflow (`.github/workflows/ci.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`

**Jobs:**
- **Test Matrix**: Tests across Python 3.9, 3.10, 3.11, 3.12
- **Dependencies**: Installs Node.js, elasticdump, InfluxDB CLI
- **Quality Checks**: 
  - Linting with flake8
  - Code formatting with black and isort
  - Type checking with mypy
  - Tests with coverage
- **Security**: Bandit and safety checks
- **Coverage**: Upload to Codecov

#### 2. Release Workflow (`.github/workflows/release.yml`)

**Triggers:**
- Git tags matching `v*` (e.g., `v1.0.0`)

**Jobs:**
- **Test**: Run full test suite
- **Build**: Create distribution packages
- **Publish to PyPI**: Automatic publishing with trusted publishing
- **Publish to TestPyPI**: For testing
- **GitHub Release**: Create release with signed artifacts

### Dependabot

Automated dependency updates configured in `.github/dependabot.yml`:

- **Python dependencies**: Weekly updates on Mondays
- **GitHub Actions**: Weekly updates on Mondays
- **Auto-assign**: Updates assigned to maintainers

### Release Process

1. **Prepare Release**:
   ```bash
   # Update version in pyproject.toml
   # Update CHANGELOG.md
   # Run quality checks
   make all-checks
   ```

2. **Create Release**:
   ```bash
   # Create and push tag
   git tag v1.0.0
   git push origin v1.0.0
   ```

3. **Automatic Workflow**:
   - GitHub Actions builds and tests
   - Publishes to PyPI and TestPyPI
   - Creates GitHub release with signed artifacts

## Project Structure

```
es2influx/
├── es2influx/              # Main package
│   ├── __init__.py
│   ├── cli.py             # CLI interface
│   ├── config.py          # Configuration management
│   ├── transform.py       # Data transformation
│   └── utils.py           # Utility functions
├── tests/                 # Test suite
├── .github/               # GitHub Actions workflows
│   ├── workflows/
│   └── dependabot.yml
├── pyproject.toml         # Project configuration
├── pytest.ini            # Test configuration
├── Makefile              # Development commands
└── README.md             # User documentation
```

## Contributing

1. **Fork and Clone**:
   ```bash
   git clone your-fork-url
   cd es2influx
   ```

2. **Set Up Development Environment**:
   ```bash
   make setup-dev
   ```

3. **Create Feature Branch**:
   ```bash
   git checkout -b feature/your-feature
   ```

4. **Development Cycle**:
   ```bash
   # Make changes
   make dev-cycle  # Format, lint, type-check, test
   ```

5. **Quality Gate**:
   ```bash
   make all-checks  # Full quality gate
   ```

6. **Submit Pull Request**:
   - All CI checks must pass
   - Code coverage must be maintained
   - Include tests for new features

## Debugging

### Test Debugging

```bash
# Run tests with more verbose output
pytest -vvv

# Run specific test with debugging
pytest tests/test_config.py::TestClass::test_method -vvv --tb=long

# Run tests with pdb
pytest --pdb

# Keep temporary files for inspection
pytest --debug
```

### Coverage Reports

```bash
# Generate HTML coverage report
make test-cov
open htmlcov/index.html
```

### CI Debugging

- Check GitHub Actions logs for detailed error information
- Run `make ci` locally to simulate CI environment
- Use `act` tool to run GitHub Actions locally (optional)

## Performance Testing

```bash
# Run with profiling
pytest --profile

# Memory usage testing
pytest --memray

# Load testing (for integration tests)
pytest tests/test_integration.py --load-test
``` 