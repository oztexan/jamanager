# Jamanager Troubleshooting Guide

## 🚨 Common Issues and Solutions

### Application Won't Start

#### Issue: "Module not found" errors
**Symptoms:**
- `ModuleNotFoundError: No module named 'fastapi'`
- `ModuleNotFoundError: No module named 'uvicorn'`

**Solutions:**
1. **Activate virtual environment:**
   ```bash
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **If using pyenv:**
   ```bash
   export PYENV_VERSION="jv3.11.11"
   eval "$(pyenv init -)"
   ```

#### Issue: "Port already in use"
**Symptoms:**
- `OSError: [Errno 48] Address already in use`
- `Port 3000 is already in use`

**Solutions:**
1. **Kill existing processes:**
   ```bash
   pkill -f uvicorn
   lsof -ti:3000 | xargs kill -9
   ```

2. **Use a different port:**
   ```bash
   python -m uvicorn main:app --host 0.0.0.0 --port 3001 --reload
   ```

3. **Check what's using the port:**
   ```bash
   lsof -i :3000
   ```

#### Issue: Database connection errors
**Symptoms:**
- `sqlalchemy.exc.OperationalError: no such table`
- `sqlite3.OperationalError: database is locked`

**Solutions:**
1. **Reset the database:**
   ```bash
   python reset_dev_database.py
   ```

2. **Check database file permissions:**
   ```bash
   ls -la jamanager.db
   chmod 664 jamanager.db
   ```

3. **Delete and recreate database:**
   ```bash
   rm jamanager.db
   python init_dev_database.py
   ```

### Static Files Not Loading

#### Issue: CSS/JS files return 404
**Symptoms:**
- Blank page or unstyled content
- Console errors: `Failed to load resource: the server responded with a status of 404`

**Solutions:**
1. **Check static directory exists:**
   ```bash
   ls -la static/
   ```

2. **Verify static file mounting in main.py:**
   ```python
   app.mount("/static", StaticFiles(directory=static_dir), name="static")
   ```

3. **Check file permissions:**
   ```bash
   chmod -R 644 static/
   ```

### WebSocket Connection Issues

#### Issue: WebSocket connection fails
**Symptoms:**
- Real-time updates not working
- Console errors: `WebSocket connection failed`

**Solutions:**
1. **Check WebSocket endpoint:**
   ```bash
   curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" -H "Sec-WebSocket-Key: test" -H "Sec-WebSocket-Version: 13" http://localhost:3000/ws
   ```

2. **Verify WebSocket router is included:**
   ```python
   app.include_router(websocket.router)
   ```

3. **Check browser console for CORS issues**

### Environment Issues

#### Issue: Environment variables not loading
**Symptoms:**
- `JAM_MANAGER_ACCESS_CODE` not working
- Database URL issues

**Solutions:**
1. **Check .env file exists:**
   ```bash
   ls -la .env
   ```

2. **Verify .env file format:**
   ```bash
   cat .env
   # Should show:
   # DATABASE_URL=sqlite+aiosqlite:///./jamanager.db
   # JAM_MANAGER_ACCESS_CODE=jam2024
   ```

3. **Restart the application after .env changes**

#### Issue: Pyenv environment not activating
**Symptoms:**
- Wrong Python version
- Package installation issues

**Solutions:**
1. **Check pyenv installation:**
   ```bash
   pyenv --version
   ```

2. **List available versions:**
   ```bash
   pyenv versions
   ```

3. **Set correct version:**
   ```bash
   pyenv local jv3.11.11
   # or
   export PYENV_VERSION="jv3.11.11"
   eval "$(pyenv init -)"
   ```

### Development Tools Issues

#### Issue: Tests failing
**Symptoms:**
- `pytest: command not found`
- Test failures

**Solutions:**
1. **Install test dependencies:**
   ```bash
   pip install pytest pytest-asyncio
   ```

2. **Run tests with verbose output:**
   ```bash
   python -m pytest tests/ -v
   ```

3. **Check test database:**
   ```bash
   # Tests should use a separate test database
   ```

#### Issue: Linting/Formatting issues
**Symptoms:**
- `flake8: command not found`
- `black: command not found`

**Solutions:**
1. **Install development tools:**
   ```bash
   pip install flake8 black
   ```

2. **Run linting:**
   ```bash
   python -m flake8 .
   ```

3. **Format code:**
   ```bash
   python -m black .
   ```

## 🔧 Debugging Commands

### Check Application Status
```bash
# Check if application is running
ps aux | grep uvicorn

# Check port usage
lsof -i :3000

# Check database status
sqlite3 jamanager.db ".tables"
```

### Log Analysis
```bash
# View application logs
tail -f logs/app.log

# Check system logs
journalctl -u jamanager -f
```

### Network Debugging
```bash
# Test API endpoints
curl http://localhost:3000/api/health

# Test WebSocket
wscat -c ws://localhost:3000/ws

# Check CORS headers
curl -H "Origin: http://localhost:3000" -H "Access-Control-Request-Method: GET" -H "Access-Control-Request-Headers: X-Requested-With" -X OPTIONS http://localhost:3000/api/songs
```

## 🆘 Getting Help

### Before Asking for Help
1. **Check this troubleshooting guide**
2. **Run the setup script:** `./setup-dev-environment.sh`
3. **Check application logs**
4. **Verify environment setup**

### Useful Information to Include
- Operating system and version
- Python version (`python --version`)
- Error messages (full traceback)
- Steps to reproduce the issue
- Current working directory
- Environment variables (without sensitive data)

### Quick Health Check
```bash
# Run this to check your environment
python -c "
import sys
print(f'Python: {sys.version}')
try:
    import fastapi
    print(f'FastAPI: {fastapi.__version__}')
except ImportError:
    print('FastAPI: Not installed')
try:
    import uvicorn
    print(f'Uvicorn: {uvicorn.__version__}')
except ImportError:
    print('Uvicorn: Not installed')
"
```

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Uvicorn Documentation](https://www.uvicorn.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [WebSocket Documentation](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)

---

**Last Updated:** 2025-10-05  
**Version:** 1.0.0
