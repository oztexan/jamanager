#!/bin/bash

# Sprint 2 Cleanup Script
# This script cleans up all Sprint 2 workspaces and agent directories

echo "🧹 Sprint 2 Cleanup Script"
echo "=========================="

# Load common configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/scripts/agents/common/config.sh"

echo "📁 Cleaning up Sprint 2 workspaces..."

# Clean up Sprint 2 merge workspace
if [ -d "$WORKZONE_DIR/workspaces/sprint-2-merge-workspace" ]; then
    echo "  🗑️  Removing Sprint 2 merge workspace..."
    rm -rf "$WORKZONE_DIR/workspaces/sprint-2-merge-workspace"
    echo "  ✅ Sprint 2 merge workspace removed"
else
    echo "  ℹ️  Sprint 2 merge workspace not found (already clean)"
fi

# Clean up Type Hints agent workspace
if [ -d "$AGENT_TYPE_HINTS" ]; then
    echo "  🗑️  Removing Type Hints agent workspace..."
    rm -rf "$AGENT_TYPE_HINTS"
    echo "  ✅ Type Hints agent workspace removed"
else
    echo "  ℹ️  Type Hints agent workspace not found (already clean)"
fi

# Clean up Error Handling agent workspace
if [ -d "$AGENT_ERROR_HANDLING" ]; then
    echo "  🗑️  Removing Error Handling agent workspace..."
    rm -rf "$AGENT_ERROR_HANDLING"
    echo "  ✅ Error Handling agent workspace removed"
else
    echo "  ℹ️  Error Handling agent workspace not found (already clean)"
fi

# Clean up any remaining agent workspaces from previous runs
if [ -d "$WORKZONE_DIR/workspaces/agent-workspaces" ]; then
    echo "  🗑️  Cleaning up any remaining agent workspaces..."
    find "$WORKZONE_DIR/workspaces/agent-workspaces" -name "agent-*" -type d -exec rm -rf {} + 2>/dev/null || true
    echo "  ✅ Agent workspaces cleaned"
fi

# Clean up any remaining merge workspaces
if [ -d "$WORKZONE_DIR/workspaces" ]; then
    echo "  🗑️  Cleaning up any remaining merge workspaces..."
    find "$WORKZONE_DIR/workspaces" -name "*merge*" -type d -exec rm -rf {} + 2>/dev/null || true
    echo "  ✅ Merge workspaces cleaned"
fi

# Clean up any remaining log files
if [ -d "$WORKZONE_DIR/logs" ]; then
    echo "  🗑️  Cleaning up log files..."
    rm -f "$WORKZONE_DIR/logs"/*.log 2>/dev/null || true
    echo "  ✅ Log files cleaned"
fi

# Clean up any remaining status files
if [ -d "$WORKZONE_DIR/workspaces/agent-workspaces" ]; then
    echo "  🗑️  Cleaning up status files..."
    rm -f "$WORKZONE_DIR/workspaces/agent-workspaces"/*.txt 2>/dev/null || true
    echo "  ✅ Status files cleaned"
fi

echo ""
echo "🎉 Sprint 2 cleanup completed!"
echo ""
echo "📋 Summary:"
echo "  - Sprint 2 merge workspace: Cleaned"
echo "  - Type Hints agent workspace: Cleaned"
echo "  - Error Handling agent workspace: Cleaned"
echo "  - Remaining agent workspaces: Cleaned"
echo "  - Remaining merge workspaces: Cleaned"
echo "  - Log files: Cleaned"
echo "  - Status files: Cleaned"
echo ""
echo "✅ Ready for a fresh Sprint 2 run!"
echo ""
echo "🚀 Next steps:"
echo "  1. Run: ./run-sprint-2.sh"
echo "  2. Or run individual steps:"
echo "     - Setup: ./scripts/agents/phase-2/setup/setup-sprint-2.sh"
echo "     - Execute: ./scripts/agents/phase-2/execution/start-sprint-2.sh"
echo "     - Merge: ./scripts/agents/phase-2/merge/merge-sprint-2.sh"
echo "     - Deploy: ./scripts/agents/phase-2/deploy-sprint-2.sh"
