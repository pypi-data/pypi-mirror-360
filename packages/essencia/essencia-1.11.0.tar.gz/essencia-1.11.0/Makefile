.PHONY: help test test-unit test-integration test-coverage test-watch install install-dev clean lint format type-check

help:
	@echo "Available commands:"
	@echo "  make install        Install package in development mode"
	@echo "  make install-dev    Install with dev dependencies"
	@echo "  make test          Run all tests"
	@echo "  make test-unit     Run unit tests only"
	@echo "  make test-integration Run integration tests only"
	@echo "  make test-coverage Run tests with coverage report"
	@echo "  make test-watch    Run tests in watch mode"
	@echo "  make lint          Run linting checks"
	@echo "  make format        Format code with black and isort"
	@echo "  make type-check    Run type checking with mypy"
	@echo "  make clean         Clean up cache and build files"

install:
	uv pip install -e .

install-dev:
	uv pip install -e ".[test,dev]"

test:
	pytest

test-unit:
	pytest -m unit

test-integration:
	pytest -m integration

test-coverage:
	pytest --cov=src/essencia --cov-report=html --cov-report=term

test-watch:
	pytest-watch

lint:
	ruff check src/ tests/
	flake8 src/ tests/

format:
	black src/ tests/
	isort src/ tests/

type-check:
	mypy src/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete
	find . -type f -name "coverage.xml" -delete