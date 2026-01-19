# Authentication Notifications Setup

**Last Updated**: January 18, 2026

This guide explains how to set up email and SMS notifications for authentication status checks.

## Overview

The notification system will:
- Check authentication status on Monday and Tuesday at 9 AM
- Send email and/or SMS notifications
- Alert you if authentication is working or failed

## Quick Setup

### Step 1: Configure Email/SMS

**Option A: Environment Variables (VM)**

Add to `~/.bashrc` or `~/.profile` on the VM:

```bash
# Email configuration
export NOTIFICATION_EMAIL_FROM="your-email@gmail.com"
export NOTIFICATION_EMAIL_PASSWORD="your-app-password"  # Gmail App Password
export NOTIFICATION_EMAIL_TO="recipient@example.com"

# SMS configuration (optional)
export SMS_EMAIL="1234567890@vtext.com"  # See carrier gateways below
```

**Option B: .env File (Local)**

Create `.env` file in project root:

```bash
NOTIFICATION_EMAIL_FROM=your-email@gmail.com
NOTIFICATION_EMAIL_PASSWORD=your-app-password
NOTIFICATION_EMAIL_TO=recipient@example.com
SMS_EMAIL=1234567890@vtext.com
```

### Step 2: Set Up Cron Jobs

**On VM:**
```bash
bash scripts/monitoring/setup_auth_notifications.sh
```

This will add cron jobs to check authentication on Monday and Tuesday at 9 AM.

### Step 3: Test

**Test notification manually:**
```bash
python scripts/monitoring/check_auth_and_notify.py
```

## Email Setup

### Gmail Setup

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate App Password**:
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" and "Other (Custom name)"
   - Enter "Tennis Bot"
   - Copy the 16-character password
3. **Use the app password** in `NOTIFICATION_EMAIL_PASSWORD`

### Other Email Providers

**Outlook/Hotmail:**
```bash
export SMTP_SERVER=smtp-mail.outlook.com
export SMTP_PORT=587
```

**Yahoo:**
```bash
export SMTP_SERVER=smtp.mail.yahoo.com
export SMTP_PORT=587
```

## SMS Setup (Email-to-SMS)

Most carriers support email-to-SMS gateways. Format: `phone_number@carrier_gateway.com`

### Carrier Gateways

| Carrier | Gateway |
|---------|---------|
| AT&T | `@txt.att.net` |
| Verizon | `@vtext.com` |
| T-Mobile | `@tmomail.net` |
| Sprint | `@messaging.sprintpcs.com` |
| US Cellular | `@email.uscc.net` |
| Cricket | `@sms.cricketwireless.net` |

### Example

For Verizon number `1234567890`:
```bash
export SMS_EMAIL="1234567890@vtext.com"
```

## Notification Schedule

**Default schedule:**
- **Monday**: 9:00 AM EST
- **Tuesday**: 9:00 AM EST

**To change schedule**, edit cron jobs:
```bash
crontab -e
```

Look for lines with `check_auth_and_notify.py` and modify the time.

## Notification Content

### Success Notification
```
Subject: ✅ Tennis Bot: Authentication Working

Status: ✅ WORKING
Time: 2026-01-20 09:00:00

Authentication is working correctly. The bot is ready to book courts.
```

### Failure Notification
```
Subject: ❌ Tennis Bot: Authentication Failed

Status: ❌ FAILED
Time: 2026-01-20 09:00:00

Authentication has failed. The bot cannot book courts.

Action Required:
1. Check the VM logs
2. Re-authenticate
3. Check keep-alive service
```

## Manual Testing

**Test email notification:**
```bash
python scripts/monitoring/check_auth_and_notify.py
```

**Test with custom email:**
```bash
NOTIFICATION_EMAIL_TO="test@example.com" python scripts/monitoring/check_auth_and_notify.py
```

## Troubleshooting

### "Email credentials not configured"
- Check that environment variables are set
- Verify `.env` file exists (if using local)
- On VM, ensure variables are in `~/.bashrc` or `~/.profile`

### "Failed to send email"
- Verify Gmail App Password is correct
- Check SMTP server and port settings
- Ensure 2FA is enabled on Gmail account

### "SMS not working"
- Verify carrier gateway format is correct
- Check phone number format (digits only, no dashes)
- Some carriers may have delays

## Security Notes

- **Never commit** `.env` file or credentials to git
- Use **App Passwords** instead of your main password
- Consider using **GCP Secret Manager** for production

## Advanced: Custom Schedule

To check authentication at different times, edit cron:

```bash
# Check Monday at 8 AM and Tuesday at 10 AM
0 8 * * 1 python scripts/monitoring/check_auth_and_notify.py
0 10 * * 2 python scripts/monitoring/check_auth_and_notify.py
```

Cron format: `minute hour day month weekday command`

## See Also

- **[AUTHENTICATION_INFO.md](AUTHENTICATION_INFO.md)** - Authentication details
- **[PRODUCTION_SETUP.md](PRODUCTION_SETUP.md)** - Production setup guide

