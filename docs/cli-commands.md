# CLI Commands Guide - Exam Hub

## 🎯 **OVERVIEW**

Comprehensive guide cho tất cả CLI commands được sử dụng trong Exam Hub project. Bao gồm development, testing, deployment, và maintenance commands.

---

## 🐍 **PYTHON & VIRTUAL ENVIRONMENT**

### **Virtual Environment Management**
```bash
# Tạo virtual environment
python -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Deactivate
deactivate

# Check Python version
python --version

# Check pip version  
pip --version

# List installed packages
pip list

# Install from requirements
pip install -r requirements.txt

# Install single package
pip install package-name

# Upgrade package
pip install --upgrade package-name

# Uninstall package
pip uninstall package-name

# Generate requirements file
pip freeze > requirements.txt
```

---

## 🚀 **FASTAPI SERVER**

### **Development Server**
```bash
# Start development server (recommended)
cd backend && python -m app.main

# Alternative: Direct uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 5001 --reload

# Start with specific config
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload --log-level debug

# Start without reload (production-like)
uvicorn app.main:app --host 0.0.0.0 --port 5001

# Background process
nohup uvicorn app.main:app --host 0.0.0.0 --port 5001 &

# Kill background process
pkill -f "uvicorn"

# Check if server is running
curl http://localhost:5001/health

# Check server logs
tail -f nohup.out
```

### **Server Management**
```bash
# Find process using port
lsof -i :5001

# Kill process by PID
kill -9 PID_NUMBER

# Kill all Python processes (careful!)
pkill -f python

# Check server status
ps aux | grep uvicorn

# Monitor server resources
htop
```

---

## 🗃️ **DATABASE MANAGEMENT (SQLAlchemy + Alembic)**

### **Alembic Migration Commands**
```bash
# Initialize Alembic (one-time setup)
alembic init alembic

# Create new migration (auto-generate from model changes)
alembic revision --autogenerate -m "Description of changes"

# Create empty migration
alembic revision -m "Manual migration description"

# Apply all pending migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade revision_id

# Show current revision
alembic current

# Show migration history
alembic history

# Show migration history with details
alembic history --verbose

# Check if database is up to date
alembic check

# Generate SQL script (don't execute)
alembic upgrade head --sql

# Merge multiple heads (if needed)
alembic merge -m "Merge heads" head1 head2
```

### **Database Direct Access (SQLite)**
```bash
# Open SQLite database
sqlite3 backend/exam_hub.db

# SQLite commands (inside sqlite3 shell):
.tables                    # List all tables
.schema table_name         # Show table schema
.schema                    # Show all schemas
.headers on                # Show column headers
.mode column               # Format output as columns
.quit                      # Exit sqlite3

# Example queries:
SELECT * FROM users LIMIT 5;
SELECT COUNT(*) FROM exams;
PRAGMA table_info(users);
```

### **Database Backup & Restore**
```bash
# Backup SQLite database
cp backend/exam_hub.db backend/exam_hub_backup_$(date +%Y%m%d_%H%M%S).db

# Restore from backup
cp backend/exam_hub_backup_YYYYMMDD_HHMMSS.db backend/exam_hub.db

# Export database to SQL
sqlite3 backend/exam_hub.db .dump > backup.sql

# Import from SQL dump
sqlite3 new_database.db < backup.sql

# Check database integrity
sqlite3 backend/exam_hub.db "PRAGMA integrity_check;"
```

---

## 📦 **NODE.JS & NPM (Frontend)**

### **Package Management**
```bash
# Check Node.js version
node --version

# Check npm version
npm --version

# Install dependencies from package.json
npm install

# Install specific package
npm install package-name

# Install as dev dependency
npm install --save-dev package-name

# Install globally
npm install -g package-name

# Uninstall package
npm uninstall package-name

# Update packages
npm update

# Check outdated packages
npm outdated

# Audit for vulnerabilities
npm audit

# Fix vulnerabilities
npm audit fix

# Clean npm cache
npm cache clean --force
```

### **Development Server**
```bash
# Start React development server
cd exam-app && npm start

# Start on specific port
PORT=3001 npm start

# Build for production
npm run build

# Test the application
npm test

# Run tests in watch mode
npm test -- --watch

# Run tests with coverage
npm test -- --coverage

# Lint code
npm run lint

# Format code (if configured)
npm run format
```

