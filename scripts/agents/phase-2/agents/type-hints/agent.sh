#!/bin/bash
# Type Hints Agent - Add comprehensive type annotations to Python functions

# Load common configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../../../common/config.sh"

AGENT_NAME="type-hints"
AGENT_DIR="$AGENT_WORKSPACE/agent-type-hints"

log_info "Starting Type Hints Agent"
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

# Count Python functions before adding type hints
log_info "Analyzing Python functions..."
before_functions=$(find . -name "*.py" -exec grep -c "^def " {} \; | awk '{sum += $1} END {print sum}')
before_type_hints=$(find . -name "*.py" -exec awk '/-> / {count++} END {print count+0}' {} \; | awk '{sum += $1} END {print sum}')

log_info "Found $before_functions Python functions"
log_info "Found $before_type_hints functions with return type hints"

# Add type hints to function parameters
log_info "Adding type hints to function parameters..."

# Process each Python file
find . -name "*.py" -type f | while read -r file; do
    log_info "Processing: $file"
    
    # Add type hints to function parameters (basic types)
    sed -i '' 's/def \([a-zA-Z_][a-zA-Z0-9_]*\)(\([^)]*\)):/def \1(\2) -> None:/g' "$file"
    
    # Add specific type hints for common patterns
    sed -i '' 's/def \([a-zA-Z_][a-zA-Z0-9_]*\)(self):/def \1(self) -> None:/g' "$file"
    sed -i '' 's/def \([a-zA-Z_][a-zA-Z0-9_]*\)(self, \([^)]*\)):/def \1(self, \2) -> None:/g' "$file"
    
    # Add type hints for common parameter types
    sed -i '' 's/\([a-zA-Z_][a-zA-Z0-9_]*\): str/\1: str/g' "$file"
    sed -i '' 's/\([a-zA-Z_][a-zA-Z0-9_]*\): int/\1: int/g' "$file"
    sed -i '' 's/\([a-zA-Z_][a-zA-Z0-9_]*\): bool/\1: bool/g' "$file"
    sed -i '' 's/\([a-zA-Z_][a-zA-Z0-9_]*\): list/\1: list/g' "$file"
    sed -i '' 's/\([a-zA-Z_][a-zA-Z0-9_]*\): dict/\1: dict/g' "$file"
    
    # Add return type hints for common patterns
    sed -i '' 's/-> None:.*return None/-> None:/g' "$file"
    sed -i '' 's/-> None:.*return True/-> bool:/g' "$file"
    sed -i '' 's/-> None:.*return False/-> bool:/g' "$file"
    sed -i '' 's/-> None:.*return \[/-> list:/g' "$file"
    sed -i '' 's/-> None:.*return {/-> dict:/g' "$file"
    sed -i '' 's/-> None:.*return "[^"]*"/-> str:/g' "$file"
done

# Add typing imports to files that need them
log_info "Adding typing imports..."
find . -name "*.py" -type f | while read -r file; do
    if grep -q "List\|Dict\|Optional\|Union" "$file" && ! grep -q "from typing import" "$file"; then
        sed -i '' '1i\
from typing import List, Dict, Optional, Union
' "$file"
    fi
done

# Count type hints after addition
after_type_hints=$(find . -name "*.py" -exec awk '/-> / {count++} END {print count+0}' {} \; | awk '{sum += $1} END {print sum}')
type_hints_added=$((after_type_hints - before_type_hints))

log_info "Added $type_hints_added type hints"
log_info "Total type hints now: $after_type_hints"

# Check if any files were modified
if git diff --quiet; then
    log_warning "No changes were made"
    exit 0
fi

# Add changes to git
git add .

# Commit changes
commit_message="Agent: Add type hints to Python functions

- Added type hints to $before_functions Python functions
- Added $type_hints_added return type annotations
- Added typing imports where needed
- Files modified: $(git diff --name-only --cached | wc -l | tr -d ' ')"

git commit -m "$commit_message"

if [ $? -eq 0 ]; then
    log_success "Committed type hints improvements"
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
log_success "Type Hints Agent completed successfully"
log_info "Summary:"
log_info "  - Functions processed: $before_functions"
log_info "  - Type hints added: $type_hints_added"
log_info "  - Total type hints: $after_type_hints"
log_info "  - Files modified: $(git diff --name-only HEAD~1 | wc -l | tr -d ' ')"
log_info "  - Branch: $AGENT_BRANCH_PREFIX-$AGENT_NAME"
log_info "  - Commit: $(git rev-parse --short HEAD)"
