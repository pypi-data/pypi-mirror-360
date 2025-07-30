.PHONY: help install install-dev test test-cov lint format clean build publish

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install the package in development mode
	pip install -e .

install-dev: ## Install the package with development dependencies
	pip install -e ".[dev]"

test: ## Run tests
	pytest tests/ -v

test-cov: ## Run tests with coverage
	pytest tests/ --cov=cflabs_serverless --cov-report=html --cov-report=term

lint: ## Run linting checks
	flake8 cflabs_serverless/ tests/
	mypy cflabs_serverless/

format: ## Format code with black and isort
	black cflabs_serverless/ tests/
	isort cflabs_serverless/ tests/

clean: ## Clean up build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

build: ## Build the package
	python -m build

publish: ## Publish to PyPI (requires twine)
	twine upload dist/*

check-prerequisites: ## Check if all prerequisites are installed
	@echo "Checking prerequisites..."
	@command -v aws >/dev/null 2>&1 || { echo "AWS CLI not found"; exit 1; }
	@command -v sam >/dev/null 2>&1 || { echo "AWS SAM CLI not found"; exit 1; }
	@command -v docker >/dev/null 2>&1 || { echo "Docker not found"; exit 1; }
	@echo "All prerequisites are installed!"

example-deploy: ## Deploy example project
	cd examples/basic_app && devops-ai deploy

example-delete: ## Delete example project
	cd examples/basic_app && devops-ai delete --force 