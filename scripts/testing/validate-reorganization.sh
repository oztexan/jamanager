#!/bin/bash

echo "=== Validating Project Reorganization ==="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if file/directory exists
check_path() {
    local path=$1
    local description=$2
    
    echo -n "Checking $description... "
    if [ -e "$path" ]; then
        echo -e "${GREEN}✅ EXISTS${NC}"
        return 0
    else
        echo -e "${RED}❌ MISSING${NC}"
        return 1
    fi
}

# Function to check if file contains expected content
check_file_content() {
    local file=$1
    local pattern=$2
    local description=$3
    
    echo -n "Checking $description... "
    if [ -f "$file" ] && grep -q "$pattern" "$file"; then
        echo -e "${GREEN}✅ CORRECT${NC}"
        return 0
    else
        echo -e "${RED}❌ INCORRECT${NC}"
        return 1
    fi
}

echo "1. Checking Sprint Organization Structure..."
echo ""

# Check sprint directories
check_path "sprints/sprint-1" "Sprint 1 directory"
check_path "sprints/sprint-1/docs" "Sprint 1 docs directory"
check_path "sprints/sprint-1/scripts" "Sprint 1 scripts directory"
check_path "sprints/sprint-2" "Sprint 2 directory"
check_path "sprints/sprint-2/docs" "Sprint 2 docs directory"
check_path "sprints/sprint-2/scripts" "Sprint 2 scripts directory"

echo ""
echo "2. Checking Script Organization..."
echo ""

# Check script directories
check_path "scripts/setup" "Setup scripts directory"
check_path "scripts/testing" "Testing scripts directory"
check_path "scripts/migration" "Migration scripts directory"

echo ""
echo "3. Checking Data Organization..."
echo ""

# Check data directories
check_path "data/development" "Development data directory"
check_path "data/backups" "Backups directory"
check_path "debug" "Debug directory"

echo ""
echo "4. Checking Sprint 1 Files..."
echo ""

# Check Sprint 1 files
check_path "sprints/sprint-1/docs/SPRINT_1_ACCEPTANCE_CRITERIA.md" "Sprint 1 acceptance criteria"
check_path "sprints/sprint-1/docs/DEV_ENVIRONMENT_CONFIG.md" "Dev environment config"
check_path "sprints/sprint-1/docs/TROUBLESHOOTING.md" "Troubleshooting guide"
check_path "sprints/sprint-1/scripts/setup-dev-environment.sh" "Setup dev environment script"
check_path "sprints/sprint-1/scripts/init_dev_database.py" "Init dev database script"
check_path "sprints/sprint-1/scripts/create_sample_backgrounds.py" "Create sample backgrounds script"

echo ""
echo "5. Checking Sprint 2 Files..."
echo ""

# Check Sprint 2 files
check_path "sprints/sprint-2/docs/SPRINT_2_PLAN.md" "Sprint 2 plan"
check_path "sprints/sprint-2/docs/SPRINT_2_ACCEPTANCE_CRITERIA.md" "Sprint 2 acceptance criteria"
check_path "sprints/sprint-2/docs/SPRINT_2_REGRESSION_REPORT.md" "Sprint 2 regression report"
check_path "sprints/sprint-2/scripts/run-sprint-2.sh" "Run sprint 2 script"
check_path "sprints/sprint-2/scripts/cleanup-sprint-2.sh" "Cleanup sprint 2 script"

echo ""
echo "6. Checking Updated Scripts..."
echo ""

# Check that scripts have been updated with correct paths
check_file_content "scripts/setup/start-clean.sh" "data/development/jamanager.db" "Start clean script database path"
check_file_content "scripts/setup/start-clean.sh" "sprints/sprint-1/scripts/init_dev_database.py" "Start clean script init path"
check_file_content "scripts/testing/check-database-status.sh" "data/development/jamanager.db" "Database status script path"
check_file_content "scripts/agents/common/database-manager.sh" "data/development/jamanager.db" "Database manager master path"

echo ""
echo "7. Checking Core Application Files..."
echo ""

# Check core application files
check_file_content "core/database.py" "data/development/jamanager.db" "Database URL in core/database.py"
check_path "PROJECT_ORGANIZATION.md" "Project organization documentation"

echo ""
echo "8. Checking Documentation Organization..."
echo ""

# Check documentation files
check_path "docs/SPRINT_WAYS_OF_WORKING.md" "Sprint ways of working"
check_path "docs/AI_WORK_ORDER_OBSERVATIONS.md" "AI work order observations"

echo ""
echo "9. Testing Script Functionality..."
echo ""

# Test if scripts are executable and have correct shebang
echo -n "Testing script executability... "
if [ -x "scripts/setup/start-clean.sh" ] && [ -x "scripts/testing/check-database-status.sh" ]; then
    echo -e "${GREEN}✅ EXECUTABLE${NC}"
else
    echo -e "${RED}❌ NOT EXECUTABLE${NC}"
fi

echo ""
echo "10. Checking for Orphaned Files..."
echo ""

# Check for files that should have been moved
orphaned_files=(
    "jamanager.db"
    "init_dev_database.py"
    "setup-dev-environment.sh"
    "SPRINT_1_ACCEPTANCE_CRITERIA.md"
    "SPRINT_2_PLAN.md"
    "TROUBLESHOOTING.md"
)

orphaned_count=0
for file in "${orphaned_files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${RED}❌ Orphaned file found: $file${NC}"
        ((orphaned_count++))
    fi
done

if [ $orphaned_count -eq 0 ]; then
    echo -e "${GREEN}✅ No orphaned files found${NC}"
fi

echo ""
echo "=== Validation Summary ==="
echo ""

# Count total checks
total_checks=0
passed_checks=0

# This is a simplified check - in a real implementation, you'd track each check
echo "Reorganization validation completed."
echo ""
echo "Next steps:"
echo "1. Run: ./scripts/setup/start-clean.sh (to test the updated setup)"
echo "2. Run: ./scripts/testing/check-database-status.sh (to verify database paths)"
echo "3. Run: ./scripts/testing/test-endpoints.sh (to test API functionality)"
echo ""
echo "If any issues are found, check the PROJECT_ORGANIZATION.md file for guidance."
