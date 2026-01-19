#!/bin/bash
# Setup cron jobs for scheduled booking execution
# Run this on the GCP VM after authentication is set up
# This script reads booking_times from config.yaml and generates cron jobs automatically

set -e

PROJECT_DIR="$HOME/tennis-booking-bot"
VENV_PYTHON="$PROJECT_DIR/venv/bin/python"
MAIN_SCRIPT="$PROJECT_DIR/src/main.py"
CONFIG_FILE="$PROJECT_DIR/config/config.yaml"
LOG_FILE="$PROJECT_DIR/logs/cron.log"

echo "=========================================="
echo "Setting up Cron Jobs for Tennis Booking Bot"
echo "=========================================="

# Ensure log directory exists
mkdir -p "$PROJECT_DIR/logs"

# Check if config file exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo "ERROR: Config file not found at $CONFIG_FILE"
    exit 1
fi

# Extract booking times from config.yaml using Python
echo "Reading booking times from config.yaml..."
BOOKING_TIMES=$(cd "$PROJECT_DIR" && $VENV_PYTHON << 'PYTHON_SCRIPT'
import yaml
import sys
from pathlib import Path

try:
    config_path = Path('config/config.yaml')
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    booking_times = config.get('booking_times', [])
    for time_str in booking_times:
        print(time_str)
except Exception as e:
    print(f"Error reading config: {e}", file=sys.stderr)
    sys.exit(1)
PYTHON_SCRIPT
)

if [ -z "$BOOKING_TIMES" ]; then
    echo "ERROR: No booking times found in config.yaml"
    exit 1
fi

echo "Found booking times:"
echo "$BOOKING_TIMES" | while read time; do
    echo "  - $time"
done

# Create temporary crontab file
TEMP_CRON=$(mktemp)

# Get current crontab (if exists)
crontab -l 2>/dev/null > "$TEMP_CRON" || true

# Remove any existing tennis-bot cron jobs
grep -v "tennis-booking-bot\|tennis-bot" "$TEMP_CRON" > "${TEMP_CRON}.new" || true
mv "${TEMP_CRON}.new" "$TEMP_CRON"

# Add header comment
cat >> "$TEMP_CRON" << EOF

# Tennis Booking Bot - Scheduled Execution
# Generated automatically from config.yaml
# Runs exactly on the hour when slots open (e.g., 7:00 for 7:00 AM booking)
EOF

# Generate cron jobs for each booking time
# Format: minute hour day month weekday command
# Run exactly on the hour when slots open (e.g., 7:00 for 7:00 AM booking)
echo "$BOOKING_TIMES" | while read time_str; do
    if [ -z "$time_str" ]; then
        continue
    fi
    
    # Parse time (format: "HH:MM")
    hour=$(echo "$time_str" | cut -d':' -f1 | sed 's/^0*//')  # Remove leading zeros
    minute=$(echo "$time_str" | cut -d':' -f2 | sed 's/^0*//')
    
    # Handle empty strings (e.g., "07" -> "7")
    if [ -z "$hour" ]; then
        hour=0
    fi
    if [ -z "$minute" ]; then
        minute=0
    fi
    
    # Convert to integers
    hour=$((10#$hour))
    minute=$((10#$minute))
    
    # Use the exact booking time for cron (slots open exactly on the hour)
    cron_minute=$minute
    cron_hour=$hour
    
    # Format time for display
    display_hour=$hour
    display_minute=$(printf "%02d" $minute)
    if [ $hour -lt 12 ]; then
        am_pm="AM"
        if [ $hour -eq 0 ]; then
            display_hour=12
        fi
    else
        am_pm="PM"
        if [ $hour -gt 12 ]; then
            display_hour=$((hour - 12))
        fi
    fi
    
    # Add cron job
    cat >> "$TEMP_CRON" << CRON_EOF
# Run at ${display_hour}:${display_minute} ${am_pm} (exactly when ${display_hour}:${display_minute} ${am_pm} slots open)
$(printf "%02d" $cron_minute) ${cron_hour} * * * cd $PROJECT_DIR && $VENV_PYTHON $MAIN_SCRIPT --headless >> $LOG_FILE 2>&1

CRON_EOF
done

# Install the new crontab
crontab "$TEMP_CRON"
rm "$TEMP_CRON"

echo "Cron jobs installed successfully!"
echo ""
echo "Current cron jobs:"
crontab -l | grep -A 10 "Tennis Booking Bot"
echo ""
echo "Logs will be written to: $LOG_FILE"
echo ""
echo "To view logs: tail -f $LOG_FILE"
echo "To edit cron jobs: crontab -e"
echo "To list cron jobs: crontab -l"

