#!/bin/bash

echo "=== Starting Jamanager Application ==="
echo ""

# Kill any existing uvicorn processes
echo "Stopping any existing processes..."
pkill -f uvicorn 2>/dev/null || true
sleep 2

# Set up environment
echo "Setting up environment..."
export PYENV_VERSION="jv3.11.11"
eval "$(pyenv init -)"

# Check Python version
echo "Python version: $(python --version)"

# Navigate to project directory
cd /Users/chrisrobertson/dev/jamanager

# Check if database exists
if [ -f "jamanager.db" ]; then
    echo "✅ Database found"
else
    echo "❌ Database not found, creating..."
    python init_dev_database.py
fi

# Start the application
echo "Starting application on port 8000..."
echo "Application will be available at: http://localhost:8000"
echo ""

uvicorn main:app --host 0.0.0.0 --port 8000 --reload




