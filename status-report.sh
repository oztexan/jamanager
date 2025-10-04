#!/bin/bash

echo "=== Jamanager Application Status Report ==="
echo "Generated: $(date)"
echo ""

# Check if application is running
echo "=== Process Status ==="
if pgrep -f uvicorn >/dev/null; then
    echo "✅ Uvicorn process is running"
    echo "Process details:"
    ps aux | grep uvicorn | grep -v grep
else
    echo "❌ No uvicorn process found"
fi

echo ""

# Check port 8000
echo "=== Port Status ==="
if lsof -i :8000 >/dev/null 2>&1; then
    echo "✅ Port 8000 is in use"
    lsof -i :8000
else
    echo "❌ Port 8000 is not in use"
fi

echo ""

# Check HTTP connectivity
echo "=== HTTP Connectivity ==="
if curl -s --connect-timeout 5 http://localhost:8000 >/dev/null 2>&1; then
    echo "✅ HTTP connection successful"
    
    # Test homepage
    echo "Testing homepage..."
    response=$(curl -s http://localhost:8000 2>/dev/null)
    if echo "$response" | grep -q "html\|<!DOCTYPE\|Jamanager"; then
        echo "✅ Homepage is responding with HTML content"
    else
        echo "❌ Homepage not responding correctly"
        echo "Response preview: ${response:0:200}..."
    fi
    
    # Test API
    echo "Testing API..."
    api_response=$(curl -s http://localhost:8000/api/songs 2>/dev/null)
    if echo "$api_response" | grep -q "title\|artist\|\[\]"; then
        echo "✅ API is responding"
    else
        echo "❌ API not responding correctly"
        echo "API response preview: ${api_response:0:200}..."
    fi
    
else
    echo "❌ HTTP connection failed"
fi

echo ""

# Check database
echo "=== Database Status ==="
if [ -f "/Users/chrisrobertson/dev/jamanager/jamanager.db" ]; then
    echo "✅ Main database exists"
    echo "Size: $(stat -f%z /Users/chrisrobertson/dev/jamanager/jamanager.db 2>/dev/null || stat -c%s /Users/chrisrobertson/dev/jamanager/jamanager.db 2>/dev/null) bytes"
else
    echo "❌ Main database not found"
fi

if [ -f "/Users/chrisrobertson/dev/jamanager-workzone/workspaces/merge-workspaces/jamanager-merge/jamanager.db" ]; then
    echo "✅ Merge workspace database exists"
    echo "Size: $(stat -f%z /Users/chrisrobertson/dev/jamanager-workzone/workspaces/merge-workspaces/jamanager-merge/jamanager.db 2>/dev/null || stat -c%s /Users/chrisrobertson/dev/jamanager-workzone/workspaces/merge-workspaces/jamanager-merge/jamanager.db 2>/dev/null) bytes"
else
    echo "❌ Merge workspace database not found"
fi

echo ""

# Check static files
echo "=== Static Files Status ==="
if [ -f "/Users/chrisrobertson/dev/jamanager/static/index.html" ]; then
    echo "✅ Main project static files exist"
else
    echo "❌ Main project static files not found"
fi

if [ -f "/Users/chrisrobertson/dev/jamanager-workzone/workspaces/merge-workspaces/jamanager-merge/static/index.html" ]; then
    echo "✅ Merge workspace static files exist"
else
    echo "❌ Merge workspace static files not found"
fi

echo ""

# Recommendations
echo "=== Recommendations ==="
if ! pgrep -f uvicorn >/dev/null; then
    echo "1. Start the application:"
    echo "   cd /Users/chrisrobertson/dev/jamanager"
    echo "   ./start-app.sh"
    echo ""
fi

if [ ! -f "/Users/chrisrobertson/dev/jamanager/jamanager.db" ]; then
    echo "2. Initialize database:"
    echo "   cd /Users/chrisrobertson/dev/jamanager"
    echo "   python init_dev_database.py"
    echo ""
fi

echo "3. Test URLs:"
echo "   Homepage: http://localhost:8000"
echo "   API: http://localhost:8000/api/songs"
echo "   Jams: http://localhost:8000/api/jams"
echo "   Admin: http://localhost:8000/jam-manager"




