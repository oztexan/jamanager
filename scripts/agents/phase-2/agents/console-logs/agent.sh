#!/bin/bash
# Console Logs Agent - Remove all console.log statements

# Load common configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../../../common/config.sh"

AGENT_NAME="console-logs"
AGENT_DIR="$AGENT_CONSOLE_LOGS"

log_info "Starting Console Logs Agent"
log_info "Agent: $AGENT_NAME"
log_info "Directory: $AGENT_DIR"

# Change to agent directory
cd "$AGENT_DIR" || exit 1

# Check if we're on the right branch
current_branch=$(git branch --show-current)
if [ "$current_branch" != "$AGENT_BRANCH_PREFIX-$AGENT_NAME" ]; then
    log_error "Not on the correct branch. Expected: $AGENT_BRANCH_PREFIX-$AGENT_NAME, Got: $current_branch"
    exit 1
fi

# Count console.log statements before removal
log_info "Counting console.log statements..."
before_count=$(find . -name "*.js" -exec grep -c "console\.log" {} \; | awk '{sum += $1} END {print sum}')
log_info "Found $before_count console.log statements"

if [ "$before_count" -eq 0 ]; then
    log_warning "No console.log statements found. Nothing to do."
    exit 0
fi

# Remove console.log statements
log_info "Removing console.log statements..."

# Find all .js files and remove console.log statements
find . -name "*.js" -type f -exec sed -i '' '/console\.log/d' {} \;

# Count console.log statements after removal
after_count=$(find . -name "*.js" -exec grep -c "console\.log" {} \; | awk '{sum += $1} END {print sum}')
log_info "Remaining console.log statements: $after_count"

# Check if any files were modified
if git diff --quiet; then
    log_warning "No changes were made"
    exit 0
fi

# Add changes to git
git add .

# Commit changes
commit_message="Agent: Remove $before_count console.log statements

- Removed console.log statements from all .js files
- Before: $before_count statements
- After: $after_count statements
- Files modified: $(git diff --name-only --cached | wc -l | tr -d ' ')"

git commit -m "$commit_message"

if [ $? -eq 0 ]; then
    log_success "Committed changes: $before_count console.log statements removed"
else
    log_error "Failed to commit changes"
    exit 1
fi

# Push changes
git push origin "$AGENT_BRANCH_PREFIX-$AGENT_NAME"

if [ $? -eq 0 ]; then
    log_success "Pushed changes to remote repository"
else
    log_error "Failed to push changes to remote repository"
    exit 1
fi

# Update status
log_success "Console Logs Agent completed successfully"
log_info "Summary:"
log_info "  - Console.log statements removed: $before_count"
log_info "  - Files modified: $(git diff --name-only HEAD~1 | wc -l | tr -d ' ')"
log_info "  - Branch: $AGENT_BRANCH_PREFIX-$AGENT_NAME"
log_info "  - Commit: $(git rev-parse --short HEAD)"
