#!/bin/bash
# Setup script for Sprint 2: Type Hints + Error Handling Agents

# Load common configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../../common/config.sh"

# Sprint 2 configuration
SPRINT_NAME="sprint-2"
SPRINT_AGENTS=("type-hints" "error-handling")
SPRINT_AGENT_DIRS=("$AGENT_TYPE_HINTS" "$AGENT_ERROR_HANDLING")
SPRINT_FEATURE_BRANCH="feature/agent-sprint-2-improvements"

log_info "Starting Sprint 2 setup: Type Hints + Error Handling Agents"
log_info "Version: $AGENT_VERSION"
log_info "Sprint: $SPRINT_NAME"

# Validate environment
validate_environment

# Create agent workspace if it doesn't exist
if [ ! -d "$AGENT_WORKSPACE" ]; then
    create_agent_workspace
fi

# Clone repositories for Sprint 2 agents
log_info "Setting up Sprint 2 agent workspaces..."
for i in "${!SPRINT_AGENTS[@]}"; do
    agent_name="${SPRINT_AGENTS[$i]}"
    agent_dir="${SPRINT_AGENT_DIRS[$i]}"
    
    log_info "Setting up agent: $agent_name"
    
    # Remove existing workspace if it exists
    if [ -d "$agent_dir" ]; then
        log_warning "Removing existing workspace for $agent_name"
        rm -rf "$agent_dir"
    fi
    
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

# Create Sprint 2 merge workspace
log_info "Setting up Sprint 2 merge workspace..."
SPRINT_MERGE_WORKSPACE="$WORKZONE_DIR/workspaces/sprint-2-merge-workspace"

if [ -d "$SPRINT_MERGE_WORKSPACE" ]; then
    log_warning "Sprint 2 merge workspace already exists, cleaning up..."
    rm -rf "$SPRINT_MERGE_WORKSPACE"
fi

git clone "$REMOTE_ORIGIN" "$SPRINT_MERGE_WORKSPACE"
cd "$SPRINT_MERGE_WORKSPACE" || exit 1
git checkout -b "$SPRINT_FEATURE_BRANCH"

log_success "Created Sprint 2 merge workspace"

# Create Sprint 2 status file
SPRINT_STATUS_FILE="$AGENT_WORKSPACE/sprint-2-status.txt"
cat > "$SPRINT_STATUS_FILE" << EOF
# Sprint 2 Status - Type Hints + Error Handling
# Generated: $(date)
# Version: $AGENT_VERSION

## Sprint 2 Agent Status
type-hints: $(get_agent_status "$AGENT_TYPE_HINTS" "type-hints")
error-handling: $(get_agent_status "$AGENT_ERROR_HANDLING" "error-handling")

## Sprint 2 Setup Status
✅ Environment validated
✅ Agent workspace created
✅ Type Hints Agent workspace created
✅ Error Handling Agent workspace created
✅ Sprint 2 merge workspace created

## Sprint 2 Goals
- Add comprehensive type annotations to Python functions
- Standardize exception handling across the codebase
- Deploy application on port 3000
- Validate acceptance criteria

## Next Steps
1. Execute Sprint 2 agents: ./scripts/agents/phase-2/execution/start-sprint-2.sh
2. Merge Sprint 2 results: ./scripts/agents/phase-2/merge/merge-sprint-2.sh
3. Test Sprint 2 application: ./scripts/agents/test-sprint-2.sh
4. Deploy on port 3000: ./scripts/agents/deploy-sprint-2.sh
EOF

log_success "Sprint 2 setup completed successfully"
log_info "Sprint 2 Status:"
log_info "  - Type Hints Agent: Ready"
log_info "  - Error Handling Agent: Ready"
log_info "  - Sprint 2 Merge Workspace: Ready"
log_info "  - Status file: $SPRINT_STATUS_FILE"

log_info "Next step: Execute Sprint 2 agents"
log_info "Run: ./scripts/agents/phase-2/execution/start-sprint-2.sh"
