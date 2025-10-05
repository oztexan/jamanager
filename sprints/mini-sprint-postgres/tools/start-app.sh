#!/bin/bash
# Application Startup Script for Jamanager
# Handles port conflicts and PostgreSQL container status

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting Jamanager Application...${NC}"
echo "=================================="

# Kill any process on port 3000
echo -e "${YELLOW}🔪 Killing any process on port 3000...${NC}"
if lsof -ti:3000 > /dev/null 2>&1; then
    lsof -ti:3000 | xargs kill -9
    echo -e "${GREEN}   ✅ Killed existing process on port 3000${NC}"
else
    echo -e "${GREEN}   ✅ Port 3000 is already free${NC}"
fi

# Check PostgreSQL container if using PostgreSQL
if grep -q "postgresql" "$PROJECT_ROOT/.env"; then
    echo -e "${YELLOW}🐘 Checking PostgreSQL container...${NC}"
    if podman ps --format "table {{.Names}}" | grep -q "jamanager-postgres"; then
        echo -e "${GREEN}   ✅ PostgreSQL container is running${NC}"
    else
        echo -e "${RED}   ❌ PostgreSQL container is not running${NC}"
        echo -e "${YELLOW}   💡 Run: podman start jamanager-postgres${NC}"
        exit 1
    fi
fi

# Start the application
echo -e "${YELLOW}🎵 Starting Jamanager on port 3000...${NC}"
cd "$PROJECT_ROOT"

# Use uvicorn with reload for development
uvicorn main:app --host 0.0.0.0 --port 3000 --reload
