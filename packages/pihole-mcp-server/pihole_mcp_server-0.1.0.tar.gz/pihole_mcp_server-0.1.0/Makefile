.PHONY: help install test test-fast test-cov test-html lint format clean check-all
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

install: ## Install package in development mode with all dependencies
	pip install -e ".[dev]"

test: ## Run all tests with coverage and fail if coverage < 100%
	python -m pytest --cov=pihole_mcp_server --cov-report=term-missing --cov-fail-under=80 -v

test-fast: ## Run tests without coverage for faster feedback
	python -m pytest -v --tb=short

test-cov: ## Run tests with coverage report but don't fail on coverage threshold
	python -m pytest --cov=pihole_mcp_server --cov-report=term-missing -v

test-html: ## Run tests and generate HTML coverage report
	python -m pytest --cov=pihole_mcp_server --cov-report=html --cov-report=term-missing -v
	@echo "Coverage report available at htmlcov/index.html"

test-unit: ## Run only unit tests (skip integration tests)
	python -m pytest -m "not integration" -v

test-integration: ## Run only integration tests
	python -m pytest -m "integration" -v

lint: ## Run all linting tools
	python -m ruff check src/ tests/
	python -m mypy src/
	python -m black --check src/ tests/

format: ## Format code with black and isort
	python -m black src/ tests/
	python -m isort src/ tests/

format-check: ## Check if code formatting is correct
	python -m black --check src/ tests/
	python -m isort --check-only src/ tests/

mypy: ## Run mypy type checking
	python -m mypy src/

ruff: ## Run ruff linting
	python -m ruff check src/ tests/

ruff-fix: ## Run ruff with auto-fix
	python -m ruff check --fix src/ tests/

clean: ## Clean up build artifacts and cache files
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf reports/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

check-all: lint test ## Run all checks (linting and tests)

dev-setup: install ## Set up development environment
	@echo "Development environment setup complete!"
	@echo "Run 'make test' to run tests"
	@echo "Run 'make lint' to run linting"
	@echo "Run 'make help' to see all available commands"

# CI targets
ci-test: ## Run tests in CI environment
	python -m pytest --cov=pihole_mcp_server --cov-report=xml --cov-report=term-missing --cov-fail-under=80 -v

ci-lint: ## Run linting in CI environment
	python -m ruff check src/ tests/
	python -m mypy src/
	python -m black --check src/ tests/
	python -m isort --check-only src/ tests/ 
