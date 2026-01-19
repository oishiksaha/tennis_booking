#!/bin/bash
# Quick script to check cron jobs on VM
# Shows all tennis-bot related cron jobs with their schedules

export CLOUDSDK_PYTHON=/opt/homebrew/bin/python3

echo "Checking cron jobs on VM..."
echo ""

gcloud compute ssh ubuntu@tennis-bot-vm --zone=us-central1-a << 'ENDSSH'
echo "=== Cron Service Status ==="
systemctl status cron 2>/dev/null | grep -E "Active:|Main PID:" || service cron status 2>/dev/null | grep -E "Active:|Main PID:" || echo "Cron service check failed"
echo ""

echo "=== Tennis Booking Bot Cron Jobs ==="
crontab -l 2>/dev/null | grep -B 1 -A 1 "tennis-booking-bot" | grep -E "^#|^[0-9]" || echo "No cron jobs found"
echo ""

echo "=== All Cron Jobs (formatted) ==="
crontab -l 2>/dev/null | grep -E "^[0-9]" | while read line; do
    minute=$(echo "$line" | awk '{print $1}')
    hour=$(echo "$line" | awk '{print $2}')
    
    # Convert to readable format
    if [ "$hour" -lt 12 ]; then
        am_pm="AM"
        display_hour=$hour
        if [ "$hour" -eq 0 ]; then
            display_hour=12
        fi
    else
        am_pm="PM"
        display_hour=$((hour - 12))
        if [ "$hour" -eq 12 ]; then
            display_hour=12
        fi
    fi
    
    printf "  %02d:%02d %s - " "$display_hour" "$minute" "$am_pm"
    echo "$line" | awk '{for(i=6;i<=NF;i++) printf "%s ", $i; print ""}'
done

echo ""
echo "=== Next Run Times ==="
echo "Cron jobs will run at:"
crontab -l 2>/dev/null | grep -E "^[0-9]" | awk '{print $2 ":" $1}' | sort | while read time; do
    hour=$(echo "$time" | cut -d':' -f1)
    minute=$(echo "$time" | cut -d':' -f2)
    
    if [ "$hour" -lt 12 ]; then
        am_pm="AM"
        display_hour=$hour
        if [ "$hour" -eq 0 ]; then
            display_hour=12
        fi
    else
        am_pm="PM"
        display_hour=$((hour - 12))
        if [ "$hour" -eq 12 ]; then
            display_hour=12
        fi
    fi
    
    printf "  %d:%02d %s\n" "$display_hour" "$minute" "$am_pm"
done
ENDSSH

