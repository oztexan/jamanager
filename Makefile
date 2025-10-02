.PHONY: help install dev test clean docker-build docker-up docker-down

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies
	pip install -r requirements.txt

dev: ## Start development server
	uvicorn jamanger.main:app --reload --port 8000

test: ## Run tests
	./scripts/run_tests.sh

clean: ## Clean up temporary files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/

docker-build: ## Build Docker image
	docker build -t jamanger .

docker-up: ## Start with Docker Compose
	docker-compose up -d

docker-down: ## Stop Docker Compose
	docker-compose down

docker-logs: ## View Docker logs
	docker-compose logs -f

setup-db: ## Initialize database
	python init_db.py

reset-db: ## Reset database with test data
	python reset_test_data.py

format: ## Format code
	black jamanger/ *.py
	isort jamanger/ *.py

lint: ## Lint code
	flake8 jamanger/ *.py
	mypy jamanger/ *.py
