#!/bin/bash
# Merge all agents for Phase 2

# Load common configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../../common/config.sh"

log_info "Starting Phase 2 agent merge"
log_info "Version: $AGENT_VERSION"

# Check if merge workspace exists
if [ ! -d "$MERGE_WORKSPACE" ]; then
    log_error "Merge workspace not found. Please run setup-agents.sh first"
    exit 1
fi

# Change to merge workspace
cd "$MERGE_WORKSPACE" || exit 1

# Check if we're on the right branch
current_branch=$(git branch --show-current)
if [ "$current_branch" != "$FEATURE_BRANCH" ]; then
    log_error "Not on the correct branch. Expected: $FEATURE_BRANCH, Got: $current_branch"
    exit 1
fi

# Merge Console Logs Agent
log_info "Merging Console Logs Agent..."
git fetch "$AGENT_CONSOLE_LOGS" "$AGENT_BRANCH_PREFIX-console-logs"

if [ $? -eq 0 ]; then
    git merge "$AGENT_CONSOLE_LOGS/$AGENT_BRANCH_PREFIX-console-logs" --no-ff -m "Merge Console Logs Agent

- Removed console.log statements from all .js files
- Agent: console-logs
- Branch: $AGENT_BRANCH_PREFIX-console-logs"

    if [ $? -eq 0 ]; then
        log_success "Console Logs Agent merged successfully"
    else
        log_error "Failed to merge Console Logs Agent"
        exit 1
    fi
else
    log_error "Failed to fetch Console Logs Agent"
    exit 1
fi

# Merge Accessibility Agent
log_info "Merging Accessibility Agent..."
git fetch "$AGENT_ACCESSIBILITY" "$AGENT_BRANCH_PREFIX-accessibility"

if [ $? -eq 0 ]; then
    git merge "$AGENT_ACCESSIBILITY/$AGENT_BRANCH_PREFIX-accessibility" --no-ff -m "Merge Accessibility Agent

- Added ARIA labels and keyboard navigation
- Agent: accessibility
- Branch: $AGENT_BRANCH_PREFIX-accessibility"

    if [ $? -eq 0 ]; then
        log_success "Accessibility Agent merged successfully"
    else
        log_error "Failed to merge Accessibility Agent"
        exit 1
    fi
else
    log_error "Failed to fetch Accessibility Agent"
    exit 1
fi

# Run validation
log_info "Running validation tests..."

# Check if tests exist
if [ -f "requirements.txt" ]; then
    # Install dependencies if needed
    if ! python -c "import pytest" 2>/dev/null; then
        log_info "Installing test dependencies..."
        pip install -r requirements.txt
    fi
    
    # Run tests
    if [ -d "tests" ]; then
        log_info "Running tests..."
        python -m pytest tests/ -v
        
        if [ $? -eq 0 ]; then
            log_success "All tests passed"
        else
            log_error "Tests failed"
            exit 1
        fi
    else
        log_warning "No tests directory found, skipping test validation"
    fi
else
    log_warning "No requirements.txt found, skipping test validation"
fi

# Check for console.log statements
log_info "Validating console.log removal..."
remaining_console_logs=$(find . -name "*.js" -exec grep -c "console\.log" {} \; | awk '{sum += $1} END {print sum}')

if [ "$remaining_console_logs" -eq 0 ]; then
    log_success "No console.log statements found"
else
    log_warning "Found $remaining_console_logs console.log statements remaining"
fi

# Check for accessibility improvements
log_info "Validating accessibility improvements..."
aria_labels=$(find . -name "*.html" -exec grep -c "aria-label" {} \; | awk '{sum += $1} END {print sum}')
tabindex_elements=$(find . -name "*.html" -exec grep -c "tabindex" {} \; | awk '{sum += $1} END {print sum}')

log_info "Found $aria_labels ARIA labels and $tabindex_elements tabindex elements"

# Push to remote
log_info "Pushing merged changes to remote..."
git push origin "$FEATURE_BRANCH"

if [ $? -eq 0 ]; then
    log_success "Pushed merged changes to remote repository"
else
    log_error "Failed to push merged changes to remote repository"
    exit 1
fi

# Summary
log_success "Phase 2 agent merge completed successfully!"
log_info "Summary:"
log_info "  - Console Logs Agent: Merged"
log_info "  - Accessibility Agent: Merged"
log_info "  - Tests: Passed"
log_info "  - Console.log statements: $remaining_console_logs remaining"
log_info "  - ARIA labels: $aria_labels added"
log_info "  - Tabindex elements: $tabindex_elements added"
log_info "  - Branch: $FEATURE_BRANCH"
log_info "  - Commit: $(git rev-parse --short HEAD)"

echo ""
echo "=== Merge Complete ==="
echo "Next step: Review changes and merge to main branch"
echo "Run: git checkout main && git merge $FEATURE_BRANCH"
