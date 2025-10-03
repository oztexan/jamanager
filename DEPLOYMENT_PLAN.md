# JaManager Deployment Plan

**Date:** December 2024  
**Project:** JaManager - Jam Session Management Application  
**Version:** 1.0.0

## 🎯 Overview

This document provides a comprehensive deployment plan for the JaManager application, a real-time jam session management system built with FastAPI and vanilla JavaScript. The application features WebSocket support, SQLite database, and a responsive frontend.

## 📊 Current Application State

### Architecture Summary
- **Backend:** FastAPI with SQLite database
- **Frontend:** Vanilla JavaScript with responsive design
- **Database:** SQLite file-based (zero configuration)
- **Real-time:** WebSocket connections for live updates
- **Authentication:** Access code-based system
- **File Storage:** Local file system for uploads

### Key Features
- ✅ Real-time voting and song queue management
- ✅ WebSocket support for live updates
- ✅ QR code generation for jam sessions
- ✅ Image upload handling
- ✅ Ultimate Guitar integration for chord sheets
- ✅ Role-based access control
- ✅ Feature flag system
- ✅ Responsive design for mobile/desktop

## 🚀 Deployment Strategies

### 1. Docker Deployment (Recommended)

#### Prerequisites
- Docker and Docker Compose installed
- Domain name (optional, for production)
- SSL certificate (for HTTPS)

#### Quick Start
```bash
# Clone repository
git clone <repository-url>
cd jamanager

# Copy environment configuration
cp env.example .env

# Start with Docker Compose
docker-compose up -d

# Check logs
docker-compose logs -f app
```

#### Production Docker Setup
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "80:8000"
    environment:
      - DATABASE_URL=sqlite+aiosqlite:///./jamanager.db
      - JAM_MANAGER_ACCESS_CODE=${JAM_MANAGER_ACCESS_CODE}
      - PORT=8000
    volumes:
      - ./static/uploads:/app/static/uploads
      - ./data:/app/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - app
    restart: unless-stopped
```

### 2. Cloud Platform Deployment

#### Heroku Deployment
```bash
# Install Heroku CLI
# Create Procfile
echo "web: uvicorn jamanager.main:app --host 0.0.0.0 --port \$PORT" > Procfile

# Deploy
heroku create jamanager-app
heroku config:set JAM_MANAGER_ACCESS_CODE=your-secure-code
git push heroku main
```

#### Railway Deployment
```bash
# Connect GitHub repository
# Set environment variables in Railway dashboard
# Deploy automatically on git push
```

#### DigitalOcean App Platform
```yaml
# .do/app.yaml
name: jamanager
services:
- name: web
  source_dir: /
  github:
    repo: your-username/jamanager
    branch: main
  run_command: uvicorn jamanager.main:app --host 0.0.0.0 --port $PORT
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: JAM_MANAGER_ACCESS_CODE
    value: your-secure-code
```

### 3. VPS/Server Deployment

#### Ubuntu/Debian Server Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo apt install python3.11 python3.11-venv python3.11-dev -y

# Install system dependencies
sudo apt install nginx supervisor sqlite3 -y

# Clone application
git clone <repository-url> /opt/jamanager
cd /opt/jamanager

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python init_sqlite_db.py

# Configure systemd service
sudo cp jamanager.service /etc/systemd/system/
sudo systemctl enable jamanager
sudo systemctl start jamanager

# Configure Nginx
sudo cp nginx.conf /etc/nginx/sites-available/jamanager
sudo ln -s /etc/nginx/sites-available/jamanager /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 🔧 Production Configuration

### Environment Variables
```bash
# Required
DATABASE_URL=sqlite+aiosqlite:///./jamanager.db
JAM_MANAGER_ACCESS_CODE=your-secure-access-code
PORT=8000

# Optional
ENABLE_ACCESS_CODE=true
CORS_ORIGINS=["https://yourdomain.com"]
LOG_LEVEL=info
```

### Security Configuration
```python
# app/core/config.py
class Settings(BaseSettings):
    # Security
    jam_manager_access_code: str = "jam2024"
    enable_access_code: bool = True
    
    # CORS
    cors_origins: list[str] = ["*"]  # Restrict in production
    
    # Database
    database_url: str = "sqlite+aiosqlite:///./jamanager.db"
    
    # File uploads
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: list[str] = ["image/jpeg", "image/png", "image/gif"]
    
    class Config:
        env_file = ".env"
