#!/bin/bash

# Exam Hub Free Deployment Setup Script
# Thiết lập CI/CD hoàn toàn miễn phí

set -e

echo "🆓 Exam Hub Free Deployment Setup"
echo "=================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}"
echo "   ____                    _   _       _     "
echo "  | ___| __  __ __ _  _ __ | | | | _   _| |__  "
echo "  |  _| |  \/  |/ _\` || \'__|| |_| || | | | \'_ \ "
echo "  | |___ \  /\  / (_| || |   |  _  || |_| | |_) |"
echo "  |_____||_|  |_|\__,_||_|   |_| |_| \__,_|_.__/ "
echo ""
echo "           Free Deployment Solution"
echo -e "${NC}"

# Check prerequisites
check_prerequisites() {
    echo -e "${YELLOW}Checking prerequisites...${NC}"
    
    command -v git >/dev/null 2>&1 || { echo -e "${RED}Git not found!${NC}"; exit 1; }
    command -v node >/dev/null 2>&1 || { echo -e "${RED}Node.js not found!${NC}"; exit 1; }
    command -v npm >/dev/null 2>&1 || { echo -e "${RED}npm not found!${NC}"; exit 1; }
    command -v docker >/dev/null 2>&1 || { echo -e "${RED}Docker not found!${NC}"; exit 1; }
    
    echo -e "${GREEN}✅ Prerequisites check passed${NC}"
}

# Setup environment variables
setup_env() {
    echo -e "${YELLOW}Setting up environment variables...${NC}"
    
    if [ ! -f ".env" ]; then
        cat > .env << EOF
# Gemini AI
GEMINI_API_KEY=your_gemini_api_key

# Database (for local development)
DATABASE_URL=postgresql://examhub_user:examhub_password@localhost:5432/examhub

# Redis (for caching)
REDIS_URL=redis://localhost:6379/0

# Environment
NODE_ENV=development
FLASK_ENV=development
EOF
        echo -e "${GREEN}✅ Created .env file${NC}"
    else
        echo -e "${BLUE}ℹ️  .env file already exists${NC}"
    fi
}

# Setup Vercel deployment
setup_vercel() {
    echo -e "${YELLOW}Setting up Vercel deployment...${NC}"
    
    echo "1. Install Vercel CLI:"
    echo "   npm install -g vercel"
    echo ""
    echo "2. Login to Vercel:"
    echo "   vercel login"
    echo ""
    echo "3. Link your project:"
    echo "   cd exam-app && vercel"
    echo ""
    echo "4. Add GitHub secrets:"
    echo "   - VERCEL_TOKEN (from vercel.com/account/tokens)"
    echo "   - ORG_ID (from .vercel/project.json)"
    echo "   - PROJECT_ID (from .vercel/project.json)"
    echo ""
}

# Setup Railway deployment
setup_railway() {
    echo -e "${YELLOW}Setting up Railway deployment...${NC}"
    
    echo "1. Create account at railway.app"
    echo "2. Install Railway CLI:"
    echo "   npm install -g @railway/cli"
    echo ""
    echo "3. Login to Railway:"
    echo "   railway login"
    echo ""
    echo "4. Create new project:"
    echo "   railway new"
    echo ""
    echo "5. Add GitHub secrets:"
    echo "   - RAILWAY_TOKEN (from dashboard)"
    echo "   - RAILWAY_TOKEN_STAGING (for staging)"
    echo ""
}

# Setup Render deployment  
setup_render() {
    echo -e "${YELLOW}Setting up Render deployment...${NC}"
    
    echo "1. Create account at render.com"
    echo "2. Connect your GitHub repository"
    echo "3. Create new services:"
    echo "   - Web Service for backend"
    echo "   - Static Site for frontend"
    echo "   - PostgreSQL database"
    echo ""
    echo "4. Add GitHub secrets:"
    echo "   - RENDER_API_KEY"
    echo "   - RENDER_SERVICE_ID"
    echo ""
}

