# 🚀 Mini-Sprint: PostgreSQL Development Setup

## 🎯 **Goal**
Set up PostgreSQL locally using Podman to match the production stack, test migration, and populate with dev data.

## 📋 **What This Mini-Sprint Does**

1. **Sets up PostgreSQL container** using Podman
2. **Tests migration script** (SQLite → PostgreSQL)
3. **Populates with dev data** using existing scripts
4. **Tests application** with PostgreSQL backend
5. **Updates dev environment** to use PostgreSQL

## 🚀 **Quick Start**

### **Automated (Recommended)**
```bash
# Run the complete mini-sprint
bash sprints/mini-sprint-postgres/run-mini-sprint.sh
```

This will:
- Set up PostgreSQL container
- Update environment configuration
- Test migration script
- Populate with dev data
- Start application with PostgreSQL
- Run comprehensive tests

### **Manual Steps**
```bash
# 1. Set up PostgreSQL container
bash sprints/mini-sprint-postgres/setup-postgres.sh

# 2. Update environment for PostgreSQL
bash sprints/mini-sprint-postgres/update-env-for-postgres.sh

# 3. Test migration (if SQLite data exists)
python sprints/sprint-3/deployment/migrate_to_postgresql.py

# 4. Populate with dev data
python sprints/mini-sprint-postgres/populate-postgres-dev-data.py

# 5. Start application
uvicorn main:app --host 0.0.0.0 --port 3000 --reload

# 6. Run tests
python sprints/mini-sprint-postgres/test-postgres-app.py
```

## 🐘 **PostgreSQL Configuration**

### **Container Details**
- **Container Name**: `jamanager-postgres`
- **Database**: `jamanager_dev`
- **Username**: `jamanager`
- **Password**: `jamanager_dev_password`
- **Port**: `5432`
- **Data Volume**: `jamanager-postgres-data`

### **Connection URL**
```
postgresql+asyncpg://jamanager:jamanager_dev_password@localhost:5432/jamanager_dev
```

## 📊 **Development Data**

The PostgreSQL database will be populated with:
- **4 Venues** (The Underground, Acoustic Corner, Jazz & Blues Club, Pop Central)
- **25 Songs** (across different genres)
- **5 Jams** (including today's jam)
- **5 Attendees** (with different instruments and skill levels)
- **Jam-Song relationships** (songs assigned to jams)
- **Sample votes** (attendees voting for songs)
- **Performance registrations** (attendees registered to perform)
- **Chord sheets** (sample chord sheet data)

## 🧪 **Testing**

### **Automated Tests**
The test suite verifies:
- ✅ Database connection
- ✅ API endpoints responding
- ✅ Jam details working
- ✅ Performance acceptable
- ✅ All Sprint 3 features functional

### **Manual Testing**
After setup, you can test:
- Home page loads correctly
- Jam pages work with PostgreSQL
- Voting functionality works
- Attendee registration works
- Boss features work
- Breadcrumb navigation works

## 🔧 **Management Commands**

### **PostgreSQL Container**
```bash
# Start container
podman start jamanager-postgres

# Stop container
podman stop jamanager-postgres

# Restart container
podman restart jamanager-postgres

# View logs
podman logs jamanager-postgres

# Access PostgreSQL shell
podman exec -it jamanager-postgres psql -U jamanager -d jamanager_dev
```

### **Application**
```bash
# Start application
uvicorn main:app --host 0.0.0.0 --port 3000 --reload

# Stop application
pkill -f uvicorn

# View application logs
tail -f app.log
```

## 🔄 **Switching Between Databases**

### **Use PostgreSQL (Current)**
```bash
# Already configured after running mini-sprint
# Just start the application
uvicorn main:app --host 0.0.0.0 --port 3000 --reload
```

### **Switch Back to SQLite**
```bash
# Restore SQLite configuration
cp .env.sqlite.backup .env

# Stop application
pkill -f uvicorn

# Start with SQLite
uvicorn main:app --host 0.0.0.0 --port 3000 --reload
```

## 📁 **Files Created**

```
sprints/mini-sprint-postgres/
├── MINI_SPRINT_PLAN.md              # This plan
├── README.md                        # This file
├── run-mini-sprint.sh              # Complete automation script
├── setup-postgres.sh               # PostgreSQL container setup
├── update-env-for-postgres.sh      # Environment configuration
├── populate-postgres-dev-data.py   # Dev data population
└── test-postgres-app.py            # Comprehensive testing
```

## 🎯 **Success Criteria**

- [ ] PostgreSQL container running locally
- [ ] Migration script works without errors
- [ ] Dev data populated successfully
- [ ] Application works with PostgreSQL
- [ ] All Sprint 3 features functional
- [ ] Performance comparable to SQLite

## 🚨 **Troubleshooting**

### **Container Issues**
```bash
# Check container status
podman ps -a

# Check container logs
podman logs jamanager-postgres

# Remove and recreate container
podman rm -f jamanager-postgres
bash sprints/mini-sprint-postgres/setup-postgres.sh
```

### **Database Connection Issues**
```bash
# Test connection
podman exec -it jamanager-postgres psql -U jamanager -d jamanager_dev -c "SELECT 1;"

# Check environment variables
cat .env | grep DATABASE_URL
```

### **Application Issues**
```bash
# Check application logs
tail -f app.log

# Check if application is running
curl http://localhost:3000/api/system/health

# Restart application
pkill -f uvicorn
uvicorn main:app --host 0.0.0.0 --port 3000 --reload
```

## 🎉 **Expected Results**

After completing this mini-sprint:
- ✅ **Production Parity**: Dev environment matches production
- ✅ **Migration Confidence**: Proven migration process
- ✅ **Performance Testing**: Real PostgreSQL performance
- ✅ **Deployment Readiness**: Ready for production deployment

## 🚀 **Next Steps**

After successful completion:
1. **Deploy to Railway**: Use the deployment package in `sprints/sprint-3/deployment/`
2. **Production Testing**: Test the deployed application
3. **User Acceptance**: Get feedback from users
4. **Sprint 4 Planning**: Plan next development sprint

---

**Status**: 🚀 **READY TO RUN**
**Estimated Time**: 30-60 minutes
**Difficulty**: Easy (automated) / Medium (manual)
