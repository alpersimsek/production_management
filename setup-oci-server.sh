#!/bin/bash

# OCI Server Setup Script for Olgahan Kimya ERP
# Run this script on your OCI server to prepare it for deployment

set -e

echo "🔧 Setting up OCI server for Olgahan Kimya ERP..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Update system
print_status "Updating system packages..."
sudo apt update -y

# Install required packages
print_status "Installing required packages..."
sudo apt install -y git curl wget unzip

# Install Docker
print_status "Installing Docker..."
sudo apt install -y docker.io
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -a -G docker ubuntu

# Install Docker Compose
print_status "Installing Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Node.js (for frontend build)
print_status "Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Configure firewall (if ufw is running)
if command -v ufw &> /dev/null; then
    print_status "Configuring firewall..."
    sudo ufw allow 80/tcp
    sudo ufw allow 443/tcp
    sudo ufw --force enable
fi

# Create application directory
print_status "Creating application directory..."
sudo mkdir -p /home/ubuntu/olgahan-erp
sudo chown ubuntu:ubuntu /home/ubuntu/olgahan-erp

# Set up log rotation
print_status "Setting up log rotation..."
sudo tee /etc/logrotate.d/olgahan-erp > /dev/null <<EOF
/home/ubuntu/olgahan-erp/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 ubuntu ubuntu
}
EOF

print_status "✅ OCI server setup completed!"
print_warning "⚠️  Please logout and login again to apply Docker group changes"
print_status "📁 Upload your application files to: /home/ubuntu/olgahan-erp"
print_status "🚀 Then run: ./deploy.sh"

echo ""
print_status "📋 Next steps:"
echo "1. Logout and login again"
echo "2. Upload your application files to /home/ubuntu/olgahan-erp"
echo "3. Run ./deploy.sh to deploy the application"
echo "4. Access your application at http://145.241.236.172"
