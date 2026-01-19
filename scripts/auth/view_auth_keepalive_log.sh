#!/bin/bash
# View the authentication keep-alive log from the VM

export CLOUDSDK_PYTHON=/opt/homebrew/bin/python3

gcloud compute ssh ubuntu@tennis-bot-vm --zone=us-central1-a --command="tail -50 /tmp/auth_keepalive.log 2>/dev/null || echo 'Log file not found or empty'"

