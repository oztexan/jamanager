# JaManager Development Makefile

.PHONY: help install dev build test clean

help: ## Show this help message
	@echo "JaManager Development Commands"
	@echo "=============================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -r requirements.txt

dev: ## Start development server
	@echo "Starting JaManager in development mode..."
	@echo "Backend: http://localhost:8000"
	uvicorn main:app --reload --host 0.0.0.0 --port 8000

build: ## Build for production
	python -m build

test: ## Run all tests
	python -m pytest tests/ -v

lint: ## Run linting
	flake8 . && black --check . && isort --check-only .

format: ## Format code
	black . && isort .

clean: ## Clean build artifacts and cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf build dist *.egg-info

docker-build: ## Build Docker images
	docker-compose build

docker-up: ## Start services with Docker Compose
	docker-compose up -d

docker-down: ## Stop Docker Compose services
	docker-compose down

docker-logs: ## View Docker Compose logs
	docker-compose logs -f

setup-db: ## Initialize the database
	python utils/init_sqlite_db.py

reset-db: ## Reset the database
	python utils/reset_database.py

init-dev-data: ## Initialize development data
	python scripts/init_dev_data.py