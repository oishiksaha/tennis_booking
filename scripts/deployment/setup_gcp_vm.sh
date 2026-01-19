#!/bin/bash
# Setup script for GCP VM deployment
# Run this on the GCP VM after initial setup

set -e

echo "=========================================="
echo "Tennis Booking Bot - GCP VM Setup"
echo "=========================================="

# Update system
echo "Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install Python and dependencies
echo "Installing Python and dependencies..."
sudo apt-get install -y python3 python3-pip python3-venv git curl

# Install Playwright system dependencies
echo "Installing Playwright system dependencies..."
sudo apt-get install -y \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpangocairo-1.0-0 \
    libatk1.0-0 \
    libcairo-gobject2 \
    libgtk-3-0 \
    libgdk-pixbuf2.0-0

# Set timezone (adjust to your timezone)
echo "Setting timezone to America/New_York..."
sudo timedatectl set-timezone America/New_York

# Create project directory
PROJECT_DIR="$HOME/tennis-booking-bot"
if [ ! -d "$PROJECT_DIR" ]; then
    echo "Creating project directory..."
    mkdir -p "$PROJECT_DIR"
fi

cd "$PROJECT_DIR"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
if [ -f "requirements.txt" ]; then
    echo "Installing Python dependencies..."
    pip install -r requirements.txt
else
    echo "WARNING: requirements.txt not found. Please upload it first."
fi

# Install Playwright browsers
echo "Installing Playwright browsers..."
playwright install chromium
playwright install-deps chromium

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p data/browser_state
mkdir -p logs

# Set permissions
chmod 755 "$PROJECT_DIR"
chmod -R 755 "$PROJECT_DIR/data"
chmod -R 755 "$PROJECT_DIR/logs"

echo ""
echo "=========================================="
echo "Setup complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Upload your project files to: $PROJECT_DIR"
echo "2. Copy your browser_state.json to: $PROJECT_DIR/data/browser_state/"
echo "3. Run: python src/main.py --authenticate (if needed)"
echo "4. Set up cron jobs using: scripts/setup_cron.sh"
echo ""

