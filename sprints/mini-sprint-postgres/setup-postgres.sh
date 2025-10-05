#!/bin/bash

# Mini-Sprint: PostgreSQL Development Setup
# Sets up PostgreSQL container using Podman for local development

set -e  # Exit on any error

echo "🐘 Setting up PostgreSQL for Jamanager Development"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Configuration
CONTAINER_NAME="jamanager-postgres"
POSTGRES_USER="jamanager"
POSTGRES_PASSWORD="jamanager_dev_password"
POSTGRES_DB="jamanager_dev"
POSTGRES_PORT="5432"
DATA_VOLUME="jamanager-postgres-data"

print_status "Configuration:"
echo "  Container Name: $CONTAINER_NAME"
echo "  Database: $POSTGRES_DB"
echo "  User: $POSTGRES_USER"
echo "  Port: $POSTGRES_PORT"
echo "  Data Volume: $DATA_VOLUME"
echo ""

# Check if Podman is installed
if ! command -v podman &> /dev/null; then
    print_error "Podman is not installed. Please install Podman first."
    exit 1
fi

print_success "Podman is available"

# Check if container already exists
if podman container exists $CONTAINER_NAME; then
    print_warning "Container $CONTAINER_NAME already exists"
    
    # Check if it's running
    if podman container inspect $CONTAINER_NAME --format '{{.State.Status}}' | grep -q "running"; then
        print_warning "Container is already running"
        print_status "Stopping existing container..."
        podman stop $CONTAINER_NAME
    fi
    
    print_status "Removing existing container..."
    podman rm $CONTAINER_NAME
fi

# Create data volume if it doesn't exist
if ! podman volume exists $DATA_VOLUME; then
    print_status "Creating data volume: $DATA_VOLUME"
    podman volume create $DATA_VOLUME
    print_success "Data volume created"
else
    print_status "Data volume already exists: $DATA_VOLUME"
fi

# Pull PostgreSQL image
print_status "Pulling PostgreSQL 15 image..."
podman pull postgres:15

# Create and start PostgreSQL container
print_status "Creating PostgreSQL container..."
podman run -d \
    --name $CONTAINER_NAME \
    --restart unless-stopped \
    -e POSTGRES_USER=$POSTGRES_USER \
    -e POSTGRES_PASSWORD=$POSTGRES_PASSWORD \
    -e POSTGRES_DB=$POSTGRES_DB \
    -e POSTGRES_INITDB_ARGS="--encoding=UTF-8 --lc-collate=C --lc-ctype=C" \
    -p $POSTGRES_PORT:5432 \
    -v $DATA_VOLUME:/var/lib/postgresql/data \
    postgres:15

print_success "PostgreSQL container created and started"

# Wait for PostgreSQL to be ready
print_status "Waiting for PostgreSQL to be ready..."
sleep 5

# Test connection
print_status "Testing PostgreSQL connection..."
max_attempts=30
attempt=1

while [ $attempt -le $max_attempts ]; do
    if podman exec $CONTAINER_NAME pg_isready -U $POSTGRES_USER -d $POSTGRES_DB > /dev/null 2>&1; then
        print_success "PostgreSQL is ready!"
        break
    fi
    
    if [ $attempt -eq $max_attempts ]; then
        print_error "PostgreSQL failed to start after $max_attempts attempts"
        print_status "Container logs:"
        podman logs $CONTAINER_NAME
        exit 1
    fi
    
    print_status "Attempt $attempt/$max_attempts - waiting for PostgreSQL..."
    sleep 2
    attempt=$((attempt + 1))
done

# Create additional database for testing
print_status "Creating additional databases..."
podman exec $CONTAINER_NAME psql -U $POSTGRES_USER -d $POSTGRES_DB -c "CREATE DATABASE jamanager_test;"
podman exec $CONTAINER_NAME psql -U $POSTGRES_USER -d $POSTGRES_DB -c "GRANT ALL PRIVILEGES ON DATABASE jamanager_test TO $POSTGRES_USER;"

print_success "Additional databases created"

# Display connection information
echo ""
echo "🎉 PostgreSQL Setup Complete!"
echo "============================="
echo ""
echo "📊 Connection Information:"
echo "  Host: localhost"
echo "  Port: $POSTGRES_PORT"
echo "  Database: $POSTGRES_DB"
echo "  Username: $POSTGRES_USER"
echo "  Password: $POSTGRES_PASSWORD"
echo ""
echo "🔗 Connection URL:"
echo "  postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@localhost:$POSTGRES_PORT/$POSTGRES_DB"
echo ""
echo "🐳 Container Management:"
echo "  Start:   podman start $CONTAINER_NAME"
echo "  Stop:    podman stop $CONTAINER_NAME"
echo "  Restart: podman restart $CONTAINER_NAME"
echo "  Logs:    podman logs $CONTAINER_NAME"
echo "  Shell:   podman exec -it $CONTAINER_NAME psql -U $POSTGRES_USER -d $POSTGRES_DB"
echo ""
echo "📁 Data Volume:"
echo "  Volume: $DATA_VOLUME"
echo "  Location: $(podman volume inspect $DATA_VOLUME --format '{{.Mountpoint}}')"
echo ""

# Test the connection with psql
print_status "Testing database connection..."
if podman exec $CONTAINER_NAME psql -U $POSTGRES_USER -d $POSTGRES_DB -c "SELECT version();" > /dev/null 2>&1; then
    print_success "Database connection test passed"
else
    print_error "Database connection test failed"
    exit 1
fi

print_success "PostgreSQL setup completed successfully!"
echo ""
echo "🚀 Next Steps:"
echo "1. Update your .env file with PostgreSQL connection details"
echo "2. Run the migration script: python sprints/sprint-3/deployment/migrate_to_postgresql.py"
echo "3. Populate with dev data: python init_dev_database.py"
echo "4. Test the application with PostgreSQL"
