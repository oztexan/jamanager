#!/bin/bash

# JaManager Docker Deployment Script
# This script automates Docker-based deployment for JaManager

set -e

# Configuration
APP_NAME="jamanager"
COMPOSE_FILE="docker-compose.yml"
PROD_COMPOSE_FILE="docker-compose.prod.yml"
BACKUP_DIR="./backups"
LOG_FILE="./deploy.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
    exit 1
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

# Check if Docker is installed
check_docker() {
    log "Checking Docker installation..."
    
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed. Please install Docker first."
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed. Please install Docker Compose first."
    fi
    
    # Check if Docker daemon is running
    if ! docker info > /dev/null 2>&1; then
        error "Docker daemon is not running. Please start Docker."
    fi
    
    success "Docker is ready"
}

# Check environment configuration
check_environment() {
    log "Checking environment configuration..."
    
    # Check if .env file exists
    if [ ! -f ".env" ]; then
        warning ".env file not found, creating from template..."
        if [ -f "env.example" ]; then
            cp env.example .env
            warning "Please edit .env file with your configuration before continuing"
            warning "Especially set JAM_MANAGER_ACCESS_CODE to a secure value"
            read -p "Press Enter to continue after editing .env file..."
        else
            error "No .env file or env.example template found"
        fi
    fi
    
    # Check if required environment variables are set
    source .env
    
    if [ -z "$JAM_MANAGER_ACCESS_CODE" ] || [ "$JAM_MANAGER_ACCESS_CODE" = "jam2024" ]; then
        warning "JAM_MANAGER_ACCESS_CODE is not set or using default value"
        warning "Please set a secure access code in .env file"
    fi
    
    success "Environment configuration checked"
}

# Backup current deployment
backup_current() {
    log "Creating backup of current deployment..."
    
    mkdir -p "$BACKUP_DIR"
    
    # Backup database if it exists
    if [ -f "jamanager.db" ]; then
        BACKUP_NAME="jamanager_backup_$(date +%Y%m%d_%H%M%S).db"
        cp jamanager.db "$BACKUP_DIR/$BACKUP_NAME"
        log "Database backed up to: $BACKUP_DIR/$BACKUP_NAME"
    fi
    
    # Backup uploads if they exist
    if [ -d "static/uploads" ]; then
        BACKUP_NAME="uploads_backup_$(date +%Y%m%d_%H%M%S).tar.gz"
        tar -czf "$BACKUP_DIR/$BACKUP_NAME" -C static uploads/
        log "Uploads backed up to: $BACKUP_DIR/$BACKUP_NAME"
    fi
    
    # Clean old backups (keep last 7 days)
    find "$BACKUP_DIR" -name "*_backup_*" -mtime +7 -delete 2>/dev/null || true
    log "Old backups cleaned up"
    
    success "Backup completed"
}

# Build Docker image
build_image() {
    log "Building Docker image..."
    
    # Build the application image
    docker-compose build --no-cache
    
    success "Docker image built successfully"
}

# Deploy with Docker Compose
deploy_docker() {
    log "Deploying with Docker Compose..."
    
    # Stop existing containers
    if docker-compose ps | grep -q "Up"; then
        log "Stopping existing containers..."
        docker-compose down
    fi
    
    # Start new containers
    log "Starting new containers..."
    docker-compose up -d
    
    # Wait for containers to be ready
    log "Waiting for containers to be ready..."
    sleep 10
    
    # Check if containers are running
    if docker-compose ps | grep -q "Up"; then
        success "Containers started successfully"
    else
        error "Failed to start containers"
    fi
}

# Check application health
check_health() {
    log "Checking application health..."
    
    # Wait a bit more for the application to fully start
    sleep 5
    
    # Check if the application is responding
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f http://localhost:8000/health > /dev/null 2>&1; then
            success "Application is healthy and responding"
            return 0
        fi
        
        log "Health check attempt $attempt/$max_attempts failed, retrying in 5 seconds..."
        sleep 5
        attempt=$((attempt + 1))
    done
    
    warning "Health check failed after $max_attempts attempts"
    warning "Application may still be starting up"
    
    # Show container logs for debugging
    log "Showing container logs for debugging:"
    docker-compose logs --tail=50
}

