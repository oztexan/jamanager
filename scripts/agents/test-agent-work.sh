#!/bin/bash
# Comprehensive test script to validate agent work

# Load common configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common/config.sh"

log_info "Starting comprehensive agent work validation"
log_info "Version: $AGENT_VERSION"

# Test results tracking
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Test function
run_test() {
    local test_name="$1"
    local test_command="$2"
    local expected_result="$3"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    log_info "Running test: $test_name"
    
    if eval "$test_command"; then
        log_success "✅ $test_name PASSED"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        log_error "❌ $test_name FAILED"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

echo ""
echo "=== Agent Work Validation Report ==="
echo "Generated: $(date)"
echo "Version: $AGENT_VERSION"
echo ""

# Test 1: Console Logs Agent Work
echo "## Console Logs Agent Validation"
echo ""

if [ -d "$AGENT_CONSOLE_LOGS" ]; then
    cd "$AGENT_CONSOLE_LOGS" || exit 1
    
    # Test console.log removal
    console_logs_remaining=$(find . -name "*.js" -exec grep -c "console\.log" {} \; | awk '{sum += $1} END {print sum}')
    
    if [ "$console_logs_remaining" -eq 0 ]; then
        log_success "✅ Console Logs Agent: All console.log statements removed"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        log_error "❌ Console Logs Agent: $console_logs_remaining console.log statements remaining"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    # Test application functionality after console.log removal
    log_info "Testing application functionality after console.log removal..."
    setup_python_environment
    
    if python -m pytest tests/ -v --tb=short >/dev/null 2>&1; then
        log_success "✅ Console Logs Agent: Application tests pass after changes"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        log_error "❌ Console Logs Agent: Application tests fail after changes"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    # Show files modified
    files_modified=$(git diff --name-only HEAD~1 | wc -l | tr -d ' ')
    log_info "Files modified by Console Logs Agent: $files_modified"
    
else
    log_error "❌ Console Logs Agent workspace not found"
    FAILED_TESTS=$((FAILED_TESTS + 1))
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
fi

echo ""

# Test 2: Accessibility Agent Work
echo "## Accessibility Agent Validation"
echo ""

if [ -d "$AGENT_ACCESSIBILITY" ]; then
    cd "$AGENT_ACCESSIBILITY" || exit 1
    
    # Test ARIA labels
    aria_labels=$(find . -name "*.html" -exec grep -c "aria-label" {} \; | awk '{sum += $1} END {print sum}')
    
    if [ "$aria_labels" -gt 0 ]; then
        log_success "✅ Accessibility Agent: $aria_labels ARIA labels added"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        log_error "❌ Accessibility Agent: No ARIA labels found"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    # Test tabindex elements
    tabindex_elements=$(find . -name "*.html" -exec grep -c "tabindex" {} \; | awk '{sum += $1} END {print sum}')
    
    if [ "$tabindex_elements" -gt 0 ]; then
        log_success "✅ Accessibility Agent: $tabindex_elements tabindex elements added"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        log_error "❌ Accessibility Agent: No tabindex elements found"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    # Test focus indicators
    focus_indicators=$(find . -name "*.css" -exec grep -c "focus" {} \; | awk '{sum += $1} END {print sum}')
    
    if [ "$focus_indicators" -gt 0 ]; then
        log_success "✅ Accessibility Agent: $focus_indicators focus indicators added"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        log_error "❌ Accessibility Agent: No focus indicators found"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    # Test application functionality after accessibility changes
    log_info "Testing application functionality after accessibility changes..."
    setup_python_environment
    
    if python -m pytest tests/ -v --tb=short >/dev/null 2>&1; then
        log_success "✅ Accessibility Agent: Application tests pass after changes"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        log_error "❌ Accessibility Agent: Application tests fail after changes"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    # Show files modified
    files_modified=$(git diff --name-only HEAD~1 | wc -l | tr -d ' ')
    log_info "Files modified by Accessibility Agent: $files_modified"
    
else
    log_error "❌ Accessibility Agent workspace not found"
    FAILED_TESTS=$((FAILED_TESTS + 3))
    TOTAL_TESTS=$((TOTAL_TESTS + 3))
fi

echo ""

# Test 3: Merge Workspace Validation
echo "## Merge Workspace Validation"
echo ""

if [ -d "$MERGE_WORKSPACE" ]; then
    cd "$MERGE_WORKSPACE" || exit 1
    
    # Test that merge workspace has both agent changes
    log_info "Checking merge workspace for combined changes..."
    
    # Check for console.log removal in merge
    merge_console_logs=$(find . -name "*.js" -exec grep -c "console\.log" {} \; | awk '{sum += $1} END {print sum}')
    
    if [ "$merge_console_logs" -eq 0 ]; then
        log_success "✅ Merge Workspace: Console.log statements removed"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        log_warning "⚠️  Merge Workspace: $merge_console_logs console.log statements remaining"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    # Check for accessibility improvements in merge
    merge_aria_labels=$(find . -name "*.html" -exec grep -c "aria-label" {} \; | awk '{sum += $1} END {print sum}')
    
    if [ "$merge_aria_labels" -gt 0 ]; then
        log_success "✅ Merge Workspace: $merge_aria_labels ARIA labels present"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        log_warning "⚠️  Merge Workspace: No ARIA labels found"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    # Test merge workspace functionality
    log_info "Testing merge workspace functionality..."
    setup_python_environment
    
    if python -m pytest tests/ -v --tb=short >/dev/null 2>&1; then
        log_success "✅ Merge Workspace: Application tests pass"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        log_error "❌ Merge Workspace: Application tests fail"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
else
    log_error "❌ Merge workspace not found"
    FAILED_TESTS=$((FAILED_TESTS + 3))
    TOTAL_TESTS=$((TOTAL_TESTS + 3))
fi

echo ""

# Summary
echo "## Test Summary"
echo ""
echo "Total Tests: $TOTAL_TESTS"
echo "Passed: $PASSED_TESTS"
echo "Failed: $FAILED_TESTS"

if [ $FAILED_TESTS -eq 0 ]; then
    log_success "🎉 All agent work validation tests PASSED!"
    echo ""
    echo "✅ Console Logs Agent: Successfully removed console.log statements"
    echo "✅ Accessibility Agent: Successfully added accessibility improvements"
    echo "✅ Application Functionality: All tests pass after agent changes"
    echo "✅ Merge Workspace: Successfully combines both agent changes"
    echo ""
    echo "The agents are working correctly and producing the expected results!"
    exit 0
else
    log_error "❌ Some agent work validation tests FAILED!"
    echo ""
    echo "Please review the failed tests above and check agent configurations."
    exit 1
fi




