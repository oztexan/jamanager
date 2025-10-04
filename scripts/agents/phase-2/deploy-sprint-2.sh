#!/bin/bash
# Deploy Sprint 2 application on port 3000

# Load common configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../../common/config.sh"

SPRINT_MERGE_WORKSPACE="$WORKZONE_DIR/workspaces/sprint-2-merge-workspace"
SPRINT_PORT=3000

log_info "Deploying Sprint 2 application on port $SPRINT_PORT"
log_info "Version: $AGENT_VERSION"
log_info "Sprint: Type Hints + Error Handling"

# Check if Sprint 2 merge workspace exists
if [ ! -d "$SPRINT_MERGE_WORKSPACE" ]; then
    log_error "Sprint 2 merge workspace not found. Please run merge-sprint-2.sh first"
    exit 1
fi

# Kill any existing processes on port 3000
log_info "Killing existing processes on port $SPRINT_PORT..."
pkill -9 -f "uvicorn.*port.*$SPRINT_PORT" 2>/dev/null || true
lsof -ti:$SPRINT_PORT | xargs kill -9 2>/dev/null || true
sleep 2

# Change to Sprint 2 merge workspace
cd "$SPRINT_MERGE_WORKSPACE" || exit 1

# Setup Python environment
setup_python_environment

# Initialize database if needed
if [ ! -f "jamanager.db" ]; then
    log_info "Initializing database..."
    if [ -f "init_dev_database.py" ]; then
        $PYTHON_CMD init_dev_database.py
        log_success "Database initialized"
    else
        log_warning "No database initialization script found"
    fi
fi

# Install dependencies
log_info "Installing dependencies..."
if [ -f "requirements.txt" ]; then
    $PIP_CMD install -r requirements.txt
    log_success "Dependencies installed"
else
    log_warning "No requirements.txt found"
fi

# Add Sprint 2 dev indicator to index.html
log_info "Adding Sprint 2 dev indicator..."
if [ -f "static/index.html" ]; then
    # Add Sprint 2 indicator
    sed -i '' 's/<body>/<body>\
        <!-- Sprint 2 Dev Environment Indicator -->\
        <div class="dev-indicator sprint-2-version">\
            🚀 SPRINT 2 - TYPE HINTS + ERROR HANDLING<br>\
            Port 3000 | Type Hints ✅ | Error Handling ✅\
        </div>/' "static/index.html"
    
    # Add CSS for Sprint 2 indicator
    sed -i '' 's/<\/style>/\
        .dev-indicator.sprint-2-version {\
            background: #9b59b6;\
        }\
    <\/style>/' "static/index.html"
    
    log_success "Sprint 2 dev indicator added"
fi

# Start the application
log_info "Starting Sprint 2 application on port $SPRINT_PORT..."
log_info "Application URL: http://localhost:$SPRINT_PORT"

# Start uvicorn in background
$PYTHON_CMD -m uvicorn main:app --host 0.0.0.0 --port $SPRINT_PORT --reload &
UVICORN_PID=$!

# Wait for application to start
log_info "Waiting for application to start..."
sleep 5

# Check if application is running
if curl -s "http://localhost:$SPRINT_PORT" > /dev/null; then
    log_success "Sprint 2 application is running on port $SPRINT_PORT"
    log_info "Application URL: http://localhost:$SPRINT_PORT"
else
    log_error "Failed to start Sprint 2 application"
    kill $UVICORN_PID 2>/dev/null || true
    exit 1
fi

# Create Sprint 2 acceptance criteria checklist
log_info "Creating Sprint 2 acceptance criteria checklist..."
cat > "$SPRINT_MERGE_WORKSPACE/SPRINT_2_ACCEPTANCE_CRITERIA.md" << EOF
# Sprint 2 Acceptance Criteria Checklist

## 🎯 Sprint 2 Goals
- Add comprehensive type annotations to Python functions
- Standardize exception handling across the codebase
- Deploy application on port 3000
- Validate acceptance criteria

## ✅ Acceptance Criteria Checklist

### 1. Application Deployment
- [ ] Application runs on port 3000
- [ ] Application accessible at http://localhost:3000
- [ ] No critical errors in startup logs
- [ ] Database initialized successfully

### 2. Type Hints Improvements
- [ ] Python functions have type annotations
- [ ] Return type hints are present
- [ ] Import statements for typing module added
- [ ] Type hints visible in code inspection

### 3. Error Handling Improvements
- [ ] Bare except clauses replaced with specific exceptions
- [ ] Proper error logging implemented
- [ ] Specific exception handlers added
- [ ] Error messages are informative

### 4. Application Functionality
- [ ] All existing features work correctly
- [ ] No regression in functionality
- [ ] API endpoints respond correctly
- [ ] WebSocket connections work
- [ ] Database operations work

### 5. Code Quality
- [ ] All tests pass
- [ ] No syntax errors
- [ ] Code is more maintainable
- [ ] Error handling is consistent

### 6. Visual Indicators
- [ ] Sprint 2 dev indicator visible (purple badge)
- [ ] Port 3000 clearly indicated
- [ ] Type Hints and Error Handling status shown

## 🧪 Testing Instructions

### Manual Testing
1. Visit http://localhost:3000
2. Check for purple "SPRINT 2" indicator in top-right
3. Test all major features:
   - View jams
   - Vote on songs
   - Register as attendee
   - View song details
4. Check browser console for errors
5. Test error scenarios (invalid inputs, etc.)

### Code Inspection
1. Check Python files for type hints
2. Verify exception handling improvements
3. Confirm no bare except clauses
4. Validate import statements

## 📊 Success Metrics
- Application runs without errors
- Type hints improve code readability
- Error handling is more robust
- No functionality regression
- All acceptance criteria met

## 🚀 Next Steps
After validation:
1. Document Sprint 2 results
2. Plan Sprint 3 (next 2-agent sprint)
3. Consider merging to main branch
4. Update QA status report
EOF

log_success "Sprint 2 deployment completed successfully"
log_info "Sprint 2 Application Status:"
log_info "  - URL: http://localhost:$SPRINT_PORT"
log_info "  - Process ID: $UVICORN_PID"
log_info "  - Dev Indicator: Purple Sprint 2 badge"
log_info "  - Features: Type Hints + Error Handling"
log_info "  - Acceptance Criteria: $SPRINT_MERGE_WORKSPACE/SPRINT_2_ACCEPTANCE_CRITERIA.md"

log_info "Next step: Validate Sprint 2 acceptance criteria"
log_info "Visit: http://localhost:$SPRINT_PORT"
log_info "Check: $SPRINT_MERGE_WORKSPACE/SPRINT_2_ACCEPTANCE_CRITERIA.md"