# Setup SonarCloud
setup_sonarcloud() {
    echo -e "${YELLOW}Setting up SonarCloud (Free)...${NC}"
    
    echo "1. Go to sonarcloud.io"
    echo "2. Login with GitHub"
    echo "3. Add your repository"
    echo "4. Get your project key and token"
    echo ""
    echo "5. Add GitHub secrets:"
    echo "   - SONAR_TOKEN"
    echo ""
    
    # Create sonar-project.properties
    cat > sonar-project.properties << EOF
sonar.projectKey=exam-hub
sonar.organization=your-org
sonar.sources=exam-app/src,backend
sonar.tests=exam-app/src,backend/tests
sonar.exclusions=**/node_modules/**,**/build/**,**/*.test.js
sonar.javascript.lcov.reportPaths=exam-app/coverage/lcov.info
sonar.python.coverage.reportPaths=backend/coverage.xml
EOF
    echo -e "${GREEN}✅ Created sonar-project.properties${NC}"
}

# Setup monitoring with free tools
setup_monitoring() {
    echo -e "${YELLOW}Setting up free monitoring...${NC}"
    
    echo "Free monitoring options:"
    echo "1. UptimeRobot (uptime monitoring)"
    echo "2. LogTail (log management)"
    echo "3. Sentry (error tracking)"
    echo "4. Google Analytics (user analytics)"
    echo ""
    
    # Create basic monitoring config
    mkdir -p monitoring
    cat > monitoring/uptime-robot.json << EOF
{
  "monitors": [
    {
      "friendly_name": "Exam Hub Frontend",
      "url": "https://exam-hub.vercel.app",
      "type": 1,
      "interval": 300
    },
    {
      "friendly_name": "Exam Hub Backend",
      "url": "https://exam-hub-backend.railway.app/health",
      "type": 1,
      "interval": 300
    }
  ]
}
EOF
    echo -e "${GREEN}✅ Created monitoring config${NC}"
}

