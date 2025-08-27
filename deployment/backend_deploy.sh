#!/bin/bash

# Habit Rabbit Backend Deployment Script
# This script automates the backend deployment process

set -e  # Exit on any error

echo "🐰 Habit Rabbit Backend Deployment Script"
echo "=========================================="

# Configuration
BACKEND_DIR="/home/ubuntu/habit-rabbit/backend"
SERVICE_NAME="habit-rabbit-backend"
VENV_DIR="$BACKEND_DIR/venv"

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

# Check if running as correct user
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root. Run as ubuntu user."
   exit 1
fi

print_status "Starting backend deployment..."

# Create backend directory if it doesn't exist
if [ ! -d "$BACKEND_DIR" ]; then
    print_status "Creating backend directory..."
    mkdir -p "$BACKEND_DIR"
fi

cd "$BACKEND_DIR"

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    print_status "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    print_error "requirements.txt not found in $BACKEND_DIR"
    print_warning "Please ensure backend files are uploaded to $BACKEND_DIR"
    exit 1
fi

# Install/Update dependencies
print_status "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check if main.py exists
if [ ! -f "main.py" ]; then
    print_error "main.py not found in $BACKEND_DIR"
    print_warning "Please ensure backend files are uploaded to $BACKEND_DIR"
    exit 1
fi

# Create systemd service file
print_status "Creating systemd service file..."
sudo tee /etc/systemd/system/$SERVICE_NAME.service > /dev/null <<EOF
[Unit]
Description=Habit Rabbit FastAPI Backend
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=$BACKEND_DIR
Environment=PATH=$VENV_DIR/bin
ExecStart=$VENV_DIR/bin/python main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable service
print_status "Configuring systemd service..."
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME

# Start/Restart the service
print_status "Starting backend service..."
if sudo systemctl is-active --quiet $SERVICE_NAME; then
    print_status "Service is running. Restarting..."
    sudo systemctl restart $SERVICE_NAME
else
    print_status "Starting service for the first time..."
    sudo systemctl start $SERVICE_NAME
fi

# Wait a moment for service to start
sleep 3

# Check service status
if sudo systemctl is-active --quiet $SERVICE_NAME; then
    print_status "✅ Backend service is running successfully!"
    
    # Test the API
    print_status "Testing API endpoint..."
    if curl -s http://localhost:8000/ > /dev/null; then
        print_status "✅ API is responding correctly!"
    else
        print_warning "⚠️  API test failed. Check service logs."
    fi
else
    print_error "❌ Failed to start backend service!"
    print_warning "Check logs with: sudo journalctl -u $SERVICE_NAME -f"
    exit 1
fi

# Set up log rotation (optional)
print_status "Setting up log rotation..."
sudo tee /etc/logrotate.d/habit-rabbit-backend > /dev/null <<EOF
/var/log/habit-rabbit-backend.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    copytruncate
}
EOF

print_status "Deployment completed successfully! 🎉"
echo ""
echo "📋 Service Management Commands:"
echo "  Status:  sudo systemctl status $SERVICE_NAME"
echo "  Logs:    sudo journalctl -u $SERVICE_NAME -f"
echo "  Restart: sudo systemctl restart $SERVICE_NAME"
echo "  Stop:    sudo systemctl stop $SERVICE_NAME"
echo ""
echo "🌐 API Available at:"
echo "  Local:   http://localhost:8000"
echo "  Docs:    http://localhost:8000/docs"
echo ""
print_status "Backend deployment complete! 🐰"
