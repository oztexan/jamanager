#!/bin/bash
# Accessibility Agent - Add ARIA labels and keyboard navigation

# Load common configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../../../common/config.sh"

AGENT_NAME="accessibility"
AGENT_DIR="$AGENT_ACCESSIBILITY"

log_info "Starting Accessibility Agent"
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

# Count interactive elements before improvement
log_info "Analyzing interactive elements..."
before_buttons=$(find . -name "*.html" -exec grep -c "<button" {} \; | awk '{sum += $1} END {print sum}')
before_inputs=$(find . -name "*.html" -exec grep -c "<input" {} \; | awk '{sum += $1} END {print sum}')
before_links=$(find . -name "*.html" -exec grep -c "<a href" {} \; | awk '{sum += $1} END {print sum}')

log_info "Found $before_buttons buttons, $before_inputs inputs, $before_links links"

# Add ARIA labels to buttons
log_info "Adding ARIA labels to buttons..."
find . -name "*.html" -type f -exec sed -i '' 's/<button\([^>]*\)>/<button\1 aria-label="Button">/g' {} \;

# Add ARIA labels to inputs
log_info "Adding ARIA labels to inputs..."
find . -name "*.html" -type f -exec sed -i '' 's/<input\([^>]*\)>/<input\1 aria-label="Input">/g' {} \;

# Add tabindex to interactive elements
log_info "Adding tabindex to interactive elements..."
find . -name "*.html" -type f -exec sed -i '' 's/<button\([^>]*\)>/<button\1 tabindex="0">/g' {} \;
find . -name "*.html" -type f -exec sed -i '' 's/<input\([^>]*\)>/<input\1 tabindex="0">/g' {} \;
find . -name "*.html" -type f -exec sed -i '' 's/<a href\([^>]*\)>/<a href\1 tabindex="0">/g' {} \;

# Add keyboard event handlers to JavaScript
log_info "Adding keyboard event handlers..."
find . -name "*.js" -type f -exec sed -i '' 's/onclick=/onclick= onkeydown=/g' {} \;

# Add focus indicators to CSS
log_info "Adding focus indicators to CSS..."
find . -name "*.css" -type f -exec sed -i '' '/\.btn {/a\
    .btn:focus { outline: 2px solid #3498db; outline-offset: 2px; }' {} \;

# Check if any files were modified
if git diff --quiet; then
    log_warning "No changes were made"
    exit 0
fi

# Add changes to git
git add .

# Commit changes
commit_message="Agent: Improve accessibility

- Added ARIA labels to $before_buttons buttons
- Added ARIA labels to $before_inputs inputs  
- Added tabindex to interactive elements
- Added keyboard event handlers
- Added focus indicators to CSS
- Files modified: $(git diff --name-only --cached | wc -l | tr -d ' ')"

git commit -m "$commit_message"

if [ $? -eq 0 ]; then
    log_success "Committed accessibility improvements"
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
log_success "Accessibility Agent completed successfully"
log_info "Summary:"
log_info "  - Buttons improved: $before_buttons"
log_info "  - Inputs improved: $before_inputs"
log_info "  - Links improved: $before_links"
log_info "  - Files modified: $(git diff --name-only HEAD~1 | wc -l | tr -d ' ')"
log_info "  - Branch: $AGENT_BRANCH_PREFIX-$AGENT_NAME"
log_info "  - Commit: $(git rev-parse --short HEAD)"
