# GitHub Secrets Setup Guide

## Required Secrets for Free Deployment

### Vercel (Frontend)
```
VERCEL_TOKEN=your_vercel_token
ORG_ID=your_org_id
PROJECT_ID=your_project_id
```

### Railway (Backend)
```
RAILWAY_TOKEN=your_railway_token
RAILWAY_TOKEN_STAGING=your_staging_token
```

### Render (Alternative)
```
RENDER_API_KEY=your_render_api_key
RENDER_SERVICE_ID=your_service_id
```

### Code Quality & Security (Free)
```
SONAR_TOKEN=your_sonarcloud_token
SNYK_TOKEN=your_snyk_token
```

### Environment Variables
```
GEMINI_API_KEY=your_gemini_api_key
```

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
