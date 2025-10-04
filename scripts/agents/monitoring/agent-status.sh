#!/bin/bash
# Monitor agent status

# Load common configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../common/config.sh"

log_info "Checking agent status..."

# Check if agent workspace exists
if [ ! -d "$AGENT_WORKSPACE" ]; then
    log_error "Agent workspace not found. Please run setup-agents.sh first"
    exit 1
fi

echo ""
echo "=== Agent Status Report ==="
echo "Generated: $(date)"
echo "Version: $AGENT_VERSION"
echo "Phase: $AGENT_PHASE"
echo ""

# Check each agent
echo "## Agent Status"
echo ""

# Console Logs Agent
console_status=$(get_agent_status "$AGENT_CONSOLE_LOGS" "console-logs")
echo "Console Logs: $console_status"

if [ -d "$AGENT_CONSOLE_LOGS" ]; then
    cd "$AGENT_CONSOLE_LOGS" || exit 1
    if [ -d ".git" ]; then
        echo "  Branch: $(git branch --show-current)"
        echo "  Last commit: $(git log --oneline -1 2>/dev/null || echo 'No commits')"
        echo "  Status: $(git status --porcelain | wc -l | tr -d ' ') files changed"
    fi
fi

echo ""

# Accessibility Agent
accessibility_status=$(get_agent_status "$AGENT_ACCESSIBILITY" "accessibility")
echo "Accessibility: $accessibility_status"

if [ -d "$AGENT_ACCESSIBILITY" ]; then
    cd "$AGENT_ACCESSIBILITY" || exit 1
    if [ -d ".git" ]; then
        echo "  Branch: $(git branch --show-current)"
        echo "  Last commit: $(git log --oneline -1 2>/dev/null || echo 'No commits')"
        echo "  Status: $(git status --porcelain | wc -l | tr -d ' ') files changed"
    fi
fi

echo ""

# Overall status
echo "## Overall Status"
echo ""

# Check if all agents are complete
all_complete=true
if [[ "$console_status" != *"Completed"* ]]; then
    all_complete=false
fi
if [[ "$accessibility_status" != *"Completed"* ]]; then
    all_complete=false
fi

if [ "$all_complete" = true ]; then
    echo "✅ All agents completed successfully"
    echo "Next step: Run merge-agents.sh to merge changes"
else
    echo "⏳ Agents still running or not started"
    echo "Run: ./scripts/agents/phase-2/execution/start-agents.sh"
fi

echo ""

# Check merge workspace
echo "## Merge Workspace"
if [ -d "$MERGE_WORKSPACE" ]; then
    cd "$MERGE_WORKSPACE" || exit 1
    echo "✅ Merge workspace exists"
    echo "  Branch: $(git branch --show-current)"
    echo "  Status: $(git status --porcelain | wc -l | tr -d ' ') files changed"
else
    echo "❌ Merge workspace not found"
fi

echo ""

# Log file location
echo "## Logs"
echo "Log file: $LOG_FILE"
if [ -f "$LOG_FILE" ]; then
    echo "Log size: $(wc -l < "$LOG_FILE") lines"
    echo "Last entry: $(tail -1 "$LOG_FILE")"
fi

echo ""
echo "=== End Status Report ==="
