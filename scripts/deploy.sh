#!/bin/bash

# Exit on any error
set -e

# Variables for environment configuration
ENVIRONMENT=${1:-production}
CONFIG_FILE="configs/config.${ENVIRONMENT}.yaml"
DEPLOYMENT_DIR="deployment"

# Function to log messages with timestamps
log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Build the project (Docker, Kubernetes, Terraform, etc)
log "Building project components for $ENVIRONMENT environment..."
bash $DEPLOYMENT_DIR/docker/build.sh

# Run Infrastructure as Code (Terraform/CloudFormation)
if [ -d "$DEPLOYMENT_DIR/terraform" ]; then
  log "Initializing Terraform for infrastructure deployment..."
  cd $DEPLOYMENT_DIR/terraform
  terraform init
  terraform apply -var-file=variables.tf -auto-approve
  cd - # Go back to the previous directory
elif [ -f "$DEPLOYMENT_DIR/cloudformation/cloudformation_stack.yaml" ]; then
  log "Deploying infrastructure with CloudFormation..."
  aws cloudformation deploy --template-file $DEPLOYMENT_DIR/cloudformation/cloudformation_stack.yaml \
    --stack-name search-engine-stack --capabilities CAPABILITY_NAMED_IAM
fi

# Deploy application components (Kubernetes, Ansible, etc)
log "Deploying application components..."
if [ -d "$DEPLOYMENT_DIR/kubernetes/manifests" ]; then
  log "Deploying Kubernetes resources..."
  kubectl apply -f $DEPLOYMENT_DIR/kubernetes/manifests/
elif [ -f "$DEPLOYMENT_DIR/ansible/playbook.yml" ]; then
  log "Running Ansible playbook for deployment..."
  ansible-playbook $DEPLOYMENT_DIR/ansible/playbook.yml -e "config_file=$CONFIG_FILE"
fi

# Post-deployment steps (migration, cache warm-up, etc)
log "Performing post-deployment steps..."

# Database Migration
if [ -f "scripts/migrate_db.sh" ]; then
  log "Running database migrations..."
  bash scripts/migrate_db.sh
fi

# Cache Warm-up
log "Warming up cache for frequently accessed data..."
curl -s http://localhost:8080/api/cache_warmup || log "Cache warm-up failed, continuing..."

# Restart Crawler
log "Restarting web crawler to refresh indexed data..."
bash scripts/crawl_start.sh

# Health Check
log "Running end-to-end tests to verify deployment..."
python tests/e2e_tests/test_search_e2e.py

log "Deployment completed successfully!"