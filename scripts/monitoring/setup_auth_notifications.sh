#!/bin/bash
# Set up authentication notifications for Monday and Tuesday

export CLOUDSDK_PYTHON=/opt/homebrew/bin/python3

echo "=========================================="
echo "Authentication Notification Setup"
echo "=========================================="
echo ""
echo "This will set up cron jobs to check authentication"
echo "and send email/SMS notifications on Monday and Tuesday."
echo ""

# Check if running on VM or locally
if [ -f ~/.ssh/google_compute_engine ]; then
    echo "Detected: Running on GCP VM"
    VM_MODE=true
else
    echo "Detected: Running locally"
    VM_MODE=false
fi

echo ""
echo "Configuration needed:"
echo "1. Email credentials (for email notifications)"
echo "2. Optional: SMS email gateway (for SMS notifications)"
echo ""
read -p "Continue with setup? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Setup cancelled"
    exit 0
fi

echo ""
echo "Setting up cron jobs..."

if [ "$VM_MODE" = true ]; then
    # On VM
    PROJECT_DIR="$HOME/tennis-booking-bot"
    VENV_PYTHON="$PROJECT_DIR/venn/bin/python"
    SCRIPT="$PROJECT_DIR/scripts/monitoring/check_auth_and_notify.py"
    
    # Add cron jobs for Monday and Tuesday at 9 AM
    (crontab -l 2>/dev/null | grep -v "check_auth_and_notify"; cat << EOF
# Authentication check notifications - Monday and Tuesday at 9 AM
0 9 * * 1 cd $PROJECT_DIR && source venv/bin/activate && export PYTHONPATH=\$HOME/tennis-booking-bot:\$PYTHONPATH && python $SCRIPT >> $PROJECT_DIR/logs/auth_check.log 2>&1
0 9 * * 2 cd $PROJECT_DIR && source venv/bin/activate && export PYTHONPATH=\$HOME/tennis-booking-bot:\$PYTHONPATH && python $SCRIPT >> $PROJECT_DIR/logs/auth_check.log 2>&1
EOF
    ) | crontab -
    
    echo "✅ Cron jobs added for Monday and Tuesday at 9 AM"
    echo ""
    echo "To configure email/SMS, set environment variables:"
    echo "  export NOTIFICATION_EMAIL_FROM='your-email@gmail.com'"
    echo "  export NOTIFICATION_EMAIL_PASSWORD='your-app-password'"
    echo "  export NOTIFICATION_EMAIL_TO='recipient@example.com'"
    echo "  export SMS_EMAIL='1234567890@vtext.com'  # Optional, for SMS"
    echo ""
    echo "Add these to ~/.bashrc or ~/.profile to persist"
    
else
    # Local setup
    PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
    SCRIPT="$PROJECT_DIR/scripts/monitoring/check_auth_and_notify.py"
    
    echo "For local setup, you can:"
    echo "1. Run manually: python $SCRIPT"
    echo "2. Set up launchd (macOS): See scripts/setup/setup_launchd.sh"
    echo ""
    echo "To configure email/SMS, create a .env file:"
    echo "  NOTIFICATION_EMAIL_FROM=your-email@gmail.com"
    echo "  NOTIFICATION_EMAIL_PASSWORD=your-app-password"
    echo "  NOTIFICATION_EMAIL_TO=recipient@example.com"
    echo "  SMS_EMAIL=1234567890@vtext.com"
fi

echo ""
echo "=========================================="
echo "Setup complete!"
echo "=========================================="

