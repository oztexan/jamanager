#!/bin/bash

echo "=== Quick Application Test ==="

# Kill any existing processes
echo "Stopping existing processes..."
pkill -f uvicorn 2>/dev/null || true
sleep 2

# Check if port is free
if lsof -i :8000 >/dev/null 2>&1; then
    echo "Port 8000 still in use, force killing..."
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    sleep 2
fi

# Start application
echo "Starting application..."
cd /Users/chrisrobertson/dev/jamanager
export PYENV_VERSION="jv3.11.11"
eval "$(pyenv init -)"

# Start in background
nohup uvicorn main:app --host 0.0.0.0 --port 8000 --reload > app.log 2>&1 &
APP_PID=$!

echo "Application started with PID: $APP_PID"

# Wait for startup
echo "Waiting for application to start..."
sleep 8

# Test application
echo "Testing application..."
if curl -s --connect-timeout 5 http://localhost:8000 >/dev/null 2>&1; then
    echo "✅ Application is responding!"
    
    # Test homepage
    response=$(curl -s http://localhost:8000)
    if echo "$response" | grep -q "html\|<!DOCTYPE"; then
        echo "✅ Homepage is working!"
    else
        echo "❌ Homepage not working correctly"
    fi
    
    # Test API
    if curl -s http://localhost:8000/api/songs | grep -q "title\|artist\|\[\]"; then
        echo "✅ API is working!"
    else
        echo "❌ API not working"
    fi
    
    echo ""
    echo "🎉 Application is running successfully!"
    echo "URLs:"
    echo "  Homepage: http://localhost:8000"
    echo "  API: http://localhost:8000/api/songs"
    echo "  Jams: http://localhost:8000/api/jams"
    
else
    echo "❌ Application not responding"
    echo "Check app.log for errors:"
    tail -20 app.log
fi




