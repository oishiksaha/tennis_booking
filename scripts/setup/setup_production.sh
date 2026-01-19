#!/bin/bash
# Complete production setup script
# Run this after the 2:30 PM test to enable production bookings

export CLOUDSDK_PYTHON=/opt/homebrew/bin/python3

echo "=========================================="
echo "Production Setup for Tennis Booking Bot"
echo "=========================================="
echo ""

echo "Step 1: Disabling test mode..."
gcloud compute ssh ubuntu@tennis-bot-vm --zone=us-central1-a << 'ENDSSH'
cd ~/tennis-booking-bot
# Disable test mode
python3 << 'PYTHON'
import yaml
from pathlib import Path

config_path = Path('config/config.yaml')
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

config['test_mode']['enabled'] = False

with open(config_path, 'w') as f:
    yaml.dump(config, f, default_flow_style=False, sort_keys=False)

print("✓ Test mode disabled")
PYTHON
ENDSSH

echo ""
echo "Step 2: Verifying authentication..."
gcloud compute ssh ubuntu@tennis-bot-vm --zone=us-central1-a << 'ENDSSH'
cd ~/tennis-booking-bot
source venv/bin/activate
export PYTHONPATH=$HOME/tennis-booking-bot:$PYTHONPATH
python scripts/test_authentication.py
ENDSSH

echo ""
echo "Step 3: Setting up cron jobs..."
gcloud compute ssh ubuntu@tennis-bot-vm --zone=us-central1-a << 'ENDSSH'
cd ~/tennis-booking-bot
bash scripts/setup_cron.sh
ENDSSH

echo ""
echo "=========================================="
echo "Production Setup Complete!"
echo "=========================================="
echo ""
echo "The bot will now run automatically at:"
echo "  - 7:00 AM daily (books 7 days ahead at 7 AM)"
echo "  - 8:00 AM daily (books 7 days ahead at 8 AM)"
echo "  - 5:00 PM daily (books 7 days ahead at 5 PM)"
echo "  - 6:00 PM daily (books 7 days ahead at 6 PM)"
echo "  - 7:00 PM daily (books 7 days ahead at 7 PM)"
echo ""
echo "Logs: ~/tennis-booking-bot/logs/cron.log"
echo "View logs: bash scripts/view_vm_logs.sh"
echo ""