```

### Nginx Configuration
```nginx
# nginx.conf
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    client_max_body_size 10M;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
    
    location /static/ {
        alias /opt/jamanager/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### Systemd Service
```ini
# jamanager.service
[Unit]
Description=JaManager FastAPI Application
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/opt/jamanager
Environment=PATH=/opt/jamanager/venv/bin
ExecStart=/opt/jamanager/venv/bin/uvicorn jamanager.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

## 📊 Monitoring & Health Checks

### Health Check Endpoint
```python
# Add to jamanager/main.py
@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers."""
    try:
        # Check database connection
        async with get_database() as db:
            await db.execute("SELECT 1")
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0"
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )
```

### Monitoring Setup
```bash
# Install monitoring tools
pip install prometheus-client

# Add to requirements.txt
prometheus-client==0.19.0
```

### Logging Configuration
```python
# app/core/logging.py
import logging
import sys
from pathlib import Path

def setup_logging(log_level: str = "INFO"):
    """Configure application logging."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_dir / "jamanager.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
```

## 🔒 Security Checklist

### Pre-Deployment Security
- [ ] Change default access code from `jam2024`
- [ ] Set up HTTPS with valid SSL certificate
- [ ] Configure CORS origins for production domain
- [ ] Set up rate limiting for API endpoints
- [ ] Enable request logging and monitoring
- [ ] Configure firewall rules
- [ ] Set up automated backups
- [ ] Review and update dependencies

### Runtime Security
- [ ] Monitor application logs for suspicious activity
- [ ] Regular security updates for system packages
- [ ] Database backup verification
- [ ] SSL certificate renewal monitoring
- [ ] Access log analysis

## 📈 Performance Optimization

### Database Optimization
```sql
-- Add indexes for better performance
CREATE INDEX IF NOT EXISTS idx_jam_songs_jam_id ON jam_songs(jam_id);
CREATE INDEX IF NOT EXISTS idx_votes_song_id ON votes(song_id);
CREATE INDEX IF NOT EXISTS idx_attendees_jam_id ON attendees(jam_id);
```

### Static File Optimization
```python
# Add to FastAPI app
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)
```

### Caching Strategy
```python
# Add Redis for caching (optional)
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

# Configure Redis caching
FastAPICache.init(RedisBackend(), prefix="jamanager-cache")
```

## 🚀 Deployment Checklist

### Pre-Deployment
- [ ] Code review completed
- [ ] All tests passing
- [ ] Security review completed
- [ ] Performance testing done
- [ ] Backup strategy implemented
- [ ] Monitoring configured
- [ ] SSL certificates obtained
- [ ] Domain DNS configured

### Deployment Steps
1. [ ] Deploy to staging environment
2. [ ] Run integration tests
3. [ ] Performance testing
4. [ ] Security scanning
5. [ ] Deploy to production
6. [ ] Verify health checks
7. [ ] Monitor application logs
8. [ ] Test all functionality

### Post-Deployment
- [ ] Monitor application performance
- [ ] Check error rates
- [ ] Verify backup processes
- [ ] Update documentation
- [ ] Notify stakeholders
- [ ] Schedule regular maintenance

## 🔄 Backup & Recovery

### Database Backup
```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/backups"
DB_FILE="/opt/jamanager/jamanager.db"

mkdir -p $BACKUP_DIR
cp $DB_FILE $BACKUP_DIR/jamanager_$DATE.db

# Keep only last 7 days of backups
find $BACKUP_DIR -name "jamanager_*.db" -mtime +7 -delete
```

### File Upload Backup
```bash
#!/bin/bash
# backup_uploads.sh
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/backups/uploads"
UPLOADS_DIR="/opt/jamanager/static/uploads"

mkdir -p $BACKUP_DIR
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz -C $UPLOADS_DIR .

# Keep only last 30 days of upload backups
find $BACKUP_DIR -name "uploads_*.tar.gz" -mtime +30 -delete
```

## 📞 Support & Maintenance

### Regular Maintenance Tasks
- Weekly: Review application logs
- Monthly: Update dependencies
- Quarterly: Security audit
- Annually: SSL certificate renewal

### Troubleshooting Guide
1. **Application won't start**: Check logs, verify database file permissions
2. **WebSocket connections failing**: Check firewall, proxy configuration
3. **File uploads not working**: Verify directory permissions, disk space
4. **Database errors**: Check file permissions, disk space, corruption

### Contact Information
- **Technical Issues**: [Your contact info]
- **Security Issues**: [Security contact]
- **Emergency**: [Emergency contact]

---

## 📋 Quick Reference

### Common Commands
```bash
# Start development server
python start_fresh.py

# Start with Docker
docker-compose up -d

# Check application health
curl http://localhost:8000/health

# View logs
docker-compose logs -f app

# Backup database
cp jamanager.db jamanager_backup_$(date +%Y%m%d).db
```

### Important URLs
- **Application**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Admin Access**: Use access code from environment variables

This deployment plan provides a comprehensive guide for deploying JaManager in various environments while maintaining security, performance, and reliability.