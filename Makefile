# JaManager Development Makefile

.PHONY: help install-backend install-frontend install dev-backend dev-frontend dev build test clean

help: ## Show this help message
	@echo "JaManager Development Commands"
	@echo "=============================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install-backend: ## Install backend dependencies
	cd backend && pip install -r requirements.txt

install-frontend: ## Install frontend dependencies
	cd frontend && npm install

install: install-backend install-frontend ## Install all dependencies

dev-backend: ## Start backend development server
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend: ## Start frontend development server
	cd frontend && npm run dev

dev: ## Start both backend and frontend in development mode
	@echo "Starting JaManager in development mode..."
	@echo "Backend: http://localhost:8000"
	@echo "Frontend: http://localhost:3000"
	@$(MAKE) -j2 dev-backend dev-frontend

build: ## Build both backend and frontend for production
	cd frontend && npm run build
	cd backend && python -m build

test: ## Run all tests
	cd backend && python -m pytest tests/ -v
	cd frontend && npm test

test-backend: ## Run backend tests only
	cd backend && python -m pytest tests/ -v

test-frontend: ## Run frontend tests only
	cd frontend && npm test

lint: ## Run linting on both backend and frontend
	cd backend && flake8 app/ && black --check app/ && isort --check-only app/
	cd frontend && npm run lint

format: ## Format code in both backend and frontend
	cd backend && black app/ && isort app/
	cd frontend && npm run format

clean: ## Clean build artifacts and cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	cd frontend && rm -rf node_modules dist
	cd backend && rm -rf build dist *.egg-info

docker-build: ## Build Docker images
	docker-compose build

docker-up: ## Start services with Docker Compose
	docker-compose up -d

docker-down: ## Stop Docker Compose services
	docker-compose down

docker-logs: ## View Docker Compose logs
	docker-compose logs -f

setup-db: ## Initialize the database
	cd backend && python app/utils/init_sqlite_db.py

reset-db: ## Reset the database
	cd backend && python app/utils/reset_database.py