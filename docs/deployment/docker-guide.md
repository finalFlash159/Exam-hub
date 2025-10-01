# 🐳 Docker Setup Guide

## 📚 Giới thiệu

Docker Compose setup này cung cấp:
- **Redis** - Rate limiting & caching
- **PostgreSQL** - Production database
- **Redis Commander** - GUI để xem Redis data (dev only)

---

## 🚀 Quick Start

### 1. Start Redis (chỉ Redis thôi)
```bash
docker compose up redis -d
```

### 2. Start tất cả services
```bash
docker compose up -d
```

### 3. Start với Redis Commander (để xem data)
```bash
docker compose --profile dev up -d
```

---

## 📖 Chi tiết các lệnh

### Start services
```bash
# Start tất cả
docker compose up -d

# Start chỉ Redis
docker compose up redis -d

# Start Redis + PostgreSQL
docker compose up redis postgres -d

# Start kèm Redis GUI (dev mode)
docker compose --profile dev up -d
```

### Stop services
```bash
# Stop tất cả
docker compose down

# Stop và xóa volumes (MẤT DATA!)
docker compose down -v
```

### View logs
```bash
# Xem logs tất cả services
docker compose logs -f

# Xem logs Redis
docker compose logs -f redis

# Xem logs PostgreSQL
docker compose logs -f postgres
```

### Check status
```bash
# Xem services đang chạy
docker compose ps

# Check health
docker compose ps --format json
```

---

## 🔧 Configuration

### Redis Configuration

**File:** `docker-compose.yml`

```yaml
redis:
  command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
```

**Giải thích:**
- `--appendonly yes` - Persist data to disk
- `--maxmemory 256mb` - Giới hạn RAM (tránh memory leak)
- `--maxmemory-policy allkeys-lru` - Xóa key cũ nhất khi hết RAM

### PostgreSQL Configuration

**Environment variables** (trong `.env.docker`):
```bash
POSTGRES_DB=exam_hub
POSTGRES_USER=exam_user
POSTGRES_PASSWORD=your_secure_password
```

---

## 📊 Volumes (Data Persistence)

### Xem volumes
```bash
docker volume ls | grep exam-hub
```

### Inspect volume
```bash
docker volume inspect exam-hub-redis-data
```

### Backup Redis data
```bash
docker compose exec redis redis-cli SAVE
docker cp exam-hub-redis:/data/dump.rdb ./backup/redis-backup.rdb
```

### Backup PostgreSQL data
```bash
docker compose exec postgres pg_dump -U exam_user exam_hub > backup/db-backup.sql
```

---

## 🌐 Access URLs

| Service | URL | Purpose |
|---------|-----|---------|
| Redis | `localhost:6379` | Rate limiting, caching |
| PostgreSQL | `localhost:5432` | Database |
| Redis Commander | `http://localhost:8081` | Redis GUI (dev) |

---

## 🔍 Redis Commander (GUI)

**Start Redis với GUI:**
```bash
docker compose --profile dev up -d
```

**Access:** http://localhost:8081

**Features:**
- View all keys
- Monitor real-time stats
- Execute Redis commands
- Debug rate limiting

---

## 🧪 Testing Redis Connection

### Test từ terminal
```bash
# Connect to Redis CLI
docker compose exec redis redis-cli

# Test commands
> PING
PONG

> SET test "Hello Redis"
OK

> GET test
"Hello Redis"

> KEYS *
1) "test"

> DEL test
(integer) 1

> exit
```

### Test từ Python
```python
import redis

# Connect
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Test
r.ping()  # True
r.set('test', 'Hello Redis')
r.get('test')  # 'Hello Redis'
```

---

## 🛠️ Troubleshooting

### Port already in use
```bash
# Check what's using port 6379
lsof -i :6379

# Kill process (if needed)
kill -9 <PID>
```

### Redis won't start
```bash
# Check logs
docker compose logs redis

# Remove and recreate
docker compose down
docker compose up redis -d
```

### Can't connect to Redis
```bash
# Check if running
docker compose ps

# Check health
docker compose exec redis redis-cli ping

# Restart
docker compose restart redis
```

### Clear all Redis data
```bash
docker compose exec redis redis-cli FLUSHALL
```

---

## 🔐 Security Best Practices

### Production
- [ ] Change PostgreSQL password
- [ ] Use Redis password (`requirepass`)
- [ ] Don't expose ports publicly
- [ ] Use Docker secrets for passwords
- [ ] Disable Redis Commander

### Example with password:
```yaml
redis:
  command: redis-server --requirepass your_redis_password
```

---

## 📝 Environment Variables

Create `.env.docker` file:
```bash
cp .env.docker.example .env.docker
```

Edit values:
```bash
POSTGRES_PASSWORD=strong_password_here
REDIS_PASSWORD=another_strong_password
```

---

## 🎓 Learning Resources

**Redis:**
- Official docs: https://redis.io/docs/
- Commands: https://redis.io/commands/
- Data types: https://redis.io/docs/data-types/

**Docker Compose:**
- Docs: https://docs.docker.com/compose/
- Best practices: https://docs.docker.com/develop/dev-best-practices/

---

## 🚀 Production Deployment

### Docker Compose Production
```bash
# Use production compose file
docker compose -f docker-compose.prod.yml up -d
```

### Kubernetes
- Convert to K8s manifests
- Use Helm charts
- Managed Redis (AWS ElastiCache, GCP Memorystore)

---

## ✅ Checklist

**Before committing:**
- [ ] `.env.docker` in `.gitignore`
- [ ] `docker-compose.yml` documented
- [ ] README updated
- [ ] Tested locally

**Before production:**
- [ ] Change all passwords
- [ ] Enable Redis password
- [ ] Setup backups
- [ ] Configure resource limits
- [ ] Remove Redis Commander
- [ ] Use managed services (AWS RDS, ElastiCache)

---

**Generated:** October 1, 2025
**Maintained by:** Exam Hub Team
