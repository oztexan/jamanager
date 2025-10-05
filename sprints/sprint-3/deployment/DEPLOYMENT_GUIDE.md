# 🚀 Sprint 3 Deployment Guide: Australia-Optimized

## 📋 **Quick Start**

### **Option 1: Railway (Recommended)**
```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login to Railway
railway login

# 3. Run deployment script
bash sprints/sprint-3/deployment/deploy.sh
```

### **Option 2: Render**
```bash
# 1. Connect GitHub repository to Render
# 2. Use render.yaml configuration
# 3. Deploy automatically
```

## 🎯 **Detailed Deployment Steps**

### **Railway Deployment (Recommended)**

#### **Prerequisites**
- Railway account (free)
- Railway CLI installed
- Git repository connected

#### **Step-by-Step Process**

1. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway**
   ```bash
   railway login
   ```

3. **Run Deployment Script**
   ```bash
   bash sprints/sprint-3/deployment/deploy.sh
   ```

4. **Manual Steps (if script fails)**
   ```bash
   # Create project
   railway project new jamanager-australia
   
   # Add PostgreSQL
   railway add postgresql
   
   # Set environment variables
   railway variables set ENVIRONMENT=production
   railway variables set DEBUG=false
   railway variables set SECRET_KEY=$(openssl rand -hex 32)
   railway variables set JAM_MANAGER_ACCESS_CODE=$(openssl rand -hex 16)
   
   # Deploy
   railway up
   
   # Run migration
   railway run python sprints/sprint-3/deployment/migrate_to_postgresql.py
   ```

### **Render Deployment (Alternative)**

#### **Prerequisites**
- Render account (free)
- GitHub repository

#### **Step-by-Step Process**

1. **Connect Repository**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

2. **Configure Service**
   - Use the `render.yaml` configuration
   - Or manually configure:
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
     - **Health Check Path**: `/api/system/health`

3. **Add Database**
   - Add PostgreSQL database
   - Note the connection string

4. **Set Environment Variables**
   - `ENVIRONMENT=production`
   - `DEBUG=false`
   - `SECRET_KEY=<generate-random-key>`
   - `JAM_MANAGER_ACCESS_CODE=<generate-random-code>`

5. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment to complete

6. **Run Migration**
   - Use Render shell to run migration script

## 🔧 **Environment Configuration**

### **Required Environment Variables**

```bash
# Environment
ENVIRONMENT=production
DEBUG=false

# Security
SECRET_KEY=your-super-secret-production-key
JAM_MANAGER_ACCESS_CODE=your-production-access-code

# Performance
DATABASE_POOL_SIZE=20
CACHE_ENABLED=true
CACHE_DEFAULT_TTL=300

# WebSocket
WEBSOCKET_ENABLED=true

# Logging
LOG_LEVEL=INFO
```

### **Database Configuration**
- **Development**: SQLite (local)
- **Production**: PostgreSQL (Railway/Render)
- **Migration**: Automatic via script

## 📊 **Performance Optimization for Australia**

### **Railway Advantages**
- ✅ AWS infrastructure with Sydney region
- ✅ Global CDN
- ✅ Automatic HTTPS
- ✅ Database included
- ✅ Environment variables
- ✅ Git-based deployments

### **Expected Performance**
- **Page Load Time**: < 2 seconds from Sydney
- **API Response Time**: < 200ms average
- **Database Queries**: Optimized with indexes
- **Caching**: In-memory cache active

## 🔍 **Testing & Verification**

### **Health Checks**
```bash
# Check application health
curl https://your-app.railway.app/api/system/health

# Check system stats
curl https://your-app.railway.app/api/system/stats

# Test API endpoints
curl https://your-app.railway.app/api/jams
curl https://your-app.railway.app/api/songs
```

### **Performance Testing**
```bash
# Run performance test
bash sprints/sprint-3/scripts/simple-performance-test.sh
```

### **User Acceptance Testing**
1. **Home Page**: Loads quickly, dev indicator shows
2. **Jam Pages**: All functionality works
3. **Voting**: Heart buttons work correctly
4. **Registration**: Attendee registration works
5. **Boss Features**: Access code entry works
6. **Breadcrumbs**: Navigation works for bosses

## 🚨 **Troubleshooting**

### **Common Issues**

#### **Database Connection Errors**
```bash
# Check database URL
railway variables

# Test database connection
railway run python -c "import os; print(os.getenv('DATABASE_URL'))"
```

#### **Migration Failures**
```bash
# Run migration manually
railway run python sprints/sprint-3/deployment/migrate_to_postgresql.py

# Check logs
railway logs
```

#### **Environment Variable Issues**
```bash
# List all variables
railway variables

# Set missing variables
railway variables set VARIABLE_NAME=value
```

### **Performance Issues**
- Check Railway dashboard for resource usage
- Monitor database connection pool
- Verify caching is enabled
- Check for slow queries in logs

## 📈 **Monitoring & Maintenance**

### **Railway Dashboard**
- Monitor CPU, memory, and network usage
- View deployment logs
- Check database performance
- Monitor environment variables

### **Application Monitoring**
- Health check endpoint: `/api/system/health`
- System stats: `/api/system/stats`
- Event system: `/api/system/events`

### **Maintenance Tasks**
- Regular database backups
- Monitor performance metrics
- Update dependencies
- Security updates

## 🔒 **Security Considerations**

### **Production Security**
- Strong, unique access codes
- HTTPS enforced
- Environment variables for secrets
- Database encryption
- CORS properly configured

### **Data Protection**
- Regular backups
- Data retention policies
- Privacy compliance
- Secure file uploads

## 💰 **Cost Management**

### **Free Tier Limits**
- **Railway**: $5/month credit (usually free for small apps)
- **Render**: 750 hours/month (sleeps after inactivity)

### **Scaling Costs**
- Monitor usage in dashboard
- Upgrade when needed
- Optimize for efficiency

## 🎯 **Success Criteria**

### **Technical Success**
- [ ] Application deploys successfully
- [ ] All Sprint 3 features work
- [ ] Performance targets met
- [ ] Database migration successful
- [ ] SSL/HTTPS working

### **User Experience Success**
- [ ] Fast loading from Australia
- [ ] All functionality accessible
- [ ] Mobile responsive
- [ ] Error-free interactions

---

**Last Updated**: 2025-10-05
**Status**: 📋 **READY FOR DEPLOYMENT**
