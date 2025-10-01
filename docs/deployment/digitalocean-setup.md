# DigitalOcean Deployment Guide - Chi tiết từng bước

## 📋 Mục lục
1. [Yêu cầu trước khi bắt đầu](#yêu-cầu)
2. [Setup DigitalOcean Account](#setup-digitalocean)
3. [Tạo Container Registry](#tạo-container-registry)
4. [Setup Droplet (Server)](#setup-droplet)
5. [Configure GitHub Secrets](#configure-github-secrets)
6. [Deploy lần đầu](#deploy-lần-đầu)
7. [Monitoring & Logs](#monitoring)
8. [Troubleshooting](#troubleshooting)

---

## 1. Yêu cầu trước khi bắt đầu {#yêu-cầu}

### Checklist:
- ✅ Tài khoản DigitalOcean với edu credit
- ✅ GitHub repository với CI/CD workflows
- ✅ Docker đã cài trên máy local (để test)
- ✅ `doctl` CLI tool (optional nhưng recommended)

### Chi phí ước tính:
- **Container Registry**: $0/month (free tier 500MB)
- **Droplet (Basic)**: $6/month (1GB RAM, 25GB SSD)
- **Redis**: Có thể dùng chung Droplet hoặc Managed Redis $15/month
- **Database**: SQLite (free) hoặc Managed PostgreSQL $15/month

**Tổng:** ~$6-36/month tùy setup

---

## 2. Setup DigitalOcean Account {#setup-digitalocean}

### Bước 1: Tạo tài khoản
1. Truy cập https://www.digitalocean.com/
2. Đăng ký với email edu để nhận $200 credit
3. Xác thực email và thêm payment method (không bị charge nếu dùng credit)

### Bước 2: Tạo Personal Access Token
1. Vào **API** → **Tokens/Keys**
2. Click **Generate New Token**
3. Đặt tên: `exam-hub-deployment`
4. Scope: **Read & Write**
5. **LƯU TOKEN NÀY** - chỉ hiện 1 lần!

```bash
# Token sẽ có dạng:
dop_v1_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Bước 3: Install doctl CLI (Optional)
```bash
# macOS
brew install doctl

# Linux
cd ~
wget https://github.com/digitalocean/doctl/releases/download/v1.94.0/doctl-1.94.0-linux-amd64.tar.gz
tar xf doctl-1.94.0-linux-amd64.tar.gz
sudo mv doctl /usr/local/bin

# Xác thực
doctl auth init
# Paste token vừa tạo
```

---

## 3. Tạo Container Registry {#tạo-container-registry}

### Bước 1: Tạo Registry qua Web UI
1. Vào **Container Registry** (thanh bên trái)
2. Click **Get Started** hoặc **Create Registry**
3. Chọn:
   - **Name**: `exam-hub-registry` (hoặc tên bạn thích)
   - **Subscription Plan**: **Starter** (Free - 500MB storage)
   - **Datacenter Region**: **Singapore** (gần VN nhất)
4. Click **Create Registry**

### Bước 2: Lấy Registry Name
```bash
# Registry URL sẽ có dạng:
registry.digitalocean.com/exam-hub-registry

# Lưu lại: exam-hub-registry
```

### Bước 3: Test login từ local
```bash
# Login với token
echo "YOUR_TOKEN" | docker login registry.digitalocean.com -u YOUR_TOKEN --password-stdin

# Test push image
docker tag exam-hub-backend:latest registry.digitalocean.com/exam-hub-registry/exam-hub-backend:latest
docker push registry.digitalocean.com/exam-hub-registry/exam-hub-backend:latest
```

---

## 4. Setup Droplet (Server) {#setup-droplet}

### Bước 1: Tạo Droplet
1. Click **Create** → **Droplets**
2. Chọn cấu hình:

**Image:**
- Distribution: **Ubuntu 22.04 LTS**

**Droplet Type:**
- **Basic** (Shared CPU)

**CPU Options:**
- **Regular** - $6/month
  - 1 GB RAM
  - 1 vCPU
  - 25 GB SSD
  - 1 TB transfer

**Datacenter Region:**
- **Singapore** (gần VN)

**Authentication:**
- Chọn **SSH Key** (recommended) hoặc **Password**
- Nếu chọn SSH:
  ```bash
  # Generate SSH key trên máy local
  ssh-keygen -t ed25519 -C "exam-hub-deployment"
  # Enter để lưu vào ~/.ssh/id_ed25519

  # Copy public key
  cat ~/.ssh/id_ed25519.pub
  # Paste vào DigitalOcean
  ```

**Hostname:**
- `exam-hub-backend-server`

3. Click **Create Droplet**
4. Đợi 1-2 phút cho Droplet khởi động

### Bước 2: Lấy IP Address
```bash
# IP sẽ hiện ra, ví dụ:
159.65.xxx.xxx

# Test SSH
ssh root@159.65.xxx.xxx
```

### Bước 3: Setup Droplet (chạy trên server)
```bash
# 1. Update system
apt update && apt upgrade -y

# 2. Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Verify
docker --version

# 3. Install Docker Compose
apt install docker-compose-plugin -y

# Verify
docker compose version

# 4. Create app directory
mkdir -p /root/exam-hub
cd /root/exam-hub

# 5. Create .env file
nano .env
```

**Nội dung `.env` file:**
```bash
# Database
DATABASE_URL=sqlite:///./exam_hub.db

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email (Brevo)
BREVO_API_KEY=your-brevo-api-key
SENDER_EMAIL=noreply@yourdomain.com
SENDER_NAME=Exam Hub

# AI Services
GENAI_PROVIDER=openai
OPENAI_API_KEY=sk-your-openai-key
GEMINI_API_KEY=your-gemini-key

# Redis
REDIS_URL=redis://redis:6379/0
RATE_LIMIT_ENABLED=true

# CORS
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com

# File Upload
MAX_FILE_SIZE=10485760
UPLOAD_DIR=/app/uploads

# DigitalOcean
DIGITALOCEAN_REGISTRY_NAME=exam-hub-registry
```

```bash
# Save: Ctrl+X, Y, Enter

# 6. Create upload directory
mkdir -p uploads

# 7. Login to Container Registry
echo "YOUR_DIGITALOCEAN_TOKEN" | docker login registry.digitalocean.com -u YOUR_DIGITALOCEAN_TOKEN --password-stdin
```

---

## 5. Configure GitHub Secrets {#configure-github-secrets}

### Vào GitHub Repository Settings

1. **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**

### Thêm các secrets sau:

| Secret Name | Value | Ví dụ |
|-------------|-------|-------|
| `DIGITALOCEAN_ACCESS_TOKEN` | Token từ bước 2 | `dop_v1_xxx...` |
| `DIGITALOCEAN_REGISTRY_NAME` | Registry name | `exam-hub-registry` |
| `DROPLET_HOST` | IP của Droplet | `159.65.xxx.xxx` |
| `DROPLET_USERNAME` | SSH username | `root` |
| `DROPLET_SSH_KEY` | Private SSH key | Nội dung file `~/.ssh/id_ed25519` |

### Lấy SSH Private Key:
```bash
# Trên máy local
cat ~/.ssh/id_ed25519

# Copy toàn bộ nội dung, bao gồm:
-----BEGIN OPENSSH PRIVATE KEY-----
...
-----END OPENSSH PRIVATE KEY-----
```

---

## 6. Deploy lần đầu {#deploy-lần-đầu}

### Option A: Deploy qua GitHub Actions (Tự động)

1. **Enable deployment** trong `backend-cd.yaml`:
```yaml
# Sửa dòng này:
if: false  # Enable this when ready

# Thành:
if: true  # Enabled!
```

2. **Commit và push:**
```bash
git add .
git commit -m "Enable CD deployment"
git push origin main
```

3. **Theo dõi deployment:**
- Vào **Actions** tab trên GitHub
- Xem workflow **Backend CD - Deployment**
- Đợi ~5-10 phút

### Option B: Deploy thủ công từ Droplet

```bash
# SSH vào droplet
ssh root@YOUR_DROPLET_IP

# Clone repo hoặc tải docker-compose.prod.yml
cd /root/exam-hub

# Download docker-compose file
curl -o docker-compose.prod.yml https://raw.githubusercontent.com/YOUR_USERNAME/Exam-hub/main/backend/docker-compose.prod.yml

# Pull image
docker pull registry.digitalocean.com/exam-hub-registry/exam-hub-backend:latest

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Check logs
docker logs exam-hub-backend -f

# Run migrations
docker exec exam-hub-backend alembic upgrade head
```

### Kiểm tra deployment

```bash
# Check container status
docker ps

# Check health endpoint
curl http://YOUR_DROPLET_IP:5001/health

# Check API
curl http://YOUR_DROPLET_IP:5001/docs
```

**Kết quả mong đợi:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-10-02T..."
}
```

---

## 7. Monitoring & Logs {#monitoring}

### View logs real-time:
```bash
# Backend logs
docker logs exam-hub-backend -f --tail 100

# Redis logs
docker logs exam-hub-redis -f --tail 50

# All services
docker-compose -f docker-compose.prod.yml logs -f
```

### Check resource usage:
```bash
# Container stats
docker stats

# Disk usage
df -h

# Memory
free -h
```

### Setup monitoring (Optional):
```bash
# Install monitoring tools
apt install htop -y

# Run htop
htop
```

---

## 8. Troubleshooting {#troubleshooting}

### Vấn đề 1: Container không start

**Kiểm tra:**
```bash
docker logs exam-hub-backend

# Thường do:
# - .env file thiếu biến
# - Port 5001 đã bị chiếm
# - Image pull fail
```

**Fix:**
```bash
# Check port
netstat -tlnp | grep 5001

# Kill process on port
kill -9 $(lsof -t -i:5001)

# Restart
docker-compose -f docker-compose.prod.yml restart
```

### Vấn đề 2: Cannot pull image

**Fix:**
```bash
# Re-login to registry
echo "YOUR_TOKEN" | docker login registry.digitalocean.com -u YOUR_TOKEN --password-stdin

# Pull again
docker pull registry.digitalocean.com/exam-hub-registry/exam-hub-backend:latest
```

### Vấn đề 3: Database migration fail

**Fix:**
```bash
# Manual migration
docker exec -it exam-hub-backend bash
alembic upgrade head
exit
```

### Vấn đề 4: Out of memory

**Fix:**
```bash
# Add swap space
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile

# Make permanent
echo '/swapfile none swap sw 0 0' | tee -a /etc/fstab
```

---

## 🎯 Quick Commands Reference

```bash
# Deploy new version
cd /root/exam-hub
docker pull registry.digitalocean.com/exam-hub-registry/exam-hub-backend:latest
docker-compose -f docker-compose.prod.yml up -d

# Restart services
docker-compose -f docker-compose.prod.yml restart

# Stop services
docker-compose -f docker-compose.prod.yml down

# View logs
docker logs exam-hub-backend -f

# Shell into container
docker exec -it exam-hub-backend bash

# Run migrations
docker exec exam-hub-backend alembic upgrade head

# Backup database
docker cp exam-hub-backend:/app/exam_hub.db ./backup_$(date +%Y%m%d).db
```

---

## 📞 Support

Nếu gặp vấn đề:
1. Check logs: `docker logs exam-hub-backend`
2. Check GitHub Actions logs
3. Tham khảo DigitalOcean docs: https://docs.digitalocean.com/
4. DigitalOcean support chat (có edu account)
