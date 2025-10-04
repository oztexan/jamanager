#!/bin/bash
# Start all agents for Phase 2

# Load common configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../../common/config.sh"

log_info "Starting Phase 2 agents execution"
log_info "Version: $AGENT_VERSION"

# Check if setup was completed
if [ ! -d "$AGENT_WORKSPACE" ]; then
    log_error "Agent workspace not found. Please run setup-agents.sh first"
    exit 1
fi

# Start agents in parallel
log_info "Starting agents in parallel..."

# Start Console Logs Agent
log_info "Starting Console Logs Agent..."
"$SCRIPT_DIR/../agents/console-logs/agent.sh" &
CONSOLE_LOGS_PID=$!

# Start Accessibility Agent  
log_info "Starting Accessibility Agent..."
"$SCRIPT_DIR/../agents/accessibility/agent.sh" &
ACCESSIBILITY_PID=$!

# Wait for both agents to complete
log_info "Waiting for agents to complete..."
wait $CONSOLE_LOGS_PID
CONSOLE_LOGS_EXIT=$?

wait $ACCESSIBILITY_PID
ACCESSIBILITY_EXIT=$?

# Check results
log_info "Agent execution completed"

if [ $CONSOLE_LOGS_EXIT -eq 0 ]; then
    log_success "Console Logs Agent completed successfully"
else
    log_error "Console Logs Agent failed with exit code $CONSOLE_LOGS_EXIT"
fi

if [ $ACCESSIBILITY_EXIT -eq 0 ]; then
    log_success "Accessibility Agent completed successfully"
else
    log_error "Accessibility Agent failed with exit code $ACCESSIBILITY_EXIT"
fi

# Overall status
if [ $CONSOLE_LOGS_EXIT -eq 0 ] && [ $ACCESSIBILITY_EXIT -eq 0 ]; then
    log_success "All agents completed successfully!"
    log_info "Next step: Run merge-agents.sh to merge changes"
    exit 0
else
    log_error "Some agents failed. Check logs for details."
    exit 1
fi
