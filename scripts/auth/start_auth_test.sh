#!/bin/bash
# Start authentication duration test on VM

export CLOUDSDK_PYTHON=/opt/homebrew/bin/python3

echo "Starting authentication duration test on VM..."
echo "This will test authentication every 2 minutes and log results"
echo ""

gcloud compute ssh ubuntu@tennis-bot-vm --zone=us-central1-a << 'ENDSSH'
cd ~/tennis-booking-bot
source venv/bin/activate
export PYTHONPATH=$HOME/tennis-booking-bot:$PYTHONPATH

# Kill any existing test
pkill -f test_auth_duration.py 2>/dev/null

# Start the test in background
nohup python scripts/test_auth_duration.py > /tmp/auth_test_output.log 2>&1 &

echo "Authentication test started with PID: $!"
echo "Log file: /tmp/auth_duration_test.log"
echo "Output log: /tmp/auth_test_output.log"
echo ""
echo "To view the test log:"
echo "  tail -f /tmp/auth_duration_test.log"
echo ""
echo "To view output:"
echo "  tail -f /tmp/auth_test_output.log"
ENDSSH

echo ""
echo "To view the test log from your local machine:"
echo "  bash scripts/view_auth_test_log.sh"

