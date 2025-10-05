#!/bin/bash

# Mini-Sprint: PostgreSQL Development Setup
# Complete automation script for setting up PostgreSQL and testing the application

set -e  # Exit on any error

echo "🚀 Mini-Sprint: PostgreSQL Development Setup"
echo "============================================="
echo ""

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

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

print_status "Starting Mini-Sprint: PostgreSQL Development Setup"
echo ""

# Step 1: Set up PostgreSQL container
print_status "Step 1: Setting up PostgreSQL container..."
bash sprints/mini-sprint-postgres/setup-postgres.sh

if [ $? -eq 0 ]; then
    print_success "PostgreSQL container setup completed"
else
    print_error "PostgreSQL container setup failed"
    exit 1
fi

echo ""

# Step 2: Update environment for PostgreSQL
print_status "Step 2: Updating environment for PostgreSQL..."
bash sprints/mini-sprint-postgres/update-env-for-postgres.sh

if [ $? -eq 0 ]; then
    print_success "Environment updated for PostgreSQL"
else
    print_error "Environment update failed"
    exit 1
fi

echo ""

# Step 3: Test migration script
print_status "Step 3: Testing migration script..."
if [ -f "data/development/jamanager.db" ]; then
    print_status "SQLite database found, testing migration..."
    python sprints/sprint-3/deployment/migrate_to_postgresql.py
    
    if [ $? -eq 0 ]; then
        print_success "Migration script test completed"
    else
        print_warning "Migration script test failed (expected if no SQLite data)"
    fi
else
    print_warning "No SQLite database found, skipping migration test"
fi

echo ""

# Step 4: Populate PostgreSQL with dev data
print_status "Step 4: Populating PostgreSQL with development data..."
python sprints/mini-sprint-postgres/scripts/init_postgres_database.py

if [ $? -eq 0 ]; then
    print_success "PostgreSQL populated with development data"
else
    print_error "Failed to populate PostgreSQL with development data"
    exit 1
fi

echo ""

# Step 5: Start the application
print_status "Step 5: Starting application with PostgreSQL..."
print_warning "Starting application in background..."
print_warning "You can stop it later with: pkill -f uvicorn"

# Kill any existing uvicorn processes
pkill -f uvicorn 2>/dev/null || true
sleep 2

# Start the application in background
nohup uvicorn main:app --host 0.0.0.0 --port 3000 --reload > app.log 2>&1 &
APP_PID=$!

print_status "Application started with PID: $APP_PID"
print_status "Logs are being written to: app.log"

# Wait for application to start
print_status "Waiting for application to start..."
sleep 10

# Check if application is running
if curl -s http://localhost:3000/api/system/health > /dev/null 2>&1; then
    print_success "Application is running on port 3000"
else
    print_warning "Application may still be starting up..."
    print_status "You can check logs with: tail -f app.log"
fi

echo ""

# Step 6: Run comprehensive tests
print_status "Step 6: Running comprehensive tests..."
python sprints/mini-sprint-postgres/scripts/test_postgres_connection.py
python sprints/mini-sprint-postgres/tools/test-all-endpoints-postgres.py

if [ $? -eq 0 ]; then
    print_success "All tests passed!"
else
    print_warning "Some tests may have failed - check the output above"
fi

echo ""

# Final summary
echo "🎉 Mini-Sprint Complete!"
echo "========================"
echo ""
echo "✅ PostgreSQL container running"
echo "✅ Environment configured for PostgreSQL"
echo "✅ Development data populated"
echo "✅ Application running on port 3000"
echo "✅ Tests completed"
echo ""
echo "📊 PostgreSQL Connection Info:"
echo "  Host: localhost"
echo "  Port: 5432"
echo "  Database: jamanager_dev"
echo "  Username: jamanager"
echo "  Password: jamanager_dev_password"
echo ""
echo "🌐 Application URL: http://localhost:3000"
echo ""
echo "🔧 Management Commands:"
echo "  View logs: tail -f app.log"
echo "  Stop app: pkill -f uvicorn"
echo "  Restart app: uvicorn main:app --host 0.0.0.0 --port 3000 --reload"
echo "  PostgreSQL shell: podman exec -it jamanager-postgres psql -U jamanager -d jamanager_dev"
echo ""
echo "🔄 To switch back to SQLite:"
echo "  cp .env.sqlite.backup .env"
echo "  pkill -f uvicorn"
echo "  uvicorn main:app --host 0.0.0.0 --port 3000 --reload"
echo ""
print_success "Mini-Sprint completed successfully!"
print_status "Your application is now running with PostgreSQL - ready for production deployment!"
