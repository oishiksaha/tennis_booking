# Production Setup Guide

## Overview
This guide ensures the bot is ready for automated weekly bookings with proper logging.

## Pre-Flight Checklist

### 1. Test Mode Status
**IMPORTANT**: Test mode must be DISABLED for production bookings.

Check `config/config.yaml`:
```yaml
test_mode:
  enabled: false  # MUST be false for production
```

### 2. Authentication Status
Verify authentication is working:
```bash
# On VM
bash scripts/test_auth_vm.sh

# Should show: ✅ AUTHENTICATION SUCCESSFUL
```

### 3. Configuration
Verify booking times in `config/config.yaml`:
```yaml
booking_times:
  - "07:00"  # 7 AM
  - "08:00"  # 8 AM
  - "17:00"  # 5 PM
  - "18:00"  # 6 PM
  - "19:00"  # 7 PM

booking_window_days: 7  # Books 7 days ahead
```

### 4. Cron Jobs Setup
Set up automated weekly bookings:
```bash
# On VM
cd ~/tennis-booking-bot
bash scripts/setup_cron.sh
```

This creates cron jobs that run at:
- 7:00 AM daily (books 7 days ahead at 7 AM)
- 8:00 AM daily (books 7 days ahead at 8 AM)
- 5:00 PM daily (books 7 days ahead at 5 PM)
- 6:00 PM daily (books 7 days ahead at 6 PM)
- 7:00 PM daily (books 7 days ahead at 7 PM)

### 5. Logging
Logs are automatically written to:
- **Cron logs**: `~/tennis-booking-bot/logs/cron.log`
- **Rotating**: Max 10MB per file, keeps 5 backups
- **Format**: Timestamp, logger name, level, message

## Log Monitoring

### View Recent Logs
```bash
# On VM
tail -f ~/tennis-booking-bot/logs/cron.log

# Or from local
bash scripts/view_vm_logs.sh  # (create this if needed)
```

### Check Specific Booking
```bash
# Search for successful bookings
grep "BOOKING SUCCESSFUL" ~/tennis-booking-bot/logs/cron.log

# Search for errors
grep "ERROR\|FAILED" ~/tennis-booking-bot/logs/cron.log

# Search by date
grep "2026-01-18" ~/tennis-booking-bot/logs/cron.log
```

### Log Structure
Each booking attempt logs:
```
================================================================================
Starting booking process at 2026-01-18 07:00:00
Test mode: DISABLED
  Target times: ['07:00', '08:00', '17:00', '18:00', '19:00']
  Booking window: 7 days ahead
================================================================================
✅ Authentication successful
[booking process details...]
================================================================================
✅ BOOKING SUCCESSFUL
   Court: Murr Tennis: Court 2
   Date: 2026-01-25
   Time: 7:00 - 8:00 AM
   Completed at: 2026-01-18 07:00:15
================================================================================
```

## Weekly Booking Schedule

The bot runs **every day** at the configured times:
- **7:00 AM**: Attempts to book 7 days ahead at 7 AM
- **8:00 AM**: Attempts to book 7 days ahead at 8 AM
- **5:00 PM**: Attempts to book 7 days ahead at 5 PM
- **6:00 PM**: Attempts to book 7 days ahead at 6 PM
- **7:00 PM**: Attempts to book 7 days ahead at 7 PM

**Example**: On Monday at 7:00 AM, it books for next Monday at 7:00 AM.

## Troubleshooting

### Authentication Expired
If bookings fail due to authentication:
```bash
# On VM (requires X11 forwarding or local machine)
python -m src.main --authenticate

# Then copy browser state to VM
# (from local machine)
gcloud compute scp data/browser_state/browser_state.json ubuntu@tennis-bot-vm:~/tennis-booking-bot/data/browser_state/ --zone=us-central1-a
```

### Check Cron Jobs
```bash
# List cron jobs
crontab -l

# Check if cron is running
systemctl status cron

# View cron execution logs
grep CRON /var/log/syslog | tail -20
```

### Verify Booking Success
```bash
# Use manual mode to view bookings
python -m src.main --manual
# Then select option 4: View my bookings
```

## Maintenance

### Weekly Tasks
1. Check logs for any errors
2. Verify bookings were made (use manual mode option 4)
3. Check authentication status (should last several days/weeks)

### Monthly Tasks
1. Review log file sizes
2. Check VM disk space
3. Verify cron jobs are still active

## Current Status

After 2:30 PM test completes:
1. ✅ Verify test booking was made
2. ✅ Disable test mode in config
3. ✅ Set up production cron jobs
4. ✅ Verify authentication is working
5. ✅ Monitor first production booking

