.PHONY: help dev debug prod install clean lint format check

help:
	@echo "Available commands:"
	@echo "  make dev      - Run in development mode (uses .env settings)"
	@echo "  make debug    - Run in debug mode (DEBUG=true, verbose logging)"
	@echo "  make prod     - Run in production mode (uses .env settings)"
	@echo "  make install  - Install dependencies"
	@echo "  make clean    - Clean up cache and temporary files"
	@echo ""
	@echo "Code Quality:"
	@echo "  make format   - Auto-format code with ruff"
	@echo "  make lint     - Lint code with ruff"
	@echo "  make check    - Format + lint (run before commit)"
	@echo ""
	@echo "Configuration: Edit .env file to change settings"

dev:
	@echo "Starting in development mode (reading from .env)..."
	@python run.py

debug:
	@echo "Starting in DEBUG mode with verbose logging..."
	@echo "Temporarily setting DEBUG=true and LOG_LEVEL=debug"
	@DEBUG=true LOG_LEVEL=debug python run.py

prod:
	@echo "Starting in production mode (reading from .env)..."
	@python run.py

install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt

clean:
	@echo "Cleaning up cache and temporary files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache .coverage htmlcov/ dist/ build/ 2>/dev/null || true
	@echo "Clean complete!"

format:
	@echo "Formatting code with ruff..."
	ruff format app/ run.py

lint:
	@echo "Linting code with ruff..."
	ruff check app/ run.py --fix

check: format lint
	@echo "✅ Code formatted and linted!"
