#!/bin/bash

# Demo Kimya ERP Deployment Script
# This script deploys the application to OCI server

set -e

echo "🚀 Starting Demo Kimya ERP Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Stop existing containers
print_status "Stopping existing containers..."
docker-compose -f docker-compose.prod.yml down || true

# Build frontend
print_status "Building frontend..."
cd frontend
npm install
npm run build
cd ..

# Build and start services
print_status "Building and starting services..."
docker-compose -f docker-compose.prod.yml up --build -d

# Wait for services to be ready
print_status "Waiting for services to start..."
sleep 30

# Check if services are running
print_status "Checking service status..."
docker-compose -f docker-compose.prod.yml ps

# Run database migrations
print_status "Running database migrations..."
docker-compose -f docker-compose.prod.yml exec api alembic upgrade head

# Seed initial data
print_status "Seeding initial data..."
docker-compose -f docker-compose.prod.yml exec api python seed_data.py

# Create demo users
print_status "Creating demo users..."
docker-compose -f docker-compose.prod.yml exec api python seed_demo_users.py

print_status "✅ Deployment completed successfully!"
print_status "🌐 Application is available at: http://145.241.236.172"
print_status "📊 Flower monitoring: http://145.241.236.172/flower/"
print_status "🔍 Health check: http://145.241.236.172/health"

echo ""
print_status "📋 Service URLs:"
echo "  - Frontend: http://145.241.236.172"
echo "  - API: http://145.241.236.172/api/"
echo "  - Flower: http://145.241.236.172/flower/"
echo "  - Health: http://145.241.236.172/health"

echo ""
print_status "🔑 Default login credentials:"
echo "  - Admin: admin@demo.com / admin123"
echo "  - Manager: manager@demo.com / manager123"
echo "  - Operator: operator@demo.com / operator123"

echo ""
print_warning "⚠️  Remember to:"
echo "  1. Change default passwords in production"
echo "  2. Update SECRET_KEY in docker-compose.prod.yml"
echo "  3. Configure SSL certificates for HTTPS"
echo "  4. Set up proper backup strategy"
echo "  5. Configure firewall rules"