# Create GitHub secrets guide
create_secrets_guide() {
    echo -e "${YELLOW}Creating GitHub secrets guide...${NC}"
    
    cat > GitHub-Secrets-Setup.md << EOF
# GitHub Secrets Setup Guide

## Required Secrets for Free Deployment

### Vercel (Frontend)
\`\`\`
VERCEL_TOKEN=your_vercel_token
ORG_ID=your_org_id
PROJECT_ID=your_project_id
\`\`\`

### Railway (Backend)
\`\`\`
RAILWAY_TOKEN=your_railway_token
RAILWAY_TOKEN_STAGING=your_staging_token
\`\`\`

### Render (Alternative)
\`\`\`
RENDER_API_KEY=your_render_api_key
RENDER_SERVICE_ID=your_service_id
\`\`\`

### Code Quality & Security (Free)
\`\`\`
SONAR_TOKEN=your_sonarcloud_token
SNYK_TOKEN=your_snyk_token
\`\`\`

### Environment Variables
\`\`\`
GEMINI_API_KEY=your_gemini_api_key
\`\`\`

## Setup Instructions

1. Go to your GitHub repository
2. Settings > Secrets and variables > Actions
3. Click "New repository secret"
4. Add each secret above

## Getting the Tokens

### Vercel Token
1. Go to vercel.com/account/tokens
2. Create new token
3. Copy the token

### Railway Token  
1. Go to railway.app
2. Account settings > Tokens
3. Create new token

### SonarCloud Token
1. Go to sonarcloud.io
2. Account > Security
3. Generate new token

### Snyk Token
1. Go to snyk.io
2. Account settings > API Token
3. Copy existing or create new token
EOF
    
    echo -e "${GREEN}✅ Created GitHub-Secrets-Setup.md${NC}"
}

# Create deployment comparison
create_comparison() {
    echo -e "${YELLOW}Creating deployment comparison...${NC}"
    
    cat > Free-vs-AWS-Comparison.md << EOF
# Free Deployment vs AWS Comparison

## 💰 Cost Comparison

| Service | AWS | Free Alternative | Monthly Cost |
|---------|-----|------------------|--------------|
| **Compute** | EKS + EC2 | Railway/Render/Vercel | \$70+ vs \$0 |
| **Database** | RDS | Railway Postgres/MongoDB Atlas | \$15+ vs \$0 |
| **Storage** | S3 | GitHub/Vercel hosting | \$5+ vs \$0 |
| **CDN** | CloudFront | Vercel/Netlify CDN | \$10+ vs \$0 |
| **Monitoring** | CloudWatch | UptimeRobot/Sentry | \$10+ vs \$0 |
| **CI/CD** | CodePipeline | GitHub Actions | \$10+ vs \$0 |
| **Total** | | | **\$120+ vs \$0** |

## 🎯 Feature Comparison

### ✅ What You Get Free
- GitHub Actions CI/CD (2000 minutes/month)
- Vercel hosting (100GB bandwidth)
- Railway (512MB RAM, \$5 credit)
- Render (750 hours/month)
- SonarCloud (unlimited public repos)
- Snyk security scanning
- PostgreSQL database
- SSL certificates
- Global CDN

### ⚠️ Limitations
- Railway: Apps sleep after 30min inactivity
- Render: Apps sleep after 15min inactivity  
- Vercel: Function execution limits
- Database: Storage limits on free tiers

### 🚀 Recommended Stack for Production

#### Option 1: Vercel + Railway
- Frontend: Vercel (\$0)
- Backend: Railway (\$5/month for always-on)
- Database: Railway Postgres (\$5/month)
- **Total: \$10/month**

#### Option 2: Netlify + Render
- Frontend: Netlify (\$0)
- Backend: Render (\$7/month)
- Database: Render Postgres (\$7/month)
- **Total: \$14/month**

#### Option 3: Self-hosted VPS
- VPS: DigitalOcean/Linode (\$6/month)
- Database: Same VPS
- CDN: Cloudflare (free)
- **Total: \$6/month**

## 📊 Performance Expectations

### Free Tier
- Cold start delays (apps sleep)
- Limited concurrent requests
- Basic monitoring
- Community support

### Paid Tier (\$10-15/month)
- Always-on applications
- Better performance
- Enhanced monitoring
- Priority support

## 🎓 Recommendation

1. **Development/Learning**: Use 100% free tier
2. **Small Production**: Upgrade to \$10-15/month
3. **Enterprise**: Consider AWS/GCP with proper budget
EOF

    echo -e "${GREEN}✅ Created comparison guide${NC}"
}

# Main execution
main() {
    echo -e "${GREEN}Starting Free Deployment Setup...${NC}"
    
    check_prerequisites
    setup_env
    setup_vercel
    setup_railway
    setup_render
    setup_sonarcloud
    setup_monitoring
    create_secrets_guide
    create_comparison
    
    echo ""
    echo -e "${GREEN}🎉 Free Deployment Setup Complete!${NC}"
    echo ""
    echo -e "${YELLOW}Next Steps:${NC}"
    echo "1. Review GitHub-Secrets-Setup.md for required secrets"
    echo "2. Choose your deployment platform (Vercel + Railway recommended)"  
    echo "3. Setup accounts and get API tokens"
    echo "4. Add secrets to GitHub repository"
    echo "5. Push to main branch to trigger deployment"
    echo ""
    echo -e "${BLUE}Quick Start Commands:${NC}"
    echo "# Local development"
    echo "docker-compose -f deployment/free-tier/docker-compose.free.yml up"
    echo ""
    echo "# Deploy to Vercel"
    echo "cd exam-app && vercel --prod"
    echo ""
    echo "# Deploy to Railway"
    echo "railway deploy"
    echo ""
    echo -e "${GREEN}💡 See Free-vs-AWS-Comparison.md for detailed comparison${NC}"
}

# Run main function
main "$@" 