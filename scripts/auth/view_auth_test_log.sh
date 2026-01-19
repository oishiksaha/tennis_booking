#!/bin/bash
# View authentication duration test log from VM

export CLOUDSDK_PYTHON=/opt/homebrew/bin/python3

echo "Authentication Duration Test Log"
echo "Press Ctrl+C to exit"
echo ""

gcloud compute ssh ubuntu@tennis-bot-vm --zone=us-central1-a --command="tail -f /tmp/auth_duration_test.log"

