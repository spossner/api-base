.PHONY: help dev debug prod install clean test lint format

help:
	@echo "Available commands:"
	@echo "  make dev      - Run in development mode (uses .env settings)"
	@echo "  make debug    - Run in debug mode (DEBUG=true, verbose logging)"
	@echo "  make prod     - Run in production mode (uses .env settings)"
	@echo "  make install  - Install dependencies"
	@echo "  make clean    - Clean up cache and temporary files"
	@echo "  make lint     - Run code linting"
	@echo "  make format   - Format code"
	@echo "  make test     - Run tests"
	@echo ""
	@echo "Configuration: Edit .env file to change settings"
	@echo "All commands use run.py which reads from .env"

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

lint:
	@echo "Running linters..."
	@command -v ruff >/dev/null 2>&1 && ruff check app/ || echo "ruff not installed, skipping..."
	@command -v pylint >/dev/null 2>&1 && pylint app/ || echo "pylint not installed, skipping..."

format:
	@echo "Formatting code..."
	@command -v black >/dev/null 2>&1 && black app/ || echo "black not installed, skipping..."
	@command -v ruff >/dev/null 2>&1 && ruff format app/ || echo "ruff not installed, skipping..."

test:
	@echo "Running tests..."
	@command -v pytest >/dev/null 2>&1 && pytest || echo "pytest not installed, run: pip install pytest"
