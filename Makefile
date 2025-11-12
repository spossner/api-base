.PHONY: help dev debug prod install clean test lint format

help:
	@echo "Available commands:"
	@echo "  make dev      - Run the API in development mode with hot reload"
	@echo "  make debug    - Run the API in debug mode with verbose logging"
	@echo "  make prod     - Run the API in production mode"
	@echo "  make install  - Install dependencies"
	@echo "  make clean    - Clean up cache and temporary files"
	@echo "  make lint     - Run code linting"
	@echo "  make format   - Format code"
	@echo "  make test     - Run tests"

dev:
	@echo "Starting FastAPI in development mode with hot reload..."
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

debug:
	@echo "Starting FastAPI in DEBUG mode..."
	@echo "Debug features enabled:"
	@echo "  - Verbose logging"
	@echo "  - Hot reload"
	@echo "  - Detailed error traces"
	@echo "  - Uvicorn access logs"
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --log-level debug --access-log

prod:
	@echo "Starting FastAPI in production mode..."
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

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
