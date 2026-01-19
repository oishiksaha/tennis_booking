#!/bin/bash
# View production booking logs from VM

export CLOUDSDK_PYTHON=/opt/homebrew/bin/python3

echo "Viewing booking logs from VM..."
echo ""

gcloud compute ssh ubuntu@tennis-bot-vm --zone=us-central1-a << 'ENDSSH'
cd ~/tennis-booking-bot

if [ ! -f logs/cron.log ]; then
    echo "No log file found at logs/cron.log"
    echo "Logs will be created when cron jobs run"
    exit 0
fi

echo "Last 50 lines of cron.log:"
echo "=========================="
tail -50 logs/cron.log

echo ""
echo "=========================="
echo "File size: $(du -h logs/cron.log | cut -f1)"
echo "Last modified: $(stat -c %y logs/cron.log 2>/dev/null || stat -f %Sm logs/cron.log)"
ENDSSH

