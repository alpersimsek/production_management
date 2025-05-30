#!/bin/bash

set -e

ENV=${1:-prod}  # default to production
TAG=${2:-latest}
BASE_DIR=~/workspace/gdpr-tool
DOCKER_NETWORK=gdpr-network

# Paths
FRONTEND_DIR=${BASE_DIR}/frontend
BACKEND_DIR=${BASE_DIR}/backend
FRONTEND_COMPOSE=${FRONTEND_DIR}/docker-compose.${ENV}.yml
BACKEND_COMPOSE=${BACKEND_DIR}/docker-compose.${ENV}.yml

# Detect docker compose
if command -v "docker" >/dev/null 2>&1; then
    COMPOSE="docker compose"
elif command -v "docker-compose" >/dev/null 2>&1; then
    COMPOSE="docker-compose"
else
    echo "Error: docker not found."
    exit 1
fi

# Create shared network if not exists
docker network inspect $DOCKER_NETWORK >/dev/null 2>&1 || docker network create $DOCKER_NETWORK

# Backend
echo "🚀 Deploying BACKEND (${ENV})"
cd "$BACKEND_DIR"
$COMPOSE -f "$BACKEND_COMPOSE" --project-name gdpr up -d --build

# Frontend
echo "🚀 Deploying FRONTEND (${ENV})"
cd "$FRONTEND_DIR"
$COMPOSE -f "$FRONTEND_COMPOSE" --project-name gdpr up -d --build

echo "✅ Deployment completed in '$ENV' mode"
