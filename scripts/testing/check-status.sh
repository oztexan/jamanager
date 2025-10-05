#!/bin/bash

echo "=== Application Status Check ==="

# Check if port 8000 is in use
echo "Checking port 8000..."
if lsof -i :8000 >/dev/null 2>&1; then
    echo "✅ Port 8000 is in use"
    lsof -i :8000
else
    echo "❌ Port 8000 is not in use"
fi

echo ""

# Check for uvicorn processes
echo "Checking for uvicorn processes..."
if pgrep -f uvicorn >/dev/null; then
    echo "✅ Uvicorn process found"
    ps aux | grep uvicorn | grep -v grep
else
    echo "❌ No uvicorn process found"
fi

echo ""

# Test HTTP connection
echo "Testing HTTP connection..."
if curl -s --connect-timeout 5 http://localhost:8000 >/dev/null 2>&1; then
    echo "✅ HTTP connection successful"
    
    # Test homepage
    echo "Testing homepage..."
    response=$(curl -s http://localhost:8000 2>/dev/null)
    if echo "$response" | grep -q "html\|<!DOCTYPE"; then
        echo "✅ Homepage is working"
    else
        echo "❌ Homepage not working"
        echo "Response: ${response:0:200}..."
    fi
    
    # Test API
    echo "Testing API..."
    api_response=$(curl -s http://localhost:8000/api/songs 2>/dev/null)
    if echo "$api_response" | grep -q "title\|artist\|\[\]"; then
        echo "✅ API is working"
    else
        echo "❌ API not working"
        echo "API response: ${api_response:0:200}..."
    fi
    
else
    echo "❌ HTTP connection failed"
fi

echo ""
echo "=== URLs to Test ==="
echo "Homepage: http://localhost:8000"
echo "Songs API: http://localhost:8000/api/songs"
echo "Jams API: http://localhost:8000/api/jams"
echo "Admin: http://localhost:8000/jam-manager"




