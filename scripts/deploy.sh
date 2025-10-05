#!/bin/bash

# JaManager Deployment Script
# This script automates the deployment process for JaManager

set -e  # Exit on any error

# Configuration
APP_NAME="jamanager"
APP_DIR="/opt/jamanager"
BACKUP_DIR="/opt/backups"
LOG_FILE="/var/log/jamanager-deploy.log"
SERVICE_NAME="jamanager"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
    exit 1
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        error "This script should not be run as root for security reasons"
    fi
}

# Check system requirements
check_requirements() {
    log "Checking system requirements..."
    
    # Check Python version
    if ! command -v python3.11 &> /dev/null; then
        error "Python 3.11 is required but not installed"
    fi
    
    # Check if virtual environment exists
    if [ ! -d "$APP_DIR/venv" ]; then
        warning "Virtual environment not found, will create one"
    fi
    
    # Check if application directory exists
    if [ ! -d "$APP_DIR" ]; then
        log "Creating application directory: $APP_DIR"
        sudo mkdir -p "$APP_DIR"
        sudo chown $USER:$USER "$APP_DIR"
    fi
    
    success "System requirements check completed"
}

# Backup current deployment
backup_current() {
    log "Creating backup of current deployment..."
    
    if [ -d "$APP_DIR" ] && [ -f "$APP_DIR/jamanager.db" ]; then
        BACKUP_NAME="jamanager_backup_$(date +%Y%m%d_%H%M%S)"
        BACKUP_PATH="$BACKUP_DIR/$BACKUP_NAME"
        
        mkdir -p "$BACKUP_DIR"
        
        # Backup database
        if [ -f "$APP_DIR/jamanager.db" ]; then
            cp "$APP_DIR/jamanager.db" "$BACKUP_PATH.db"
            log "Database backed up to: $BACKUP_PATH.db"
        fi
        
        # Backup uploads
        if [ -d "$APP_DIR/static/uploads" ]; then
            tar -czf "$BACKUP_PATH_uploads.tar.gz" -C "$APP_DIR/static" uploads/
            log "Uploads backed up to: $BACKUP_PATH_uploads.tar.gz"
        fi
        
        # Clean old backups (keep last 7 days)
        find "$BACKUP_DIR" -name "jamanager_backup_*" -mtime +7 -delete
        log "Old backups cleaned up"
        
        success "Backup completed"
    else
        warning "No existing deployment found to backup"
    fi
}

# Deploy application
deploy_app() {
    log "Deploying application..."
    
    # Stop service if running
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        log "Stopping $SERVICE_NAME service..."
        sudo systemctl stop "$SERVICE_NAME"
    fi
    
    # Copy application files
    log "Copying application files..."
    rsync -av --exclude='venv' --exclude='__pycache__' --exclude='*.pyc' \
          --exclude='.git' --exclude='logs' \
          ./ "$APP_DIR/"
    
    # Set up virtual environment
    log "Setting up Python virtual environment..."
    cd "$APP_DIR"
    
    if [ ! -d "venv" ]; then
        python3.11 -m venv venv
    fi
    
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Initialize database
    log "Initializing database..."
    python init_sqlite_db.py
    
    # Set permissions
    log "Setting file permissions..."
    chmod +x "$APP_DIR/run.py"
    chmod +x "$APP_DIR/start_fresh.py"
    
    # Create necessary directories
    mkdir -p "$APP_DIR/static/uploads"
    mkdir -p "$APP_DIR/logs"
    
    success "Application deployed successfully"
}

# Configure systemd service
setup_service() {
    log "Configuring systemd service..."
    
    # Create systemd service file
    sudo tee /etc/systemd/system/$SERVICE_NAME.service > /dev/null <<EOF
[Unit]
Description=JaManager FastAPI Application
After=network.target

[Service]
Type=exec
User=$USER
Group=$USER
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
Environment=DATABASE_URL=sqlite+aiosqlite:///./data/development/jamanager.db
Environment=JAM_MANAGER_ACCESS_CODE=\${JAM_MANAGER_ACCESS_CODE:-jam2024}
ExecStart=$APP_DIR/venv/bin/uvicorn jamanager.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
    
    # Reload systemd and enable service
    sudo systemctl daemon-reload
    sudo systemctl enable "$SERVICE_NAME"
    
    success "Systemd service configured"
}

