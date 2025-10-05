#!/bin/bash

echo "=== Testing API Endpoints ==="
echo ""

# Base URL
BASE_URL="http://localhost:8000"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to test endpoint
test_endpoint() {
    local endpoint=$1
    local description=$2
    local expected_field=$3
    
    echo -n "Testing $description... "
    
    response=$(curl -s "$BASE_URL$endpoint" 2>/dev/null)
    if [ $? -eq 0 ] && [ -n "$response" ]; then
        if [ -n "$expected_field" ]; then
            if echo "$response" | grep -q "$expected_field"; then
                echo -e "${GREEN}✅ PASS${NC}"
                return 0
            else
                echo -e "${RED}❌ FAIL - Missing expected field: $expected_field${NC}"
                return 1
            fi
        else
            echo -e "${GREEN}✅ PASS${NC}"
            return 0
        fi
    else
        echo -e "${RED}❌ FAIL - No response${NC}"
        return 1
    fi
}

# Check if application is running
echo "Checking if application is running..."
if ! curl -s "$BASE_URL" >/dev/null 2>&1; then
    echo -e "${RED}❌ Application is not running on $BASE_URL${NC}"
    echo "Please start the application first:"
    echo "  ./scripts/setup/start-clean.sh"
    echo "  or"
    echo "  make start"
    exit 1
fi

echo -e "${GREEN}✅ Application is running${NC}"
echo ""

# Test endpoints
echo "Testing API endpoints..."
echo ""

# Basic endpoints
test_endpoint "/" "Home page" "jamanager"
test_endpoint "/api/dev-info" "Dev info API" "git_branch"
test_endpoint "/api/songs" "Songs API" "title"
test_endpoint "/api/jams" "Jams API" "name"
test_endpoint "/api/venues" "Venues API" "name"

echo ""

# Test specific jam endpoint (if jams exist)
echo "Testing specific jam endpoint..."
jam_response=$(curl -s "$BASE_URL/api/jams" 2>/dev/null)
if echo "$jam_response" | grep -q "id"; then
    # Get first jam ID
    jam_id=$(echo "$jam_response" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
    if [ -n "$jam_id" ]; then
        test_endpoint "/api/jams/$jam_id" "Specific jam API" "name"
    else
        echo -e "${YELLOW}⚠️  No jam ID found in response${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  No jams found in database${NC}"
fi

echo ""

# Test static file serving
echo "Testing static file serving..."
test_endpoint "/static/index.html" "Static HTML serving" "jamanager"
test_endpoint "/static/css/base.css" "CSS file serving" "body"
test_endpoint "/static/js/app.js" "JavaScript file serving" "function"

echo ""

# Test WebSocket endpoint (basic check)
echo "Testing WebSocket endpoint..."
ws_response=$(curl -s "$BASE_URL/ws" 2>/dev/null)
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ WebSocket endpoint accessible${NC}"
else
    echo -e "${YELLOW}⚠️  WebSocket endpoint not accessible (may require WebSocket client)${NC}"
fi

echo ""
echo "=== Test Summary ==="
echo "All critical endpoints have been tested."
echo "Check the results above for any failures."
echo ""
echo "For more detailed testing, run:"
echo "  python -m pytest tests/ -v"
echo ""
echo "Application URL: $BASE_URL"
echo "Database location: data/development/jamanager.db"