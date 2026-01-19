#!/bin/bash
# Script to re-authenticate on the VM
# This opens a browser session on the VM for authentication

export CLOUDSDK_PYTHON=/opt/homebrew/bin/python3

echo "Re-authenticating on VM..."
echo "This will open a browser window on the VM for you to sign in."
echo ""

gcloud compute ssh ubuntu@tennis-bot-vm --zone=us-central1-a --command="cd ~/tennis-booking-bot && source venv/bin/activate && export PYTHONPATH=\$HOME/tennis-booking-bot:\$PYTHONPATH && DISPLAY=:0 python -m src.main --authenticate"

