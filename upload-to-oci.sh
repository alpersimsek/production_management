#!/bin/bash

# Upload Script for Olgahan Kimya ERP to OCI Server
# This script helps upload your application files to the OCI server

set -e

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

# Default values
SERVER_IP="145.241.236.172"
KEY_FILE=""
USERNAME="ubuntu"
REMOTE_DIR="/home/ubuntu/olgahan-erp"

# Help function
show_help() {
    echo "Upload Script for Olgahan Kimya ERP"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -k, --key FILE     SSH private key file (required)"
    echo "  -s, --server IP    Server IP address (default: 145.241.236.172)"
    echo "  -u, --user USER    Username (default: ubuntu)"
    echo "  -d, --dir DIR      Remote directory (default: /home/ubuntu/olgahan-erp)"
    echo "  -h, --help         Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 -k ~/.ssh/my-key.pem"
    echo "  $0 -k ~/.ssh/my-key.pem -s 192.168.1.100"
    echo "  $0 -k ~/.ssh/my-key.pem -u ubuntu -d /home/ubuntu/my-app"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -k|--key)
            KEY_FILE="$2"
            shift 2
            ;;
        -s|--server)
            SERVER_IP="$2"
            shift 2
            ;;
        -u|--user)
            USERNAME="$2"
            shift 2
            ;;
        -d|--dir)
            REMOTE_DIR="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Check if key file is provided
if [[ -z "$KEY_FILE" ]]; then
    print_error "SSH key file is required!"
    show_help
    exit 1
fi

# Check if key file exists
if [[ ! -f "$KEY_FILE" ]]; then
    print_error "SSH key file not found: $KEY_FILE"
    exit 1
fi

# Check if rsync is available
if ! command -v rsync &> /dev/null; then
    print_error "rsync is not installed. Please install rsync first."
    exit 1
fi

print_status "🚀 Starting upload to OCI server..."
print_status "Server: $USERNAME@$SERVER_IP"
print_status "Remote Directory: $REMOTE_DIR"
print_status "Key File: $KEY_FILE"

# Test SSH connection
print_status "Testing SSH connection..."
if ! ssh -i "$KEY_FILE" -o ConnectTimeout=10 -o BatchMode=yes "$USERNAME@$SERVER_IP" "echo 'SSH connection successful'" 2>/dev/null; then
    print_error "Cannot connect to server. Please check:"
    echo "  - Server IP: $SERVER_IP"
    echo "  - Username: $USERNAME"
    echo "  - Key file: $KEY_FILE"
    echo "  - Server is running and accessible"
    exit 1
fi

# Create remote directory
print_status "Creating remote directory..."
ssh -i "$KEY_FILE" "$USERNAME@$SERVER_IP" "mkdir -p $REMOTE_DIR"

# Upload files
print_status "Uploading application files..."
rsync -avz --progress \
    --exclude 'node_modules' \
    --exclude '.git' \
    --exclude 'venv' \
    --exclude '__pycache__' \
    --exclude '*.pyc' \
    --exclude '.env' \
    --exclude 'logs' \
    --exclude 'uploads' \
    -e "ssh -i $KEY_FILE" \
    ./ "$USERNAME@$SERVER_IP:$REMOTE_DIR/"

# Set proper permissions
print_status "Setting permissions..."
ssh -i "$KEY_FILE" "$USERNAME@$SERVER_IP" "chmod +x $REMOTE_DIR/*.sh"

print_status "✅ Upload completed successfully!"
print_status "📁 Files uploaded to: $REMOTE_DIR"
print_status "🚀 Next steps:"
echo "  1. SSH to your server: ssh -i $KEY_FILE $USERNAME@$SERVER_IP"
echo "  2. Navigate to: cd $REMOTE_DIR"
echo "  3. Run deployment: ./deploy.sh"
echo "  4. Access your app: http://$SERVER_IP"