# Configure Nginx
setup_nginx() {
    log "Configuring Nginx..."
    
    # Check if Nginx is installed
    if ! command -v nginx &> /dev/null; then
        warning "Nginx not installed, skipping Nginx configuration"
        return
    fi
    
    # Create Nginx configuration
    sudo tee /etc/nginx/sites-available/$APP_NAME > /dev/null <<EOF
server {
    listen 80;
    server_name _;
    
    client_max_body_size 10M;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
    }
    
    location /static/ {
        alias $APP_DIR/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF
    
    # Enable site
    sudo ln -sf /etc/nginx/sites-available/$APP_NAME /etc/nginx/sites-enabled/
    sudo nginx -t
    sudo systemctl reload nginx
    
    success "Nginx configured"
}

# Start services
start_services() {
    log "Starting services..."
    
    # Start application service
    sudo systemctl start "$SERVICE_NAME"
    
    # Wait for service to start
    sleep 5
    
    # Check if service is running
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        success "Application service started successfully"
    else
        error "Failed to start application service"
    fi
    
    # Check health endpoint
    log "Checking application health..."
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        success "Application is healthy and responding"
    else
        warning "Health check failed, but service is running"
    fi
}

# Setup monitoring
setup_monitoring() {
    log "Setting up monitoring..."
    
    # Create log rotation configuration
    sudo tee /etc/logrotate.d/$APP_NAME > /dev/null <<EOF
$APP_DIR/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 $USER $USER
    postrotate
        systemctl reload $SERVICE_NAME
    endscript
}
EOF
    
    # Create backup script
    tee "$APP_DIR/backup.sh" > /dev/null <<EOF
#!/bin/bash
# Automated backup script for JaManager

DATE=\$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="$BACKUP_DIR"
DB_FILE="$APP_DIR/jamanager.db"

mkdir -p \$BACKUP_DIR

# Backup database
if [ -f "\$DB_FILE" ]; then
    cp "\$DB_FILE" "\$BACKUP_DIR/jamanager_\$DATE.db"
    echo "Database backed up: jamanager_\$DATE.db"
fi

# Backup uploads
if [ -d "$APP_DIR/static/uploads" ]; then
    tar -czf "\$BACKUP_DIR/uploads_\$DATE.tar.gz" -C "$APP_DIR/static" uploads/
    echo "Uploads backed up: uploads_\$DATE.tar.gz"
fi

# Clean old backups (keep last 7 days)
find "\$BACKUP_DIR" -name "jamanager_*.db" -mtime +7 -delete
find "\$BACKUP_DIR" -name "uploads_*.tar.gz" -mtime +7 -delete

echo "Backup completed: \$DATE"
EOF
    
    chmod +x "$APP_DIR/backup.sh"
    
    # Add to crontab for daily backups
    (crontab -l 2>/dev/null; echo "0 2 * * * $APP_DIR/backup.sh >> $APP_DIR/logs/backup.log 2>&1") | crontab -
    
    success "Monitoring and backup configured"
}

# Main deployment function
main() {
    log "Starting JaManager deployment..."
    
    check_root
    check_requirements
    backup_current
    deploy_app
    setup_service
    setup_nginx
    start_services
    setup_monitoring
    
    success "Deployment completed successfully!"
    
    echo ""
    echo "🎉 JaManager has been deployed successfully!"
    echo ""
    echo "📍 Application URL: http://localhost:8000"
    echo "📍 Health Check: http://localhost:8000/health"
    echo "📍 API Docs: http://localhost:8000/docs"
    echo ""
    echo "🔧 Management Commands:"
    echo "  sudo systemctl status $SERVICE_NAME    # Check service status"
    echo "  sudo systemctl restart $SERVICE_NAME   # Restart service"
    echo "  sudo systemctl stop $SERVICE_NAME      # Stop service"
    echo "  sudo journalctl -u $SERVICE_NAME -f    # View logs"
    echo ""
    echo "📊 Backup:"
    echo "  $APP_DIR/backup.sh                     # Manual backup"
    echo "  Daily backups at 2 AM (configured in crontab)"
    echo ""
    echo "⚠️  Don't forget to:"
    echo "  1. Set JAM_MANAGER_ACCESS_CODE environment variable"
    echo "  2. Configure SSL certificate for production"
    echo "  3. Set up proper firewall rules"
    echo "  4. Configure monitoring and alerting"
}

# Run main function
main "$@"