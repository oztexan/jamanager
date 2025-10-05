#!/bin/bash

echo "=== Complete Fresh Setup for Jamanager ==="
echo "This script will set up a completely fresh development environment"
echo ""

# Set up environment
export PYENV_VERSION="jv3.11.11"
eval "$(pyenv init -)"

# Navigate to project directory
cd /Users/chrisrobertson/dev/jamanager

echo "1. Cleaning up existing environment..."
# Kill any existing processes
pkill -f uvicorn 2>/dev/null || true
sleep 2

# Remove old database files
if [ -f "data/development/jamanager.db" ]; then
    echo "   Removing old development database..."
    rm -f data/development/jamanager.db
fi

echo "2. Setting up fresh database..."
# Create database directory if it doesn't exist
mkdir -p data/development

# Run the database initialization script
echo "   Running database initialization..."
python sprints/sprint-1/scripts/init_dev_database.py

echo "3. Creating sample background images..."
# Create sample background images
python sprints/sprint-1/scripts/create_sample_backgrounds.py

echo "4. Setting up development environment..."
# Run the development environment setup
bash sprints/sprint-1/scripts/setup-dev-environment.sh

echo "5. Verifying setup..."
# Check if database was created
if [ -f "data/development/jamanager.db" ]; then
    echo "   ✅ Database created successfully"
else
    echo "   ❌ Database creation failed"
    exit 1
fi

# Check if background images were created
if [ -d "static/uploads" ] && [ "$(ls -A static/uploads)" ]; then
    echo "   ✅ Background images created successfully"
else
    echo "   ❌ Background images creation failed"
    exit 1
fi

echo ""
echo "=== Setup Complete ==="
echo "✅ Fresh development environment is ready!"
echo ""
echo "Next steps:"
echo "1. Start the application: ./scripts/setup/start-clean.sh"
echo "2. Or use: make start"
echo "3. Application will be available at: http://localhost:8000"
echo ""
echo "Database location: data/development/jamanager.db"
echo "Background images: static/uploads/"
echo "Debug files: debug/"