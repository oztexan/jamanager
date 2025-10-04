#!/bin/bash
# Setup script for Phase 2: Two-Agent Pilot

# Load common configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../../common/config.sh"

# Agent configuration
AGENTS=("console-logs" "accessibility")
AGENT_DIRS=("$AGENT_CONSOLE_LOGS" "$AGENT_ACCESSIBILITY")

log_info "Starting Phase 2 setup: Two-Agent Pilot"
log_info "Version: $AGENT_VERSION"

# Validate environment
validate_environment

# Create agent workspace
create_agent_workspace

# Clone repositories for each agent
log_info "Cloning repositories for agents..."
for i in "${!AGENTS[@]}"; do
    agent_name="${AGENTS[$i]}"
    agent_dir="${AGENT_DIRS[$i]}"
    
    log_info "Setting up agent: $agent_name"
    
    # Clone the repository
    git clone "$REMOTE_ORIGIN" "$agent_dir"
    
    if [ $? -eq 0 ]; then
        log_success "Cloned repository for $agent_name"
    else
        log_error "Failed to clone repository for $agent_name"
        exit 1
    fi
    
    # Create feature branch
    cd "$agent_dir" || exit 1
    git checkout -b "$AGENT_BRANCH_PREFIX-$agent_name"
    
    if [ $? -eq 0 ]; then
        log_success "Created feature branch for $agent_name"
    else
        log_error "Failed to create feature branch for $agent_name"
        exit 1
    fi
done

# Create merge workspace
log_info "Setting up merge workspace..."
if [ -d "$MERGE_WORKSPACE" ]; then
    log_warning "Merge workspace already exists, cleaning up..."
    rm -rf "$MERGE_WORKSPACE"
fi

git clone "$REMOTE_ORIGIN" "$MERGE_WORKSPACE"
cd "$MERGE_WORKSPACE" || exit 1
git checkout -b "$FEATURE_BRANCH"

log_success "Created merge workspace"

# Create agent status file
STATUS_FILE="$AGENT_WORKSPACE/agent-status.txt"
cat > "$STATUS_FILE" << EOF
# Agent Status - Phase 2
# Generated: $(date)
# Version: $AGENT_VERSION

## Agent Status
console-logs: $(get_agent_status "$AGENT_CONSOLE_LOGS" "console-logs")
accessibility: $(get_agent_status "$AGENT_ACCESSIBILITY" "accessibility")

## Setup Status
✅ Environment validated
✅ Agent workspace created
✅ Repositories cloned
✅ Feature branches created
✅ Merge workspace created

## Next Steps
1. Run: ./scripts/agents/phase-2/execution/start-agents.sh
2. Monitor: ./scripts/agents/monitoring/agent-status.sh
3. Merge: ./scripts/agents/phase-2/merge/merge-agents.sh
EOF

log_success "Setup completed successfully!"
log_info "Status file created: $STATUS_FILE"
log_info "Next step: Run start-agents.sh to begin agent execution"

# Display status
echo ""
echo "=== Agent Status ==="
cat "$STATUS_FILE"
echo ""
echo "=== Ready to Start Agents ==="
echo "Run: ./scripts/agents/phase-2/execution/start-agents.sh"
