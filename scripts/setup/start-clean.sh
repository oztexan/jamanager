#!/bin/bash

echo "=== Starting Jamanager Application (Clean) ==="

# Kill any existing processes
echo "Stopping existing processes..."
pkill -f uvicorn 2>/dev/null || true
sleep 3

# Force kill if needed
if lsof -i :8000 >/dev/null 2>&1; then
    echo "Force killing processes on port 8000..."
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    sleep 2
fi

# Set up environment
echo "Setting up Python environment..."
export PYENV_VERSION="jv3.11.11"
eval "$(pyenv init -)"

# Navigate to project directory
cd /Users/chrisrobertson/dev/jamanager

# Check if database exists
if [ -f "data/development/jamanager.db" ]; then
    echo "✅ Database found"
else
    echo "Creating database..."
    python sprints/sprint-1/scripts/init_dev_database.py
fi

# Start the application
echo "Starting application on port 8000..."
echo "Application will be available at: http://localhost:8000"
echo ""

# Start uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload