#!/bin/bash

echo "=== Testing Application ==="
echo ""

# Check if port 8000 is in use
echo "Checking port 8000..."
if lsof -i :8000 >/dev/null 2>&1; then
    echo "✅ Port 8000 is in use"
    lsof -i :8000
else
    echo "❌ Port 8000 is not in use"
fi

echo ""

# Test HTTP connection
echo "Testing HTTP connection..."
if curl -s --connect-timeout 5 http://localhost:8000 >/dev/null 2>&1; then
    echo "✅ HTTP connection successful"
    
    # Test homepage
    echo "Testing homepage..."
    response=$(curl -s http://localhost:8000)
    if echo "$response" | grep -q "Jamanager\|html\|<!DOCTYPE"; then
        echo "✅ Homepage is responding"
    else
        echo "❌ Homepage not responding correctly"
        echo "Response: $response"
    fi
    
    # Test API
    echo "Testing API..."
    if curl -s http://localhost:8000/api/songs | grep -q "title\|artist"; then
        echo "✅ API is responding"
    else
        echo "❌ API not responding"
    fi
    
else
    echo "❌ HTTP connection failed"
fi

echo ""
echo "=== Application URLs ==="
echo "Homepage: http://localhost:8000"
echo "API: http://localhost:8000/api/songs"
echo "Jams: http://localhost:8000/api/jams"



