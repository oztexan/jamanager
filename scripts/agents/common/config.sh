#!/bin/bash
# Common configuration for all agents

# Version information
AGENT_VERSION="2.0.0"
AGENT_PHASE="phase-2"

# Base directories
BASE_DIR="/Users/chrisrobertson/dev"
MAIN_REPO="$BASE_DIR/jamanager"
AGENT_WORKSPACE="$BASE_DIR/jamanager-agents"
MERGE_WORKSPACE="$BASE_DIR/jamanager-merge"

# Agent directories
AGENT_CONSOLE_LOGS="$AGENT_WORKSPACE/agent-console-logs"
AGENT_ACCESSIBILITY="$AGENT_WORKSPACE/agent-accessibility"

# Git configuration
MAIN_BRANCH="main"
FEATURE_BRANCH="feature/agent-hygiene-improvements"
AGENT_BRANCH_PREFIX="feature/agent"

# Remote repository
REMOTE_ORIGIN="https://github.com/oztexan/jamanager.git"

# Logging
LOG_DIR="$BASE_DIR/jamanager-logs"
LOG_FILE="$LOG_DIR/agent-$(date +%Y%m%d-%H%M%S).log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Status indicators
STATUS_SUCCESS="✅"
STATUS_FAILURE="❌"
STATUS_RUNNING="🔄"
STATUS_WAITING="⏳"

# Create log directory
mkdir -p "$LOG_DIR"

# Logging function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Success logging
log_success() {
    log "${GREEN}${STATUS_SUCCESS} $1${NC}"
}

# Error logging
log_error() {
    log "${RED}${STATUS_FAILURE} $1${NC}"
}

# Warning logging
log_warning() {
    log "${YELLOW}⚠️  $1${NC}"
}

# Info logging
log_info() {
    log "${BLUE}ℹ️  $1${NC}"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Validate environment
validate_environment() {
    log_info "Validating environment..."
    
    # Check if git is available
    if ! command_exists git; then
        log_error "Git is not installed"
        exit 1
    fi
    
    # Check if main repo exists
    if [ ! -d "$MAIN_REPO" ]; then
        log_error "Main repository not found at $MAIN_REPO"
        exit 1
    fi
    
    # Check if we're in the right directory
    if [ ! -f "$MAIN_REPO/main.py" ]; then
        log_error "Not in the correct repository directory"
        exit 1
    fi
    
    log_success "Environment validation passed"
}

# Create agent workspace
create_agent_workspace() {
    log_info "Creating agent workspace at $AGENT_WORKSPACE"
    
    if [ -d "$AGENT_WORKSPACE" ]; then
        log_warning "Agent workspace already exists, cleaning up..."
        rm -rf "$AGENT_WORKSPACE"
    fi
    
    mkdir -p "$AGENT_WORKSPACE"
    log_success "Agent workspace created"
}

# Get agent status
get_agent_status() {
    local agent_dir="$1"
    local agent_name="$2"
    
    if [ ! -d "$agent_dir" ]; then
        echo "$STATUS_WAITING Not started"
        return
    fi
    
    cd "$agent_dir" || return 1
    
    if git status --porcelain | grep -q .; then
        echo "$STATUS_RUNNING In progress"
    else
        local last_commit=$(git log --oneline -1 2>/dev/null)
        if [ -n "$last_commit" ]; then
            echo "$STATUS_SUCCESS Completed - $last_commit"
        else
            echo "$STATUS_WAITING Ready"
        fi
    fi
}

# Export functions for use in other scripts
export -f log log_success log_error log_warning log_info
export -f command_exists validate_environment create_agent_workspace get_agent_status
