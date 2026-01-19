#!/bin/bash
# Quick script to test authentication on VM

export CLOUDSDK_PYTHON=/opt/homebrew/bin/python3

echo "Testing authentication on VM..."
echo ""

gcloud compute ssh ubuntu@tennis-bot-vm --zone=us-central1-a << 'ENDSSH'
cd ~/tennis-booking-bot
source venv/bin/activate
export PYTHONPATH=$HOME/tennis-booking-bot:$PYTHONPATH
python scripts/test_authentication.py
ENDSSH

