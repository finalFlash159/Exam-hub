#!/bin/bash

# Exam Hub CI/CD Setup Script
# This script helps setup the CI/CD pipeline for Exam Hub

set -e  # Exit on any error

echo "🚀 Exam Hub CI/CD Setup"
echo "========================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
check_prerequisites() {
    echo -e "${YELLOW}Checking prerequisites...${NC}"
    
    # Check if git is installed
    if ! command -v git &> /dev/null; then
        echo -e "${RED}Git is not installed. Please install git first.${NC}"
        exit 1
    fi
    
    # Check if docker is installed
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Docker is not installed. Please install Docker first.${NC}"
        exit 1
    fi
    
    # Check if terraform is installed
    if ! command -v terraform &> /dev/null; then
        echo -e "${YELLOW}Terraform is not installed. Installing...${NC}"
        # Install terraform (for macOS with Homebrew)
        if command -v brew &> /dev/null; then
            brew tap hashicorp/tap
            brew install hashicorp/tap/terraform
        else
            echo -e "${RED}Please install Terraform manually: https://terraform.io/downloads${NC}"
            exit 1
        fi
    fi
    
    # Check if kubectl is installed
    if ! command -v kubectl &> /dev/null; then
        echo -e "${YELLOW}kubectl is not installed. Installing...${NC}"
        if command -v brew &> /dev/null; then
            brew install kubectl
        else
            echo -e "${RED}Please install kubectl manually${NC}"
            exit 1
        fi
    fi
    
    echo -e "${GREEN}✅ Prerequisites check complete${NC}"
}

# Setup GitHub Secrets
setup_github_secrets() {
    echo -e "${YELLOW}Setting up GitHub Secrets...${NC}"
    echo "Please set the following secrets in your GitHub repository:"
    echo "Repository Settings > Secrets and variables > Actions > New repository secret"
    echo ""
    echo "Required secrets:"
    echo "- SONAR_TOKEN: Your SonarQube token"
    echo "- SONAR_HOST_URL: Your SonarQube server URL"
    echo "- SNYK_TOKEN: Your Snyk authentication token"
    echo "- AWS_ACCESS_KEY_ID: Your AWS access key"
    echo "- AWS_SECRET_ACCESS_KEY: Your AWS secret key"
    echo "- KUBE_CONFIG_STAGING: Base64 encoded kubeconfig for staging"
    echo "- KUBE_CONFIG_PRODUCTION: Base64 encoded kubeconfig for production"
    echo ""
    read -p "Press Enter when you have configured the secrets..."
}

# Setup SonarQube
setup_sonarqube() {
    echo -e "${YELLOW}Setting up SonarQube...${NC}"
    
    read -p "Do you want to run SonarQube locally with Docker? (y/n): " run_sonar
    
    if [[ $run_sonar == "y" ]]; then
        echo "Starting SonarQube container..."
        docker run -d --name sonarqube -p 9000:9000 sonarqube:community
        echo "SonarQube will be available at http://localhost:9000"
        echo "Default credentials: admin/admin"
        echo "Please change the password after first login"
    else
        echo "Please setup SonarQube manually and update the SONAR_HOST_URL secret"
    fi
}

# Setup AWS Infrastructure
setup_aws_infrastructure() {
    echo -e "${YELLOW}Setting up AWS Infrastructure...${NC}"
    
    read -p "Enter your AWS region (default: us-west-2): " aws_region
    aws_region=${aws_region:-us-west-2}
    
    read -p "Enter your AWS profile (default: default): " aws_profile  
    aws_profile=${aws_profile:-default}
    
    echo "Creating S3 bucket for Terraform state..."
    aws s3 mb s3://exam-hub-terraform-state --region $aws_region --profile $aws_profile
    
    echo "Enabling S3 bucket versioning..."
    aws s3api put-bucket-versioning \
        --bucket exam-hub-terraform-state \
        --versioning-configuration Status=Enabled \
        --profile $aws_profile
    
    echo -e "${GREEN}✅ AWS infrastructure setup complete${NC}"
}

# Create necessary directories
create_directories() {
    echo -e "${YELLOW}Creating necessary directories...${NC}"
    
    directories=(
        ".github/workflows"
        "terraform/staging"
        "terraform/production"
        "k8s/staging"
        "k8s/production"
        "tests/performance"
        "backend/tests"
        "scripts"
    )
    
    for dir in "${directories[@]}"; do
        mkdir -p "$dir"
        echo "Created directory: $dir"
    done
    
    echo -e "${GREEN}✅ Directory structure created${NC}"
}

# Setup monitoring
setup_monitoring() {
    echo -e "${YELLOW}Setting up monitoring...${NC}"
    
    read -p "Do you want to setup basic monitoring with Prometheus and Grafana? (y/n): " setup_monitoring
    
    if [[ $setup_monitoring == "y" ]]; then
        echo "Creating monitoring namespace and deployments..."
        kubectl create namespace monitoring || true
        
        # Basic Prometheus deployment
        cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prometheus
  namespace: monitoring
spec:
  replicas: 1
  selector:
    matchLabels:
      app: prometheus
  template:
    metadata:
      labels:
        app: prometheus
    spec:
      containers:
      - name: prometheus
        image: prom/prometheus:latest
        ports:
        - containerPort: 9090
EOF
        
        echo -e "${GREEN}✅ Basic monitoring setup complete${NC}"
    fi
}

# Main execution
main() {
    echo -e "${GREEN}Starting Exam Hub CI/CD setup...${NC}"
    
    check_prerequisites
    create_directories
    setup_github_secrets
    setup_sonarqube
    setup_aws_infrastructure
    setup_monitoring
    
    echo ""
    echo -e "${GREEN}🎉 CI/CD Setup Complete!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Commit and push your changes to trigger the pipeline"
    echo "2. Monitor your GitHub Actions workflows"
    echo "3. Check SonarQube for code quality reports"
    echo "4. Verify your staging deployment"
    echo ""
    echo "Useful commands:"
    echo "- View GitHub Actions: https://github.com/$(git config remote.origin.url | sed 's/.*github.com[:/]\\(.*\\).git/\\1/')/actions"
    echo "- Check deployments: kubectl get deployments -n exam-hub-staging"
    echo "- View logs: kubectl logs -f deployment/exam-hub-frontend -n exam-hub-staging"
}

# Run main function
main "$@" 