#!/bin/bash
set -e

echo "🚀 Starting Exam Hub Backend Deployment..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
REGISTRY_NAME="${DIGITALOCEAN_REGISTRY_NAME}"
IMAGE_NAME="exam-hub-backend"
CONTAINER_NAME="exam-hub-backend"

echo -e "${YELLOW}Step 1: Logging in to DigitalOcean Container Registry...${NC}"
echo "$DIGITALOCEAN_ACCESS_TOKEN" | docker login registry.digitalocean.com -u "$DIGITALOCEAN_ACCESS_TOKEN" --password-stdin

echo -e "${YELLOW}Step 2: Pulling latest image...${NC}"
docker pull "registry.digitalocean.com/${REGISTRY_NAME}/${IMAGE_NAME}:latest"

echo -e "${YELLOW}Step 3: Stopping old container...${NC}"
docker stop ${CONTAINER_NAME} 2>/dev/null || true
docker rm ${CONTAINER_NAME} 2>/dev/null || true

echo -e "${YELLOW}Step 4: Starting new container...${NC}"
docker-compose -f docker-compose.prod.yml up -d

echo -e "${YELLOW}Step 5: Running database migrations...${NC}"
docker exec ${CONTAINER_NAME} alembic upgrade head

echo -e "${YELLOW}Step 6: Checking container health...${NC}"
sleep 5
if docker ps | grep -q ${CONTAINER_NAME}; then
  echo -e "${GREEN}✅ Deployment successful!${NC}"
  docker logs ${CONTAINER_NAME} --tail 20
else
  echo -e "${RED}❌ Deployment failed!${NC}"
  docker logs ${CONTAINER_NAME}
  exit 1
fi

echo -e "${YELLOW}Step 7: Cleaning up old images...${NC}"
docker image prune -af

echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
echo ""
echo "Service status:"
docker-compose -f docker-compose.prod.yml ps
