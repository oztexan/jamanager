#!/bin/bash

# Sprint 3 Deployment Script - Australia Optimized
# Deploys Jamanager to Railway with PostgreSQL

set -e  # Exit on any error

echo "🚀 Sprint 3 Deployment: Jamanager to Railway (Australia Optimized)"
echo "=================================================================="

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

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    print_warning "Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

# Check if user is logged in to Railway
if ! railway whoami &> /dev/null; then
    print_warning "Not logged in to Railway. Please log in:"
    railway login
fi

print_status "Starting deployment process..."

# Step 1: Create Railway project (if not exists)
print_status "Step 1: Setting up Railway project..."
if [ -z "$RAILWAY_PROJECT_ID" ]; then
    print_status "Creating new Railway project..."
    railway project new jamanager-australia
    print_success "Railway project created"
else
    print_status "Using existing Railway project: $RAILWAY_PROJECT_ID"
fi

# Step 2: Add PostgreSQL database
print_status "Step 2: Adding PostgreSQL database..."
railway add postgresql
print_success "PostgreSQL database added"

# Step 3: Set environment variables
print_status "Step 3: Setting environment variables..."
railway variables set ENVIRONMENT=production
railway variables set DEBUG=false
railway variables set SECRET_KEY=$(openssl rand -hex 32)
railway variables set JAM_MANAGER_ACCESS_CODE=$(openssl rand -hex 16)
railway variables set DATABASE_POOL_SIZE=20
railway variables set CACHE_ENABLED=true
railway variables set CACHE_DEFAULT_TTL=300
railway variables set WEBSOCKET_ENABLED=true
railway variables set LOG_LEVEL=INFO
print_success "Environment variables set"

# Step 4: Deploy the application
print_status "Step 4: Deploying application..."
railway up
print_success "Application deployed"

# Step 5: Run database migration
print_status "Step 5: Running database migration..."
railway run python sprints/sprint-3/deployment/migrate_to_postgresql.py
print_success "Database migration completed"

# Step 6: Get deployment URL
print_status "Step 6: Getting deployment information..."
DEPLOYMENT_URL=$(railway domain)
print_success "Deployment URL: $DEPLOYMENT_URL"

# Step 7: Health check
print_status "Step 7: Running health check..."
sleep 10  # Wait for deployment to be ready

if curl -f -s "$DEPLOYMENT_URL/api/system/health" > /dev/null; then
    print_success "Health check passed"
else
    print_warning "Health check failed - deployment may still be starting"
fi

# Step 8: Performance test
print_status "Step 8: Running performance test..."
if curl -f -s "$DEPLOYMENT_URL/api/jams" > /dev/null; then
    print_success "API endpoints responding"
else
    print_warning "API endpoints not responding yet"
fi

echo ""
echo "🎉 Deployment Summary"
echo "===================="
echo "✅ Application deployed to Railway"
echo "✅ PostgreSQL database configured"
echo "✅ Environment variables set"
echo "✅ Database migration completed"
echo "🌐 URL: $DEPLOYMENT_URL"
echo ""
echo "📋 Next Steps:"
echo "1. Test the application at: $DEPLOYMENT_URL"
echo "2. Update CORS_ORIGINS in Railway dashboard if needed"
echo "3. Set up custom domain (optional)"
echo "4. Configure monitoring and alerts"
echo ""
echo "🔧 Railway Dashboard: https://railway.app/dashboard"
echo "📊 Monitor your deployment and usage"
echo ""
print_success "Deployment completed successfully!"
