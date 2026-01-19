#!/bin/bash
# Set up email notifications on the VM

export CLOUDSDK_PYTHON=/opt/homebrew/bin/python3

VM_NAME="tennis-bot-vm"
ZONE="us-central1-a"
VM_USER="ubuntu"

echo "=========================================="
echo "Email Notifications Setup"
echo "=========================================="
echo ""

# Check if running locally or on VM
if [ -f ~/.ssh/google_compute_engine ]; then
    echo "Detected: Running on GCP VM"
    ON_VM=true
else
    echo "Detected: Running locally - will configure VM"
    ON_VM=false
fi

echo ""
echo "This will configure email notifications for booking attempts."
echo ""

# Get email configuration
if [ "$ON_VM" = false ]; then
    echo "Email Configuration:"
    echo ""
    read -p "Gmail address (tennisbot2026@gmail.com): " EMAIL_FROM
    EMAIL_FROM=${EMAIL_FROM:-tennisbot2026@gmail.com}
    
    echo ""
    echo "Email Provider Options:"
    echo "1. Gmail (requires App Password with 2FA)"
    echo "2. Outlook/Hotmail (uses regular password - recommended)"
    echo "3. Yahoo (uses regular password)"
    echo ""
    read -p "Choose provider (1=gmail, 2=outlook, 3=yahoo) [2]: " PROVIDER
    PROVIDER=${PROVIDER:-2}
    
    case $PROVIDER in
        1)
            SMTP_SERVER="smtp.gmail.com"
            SMTP_PORT="587"
            echo ""
            echo "To get Gmail App Password:"
            echo "1. Go to: https://myaccount.google.com/apppasswords"
            echo "2. Enable 2FA if needed"
            echo "3. Create App Password for 'Mail'"
            echo "4. Copy the 16-character password"
            echo ""
            read -p "Gmail App Password (16 characters): " EMAIL_PASSWORD
            ;;
        2)
            SMTP_SERVER="smtp-mail.outlook.com"
            SMTP_PORT="587"
            echo ""
            echo "Using Outlook/Hotmail (regular password)"
            read -p "Outlook password: " EMAIL_PASSWORD
            ;;
        3)
            SMTP_SERVER="smtp.mail.yahoo.com"
            SMTP_PORT="587"
            echo ""
            echo "Using Yahoo (regular password)"
            read -p "Yahoo password: " EMAIL_PASSWORD
            ;;
        *)
            echo "Invalid choice, using Outlook"
            SMTP_SERVER="smtp-mail.outlook.com"
            SMTP_PORT="587"
            read -p "Email password: " EMAIL_PASSWORD
            ;;
    esac
    
    echo ""
    read -p "Recipient email (where to send notifications): " EMAIL_TO
    
    echo ""
    echo "Configuring on VM..."
    
    # Configure on VM
    gcloud compute ssh "$VM_USER@$VM_NAME" --zone="$ZONE" << ENDSSH
# Set environment variables
export SMTP_SERVER="$SMTP_SERVER"
export SMTP_PORT="$SMTP_PORT"
export NOTIFICATION_EMAIL_FROM="$EMAIL_FROM"
export NOTIFICATION_EMAIL_PASSWORD="$EMAIL_PASSWORD"
export NOTIFICATION_EMAIL_TO="$EMAIL_TO"

# Add to ~/.bashrc to persist
if ! grep -q "NOTIFICATION_EMAIL_FROM" ~/.bashrc 2>/dev/null; then
    echo "" >> ~/.bashrc
    echo "# Tennis Bot Email Notifications" >> ~/.bashrc
    echo "export SMTP_SERVER=\"$SMTP_SERVER\"" >> ~/.bashrc
    echo "export SMTP_PORT=\"$SMTP_PORT\"" >> ~/.bashrc
    echo "export NOTIFICATION_EMAIL_FROM=\"$EMAIL_FROM\"" >> ~/.bashrc
    echo "export NOTIFICATION_EMAIL_PASSWORD=\"$EMAIL_PASSWORD\"" >> ~/.bashrc
    echo "export NOTIFICATION_EMAIL_TO=\"$EMAIL_TO\"" >> ~/.bashrc
    echo "✅ Added to ~/.bashrc"
else
    echo "⚠️  Email variables already in ~/.bashrc"
    echo "   You may need to update them manually"
fi

# Test notification
echo ""
echo "Testing email notification..."
cd ~/tennis-booking-bot
source venv/bin/activate
export PYTHONPATH=\$HOME/tennis-booking-bot:\$PYTHONPATH
python scripts/monitoring/check_auth_and_notify.py

echo ""
echo "✅ Email configuration complete!"
echo ""
echo "Environment variables set:"
echo "  NOTIFICATION_EMAIL_FROM=$EMAIL_FROM"
echo "  NOTIFICATION_EMAIL_TO=$EMAIL_TO"
echo ""
echo "Notifications will be sent automatically after each booking attempt."
ENDSSH

else
    # Running on VM directly
    echo "Enter email configuration:"
    read -p "Gmail address: " EMAIL_FROM
    read -p "Gmail App Password: " EMAIL_PASSWORD
    read -p "Recipient email: " EMAIL_TO
    
    export NOTIFICATION_EMAIL_FROM="$EMAIL_FROM"
    export NOTIFICATION_EMAIL_PASSWORD="$EMAIL_PASSWORD"
    export NOTIFICATION_EMAIL_TO="$EMAIL_TO"
    
    # Add to ~/.bashrc
    if ! grep -q "NOTIFICATION_EMAIL_FROM" ~/.bashrc 2>/dev/null; then
        echo "" >> ~/.bashrc
        echo "# Tennis Bot Email Notifications" >> ~/.bashrc
        echo "export NOTIFICATION_EMAIL_FROM=\"$EMAIL_FROM\"" >> ~/.bashrc
        echo "export NOTIFICATION_EMAIL_PASSWORD=\"$EMAIL_PASSWORD\"" >> ~/.bashrc
        echo "export NOTIFICATION_EMAIL_TO=\"$EMAIL_TO\"" >> ~/.bashrc
        echo "✅ Added to ~/.bashrc"
    else
        echo "⚠️  Email variables already in ~/.bashrc"
    fi
    
    # Test notification
    echo ""
    echo "Testing email notification..."
    cd ~/tennis-booking-bot
    source venv/bin/activate
    export PYTHONPATH=$HOME/tennis-booking-bot:$PYTHONPATH
    python scripts/monitoring/check_auth_and_notify.py
fi

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Email notifications are now configured."
echo "You will receive an email after each booking attempt."
echo ""

