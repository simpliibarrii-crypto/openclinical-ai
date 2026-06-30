.PHONY: install lint format test clean build run dev docker-up docker-down help

install:  ## Install package and dev dependencies
	pip install -e .[dev]
	pre-commit install

lint:  ## Run linters
	ruff check .

format:  ## Format code
	black .

test:  ## Run tests
	pytest -v

clean:  ## Clean build artifacts
	rm -rf build/ dist/ *.egg-info .pytest_cache __pycache__/
	find . -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true

build:  ## Build package
	python -m build
	docker build -t openclinical-ai:latest .

run:  ## Run application
	uvicorn runtime.main:app --reload --host 0.0.0.0 --port 8000

docker-up:  ## Start Docker services
	docker compose up -d

docker-down:  ## Stop Docker services
	docker compose down

dev:  ## Run in development mode
	uvicorn runtime.main:app --reload --host 0.0.0.0 --port 8000 --log-level debug

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
