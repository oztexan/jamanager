#!/bin/bash

echo "=== Jamanager Application Endpoint Test ==="
echo "Timestamp: $(date)"
echo ""

# Kill any existing processes
echo "1. Stopping existing processes..."
pkill -f uvicorn 2>/dev/null || true
sleep 3

# Force kill if needed
if lsof -i :8000 >/dev/null 2>&1; then
    echo "Force killing processes on port 8000..."
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    sleep 2
fi

# Set up environment
echo "2. Setting up Python environment..."
export PYENV_VERSION="jv3.11.11"
eval "$(pyenv init -)"

# Navigate to project directory
cd /Users/chrisrobertson/dev/jamanager

# Check if database exists
if [ -f "jamanager.db" ]; then
    echo "✅ Database found"
else
    echo "Creating database..."
    python init_dev_database.py
fi

# Start the application
echo "3. Starting application..."
nohup uvicorn main:app --host 0.0.0.0 --port 8000 --reload > app.log 2>&1 &
APP_PID=$!
echo "Application started with PID: $APP_PID"

# Wait for startup
echo "4. Waiting for application to start..."
sleep 8

# Test endpoints
echo "5. Testing endpoints..."
echo ""

# Test homepage
echo "Testing homepage (/)..."
if curl -s --connect-timeout 5 http://localhost:8000 >/dev/null 2>&1; then
    response=$(curl -s http://localhost:8000)
    if echo "$response" | grep -q "html\|<!DOCTYPE\|Jamanager"; then
        echo "✅ Homepage: WORKING"
    else
        echo "❌ Homepage: Not returning HTML"
        echo "Response: ${response:0:200}..."
    fi
else
    echo "❌ Homepage: Not responding"
fi

echo ""

# Test Songs API
echo "Testing Songs API (/api/songs)..."
if curl -s --connect-timeout 5 http://localhost:8000/api/songs >/dev/null 2>&1; then
    response=$(curl -s http://localhost:8000/api/songs)
    if echo "$response" | grep -q "title\|artist\|\[\]"; then
        echo "✅ Songs API: WORKING"
        echo "Response preview: ${response:0:100}..."
    else
        echo "❌ Songs API: Not returning expected data"
        echo "Response: ${response:0:200}..."
    fi
else
    echo "❌ Songs API: Not responding"
fi

echo ""

# Test Jams API
echo "Testing Jams API (/api/jams)..."
if curl -s --connect-timeout 5 http://localhost:8000/api/jams >/dev/null 2>&1; then
    response=$(curl -s http://localhost:8000/api/jams)
    if echo "$response" | grep -q "name\|slug\|\[\]"; then
        echo "✅ Jams API: WORKING"
        echo "Response preview: ${response:0:100}..."
    else
        echo "❌ Jams API: Not returning expected data"
        echo "Response: ${response:0:200}..."
    fi
else
    echo "❌ Jams API: Not responding"
fi

echo ""

# Test Venues API
echo "Testing Venues API (/api/venues)..."
if curl -s --connect-timeout 5 http://localhost:8000/api/venues >/dev/null 2>&1; then
    response=$(curl -s http://localhost:8000/api/venues)
    if echo "$response" | grep -q "name\|address\|\[\]"; then
        echo "✅ Venues API: WORKING"
        echo "Response preview: ${response:0:100}..."
    else
        echo "❌ Venues API: Not returning expected data"
        echo "Response: ${response:0:200}..."
    fi
else
    echo "❌ Venues API: Not responding"
fi

echo ""

# Test Admin Panel
echo "Testing Admin Panel (/jam-manager)..."
if curl -s --connect-timeout 5 http://localhost:8000/jam-manager >/dev/null 2>&1; then
    response=$(curl -s http://localhost:8000/jam-manager)
    if echo "$response" | grep -q "html\|<!DOCTYPE"; then
        echo "✅ Admin Panel: WORKING"
    else
        echo "❌ Admin Panel: Not returning HTML"
        echo "Response: ${response:0:200}..."
    fi
else
    echo "❌ Admin Panel: Not responding"
fi

echo ""

# Summary
echo "=== Test Summary ==="
echo "Application PID: $APP_PID"
echo "Application URL: http://localhost:8000"
echo ""

if curl -s --connect-timeout 5 http://localhost:8000 >/dev/null 2>&1; then
    echo "🎉 Application is running successfully!"
    echo ""
    echo "Available endpoints:"
    echo "  Homepage: http://localhost:8000"
    echo "  Songs API: http://localhost:8000/api/songs"
    echo "  Jams API: http://localhost:8000/api/jams"
    echo "  Venues API: http://localhost:8000/api/venues"
    echo "  Admin Panel: http://localhost:8000/jam-manager"
    echo ""
    echo "To stop the application: kill $APP_PID"
else
    echo "❌ Application is not responding"
    echo "Check app.log for errors:"
    tail -20 app.log
fi




