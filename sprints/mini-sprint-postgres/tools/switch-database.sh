#!/bin/bash
# Database Switching Tool for Jamanager
# Allows easy switching between SQLite and PostgreSQL development environments

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
ENV_FILE="$PROJECT_ROOT/.env"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔄 Jamanager Database Switcher${NC}"
echo "=================================="

# Check if .env file exists
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}❌ .env file not found at $ENV_FILE${NC}"
    exit 1
fi

# Create backup files if they don't exist
if [ ! -f "$ENV_FILE.sqlite.backup" ]; then
    echo -e "${YELLOW}📋 Creating SQLite backup...${NC}"
    cp "$ENV_FILE" "$ENV_FILE.sqlite.backup"
fi

if [ ! -f "$ENV_FILE.postgres.backup" ]; then
    echo -e "${YELLOW}📋 Creating PostgreSQL backup...${NC}"
    cp "$ENV_FILE" "$ENV_FILE.postgres.backup"
fi

# Function to switch to SQLite
switch_to_sqlite() {
    echo -e "${GREEN}🗃️ Switching to SQLite...${NC}"
    
    # Update DATABASE_URL for SQLite with aiosqlite
    sed -i.bak 's|^DATABASE_URL=.*|DATABASE_URL=sqlite+aiosqlite:///data/development/jamanager.db|' "$ENV_FILE"
    
    echo -e "${GREEN}✅ Switched to SQLite database${NC}"
    echo -e "${BLUE}📍 Database location: data/development/jamanager.db${NC}"
    echo -e "${YELLOW}💡 Make sure the data/development directory exists${NC}"
}

# Function to switch to PostgreSQL
switch_to_postgres() {
    echo -e "${GREEN}🐘 Switching to PostgreSQL...${NC}"
    
    # Update DATABASE_URL for PostgreSQL
    sed -i.bak 's|^DATABASE_URL=.*|DATABASE_URL=postgresql+asyncpg://jamanager:jamanager@localhost:5432/jamanager_dev|' "$ENV_FILE"
    
    echo -e "${GREEN}✅ Switched to PostgreSQL database${NC}"
    echo -e "${BLUE}📍 Database: jamanager_dev on localhost:5432${NC}"
    echo -e "${YELLOW}💡 Make sure PostgreSQL container is running${NC}"
}

# Function to show current database
show_current() {
    echo -e "${BLUE}📊 Current Database Configuration:${NC}"
    echo "=================================="
    
    if grep -q "sqlite" "$ENV_FILE"; then
        echo -e "${GREEN}🗃️ Current: SQLite${NC}"
        grep "DATABASE_URL" "$ENV_FILE"
    elif grep -q "postgresql" "$ENV_FILE"; then
        echo -e "${GREEN}🐘 Current: PostgreSQL${NC}"
        grep "DATABASE_URL" "$ENV_FILE"
    else
        echo -e "${YELLOW}❓ Unknown database type${NC}"
        grep "DATABASE_URL" "$ENV_FILE"
    fi
}

# Function to restore from backup
restore_backup() {
    local backup_type=$1
    local backup_file="$ENV_FILE.$backup_type.backup"
    
    if [ ! -f "$backup_file" ]; then
        echo -e "${RED}❌ Backup file not found: $backup_file${NC}"
        return 1
    fi
    
    echo -e "${YELLOW}🔄 Restoring from $backup_type backup...${NC}"
    cp "$backup_file" "$ENV_FILE"
    echo -e "${GREEN}✅ Restored from $backup_type backup${NC}"
}

# Main menu
case "${1:-menu}" in
    "sqlite")
        switch_to_sqlite
        ;;
    "postgres"|"postgresql")
        switch_to_postgres
        ;;
    "current"|"status")
        show_current
        ;;
    "restore-sqlite")
        restore_backup "sqlite"
        ;;
    "restore-postgres")
        restore_backup "postgres"
        ;;
    "menu"|*)
        echo -e "${BLUE}Available commands:${NC}"
        echo "  sqlite          - Switch to SQLite database"
        echo "  postgres        - Switch to PostgreSQL database"
        echo "  current         - Show current database configuration"
        echo "  restore-sqlite  - Restore from SQLite backup"
        echo "  restore-postgres- Restore from PostgreSQL backup"
        echo ""
        echo -e "${YELLOW}Usage: $0 [command]${NC}"
        echo ""
        show_current
        ;;
esac

# Clean up backup files created by sed
rm -f "$ENV_FILE.bak"