---

## 🧪 **TESTING**

### **Python Testing (pytest)**
```bash
# Install pytest
pip install pytest pytest-cov pytest-mock

# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_auth_service.py

# Run with verbose output
python -m pytest -v

# Run with coverage
python -m pytest --cov=app tests/

# Run with coverage report
python -m pytest --cov=app --cov-report=html tests/

# Run specific test function
python -m pytest tests/test_auth_service.py::test_register_user

# Run tests matching pattern
python -m pytest -k "test_auth"

# Stop on first failure
python -m pytest -x

# Show local variables on failure
python -m pytest -l

# Run tests in parallel
python -m pytest -n auto
```

### **API Testing (curl)**
```bash
# Health check
curl http://localhost:5001/health

# POST request with JSON
curl -X POST "http://localhost:5001/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "test123", "full_name": "Test User"}'

# GET with Bearer token
curl -X GET "http://localhost:5001/exam/" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# POST with file upload
curl -X POST "http://localhost:5001/upload/upload" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -F "file=@test.txt"

# Pretty print JSON response
curl http://localhost:5001/health | jq

# Save response to file
curl http://localhost:5001/health > response.json

# Show response headers
curl -I http://localhost:5001/health

# Follow redirects
curl -L http://localhost:5001/some-endpoint

# Timeout after 30 seconds
curl --max-time 30 http://localhost:5001/health
```

---

## 🐳 **DOCKER**

### **Docker Commands**
```bash
# Build image
docker build -t exam-hub-backend .

# Run container
docker run -p 5001:5001 exam-hub-backend

# Run in background
docker run -d -p 5001:5001 exam-hub-backend

# Run with environment variables
docker run -p 5001:5001 -e GEMINI_API_KEY=your_key exam-hub-backend

# List running containers
docker ps

# List all containers
docker ps -a

# Stop container
docker stop container_id

# Remove container
docker rm container_id

# View container logs
docker logs container_id

# Execute command in running container
docker exec -it container_id /bin/bash

# Build and run with Docker Compose
docker-compose up -d

# View Docker Compose logs
docker-compose logs -f

# Stop Docker Compose
docker-compose down

# Rebuild services
docker-compose build

# Remove all containers and volumes
docker-compose down -v
```

### **Docker Maintenance**
```bash
# Remove unused images
docker image prune

# Remove unused containers
docker container prune

# Remove unused volumes
docker volume prune

# Remove unused networks
docker network prune

# Remove everything unused
docker system prune

# Show disk usage
docker system df

# Remove specific image
docker rmi image_id

# Tag image
docker tag exam-hub-backend:latest exam-hub-backend:v1.0
```

---

## 🔧 **GIT**

### **Basic Git Commands**
```bash
# Check status
git status

# Add files to staging
git add .
git add specific_file.py

# Commit changes
git commit -m "Commit message"

# Push to remote
git push origin branch_name

# Pull from remote
git pull origin branch_name

# Create new branch
git checkout -b new-branch-name

# Switch branch
git checkout branch_name

# List branches
git branch

# Delete branch
git branch -d branch_name

# View commit history
git log --oneline

# Show changes
git diff

# Show staged changes
git diff --cached

# Unstage file
git reset HEAD file_name

# Discard changes
git checkout -- file_name
```

### **Advanced Git Commands**
```bash
# Stash changes
git stash

# Apply stashed changes
git stash pop

# List stashes
git stash list

# Create tag
git tag v1.0.0

# Push tags
git push --tags

# Rebase branch
git rebase main

# Interactive rebase
git rebase -i HEAD~3

# Merge branch
git merge feature-branch

# Cherry-pick commit
git cherry-pick commit_hash

# Show remote URLs
git remote -v

# Add remote
git remote add origin https://github.com/user/repo.git
```

---

## 🔍 **DEBUGGING & MONITORING**

### **Log Analysis**
```bash
# View server logs (if using systemd)
journalctl -u your-service-name -f

# Search in logs
grep "ERROR" /var/log/your-app.log

# Tail logs with pattern
tail -f /var/log/your-app.log | grep "authentication"

# Count log entries
wc -l /var/log/your-app.log

# View logs from specific time
journalctl --since "2025-01-15 10:00:00"

# View logs for specific user
journalctl _UID=1000
```