# Setup production configuration
setup_production() {
    log "Setting up production configuration..."
    
    # Create production docker-compose file if it doesn't exist
    if [ ! -f "$PROD_COMPOSE_FILE" ]; then
        log "Creating production docker-compose configuration..."
        
        cat > "$PROD_COMPOSE_FILE" << 'EOF'
version: '3.8'

services:
  app:
    build: .
    ports:
      - "80:8000"
    environment:
      - DATABASE_URL=sqlite+aiosqlite:///./data/development/jamanager.db
      - JAM_MANAGER_ACCESS_CODE=${JAM_MANAGER_ACCESS_CODE}
      - PORT=8000
    volumes:
      - ./static/uploads:/app/static/uploads
      - ./data:/app/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - app
    restart: unless-stopped
    profiles:
      - ssl
EOF
        
        success "Production configuration created: $PROD_COMPOSE_FILE"
    fi
    
    # Create nginx configuration if it doesn't exist
    if [ ! -f "nginx.conf" ]; then
        log "Creating nginx configuration..."
        
        cat > nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream app {
        server app:8000;
    }
    
    server {
        listen 80;
        server_name _;
        
        client_max_body_size 10M;
        
        location / {
            proxy_pass http://app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        location /ws {
            proxy_pass http://app;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
        }
        
        location /static/ {
            alias /app/static/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
EOF
        
        success "Nginx configuration created"
    fi
}

# Show deployment status
show_status() {
    log "Deployment Status:"
    echo ""
    
    # Show container status
    docker-compose ps
    
    echo ""
    echo "📍 Application URLs:"
    echo "  Main App: http://localhost:8000"
    echo "  Health Check: http://localhost:8000/health"
    echo "  API Docs: http://localhost:8000/docs"
    echo ""
    
    echo "🔧 Management Commands:"
    echo "  docker-compose ps                    # Show container status"
    echo "  docker-compose logs -f               # View logs"
    echo "  docker-compose restart               # Restart containers"
    echo "  docker-compose down                  # Stop containers"
    echo "  docker-compose up -d                 # Start containers"
    echo ""
    
    echo "📊 Monitoring:"
    echo "  docker stats                         # Show resource usage"
    echo "  docker-compose logs app              # Show app logs only"
    echo ""
}

# Cleanup function
cleanup() {
    log "Cleaning up..."
    
    # Remove unused Docker images
    docker image prune -f
    
    # Remove unused volumes
    docker volume prune -f
    
    success "Cleanup completed"
}

# Main deployment function
main() {
    local mode=${1:-"development"}
    
    log "Starting JaManager Docker deployment in $mode mode..."
    
    check_docker
    check_environment
    backup_current
    
    if [ "$mode" = "production" ]; then
        setup_production
        log "Using production configuration..."
        COMPOSE_FILE="$PROD_COMPOSE_FILE"
    fi
    
    build_image
    deploy_docker
    check_health
    show_status
    cleanup
    
    success "Docker deployment completed successfully!"
    
    echo ""
    echo "🎉 JaManager has been deployed with Docker!"
    echo ""
    echo "⚠️  Important Notes:"
    echo "  1. Make sure JAM_MANAGER_ACCESS_CODE is set securely in .env"
    echo "  2. For production, configure SSL certificates"
    echo "  3. Set up proper firewall rules"
    echo "  4. Monitor application logs regularly"
    echo ""
    echo "📚 For more information, see DEPLOYMENT_PLAN.md"
}

# Show usage information
usage() {
    echo "Usage: $0 [development|production]"
    echo ""
    echo "Modes:"
    echo "  development  - Deploy for development (default)"
    echo "  production   - Deploy for production with nginx"
    echo ""
    echo "Examples:"
    echo "  $0                    # Deploy in development mode"
    echo "  $0 development        # Deploy in development mode"
    echo "  $0 production         # Deploy in production mode"
}

# Handle command line arguments
case "${1:-}" in
    -h|--help)
        usage
        exit 0
        ;;
    development|production|"")
        main "$1"
        ;;
    *)
        error "Invalid mode: $1. Use -h for help."
        ;;
esac