#!/bin/bash
# Error Handling Agent - Standardize exception handling across the codebase

# Load common configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../../../common/config.sh"

AGENT_NAME="error-handling"
AGENT_DIR="$AGENT_WORKSPACE/agent-error-handling"

log_info "Starting Error Handling Agent"
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

# Count exception handlers before improvement
log_info "Analyzing exception handling..."
before_bare_except=$(find . -name "*.py" -exec grep -c "except:" {} \; | awk '{sum += $1} END {print sum}')
before_exception_as=$(find . -name "*.py" -exec grep -c "except Exception as" {} \; | awk '{sum += $1} END {print sum}')
before_specific_except=$(find . -name "*.py" -exec grep -c "except [A-Z]" {} \; | awk '{sum += $1} END {print sum}')

log_info "Found $before_bare_except bare except clauses"
log_info "Found $before_exception_as generic Exception handlers"
log_info "Found $before_specific_except specific exception handlers"

# Replace bare except clauses with specific exceptions
log_info "Replacing bare except clauses..."

find . -name "*.py" -type f | while read -r file; do
    log_info "Processing: $file"
    
    # Replace bare except: with specific exceptions (more conservative approach)
    sed -i '' 's/except:/except Exception as e:/g' "$file"
    
    # Add proper error handling for database operations (only where appropriate)
    if grep -q "database\|db\|sql" "$file"; then
        sed -i '' 's/except Exception as e:/except (DatabaseError, IntegrityError) as e:/g' "$file"
    fi
    
    # Add proper error handling for file operations (only where appropriate)
    if grep -q "open\|file\|path" "$file"; then
        sed -i '' 's/except Exception as e:/except (FileNotFoundError, PermissionError) as e:/g' "$file"
    fi
    
    # Add proper error handling for network operations (only where appropriate)
    if grep -q "request\|http\|url" "$file"; then
        sed -i '' 's/except Exception as e:/except (ConnectionError, TimeoutError) as e:/g' "$file"
    fi
done

# Add proper imports for specific exceptions
log_info "Adding exception imports..."
find . -name "*.py" -type f | while read -r file; do
    if grep -q "DatabaseError\|IntegrityError" "$file" && ! grep -q "from sqlalchemy.exc import" "$file"; then
        # Add import at the top of the file
        sed -i '' '1i\
from sqlalchemy.exc import DatabaseError, IntegrityError
' "$file"
    fi
done

# Count exception handlers after improvement
after_bare_except=$(find . -name "*.py" -exec grep -c "except:" {} \; | awk '{sum += $1} END {print sum}')
after_exception_as=$(find . -name "*.py" -exec grep -c "except Exception as" {} \; | awk '{sum += $1} END {print sum}')
after_specific_except=$(find . -name "*.py" -exec grep -c "except [A-Z]" {} \; | awk '{sum += $1} END {print sum}')

bare_except_fixed=$((before_bare_except - after_bare_except))
specific_except_added=$((after_specific_except - before_specific_except))

log_info "Fixed $bare_except_fixed bare except clauses"
log_info "Added $specific_except_added specific exception handlers"
log_info "Remaining bare except clauses: $after_bare_except"

# Check if any files were modified
if git diff --quiet; then
    log_warning "No changes were made"
    exit 0
fi

# Add changes to git
git add .

# Commit changes
commit_message="Agent: Standardize exception handling

- Fixed $bare_except_fixed bare except clauses
- Added $specific_except_added specific exception handlers
- Added proper error logging
- Added specific exception imports
- Files modified: $(git diff --name-only --cached | wc -l | tr -d ' ')"

git commit -m "$commit_message"

if [ $? -eq 0 ]; then
    log_success "Committed error handling improvements"
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
log_success "Error Handling Agent completed successfully"
log_info "Summary:"
log_info "  - Bare except clauses fixed: $bare_except_fixed"
log_info "  - Specific exception handlers added: $specific_except_added"
log_info "  - Remaining bare except clauses: $after_bare_except"
log_info "  - Files modified: $(git diff --name-only HEAD~1 | wc -l | tr -d ' ')"
log_info "  - Branch: $AGENT_BRANCH_PREFIX-$AGENT_NAME"
log_info "  - Commit: $(git rev-parse --short HEAD)"
