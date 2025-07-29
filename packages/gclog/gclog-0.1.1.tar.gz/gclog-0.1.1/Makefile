.PHONY: help install install-dev test test-cov lint clean build publish bump-patch bump-minor bump-major commit setup-hooks

# Default target
help: ## Show this help message
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Installation
install: ## Install the package
	uv sync

install-dev: ## Install with development dependencies
	uv sync --group dev

# Testing
test: ## Run tests
	uv run pytest tests/ -v

test-cov: ## Run tests with coverage report
	uv run pytest --cov=gclog --cov-report=term-missing --cov-report=xml tests/

# Code Quality
lint: ## Run linting and formatting with ruff
	uv run ruff check . --fix
	uv run ruff format .

# Pre-commit
setup-hooks: ## Install pre-commit hooks
	uv run pre-commit install
	uv run pre-commit install --hook-type commit-msg

run-hooks: ## Run pre-commit hooks on all files
	uv run pre-commit run --all-files

# Building and Publishing
clean: ## Clean build artifacts
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

build: clean ## Build the package
	uv run python -m build

publish-test: build ## Publish to TestPyPI
	uv run twine upload --repository testpypi dist/*

publish: build ## Publish to PyPI
	uv run twine upload dist/*

# Version Management
bump-patch: ## Bump patch version (0.1.1 -> 0.1.2)
	uv run cz bump --increment PATCH

bump-minor: ## Bump minor version (0.1.1 -> 0.2.0)
	uv run cz bump --increment MINOR

bump-major: ## Bump major version (0.1.1 -> 1.0.0)
	uv run cz bump --increment MAJOR

bump: ## Auto-bump version based on conventional commits
	uv run cz bump

# Git helpers
commit: ## Interactive commit with conventional commit format
	uv run cz commit

# Development workflow
dev-setup: install-dev setup-hooks ## Complete development setup
	@echo "✅ Development environment ready!"
	@echo "📋 Next steps:"
	@echo "  - Run 'make test' to verify everything works"
	@echo "  - Use 'make commit' for conventional commits"
	@echo "  - Use 'make bump' to release new versions"

# CI/Local verification
ci: lint test-cov ## Run all CI checks locally
	@echo "✅ All checks passed!"

# Quick development commands
quick-test: ## Run tests without coverage (faster)
	uv run pytest tests/ -x --tb=short