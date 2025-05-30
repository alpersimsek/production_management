#!/bin/bash

set -e

# Default values
ENV="prod"
FULL_CLEAN=false
PROJECT=gdpr
BASE_DIR=~/workspace/gdpr-tool
DOCKER_NETWORK=gdpr-network

# Parse arguments
for arg in "$@"; do
  case $arg in
    dev|prod)
      ENV=$arg
      shift
      ;;
    --full)
      FULL_CLEAN=true
      shift
      ;;
    *)
      echo "Usage: ./undeploy.sh [dev|prod] [--full]"
      exit 1
      ;;
  esac
done

BACKEND_COMPOSE=${BASE_DIR}/backend/docker-compose.${ENV}.yml
FRONTEND_COMPOSE=${BASE_DIR}/frontend/docker-compose.${ENV}.yml

# Detect docker compose
if docker compose version >/dev/null 2>&1; then
    COMPOSE="docker compose"
elif command -v docker-compose >/dev/null 2>&1; then
    COMPOSE="docker-compose"
else
    echo "❌ Error: docker compose not available"
    exit 1
fi

echo "🧹 Stopping and removing all services under project '$PROJECT'..."

cd "$BASE_DIR"
$COMPOSE --project-name "$PROJECT" down --volumes --remove-orphans

echo "🔌 Removing shared Docker network if unused..."
docker network rm "$DOCKER_NETWORK" 2>/dev/null || echo "⚠️  Network '$DOCKER_NETWORK' in use or already gone"

if [ "$FULL_CLEAN" = true ]; then
  echo "🗑️  Removing built images: ${PROJECT}-frontend and ${PROJECT}-backend"
  docker rmi ${PROJECT}-frontend:latest ${PROJECT}-backend:latest postgres:17 2>/dev/null || true
  docker image prune -f
  docker builder prune -af
fi

echo "✅ Undeploy complete."