### **Process Monitoring**
```bash
# Show running processes
ps aux | grep python

# Monitor system resources
htop
top

# Check memory usage
free -h

# Check disk usage
df -h

# Check port usage
netstat -tlnp | grep :5001
ss -tlnp | grep :5001

# Monitor network connections
netstat -an | grep ESTABLISHED

# Check system load
uptime

# Monitor file changes
watch -n 1 'ls -la backend/'
```

---

## 📊 **PERFORMANCE & PROFILING**

### **Python Profiling**
```bash
# Profile Python script
python -m cProfile -o profile.stats app/main.py

# View profile results
python -c "import pstats; pstats.Stats('profile.stats').sort_stats('cumulative').print_stats()"

# Memory profiling
pip install memory-profiler
python -m memory_profiler your_script.py

# Line profiling
pip install line-profiler
kernprof -l -v your_script.py
```

### **Database Performance**
```bash
# SQLite query performance
sqlite3 backend/exam_hub.db
.timer on
SELECT COUNT(*) FROM users;

# Analyze query plan
EXPLAIN QUERY PLAN SELECT * FROM exams WHERE creator_id = 'user123';

# Check database size
ls -lh backend/exam_hub.db

# Vacuum database (optimize)
sqlite3 backend/exam_hub.db "VACUUM;"
```

---

## 🚀 **DEPLOYMENT**

### **Production Deployment**
```bash
# Install production dependencies only
pip install -r requirements.prod.txt

# Run with Gunicorn (production WSGI server)
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app

# Run with specific bind address
gunicorn -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:5001 app.main:app

# Create systemd service file
sudo nano /etc/systemd/system/exam-hub.service

# Enable and start service
sudo systemctl enable exam-hub
sudo systemctl start exam-hub
sudo systemctl status exam-hub

# View service logs
sudo journalctl -u exam-hub -f

# Restart service
sudo systemctl restart exam-hub
```

### **Environment Management**
```bash
# Set environment variables
export GEMINI_API_KEY=your_api_key
export DATABASE_URL=postgresql://user:pass@localhost/db

# Load from .env file
set -a; source .env; set +a

# Check environment variables
env | grep GEMINI
echo $DATABASE_URL

# Create production .env
cp deployment.env.example .env
nano .env
```

---

## 🔧 **MAINTENANCE**

### **Cleanup Commands**
```bash
# Clean Python cache
find . -type d -name __pycache__ -exec rm -r {} +
find . -name "*.pyc" -delete

# Clean npm cache
npm cache clean --force

# Clean Docker
docker system prune -a

# Clean logs (be careful!)
sudo truncate -s 0 /var/log/your-app.log

# Archive old logs
tar -czf logs_$(date +%Y%m%d).tar.gz /var/log/your-app/

# Clean temporary files
rm -rf /tmp/your-app-*
```

### **Backup Commands**
```bash
# Backup database
cp backend/exam_hub.db backups/exam_hub_$(date +%Y%m%d_%H%M%S).db

# Backup entire project
tar -czf exam-hub-backup-$(date +%Y%m%d).tar.gz \
  --exclude=node_modules \
  --exclude=venv \
  --exclude=__pycache__ \
  .

# Backup to remote server
rsync -avz --exclude='node_modules' --exclude='venv' \
  . user@remote-server:/backups/exam-hub/
```

---

## 📋 **QUICK REFERENCE**

### **Daily Development Workflow**
```bash
# 1. Start development environment
cd /path/to/Exam-hub
source backend/venv/bin/activate
cd backend && python -m app.main

# 2. In another terminal - start frontend
cd exam-app && npm start

# 3. Run tests
python -m pytest tests/

# 4. Check API health
curl http://localhost:5001/health

# 5. Git workflow
git status
git add .
git commit -m "Feature: description"
git push origin feature-branch
```

### **Emergency Debugging**
```bash
# 1. Check if services are running
ps aux | grep -E "(python|uvicorn|node)"

# 2. Check port availability
lsof -i :5001
lsof -i :3000

# 3. Check logs for errors
tail -n 50 /path/to/logfile | grep ERROR

# 4. Restart services
pkill -f uvicorn
python -m app.main

# 5. Database integrity check
sqlite3 backend/exam_hub.db "PRAGMA integrity_check;"
```

---

*CLI Commands guide for Exam Hub - Updated $(date)*
