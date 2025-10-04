#!/bin/bash
# Quick database status check

echo "=== Database Status Check ==="
echo ""

# Check main project database
MAIN_DB="/Users/chrisrobertson/dev/jamanager/jamanager.db"
echo "Main Project DB: $MAIN_DB"
if [ -f "$MAIN_DB" ]; then
    echo "  Status: ✅ Exists"
    echo "  Size: $(stat -f%z "$MAIN_DB" 2>/dev/null || stat -c%s "$MAIN_DB" 2>/dev/null) bytes"
else
    echo "  Status: ❌ Not found"
fi

echo ""

# Check merge workspace database
MERGE_DB="/Users/chrisrobertson/dev/jamanager-workzone/workspaces/merge-workspaces/jamanager-merge/jamanager.db"
echo "Merge Workspace DB: $MERGE_DB"
if [ -f "$MERGE_DB" ]; then
    echo "  Status: ✅ Exists"
    echo "  Size: $(stat -f%z "$MERGE_DB" 2>/dev/null || stat -c%s "$MERGE_DB" 2>/dev/null) bytes"
else
    echo "  Status: ❌ Not found"
fi

echo ""

# Check agent workspace databases
echo "Agent Workspace Databases:"
for agent_dir in /Users/chrisrobertson/dev/jamanager-workzone/workspaces/agent-workspaces/*; do
    if [ -d "$agent_dir" ]; then
        agent_name=$(basename "$agent_dir")
        agent_db="$agent_dir/jamanager.db"
        if [ -f "$agent_db" ]; then
            echo "  $agent_name: ✅ Exists ($(stat -f%z "$agent_db" 2>/dev/null || stat -c%s "$agent_db" 2>/dev/null) bytes)"
        else
            echo "  $agent_name: ❌ Not found"
        fi
    fi
done

echo ""
echo "=== Application Status ==="
echo "Application URL: http://localhost:8000"
echo ""

# Check if application is running
if curl -s http://localhost:8000 >/dev/null 2>&1; then
    echo "Application Status: ✅ Running"
    
    # Test API endpoints
    echo ""
    echo "API Endpoints:"
    if curl -s http://localhost:8000/api/songs | grep -q "title"; then
        echo "  Songs API: ✅ Working"
    else
        echo "  Songs API: ❌ Not responding"
    fi
    
    if curl -s http://localhost:8000/api/jams | grep -q "name"; then
        echo "  Jams API: ✅ Working"
    else
        echo "  Jams API: ❌ Not responding"
    fi
else
    echo "Application Status: ❌ Not running"
fi

echo ""
echo "=== Recommendations ==="
echo "1. Use the main project database as the master source"
echo "2. Copy master database to workspaces as needed"
echo "3. Keep merge workspace database in sync with master"
echo "4. Use database-manager.sh for proper database management"




