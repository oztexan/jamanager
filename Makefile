# Jamanager Database Management

.PHONY: help db-start db-stop db-init db-reset db-status

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

db-start: ## Start PostgreSQL container
	podman run -d \
		--name jamanager-postgres \
		-e POSTGRES_PASSWORD=jamanager123 \
		-p 5432:5432 \
		postgres:15
	@echo "✅ PostgreSQL container started"

db-stop: ## Stop and remove PostgreSQL container
	podman stop jamanager-postgres || true
	podman rm jamanager-postgres || true
	@echo "✅ PostgreSQL container stopped and removed"

db-status: ## Check database container status
	podman ps | grep jamanager-postgres || echo "❌ Database container not running"

db-init: ## Initialize database with schema and sample data
	pyenv activate jv3.11.11 && python init_database.py

db-reset: ## Reset database (drop and recreate)
	pyenv activate jv3.11.11 && python reset_database.py

db-shell: ## Connect to database shell
	podman exec -it jamanager-postgres psql -U postgres -d jamanager

dev-setup: ## Complete development setup
	@echo "🚀 Setting up development environment..."
	@make db-start
	@sleep 3
	@make db-init
	@echo "✅ Development environment ready!"

clean: ## Clean up everything
	@make db-stop
	@echo "✅ Cleanup complete"