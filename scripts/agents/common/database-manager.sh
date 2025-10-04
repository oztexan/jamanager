#!/bin/bash
# Database Management for Agent System

# Load common configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/config.sh"

# Database management functions
MASTER_DB="$MAIN_REPO/jamanager.db"
SHARED_DB="$WORKZONE_DIR/shared-database.db"

# Create shared database directory
mkdir -p "$WORKZONE_DIR/shared-database"

log_info "Database Manager - Agent System"
log_info "Master DB: $MASTER_DB"
log_info "Shared DB: $SHARED_DB"

# Function to copy database
copy_database() {
    local source="$1"
    local destination="$2"
    
    if [ -f "$source" ]; then
        log_info "Copying database from $source to $destination"
        cp "$source" "$destination"
        log_success "Database copied successfully"
    else
        log_error "Source database not found: $source"
        return 1
    fi
}

# Function to sync master database to shared location
sync_master_to_shared() {
    log_info "Syncing master database to shared location..."
    copy_database "$MASTER_DB" "$SHARED_DB"
}

# Function to sync shared database to workspace
sync_shared_to_workspace() {
    local workspace_dir="$1"
    local workspace_db="$workspace_dir/jamanager.db"
    
    log_info "Syncing shared database to workspace: $workspace_dir"
    copy_database "$SHARED_DB" "$workspace_db"
}

# Function to sync workspace database back to shared
sync_workspace_to_shared() {
    local workspace_dir="$1"
    local workspace_db="$workspace_dir/jamanager.db"
    
    log_info "Syncing workspace database to shared: $workspace_dir"
    copy_database "$workspace_db" "$SHARED_DB"
}

# Function to sync shared database back to master
sync_shared_to_master() {
    log_info "Syncing shared database back to master..."
    copy_database "$SHARED_DB" "$MASTER_DB"
}

# Function to setup fresh database for workspace
setup_fresh_database() {
    local workspace_dir="$1"
    local workspace_db="$workspace_dir/jamanager.db"
    
    log_info "Setting up fresh database for workspace: $workspace_dir"
    
    # Remove existing database
    if [ -f "$workspace_db" ]; then
        rm "$workspace_db"
        log_info "Removed existing workspace database"
    fi
    
    # Copy from shared
    copy_database "$SHARED_DB" "$workspace_db"
}

# Function to initialize shared database with dev data
init_shared_database() {
    log_info "Initializing shared database with development data..."
    
    # Copy master database to shared
    sync_master_to_shared
    
    # Initialize with dev data if needed
    if [ -f "$MAIN_REPO/init_dev_database.py" ]; then
        log_info "Running database initialization..."
        cd "$MAIN_REPO"
        source "$SCRIPT_DIR/config.sh"
        setup_python_environment
        
        # Update database path for initialization
        export DATABASE_URL="sqlite+aiosqlite:///$SHARED_DB"
        python init_dev_database.py
        
        log_success "Shared database initialized with development data"
    fi
}

# Function to get database status
get_database_status() {
    echo ""
    echo "=== Database Status ==="
    echo "Master DB: $MASTER_DB"
    if [ -f "$MASTER_DB" ]; then
        echo "  Status: ✅ Exists ($(stat -f%z "$MASTER_DB" 2>/dev/null || stat -c%s "$MASTER_DB" 2>/dev/null) bytes)"
    else
        echo "  Status: ❌ Not found"
    fi
    
    echo "Shared DB: $SHARED_DB"
    if [ -f "$SHARED_DB" ]; then
        echo "  Status: ✅ Exists ($(stat -f%z "$SHARED_DB" 2>/dev/null || stat -c%s "$SHARED_DB" 2>/dev/null) bytes)"
    else
        echo "  Status: ❌ Not found"
    fi
    
    echo ""
    echo "=== Workspace Databases ==="
    for workspace in "$AGENT_WORKSPACE"/*; do
        if [ -d "$workspace" ]; then
            workspace_name=$(basename "$workspace")
            workspace_db="$workspace/jamanager.db"
            if [ -f "$workspace_db" ]; then
                echo "  $workspace_name: ✅ Exists ($(stat -f%z "$workspace_db" 2>/dev/null || stat -c%s "$workspace_db" 2>/dev/null) bytes)"
            else
                echo "  $workspace_name: ❌ Not found"
            fi
        fi
    done
    
    if [ -d "$MERGE_WORKSPACE" ]; then
        merge_db="$MERGE_WORKSPACE/jamanager.db"
        if [ -f "$merge_db" ]; then
            echo "  merge-workspace: ✅ Exists ($(stat -f%z "$merge_db" 2>/dev/null || stat -c%s "$merge_db" 2>/dev/null) bytes)"
        else
            echo "  merge-workspace: ❌ Not found"
        fi
    fi
}

# Main function
case "${1:-status}" in
    "init")
        init_shared_database
        ;;
    "sync-master-to-shared")
        sync_master_to_shared
        ;;
    "sync-shared-to-workspace")
        if [ -z "$2" ]; then
            log_error "Workspace directory required"
            exit 1
        fi
        sync_shared_to_workspace "$2"
        ;;
    "sync-workspace-to-shared")
        if [ -z "$2" ]; then
            log_error "Workspace directory required"
            exit 1
        fi
        sync_workspace_to_shared "$2"
        ;;
    "sync-shared-to-master")
        sync_shared_to_master
        ;;
    "setup-fresh")
        if [ -z "$2" ]; then
            log_error "Workspace directory required"
            exit 1
        fi
        setup_fresh_database "$2"
        ;;
    "status")
        get_database_status
        ;;
    *)
        echo "Usage: $0 {init|sync-master-to-shared|sync-shared-to-workspace|sync-workspace-to-shared|sync-shared-to-master|setup-fresh|status}"
        echo ""
        echo "Commands:"
        echo "  init                    - Initialize shared database with dev data"
        echo "  sync-master-to-shared   - Copy master DB to shared location"
        echo "  sync-shared-to-workspace <dir> - Copy shared DB to workspace"
        echo "  sync-workspace-to-shared <dir> - Copy workspace DB to shared"
        echo "  sync-shared-to-master   - Copy shared DB back to master"
        echo "  setup-fresh <dir>       - Setup fresh DB for workspace"
        echo "  status                  - Show database status"
        exit 1
        ;;
esac




