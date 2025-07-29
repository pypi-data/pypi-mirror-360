.PHONY: help install install-dev test test-cov lint format type-check clean build upload-test upload docs

# Default target
help:
	@echo "Available targets:"
	@echo "  install      - Install package in production mode"
	@echo "  install-dev  - Install package in development mode with dev dependencies"
	@echo "  test         - Run tests"
	@echo "  test-cov     - Run tests with coverage report"
	@echo "  lint         - Run linting (flake8)"
	@echo "  format       - Format code (black, isort)"
	@echo "  format-check - Check code formatting"
	@echo "  type-check   - Run type checking (mypy)"
	@echo "  security     - Run security checks (bandit, safety)"
	@echo "  clean        - Clean build artifacts"
	@echo "  build        - Build package"
	@echo "  upload-test  - Upload to TestPyPI"
	@echo "  upload       - Upload to PyPI"
	@echo "  all-checks   - Run all quality checks"

# Installation
install:
	uv pip install -e .

install-dev:
	uv pip install -e ".[dev]"

# Testing
test:
	uv run pytest tests/ -v

test-cov:
	uv run pytest tests/ -v --cov=es2influx --cov-report=term-missing --cov-report=html

test-unit:
	uv run pytest tests/ -v -m "unit"

test-integration:
	uv run pytest tests/ -v -m "integration"

# Code quality
lint:
	uv run flake8 es2influx --count --select=E9,F63,F7,F82 --show-source --statistics
	uv run flake8 es2influx --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

format:
	uv run black es2influx tests
	uv run isort es2influx tests

format-check:
	uv run black --check --diff es2influx tests
	uv run isort --check-only --diff es2influx tests

type-check:
	uv run mypy es2influx

security:
	uv run bandit -r es2influx
	uv run safety check

# Quality gate - run all checks
all-checks: lint format-check type-check test-cov security
	@echo "✅ All quality checks passed!"

# Build and upload
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

build: clean
	uv run python -m build

upload-test: build
	uv run python -m twine upload --repository testpypi dist/*

upload: build
	uv run python -m twine upload dist/*

# Development setup
setup-dev: install-dev
	@echo "Development environment setup complete!"
	@echo "Run 'make test' to verify everything works."

# Quick development cycle
dev-cycle: format lint type-check test
	@echo "✅ Development cycle complete!"

# CI simulation
ci: all-checks
	@echo "✅ CI checks complete!" 