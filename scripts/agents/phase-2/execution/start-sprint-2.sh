#!/bin/bash
# Start Sprint 2 agents: Type Hints + Error Handling

# Load common configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../../common/config.sh"

log_info "Starting Sprint 2 agents execution"
log_info "Version: $AGENT_VERSION"
log_info "Sprint: Type Hints + Error Handling"

# Check if Sprint 2 setup was completed
if [ ! -d "$AGENT_WORKSPACE/agent-type-hints" ] || [ ! -d "$AGENT_WORKSPACE/agent-error-handling" ]; then
    log_error "Sprint 2 agent workspaces not found. Please run setup-sprint-2.sh first"
    exit 1
fi

# Start Sprint 2 agents in parallel
log_info "Starting Sprint 2 agents in parallel..."

# Start Type Hints Agent
log_info "Starting Type Hints Agent..."
"$SCRIPT_DIR/../agents/type-hints/agent.sh" &
TYPE_HINTS_PID=$!

# Start Error Handling Agent  
log_info "Starting Error Handling Agent..."
"$SCRIPT_DIR/../agents/error-handling/agent.sh" &
ERROR_HANDLING_PID=$!

# Wait for both agents to complete
log_info "Waiting for Sprint 2 agents to complete..."
wait $TYPE_HINTS_PID
TYPE_HINTS_EXIT=$?

wait $ERROR_HANDLING_PID
ERROR_HANDLING_EXIT=$?

# Check results
log_info "Sprint 2 agent execution completed"

if [ $TYPE_HINTS_EXIT -eq 0 ]; then
    log_success "Type Hints Agent completed successfully"
else
    log_error "Type Hints Agent failed with exit code $TYPE_HINTS_EXIT"
fi

if [ $ERROR_HANDLING_EXIT -eq 0 ]; then
    log_success "Error Handling Agent completed successfully"
else
    log_error "Error Handling Agent failed with exit code $ERROR_HANDLING_EXIT"
fi

# Overall status
if [ $TYPE_HINTS_EXIT -eq 0 ] && [ $ERROR_HANDLING_EXIT -eq 0 ]; then
    log_success "All Sprint 2 agents completed successfully!"
    log_info "Next step: Run merge-sprint-2.sh to merge changes"
    exit 0
else
    log_error "Some Sprint 2 agents failed. Check logs for details."
    exit 1
fi
