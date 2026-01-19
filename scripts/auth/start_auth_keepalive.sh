#!/bin/bash
# Start authentication keep-alive service on VM

export CLOUDSDK_PYTHON=/opt/homebrew/bin/python3

echo "Starting authentication keep-alive service on VM..."
echo "This will visit the booking page every 10 minutes to keep the session alive"
echo ""

gcloud compute ssh ubuntu@tennis-bot-vm --zone=us-central1-a << 'ENDSSH'
cd ~/tennis-booking-bot
source venv/bin/activate
export PYTHONPATH=$HOME/tennis-booking-bot:$PYTHONPATH

# Kill any existing keep-alive service
pkill -f auth_keepalive.py 2>/dev/null

# Start the keep-alive service in background
nohup python scripts/auth_keepalive.py > /tmp/auth_keepalive_output.log 2>&1 &
PID=$!

echo "Keep-alive service started with PID: $PID"
echo "Log file: /tmp/auth_keepalive.log"
echo "Output log: /tmp/auth_keepalive_output.log"
echo ""
echo "To view the keep-alive log:"
echo "  tail -f /tmp/auth_keepalive.log"
echo ""
echo "To view output:"
echo "  tail -f /tmp/auth_keepalive_output.log"
echo ""
echo "To stop the service:"
echo "  pkill -f auth_keepalive.py"
ENDSSH

echo ""
echo "To view the keep-alive log from your local machine:"
echo "  bash scripts/view_auth_keepalive_log.sh"

