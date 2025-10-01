# Deployment Checklist - Exam Hub Backend

## 📋 Pre-Deployment Checklist

### 1. Code & Tests
- [ ] All CI tests passing (88+ tests)
- [ ] Code coverage >49%
- [ ] No security vulnerabilities
- [ ] All environment variables documented

### 2. DigitalOcean Setup
- [ ] Account created with edu credit
- [ ] Personal Access Token created
- [ ] Container Registry created
- [ ] Droplet provisioned
- [ ] SSH key configured

### 3. GitHub Configuration
- [ ] All secrets added to repository
- [ ] CI workflow enabled and working
- [ ] CD workflow reviewed

### 4. Environment Configuration
- [ ] `.env` file created on server
- [ ] All API keys configured (Brevo, OpenAI/Gemini)
- [ ] Database URL set
- [ ] CORS origins configured
- [ ] SECRET_KEY changed from default

### 5. Domain & SSL (Optional)
- [ ] Domain purchased
- [ ] DNS A record pointing to Droplet IP
- [ ] SSL certificate configured (Let's Encrypt)
- [ ] HTTPS enabled

---

## 🚀 Deployment Steps

### Phase 1: Initial Setup (One-time)
1. [ ] Create DigitalOcean account
2. [ ] Generate access token
3. [ ] Create Container Registry
4. [ ] Create Droplet
5. [ ] Configure GitHub Secrets
6. [ ] SSH into Droplet and install Docker

### Phase 2: First Deployment
1. [ ] Build Docker image locally (test)
2. [ ] Push image to registry
3. [ ] Deploy to Droplet
4. [ ] Run database migrations
5. [ ] Test health endpoint
6. [ ] Test API endpoints

### Phase 3: Automation
1. [ ] Enable CD workflow
2. [ ] Push to main branch
3. [ ] Verify auto-deployment
4. [ ] Monitor logs

---

## ✅ Post-Deployment Verification

### Health Checks
```bash
# 1. Container running
docker ps | grep exam-hub-backend

# 2. Health endpoint
curl http://YOUR_IP:5001/health

# 3. API docs
curl http://YOUR_IP:5001/docs

# 4. Database connection
docker exec exam-hub-backend alembic current
```

### Expected Results
- ✅ Container status: **Up**
- ✅ Health: `{"status": "healthy"}`
- ✅ API docs: **200 OK**
- ✅ Database: **Migration version shown**

---

## 🔄 Regular Maintenance

### Daily
- [ ] Check container logs for errors
- [ ] Monitor resource usage

### Weekly
- [ ] Review deployment logs
- [ ] Check disk space
- [ ] Backup database

### Monthly
- [ ] Update dependencies
- [ ] Review security updates
- [ ] Clean up old Docker images

---

## 🆘 Emergency Rollback

If deployment fails:

```bash
# 1. Stop current container
docker-compose -f docker-compose.prod.yml down

# 2. Pull previous version
docker pull registry.digitalocean.com/exam-hub-registry/exam-hub-backend:PREVIOUS_TAG

# 3. Update docker-compose to use previous tag
# Edit docker-compose.prod.yml, change 'latest' to previous tag

# 4. Start with previous version
docker-compose -f docker-compose.prod.yml up -d

# 5. Verify
curl http://YOUR_IP:5001/health
```

---

## 📊 Cost Tracking

| Service | Plan | Cost/Month | Notes |
|---------|------|------------|-------|
| Container Registry | Starter | $0 | 500MB free |
| Droplet | Basic | $6 | 1GB RAM |
| Redis (on Droplet) | - | $0 | Using Docker |
| Database (SQLite) | - | $0 | File-based |
| **Total** | | **$6/month** | With edu credit: FREE |

**Edu Credit:** $200 = ~33 months of free hosting!

---

## 📝 Notes

- Keep `DIGITALOCEAN_ACCESS_TOKEN` secret and secure
- Rotate access tokens every 6 months
- Enable 2FA on DigitalOcean account
- Backup `.env` file securely
- Document any infrastructure changes
