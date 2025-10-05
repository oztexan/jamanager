#!/bin/bash
# Test application access

echo "=== Testing Application Access ==="
echo ""

# Test if port 8000 is accessible
echo "Testing port 8000..."
if curl -s --connect-timeout 5 http://localhost:8000 >/dev/null 2>&1; then
    echo "✅ Port 8000 is accessible"
    
    # Test homepage
    echo ""
    echo "Testing homepage..."
    if curl -s http://localhost:8000 | grep -q "Jamanager"; then
        echo "✅ Homepage is working"
    else
        echo "❌ Homepage not responding correctly"
    fi
    
    # Test API endpoints
    echo ""
    echo "Testing API endpoints..."
    if curl -s http://localhost:8000/api/songs | grep -q "title"; then
        echo "✅ Songs API is working"
    else
        echo "❌ Songs API not responding"
    fi
    
    if curl -s http://localhost:8000/api/jams | grep -q "name"; then
        echo "✅ Jams API is working"
    else
        echo "❌ Jams API not responding"
    fi
    
else
    echo "❌ Port 8000 is not accessible"
    echo ""
    echo "Checking for running processes..."
    if pgrep -f uvicorn >/dev/null; then
        echo "✅ Uvicorn process is running"
    else
        echo "❌ No uvicorn process found"
    fi
fi

echo ""
echo "=== Application URLs ==="
echo "Homepage: http://localhost:8000"
echo "Songs API: http://localhost:8000/api/songs"
echo "Jams API: http://localhost:8000/api/jams"
echo "Jam Interface: http://localhost:8000/jam.html"
echo "Admin Panel: http://localhost:8000/admin.html"




