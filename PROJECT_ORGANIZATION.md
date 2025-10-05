# 📁 Project Organization Guide

## 🎯 **Organization Philosophy**
This project follows a sprint-based organization structure to maintain clarity and separate concerns by development phases.

## 📂 **Directory Structure**

### **Core Application**
```
├── main.py                    # FastAPI application entry point
├── run.py                     # Application runner
├── requirements.txt           # Python dependencies
├── pyproject.toml            # Project configuration
├── env.example               # Environment variables template
├── Dockerfile                # Container configuration
├── docker-compose.yml        # Multi-container setup
├── Makefile                  # Build automation
└── README.md                 # Project overview
```

### **Application Code**
```
├── api/                      # API endpoints
│   ├── endpoints/            # Individual endpoint modules
│   └── dependencies/         # FastAPI dependencies
├── core/                     # Core business logic
├── models/                   # Database models
├── services/                 # Business services
├── static/                   # Frontend assets
└── utils/                    # Utility functions
```

### **Sprint Organization**
```
├── sprints/
│   ├── sprint-1/             # Developer Experience & Documentation
│   │   ├── docs/             # Sprint 1 documentation
│   │   ├── scripts/          # Sprint 1 scripts
│   │   └── data/             # Sprint 1 data files
│   ├── sprint-2/             # Code Quality & Testing
│   │   ├── docs/             # Sprint 2 documentation
│   │   ├── scripts/          # Sprint 2 scripts
│   │   └── tests/            # Sprint 2 specific tests
│   ├── sprint-3/             # Future sprint
│   └── sprint-4/             # Future sprint
```

### **Scripts Organization**
```
├── scripts/
│   ├── setup/                # Environment setup scripts
│   ├── testing/              # Test and validation scripts
│   ├── migration/            # Database migration scripts
│   ├── deploy.sh             # Deployment script
│   └── agents/               # Multi-agent system scripts
```

### **Documentation**
```
├── docs/                     # Project documentation
│   ├── README.md             # Main documentation
│   ├── TECHNICAL_ARCHITECTURE.md
│   ├── DATABASE_ERD.md
│   ├── DEPLOYMENT_PLAN.md
│   └── ...                   # Other documentation
```

### **Testing**
```
├── tests/                    # Test suite
│   ├── unit/                 # Unit tests
│   ├── integration/          # Integration tests
│   └── api/                  # API tests
```

### **Data Management**
```
├── data/
│   ├── backups/              # Database backups
│   └── development/          # Development database
```

### **Debug & Development**
```
├── debug/                    # Debug files and test utilities
└── __pycache__/              # Python cache (ignored)
```

## 🏷️ **File Naming Conventions**

### **Sprint Files**
- `SPRINT_X_PLAN.md` - Sprint planning document
- `SPRINT_X_ACCEPTANCE_CRITERIA.md` - Acceptance criteria
- `SPRINT_X_REGRESSION_REPORT.md` - Regression test results

### **Scripts**
- `setup-*.sh` - Environment setup scripts
- `test-*.sh` - Testing scripts
- `run-*.sh` - Execution scripts
- `cleanup-*.sh` - Cleanup scripts

### **Documentation**
- `*_CONFIG.md` - Configuration documentation
- `*_REQUIREMENTS.md` - Requirements documentation
- `*_STATUS.md` - Status reports

## 📋 **Sprint-Specific Organization**

### **Sprint 1: Developer Experience & Documentation**
- **Location**: `sprints/sprint-1/`
- **Focus**: Setup, documentation, dev tools
- **Files**:
  - `docs/SPRINT_1_ACCEPTANCE_CRITERIA.md`
  - `docs/DEV_ENVIRONMENT_CONFIG.md`
  - `docs/TROUBLESHOOTING.md`
  - `scripts/setup-dev-environment.sh`
  - `scripts/create_sample_backgrounds.py`
  - `scripts/init_dev_database.py`

### **Sprint 2: Code Quality & Testing**
- **Location**: `sprints/sprint-2/`
- **Focus**: Type hints, testing, error handling
- **Files**:
  - `docs/SPRINT_2_PLAN.md`
  - `docs/SPRINT_2_ACCEPTANCE_CRITERIA.md`
  - `docs/SPRINT_2_REGRESSION_REPORT.md`
  - `scripts/run-sprint-2.sh`
  - `scripts/run-sprint-2-fresh.sh`
  - `scripts/cleanup-sprint-2.sh`
  - `tests/` (sprint-specific tests)

## 🚀 **Benefits of This Organization**

1. **Clear Separation**: Each sprint has its own space
2. **Easy Navigation**: Related files are grouped together
3. **Maintainability**: Easy to find and update sprint-specific code
4. **Scalability**: Easy to add new sprints
5. **Clean Root**: Core application files are clearly separated from sprint work

## 📝 **Maintenance Guidelines**

1. **New Sprint Files**: Always place in appropriate sprint directory
2. **Scripts**: Use the scripts/ directory with appropriate subdirectories
3. **Documentation**: Keep sprint docs in sprint directories, project docs in docs/
4. **Testing**: Sprint-specific tests go in sprint directories, general tests in tests/
5. **Data**: Use data/ directory for databases and backups

## 🔄 **Migration Notes**

This organization was implemented to clean up the previously cluttered root directory. All files have been moved to their appropriate locations while maintaining functionality.

---
**Last Updated**: 2025-10-05  
**Status**: ✅ **IMPLEMENTED** - Project reorganized by sprint structure
