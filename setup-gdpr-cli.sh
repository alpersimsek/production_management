#!/bin/bash
# GDPR Tool CLI - Environment Setup Script

set -e  # Exit on any error

echo "🚀 GDPR Tool CLI - Environment Setup"
echo "===================================="
echo ""
echo "This script sets up the environment for the GDPR Tool CLI."
echo "The CLI will automatically install itself when first run."
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"

# Check if backend directory exists
if [ ! -d "$BACKEND_DIR" ]; then
    echo "❌ Backend directory not found at $BACKEND_DIR"
    exit 1
fi

print_info "Setting up environment from: $SCRIPT_DIR"

# Setup virtual environment
print_info "Setting up virtual environment..."
cd "$BACKEND_DIR"

if [ ! -d ".venv" ]; then
    print_info "Creating virtual environment..."
    python3 -m venv .venv
    print_status "Virtual environment created"
else
    print_info "Virtual environment already exists"
fi

# Activate virtual environment and install dependencies
print_info "Installing Python dependencies..."
source .venv/bin/activate
pip install -r requirements.txt
print_status "Dependencies installed"

# Create output directory
print_info "Creating output directory..."
if [ "$EUID" -eq 0 ]; then
    mkdir -p /var/tmp/cli_masking
    chmod 777 /var/tmp/cli_masking
    print_status "Output directory created: /var/tmp/cli_masking"
else
    if sudo mkdir -p /var/tmp/cli_masking 2>/dev/null && sudo chmod 777 /var/tmp/cli_masking 2>/dev/null; then
        print_status "Output directory created: /var/tmp/cli_masking"
    else
        print_warning "Could not create system output directory (requires sudo)"
        print_info "Output will be saved to: $HOME/cli_masking"
        mkdir -p "$HOME/cli_masking"
        print_status "User output directory created: $HOME/cli_masking"
    fi
fi

echo ""
echo "🎉 Environment Setup Complete!"
echo "============================="
echo ""
print_status "Setup Summary:"
echo "  • Project Directory: $SCRIPT_DIR"
echo "  • Virtual Environment: $BACKEND_DIR/.venv"
echo "  • Output Directory: /var/tmp/cli_masking"
echo ""

print_status "Next Steps:"
echo "  1. Run: ./gdpr-cli help"
echo "  2. The CLI will automatically install itself globally"
echo "  3. After installation, you can run 'gdpr-cli' from anywhere"
echo ""

print_status "Environment setup completed successfully!"