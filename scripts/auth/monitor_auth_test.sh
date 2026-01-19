#!/bin/bash
# Monitor the authentication test in real-time

export CLOUDSDK_PYTHON=/opt/homebrew/bin/python3

echo "Monitoring authentication test (every 2 minutes)..."
echo "Press Ctrl+C to stop"
echo ""

gcloud compute ssh ubuntu@tennis-bot-vm --zone=us-central1-a --command="tail -f /tmp/auth_duration_test.log"

