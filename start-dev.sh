#!/bin/bash

# Exam Hub Development Startup Script
echo "🚀 Starting Exam Hub Development Environment..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Kill any existing processes on our ports
echo -e "${YELLOW}Cleaning up existing processes...${NC}"
pkill -f "uvicorn"
pkill -f "npm start"
sleep 2

# Set environment variables for development
export REACT_APP_BACKEND_URL=http://localhost:5001
export ENV=development

echo -e "${BLUE}Development environment set:${NC}"
echo -e "${BLUE}  - REACT_APP_BACKEND_URL: $REACT_APP_BACKEND_URL${NC}"
echo -e "${BLUE}  - ENV: $ENV (enables DEBUG logging)${NC}"

# Check if python virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo -e "${YELLOW}Warning: No virtual environment detected. Make sure you're in the right environment.${NC}"
    echo -e "${YELLOW}Run: cd backend && source venv/bin/activate${NC}"
fi

# Check if uploads directory exists
if [ ! -d "backend/uploads" ]; then
    echo -e "${YELLOW}Creating uploads directory...${NC}"
    mkdir -p backend/uploads
fi

# Start backend
echo -e "${GREEN}Starting FastAPI backend on port 5001...${NC}"
cd backend
ENV=development python app.py &
BACKEND_PID=$!
echo -e "${GREEN}Backend started with PID: $BACKEND_PID${NC}"

# Wait for backend to start
echo -e "${YELLOW}Waiting for backend to start...${NC}"
sleep 5

# Start frontend
echo -e "${GREEN}Starting React frontend on port 3000...${NC}"
cd ../exam-app
REACT_APP_BACKEND_URL=http://localhost:5001 npm start &
FRONTEND_PID=$!
echo -e "${GREEN}Frontend started with PID: $FRONTEND_PID${NC}"

echo ""
echo -e "${GREEN}Development Environment Started!${NC}"
echo ""
echo -e "${BLUE}Backend API:${NC} http://localhost:5001"
echo -e "${BLUE}API Docs:${NC} http://localhost:5001/docs"
echo -e "${BLUE}Redoc:${NC} http://localhost:5001/redoc"
echo -e "${BLUE}Health Check:${NC} http://localhost:5001/health"
echo -e "${BLUE}Frontend:${NC} http://localhost:3000"
echo ""
echo -e "${RED}To stop:${NC} Press Ctrl+C"

# Wait for user to stop
wait 